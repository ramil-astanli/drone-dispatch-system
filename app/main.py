from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.models import Base  # noqa: F401 – registers all ORM models with metadata


async def _migrate(conn) -> None:
    """Create tables and add any columns missing from the existing schema (dev helper)."""
    await conn.run_sync(Base.metadata.create_all)

    def _add_missing_columns(sync_conn) -> None:
        from sqlalchemy import inspect, text
        import enum as _enum
        inspector = inspect(sync_conn)

        # ── column renames (old_name → new_name per table) ────────────────────
        _renames: dict[str, list[tuple[str, str]]] = {
            "customers": [("full_name", "name")],
        }
        for tbl, pairs in _renames.items():
            try:
                existing = {c["name"] for c in inspector.get_columns(tbl)}
            except Exception:
                continue
            for old, new in pairs:
                if old in existing and new not in existing:
                    sync_conn.execute(
                        text(f'ALTER TABLE "{tbl}" RENAME COLUMN "{old}" TO "{new}"')
                    )

        # ── add brand-new columns ─────────────────────────────────────────────
        for table in Base.metadata.sorted_tables:
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            for col in table.columns:
                if col.name in existing:
                    continue
                col_type = col.type.compile(dialect=sync_conn.dialect)
                default = ""
                if col.default is not None and not col.default.is_callable:
                    val = col.default.arg
                    if isinstance(val, _enum.Enum):
                        val = val.value
                    if isinstance(val, str):
                        default = f" DEFAULT '{val}'"
                    else:
                        default = f" DEFAULT {val}"
                nullable = "" if col.nullable else " NOT NULL"
                sync_conn.execute(
                    text(f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col_type}{default}{nullable}')
                )

    await conn.run_sync(_add_missing_columns)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await _migrate(conn)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=True,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}
