import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import created_at_col, intpk, str_300

if TYPE_CHECKING:
    from app.models.drone import Drone
    from app.models.package import Package


class RouteStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[intpk]
    drone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("drones.id", ondelete="SET NULL"), nullable=True
    )
    # Unique constraint enforces the one-Package → one-Route invariant at DB level.
    package_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("packages.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    origin_address: Mapped[str_300] = mapped_column(nullable=False)
    destination_address: Mapped[str_300] = mapped_column(nullable=False)
    status: Mapped[RouteStatus] = mapped_column(
        SAEnum(RouteStatus), default=RouteStatus.PENDING, nullable=False
    )
    created_at: Mapped[created_at_col]
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    drone: Mapped["Drone | None"] = relationship(
        back_populates="routes", lazy="selectin"
    )
    package: Mapped["Package"] = relationship(
        back_populates="route", lazy="selectin"
    )
