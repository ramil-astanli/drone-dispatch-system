from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PackageNotFoundError
from app.models.package import Package
from app.schemas.package import PackageCreate, PackageUpdate
from app.services.base import BaseService


class PackageService(BaseService[Package]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Package, db)

    async def get_or_404(self, package_id: int) -> Package:
        package = await self.get_by_id(package_id)
        if package is None:
            raise PackageNotFoundError(package_id)
        return package

    async def get_by_customer(self, customer_id: int) -> list[Package]:
        result = await self.db.execute(
            select(Package).where(Package.customer_id == customer_id)
        )
        return list(result.scalars().all())

    async def register(self, payload: PackageCreate) -> Package:
        return await self.create(payload)

    async def patch(self, package_id: int, payload: PackageUpdate) -> Package:
        package = await self.get_or_404(package_id)
        return await self.update(package, payload)
