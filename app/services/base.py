from typing import Generic, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseService(Generic[ModelT]):
    """
    Generic CRUD base — subclasses pass their ORM model class to __init__
    and inherit get_by_id, get_all, create, update, and delete for free.
    """

    def __init__(self, model: type[ModelT], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, record_id: int) -> ModelT | None:
        return await self.db.get(self.model, record_id)

    async def get_all(self, *, offset: int = 0, limit: int = 100) -> list[ModelT]:
        result = await self.db.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, payload: PydanticBaseModel) -> ModelT:
        instance = self.model(**payload.model_dump())
        self.db.add(instance)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with the same unique value already exists.",
            ) from exc
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelT, payload: PydanticBaseModel) -> ModelT:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.db.delete(instance)
        await self.db.flush()
