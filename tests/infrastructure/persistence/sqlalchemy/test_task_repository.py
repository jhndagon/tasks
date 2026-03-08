import asyncio
import os
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Needed because app.infrastructure.persistence.sqlalchemy.database builds a global engine at import time.
os.environ.setdefault("TURSO_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.domain.task.entity import Task
from app.domain.task.errors import TaskNotFoundError
from app.domain.task.value_objects import TaskTitle
from app.infrastructure.persistence.sqlalchemy.database import Base
from app.infrastructure.persistence.sqlalchemy.repositories.task_repository import SQLAlchemyTaskRepository


async def _build_session_factory(db_url: str) -> tuple[object, async_sessionmaker]:
    engine = create_async_engine(db_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return engine, session_factory


def test_repository_create_and_get_by_id(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_create.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                created = await repository.create(title=TaskTitle("Tarea repo"))

                loaded = await repository.get_by_id(created.id)

                assert loaded is not None
                assert loaded.id == created.id
                assert loaded.title.value == "Tarea repo"
                assert loaded.done is False
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_list_returns_ordered_tasks(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_list.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                first = await repository.create(title=TaskTitle("A"))
                second = await repository.create(title=TaskTitle("B"))

                tasks = await repository.list()

                assert [task.id for task in tasks] == [first.id, second.id]
                assert [task.title.value for task in tasks] == ["A", "B"]
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_list_filters_by_done(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(
            f"sqlite+aiosqlite:///{tmp_path / 'repo_list_filtered.db'}"
        )
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                pending = await repository.create(title=TaskTitle("Pendiente"))
                completed = await repository.create(title=TaskTitle("Completada"))

                completed.mark_done()
                await repository.save(completed)

                pending_tasks = await repository.list(done=False)
                completed_tasks = await repository.list(done=True)

                assert [task.id for task in pending_tasks] == [pending.id]
                assert [task.id for task in completed_tasks] == [completed.id]
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_list_filters_by_title_contains(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(
            f"sqlite+aiosqlite:///{tmp_path / 'repo_list_title_filtered.db'}"
        )
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                first = await repository.create(title=TaskTitle("Comprar fruta"))
                await repository.create(title=TaskTitle("Estudiar SQLAlchemy"))
                third = await repository.create(title=TaskTitle("Ir de compras"))

                matches = await repository.list(title_contains="COMPR")

                assert [task.id for task in matches] == [first.id, third.id]
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_save_updates_task(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_save.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                created = await repository.create(title=TaskTitle("Original"))

                created.rename(TaskTitle("Editada"))
                created.mark_done()

                updated = await repository.save(created)

                assert updated.title.value == "Editada"
                assert updated.done is True
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_save_raises_if_task_does_not_exist(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_save_missing.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                missing = Task.reconstitute(
                    id=999,
                    title=TaskTitle("Fantasma"),
                    done=False,
                    created_at=datetime(2026, 3, 2, 12, 0, 0),
                )

                with pytest.raises(TaskNotFoundError):
                    await repository.save(missing)
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_delete_removes_task(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_delete.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                created = await repository.create(title=TaskTitle("Eliminar"))

                await repository.delete(created)
                loaded = await repository.get_by_id(created.id)

                assert loaded is None
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_repository_delete_raises_if_task_does_not_exist(tmp_path) -> None:
    async def scenario() -> None:
        engine, session_factory = await _build_session_factory(f"sqlite+aiosqlite:///{tmp_path / 'repo_delete_missing.db'}")
        try:
            async with session_factory() as session:
                repository = SQLAlchemyTaskRepository(session)
                missing = Task.reconstitute(
                    id=777,
                    title=TaskTitle("No existe"),
                    done=False,
                    created_at=datetime(2026, 3, 2, 12, 0, 0),
                )

                with pytest.raises(TaskNotFoundError):
                    await repository.delete(missing)
        finally:
            await engine.dispose()

    asyncio.run(scenario())
