from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.route import RouteStatus


class RouteBase(BaseModel):
    origin_address: str = Field(..., max_length=300)
    destination_address: str = Field(..., max_length=300)


class RouteCreate(RouteBase):
    package_id: int
    drone_id: int | None = None


class RouteUpdate(BaseModel):
    drone_id: int | None = None
    origin_address: str | None = Field(default=None, max_length=300)
    destination_address: str | None = Field(default=None, max_length=300)
    status: RouteStatus | None = None
    completed_at: datetime | None = None


class RouteRead(RouteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    package_id: int
    drone_id: int | None
    status: RouteStatus
    created_at: datetime
    completed_at: datetime | None
