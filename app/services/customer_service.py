from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CustomerNotFoundError, EmailAlreadyRegisteredError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.base import BaseService


class CustomerService(BaseService[Customer]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Customer, db)

    async def get_or_404(self, customer_id: int) -> Customer:
        customer = await self.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    async def get_by_email(self, email: str) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    async def register(self, payload: CustomerCreate) -> Customer:
        if await self.get_by_email(payload.email):
            raise EmailAlreadyRegisteredError(payload.email)
        return await self.create(payload)

    async def patch(self, customer_id: int, payload: CustomerUpdate) -> Customer:
        customer = await self.get_or_404(customer_id)
        return await self.update(customer, payload)
