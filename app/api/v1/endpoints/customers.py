from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter()


def get_customer_service(db: AsyncSession = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


@router.post(
    "/",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer",
    responses={409: {"description": "Email already registered"}},
)
async def create_customer(
    payload: CustomerCreate,
    svc: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return await svc.register(payload)


@router.get(
    "/",
    response_model=list[CustomerRead],
    summary="List all customers",
)
async def list_customers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    svc: CustomerService = Depends(get_customer_service),
) -> list[CustomerRead]:
    return await svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Get a customer by ID",
    responses={404: {"description": "Customer not found"}},
)
async def get_customer(
    customer_id: int,
    svc: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return await svc.get_or_404(customer_id)


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Partially update a customer",
    responses={404: {"description": "Customer not found"}},
)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    svc: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return await svc.patch(customer_id, payload)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer",
    responses={404: {"description": "Customer not found"}},
)
async def delete_customer(
    customer_id: int,
    svc: CustomerService = Depends(get_customer_service),
) -> None:
    customer = await svc.get_or_404(customer_id)
    await svc.delete(customer)
