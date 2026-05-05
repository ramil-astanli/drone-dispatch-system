from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PackageAlreadyDispatchedError, PackageNotFoundError
from app.models.drone import DroneStatus
from app.models.package import Package
from app.models.route import Route, RouteStatus
from app.services.drone_service import DroneService


class DispatchService:
    """
    Orchestrates the full dispatch flow:
      1. Validate the package exists and has not already been dispatched.
      2. Elect the best available drone (highest battery, IDLE, > 25 %).
      3. Create a PENDING Route linking drone → package.
      4. Transition the drone to LOADING.
    All steps share the same unit-of-work; get_db commits or rolls back atomically.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._drone_svc = DroneService(db)

    async def dispatch(
        self, package_id: int, origin_address: str, destination_address: str
    ) -> Route:
        # ── 1. Resolve package ────────────────────────────────────────────────
        package: Package | None = await self.db.get(Package, package_id)
        if package is None:
            raise PackageNotFoundError(package_id)

        # ── 2. Guard: already dispatched? ─────────────────────────────────────
        # package.route is loaded via lazy="selectin" on the relationship
        if package.route is not None:
            raise PackageAlreadyDispatchedError(package_id)

        # ── 3. Elect best drone ───────────────────────────────────────────────
        # Raises NoDronesAvailableError automatically if none qualify
        drone = await self._drone_svc.get_best_available()

        # ── 4. Build route ────────────────────────────────────────────────────
        # Destination is always the recipient customer's registered address.
        route = Route(
            drone_id=drone.id,
            package_id=package.id,
            origin_address=origin_address,
            destination_address=destination_address,
            status=RouteStatus.PENDING,
        )
        self.db.add(route)

        # ── 5. Mark drone as loading ──────────────────────────────────────────
        drone.status = DroneStatus.LOADING

        await self.db.flush()
        await self.db.refresh(route)
        return route
