import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import intpk, str_300

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.route import Route


class PackagePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[intpk]
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str_300] = mapped_column(nullable=False)
    priority: Mapped[PackagePriority] = mapped_column(
        SAEnum(PackagePriority), default=PackagePriority.MEDIUM, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="packages", lazy="selectin"
    )
    # back-reference from Route; uselist inferred as scalar via Mapped[... | None]
    route: Mapped["Route | None"] = relationship(
        back_populates="package", lazy="selectin"
    )
