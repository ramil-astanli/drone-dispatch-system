from pydantic import BaseModel, ConfigDict, Field

from app.models.drone import DroneModel, DroneStatus


class DroneBase(BaseModel):
    serial_number: str = Field(..., max_length=50)
    model: DroneModel
    weight_limit: float = Field(..., gt=0)
    battery_capacity: int = Field(default=100, ge=0, le=100)


class DroneCreate(DroneBase):
    status: DroneStatus = DroneStatus.IDLE


class DroneUpdate(BaseModel):
    model: DroneModel | None = None
    status: DroneStatus | None = None
    weight_limit: float | None = Field(default=None, gt=0)
    battery_capacity: int | None = Field(default=None, ge=0, le=100)


class DroneRead(DroneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: DroneStatus
