from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.exc import NoSuchModuleError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.config.env import get_settings


class Base(DeclarativeBase):
    pass


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url
    if database_url.startswith("sqlite+libsql://"):
        return database_url
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if database_url.startswith("sqlite:///:memory:"):
        return "sqlite+aiosqlite:///:memory:"
    if database_url.startswith("libsql://"):
        return database_url.replace("libsql://", "sqlite+libsql://", 1)
    return database_url


def _build_connect_args(auth_token: str | None) -> dict[str, object]:
    connect_args: dict[str, object] = {}
    if auth_token:
        connect_args["auth_token"] = auth_token
    return connect_args


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    database_url = _normalize_database_url(settings.turso_database_url)
    connect_args = _build_connect_args(settings.turso_auth_token)
    try:
        return create_async_engine(database_url, connect_args=connect_args, future=True)
    except NoSuchModuleError as exc:
        if database_url.startswith("sqlite+libsql://"):
            raise RuntimeError(
                "Turso driver missing. Install optional dependency with: "
                "pip install -r requirements-turso.txt"
            ) from exc
        raise


engine = _build_engine()
SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, autocommit=False, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


async def init_db() -> None:
    from app.infrastructure.persistence.sqlalchemy.models.task_model import TaskModel  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as exc:
        raise RuntimeError("Database initialization failed") from exc


async def close_db() -> None:
    await engine.dispose()
