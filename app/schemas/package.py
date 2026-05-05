from pydantic import BaseModel, ConfigDict, Field

from app.models.package import PackagePriority


class PackageBase(BaseModel):
    description: str = Field(..., max_length=300)
    weight: float = Field(..., gt=0)
    priority: PackagePriority = PackagePriority.MEDIUM


class PackageCreate(PackageBase):
    customer_id: int


class PackageUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=300)
    weight: float | None = Field(default=None, gt=0)
    priority: PackagePriority | None = None


class PackageRead(PackageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
