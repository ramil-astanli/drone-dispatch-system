from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.services import route_service

router = APIRouter()


@router.get("/", response_model=list[RouteRead])
async def list_routes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[RouteRead]:
    return await route_service.get_all(db, offset=offset, limit=limit)


@router.get("/{route_id}", response_model=RouteRead)
async def get_route(route_id: int, db: AsyncSession = Depends(get_db)) -> RouteRead:
    route = await route_service.get_by_id(db, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return route


@router.post("/", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
async def create_route(
    payload: RouteCreate, db: AsyncSession = Depends(get_db)
) -> RouteRead:
    return await route_service.create(db, payload)


@router.patch("/{route_id}", response_model=RouteRead)
async def update_route(
    route_id: int, payload: RouteUpdate, db: AsyncSession = Depends(get_db)
) -> RouteRead:
    route = await route_service.get_by_id(db, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return await route_service.update(db, route, payload)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: int, db: AsyncSession = Depends(get_db)) -> None:
    route = await route_service.get_by_id(db, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    await route_service.delete(db, route)
