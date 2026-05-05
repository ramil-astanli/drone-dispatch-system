from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.package import PackageCreate, PackageRead, PackageUpdate
from app.services.package_service import PackageService

router = APIRouter()


def get_package_service(db: AsyncSession = Depends(get_db)) -> PackageService:
    return PackageService(db)


@router.post(
    "/",
    response_model=PackageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new package",
)
async def create_package(
    payload: PackageCreate,
    svc: PackageService = Depends(get_package_service),
) -> PackageRead:
    return await svc.register(payload)


@router.get(
    "/",
    response_model=list[PackageRead],
    summary="List all packages",
)
async def list_packages(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    svc: PackageService = Depends(get_package_service),
) -> list[PackageRead]:
    return await svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{package_id}",
    response_model=PackageRead,
    summary="Get a package by ID",
    responses={404: {"description": "Package not found"}},
)
async def get_package(
    package_id: int,
    svc: PackageService = Depends(get_package_service),
) -> PackageRead:
    return await svc.get_or_404(package_id)


@router.patch(
    "/{package_id}",
    response_model=PackageRead,
    summary="Partially update a package",
    responses={404: {"description": "Package not found"}},
)
async def update_package(
    package_id: int,
    payload: PackageUpdate,
    svc: PackageService = Depends(get_package_service),
) -> PackageRead:
    return await svc.patch(package_id, payload)


@router.delete(
    "/{package_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a package",
    responses={404: {"description": "Package not found"}},
)
async def delete_package(
    package_id: int,
    svc: PackageService = Depends(get_package_service),
) -> None:
    package = await svc.get_or_404(package_id)
    await svc.delete(package)
