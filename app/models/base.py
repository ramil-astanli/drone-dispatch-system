"""
Reusable SQLAlchemy 2.0 Annotated column types.

Declare a column once here; reference it with Mapped[<alias>] anywhere in the
model layer to keep column definitions DRY and consistent.
"""
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import mapped_column

# ── Primary key ──────────────────────────────────────────────────────────────
intpk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

# ── String widths ─────────────────────────────────────────────────────────────
str_50 = Annotated[str, mapped_column(String(50))]
str_100 = Annotated[str, mapped_column(String(100))]
str_150 = Annotated[str, mapped_column(String(150))]
str_254 = Annotated[str, mapped_column(String(254))]
str_300 = Annotated[str, mapped_column(String(300))]

# ── Timestamps ────────────────────────────────────────────────────────────────
created_at_col = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
]
