from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.drone import DroneCreate, DroneRead, DroneUpdate
from app.services.drone_service import DroneService

router = APIRouter()


def get_drone_service(db: AsyncSession = Depends(get_db)) -> DroneService:
    return DroneService(db)


@router.post(
    "/",
    response_model=DroneRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new drone",
    responses={401: {"description": "Not authenticated"}},
)
async def register_drone(
    payload: DroneCreate,
    svc: DroneService = Depends(get_drone_service),
    _: User = Depends(get_current_user),
) -> DroneRead:
    return await svc.register(payload)


@router.get(
    "/available",
    response_model=list[DroneRead],
    summary="List drones ready for delivery (IDLE + battery > 25 %)",
)
async def list_available_drones(
    svc: DroneService = Depends(get_drone_service),
) -> list[DroneRead]:
    return await svc.get_available()


@router.get(
    "/{drone_id}",
    response_model=DroneRead,
    summary="Get a drone by ID",
)
async def get_drone(
    drone_id: int,
    svc: DroneService = Depends(get_drone_service),
) -> DroneRead:
    return await svc.get_or_404(drone_id)


@router.get(
    "/",
    response_model=list[DroneRead],
    summary="List all drones",
)
async def list_drones(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    svc: DroneService = Depends(get_drone_service),
) -> list[DroneRead]:
    return await svc.get_all(offset=offset, limit=limit)


@router.patch(
    "/{drone_id}",
    response_model=DroneRead,
    summary="Partially update a drone",
)
async def update_drone(
    drone_id: int,
    payload: DroneUpdate,
    svc: DroneService = Depends(get_drone_service),
) -> DroneRead:
    return await svc.patch(drone_id, payload)


@router.delete(
    "/{drone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a drone",
)
async def delete_drone(
    drone_id: int,
    svc: DroneService = Depends(get_drone_service),
) -> None:
    drone = await svc.get_or_404(drone_id)
    await svc.delete(drone)
