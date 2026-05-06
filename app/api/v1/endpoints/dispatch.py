from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.route import RouteRead
from app.services.dispatch_service import DispatchService

router = APIRouter()


class DispatchRequest(BaseModel):
    package_id: int = Field(..., description="ID of the package to dispatch")
    origin_address: str = Field(
        ..., max_length=300, description="Pickup / depot address"
    )
    destination_address: str = Field(
        ..., max_length=300, description="Delivery address"
    )


@router.post(
    "/",
    response_model=RouteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch a package",
    responses={
        404: {"description": "Package not found"},
        409: {"description": "Package already dispatched or no drones available"},
    },
)
async def dispatch_package(
    payload: DispatchRequest,
    db: AsyncSession = Depends(get_db),
) -> RouteRead:
    """
    Assign the best available drone to a package and open a delivery route.

    **Election criteria:** IDLE status and battery capacity > 25 %, ranked by
    highest battery first.

    **Side-effects on success:**
    - A new `Route` with status `PENDING` is created.
    - The elected drone transitions to `LOADING`.
    """
    svc = DispatchService(db)
    return await svc.dispatch(
        payload.package_id,
        payload.origin_address,
        payload.destination_address,
    )
