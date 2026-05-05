from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import intpk, str_50, str_254


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[str_50] = mapped_column(unique=True, nullable=False)
    email: Mapped[str_254] = mapped_column(unique=True, nullable=False)
    # bcrypt produces 60-char hashes; 128 gives comfortable headroom
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
