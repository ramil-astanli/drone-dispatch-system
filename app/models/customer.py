from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import intpk, str_150, str_254, str_300

if TYPE_CHECKING:
    from app.models.package import Package


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[intpk]
    name: Mapped[str_150] = mapped_column(nullable=False)
    email: Mapped[str_254] = mapped_column(unique=True, nullable=False)
    address: Mapped[str_300] = mapped_column(nullable=False)

    packages: Mapped[list["Package"]] = relationship(
        back_populates="customer", lazy="selectin"
    )
