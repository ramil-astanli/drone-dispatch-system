import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.database import Base
from app.models.base import intpk, str_50, str_100

if TYPE_CHECKING:
    from app.models.route import Route


class DroneModel(str, enum.Enum):
    LIGHTWEIGHT = "Lightweight"
    MIDDLEWEIGHT = "Middleweight"
    CRUISERWEIGHT = "Cruiserweight"
    HEAVYWEIGHT = "Heavyweight"


class DroneStatus(str, enum.Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    DELIVERING = "DELIVERING"
    DELIVERED = "DELIVERED"
    RETURNING = "RETURNING"
    CHARGING = "CHARGING"


class Drone(Base):
    __tablename__ = "drones"

    id: Mapped[intpk]
    serial_number: Mapped[str_50] = mapped_column(unique=True, nullable=False)
    model: Mapped[DroneModel] = mapped_column(
        SAEnum(DroneModel), nullable=False
    )
    weight_limit: Mapped[float] = mapped_column(Float, nullable=False)
    battery_capacity: Mapped[int] = mapped_column(
        Integer, default=100, nullable=False
    )
    status: Mapped[DroneStatus] = mapped_column(
        SAEnum(DroneStatus), default=DroneStatus.IDLE, nullable=False
    )

    routes: Mapped[list["Route"]] = relationship(
        back_populates="drone", lazy="selectin"
    )

    @validates("battery_capacity")
    def validate_battery_capacity(self, key: str, value: int) -> int:
        if not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError(
                f"battery_capacity must be an integer between 0 and 100, got {value!r}"
            )
        return value
