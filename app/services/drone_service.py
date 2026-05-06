from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DroneNotFoundError, NoDronesAvailableError
from app.models.drone import Drone, DroneStatus
from app.schemas.drone import DroneCreate, DroneUpdate
from app.services.base import BaseService


class DroneService(BaseService[Drone]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Drone, db)


    async def get_or_404(self, drone_id: int) -> Drone:
        """Return the drone or raise a 404 HTTP exception."""
        drone = await self.get_by_id(drone_id)
        if drone is None:
            raise DroneNotFoundError(drone_id)
        return drone

    async def register(self, payload: DroneCreate) -> Drone:
        """Persist a new drone and return it."""
        return await self.create(payload)

    async def get_available(self) -> list[Drone]:
        """
        Return all drones that are IDLE with battery > 25 %,
        ordered from highest to lowest battery.
        """
        result = await self.db.execute(
            select(Drone)
            .where(Drone.status == DroneStatus.IDLE)
            .where(Drone.battery_capacity > 25)
            .order_by(Drone.battery_capacity.desc())
        )
        return list(result.scalars().all())

    async def get_best_available(self) -> Drone:
        """
        Return the single drone with the highest battery that is still
        eligible for dispatch.  Raises NoDronesAvailableError if none exist.
        """
        result = await self.db.execute(
            select(Drone)
            .where(Drone.status == DroneStatus.IDLE)
            .where(Drone.battery_capacity > 25)
            .order_by(Drone.battery_capacity.desc())
            .limit(1)
        )
        drone = result.scalar_one_or_none()
        if drone is None:
            raise NoDronesAvailableError()
        return drone

    async def patch(self, drone_id: int, payload: DroneUpdate) -> Drone:
        drone = await self.get_or_404(drone_id)
        return await self.update(drone, payload)
