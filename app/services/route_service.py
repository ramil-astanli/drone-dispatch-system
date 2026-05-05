from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.schemas.route import RouteCreate, RouteUpdate


async def get_all(db: AsyncSession, *, offset: int = 0, limit: int = 100) -> list[Route]:
    result = await db.execute(select(Route).offset(offset).limit(limit))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, route_id: int) -> Route | None:
    return await db.get(Route, route_id)


async def get_by_drone(db: AsyncSession, drone_id: int) -> list[Route]:
    result = await db.execute(select(Route).where(Route.drone_id == drone_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, payload: RouteCreate) -> Route:
    route = Route(**payload.model_dump())
    db.add(route)
    await db.flush()
    await db.refresh(route)
    return route


async def update(db: AsyncSession, route: Route, payload: RouteUpdate) -> Route:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(route, field, value)
    await db.flush()
    await db.refresh(route)
    return route


async def delete(db: AsyncSession, route: Route) -> None:
    await db.delete(route)
    await db.flush()
