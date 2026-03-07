from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from app.application.task.create_task.command import CreateTaskCommand
from app.application.task.create_task.handler import CreateTaskHandler
from app.application.task.delete_task.command import DeleteTaskCommand
from app.application.task.delete_task.handler import DeleteTaskHandler
from app.application.task.list_tasks.handler import ListTasksHandler
from app.application.task.list_tasks.query import ListTasksQuery
from app.application.task.update_task.command import UpdateTaskCommand
from app.application.task.update_task.handler import UpdateTaskHandler
from app.domain.task.entity import Task
from app.domain.task.errors import TaskNotFoundError
from app.domain.task.value_objects import TaskTitle


class FakeTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    async def create(self, *, title: TaskTitle) -> Task:
        task = Task.reconstitute(
            id=self._next_id,
            title=title,
            done=False,
            created_at=datetime(2026, 3, 2, 12, 0, 0),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    async def list(self, *, done: bool | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if done is None:
            return tasks
        return [task for task in tasks if task.done is done]

    async def get_by_id(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    async def save(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    async def delete(self, task: Task) -> None:
        self._tasks.pop(task.id, None)


def test_create_task_handler_creates_task_with_normalized_title() -> None:
    repository = FakeTaskRepository()
    handler = CreateTaskHandler(repository)

    created = asyncio.run(handler.execute(CreateTaskCommand(title="  Estudiar DDD  ")))

    assert created.id == 1
    assert created.title.value == "Estudiar DDD"
    assert created.done is False


def test_list_tasks_handler_returns_existing_tasks() -> None:
    repository = FakeTaskRepository()
    create_handler = CreateTaskHandler(repository)
    list_handler = ListTasksHandler(repository)

    asyncio.run(create_handler.execute(CreateTaskCommand(title="A")))
    asyncio.run(create_handler.execute(CreateTaskCommand(title="B")))

    tasks = asyncio.run(list_handler.execute(ListTasksQuery()))

    assert len(tasks) == 2
    assert [task.title.value for task in tasks] == ["A", "B"]


def test_list_tasks_handler_filters_by_done() -> None:
    repository = FakeTaskRepository()
    create_handler = CreateTaskHandler(repository)
    update_handler = UpdateTaskHandler(repository)
    list_handler = ListTasksHandler(repository)

    first = asyncio.run(create_handler.execute(CreateTaskCommand(title="Pendiente")))
    second = asyncio.run(create_handler.execute(CreateTaskCommand(title="Completada")))
    asyncio.run(update_handler.execute(UpdateTaskCommand(task_id=second.id, done=True)))

    pending = asyncio.run(list_handler.execute(ListTasksQuery(done=False)))
    completed = asyncio.run(list_handler.execute(ListTasksQuery(done=True)))

    assert [task.id for task in pending] == [first.id]
    assert [task.id for task in completed] == [second.id]


def test_update_task_handler_updates_title_and_done() -> None:
    repository = FakeTaskRepository()
    create_handler = CreateTaskHandler(repository)
    update_handler = UpdateTaskHandler(repository)

    created = asyncio.run(create_handler.execute(CreateTaskCommand(title="Inicial")))

    updated = asyncio.run(
        update_handler.execute(
            UpdateTaskCommand(task_id=created.id, title="Actualizada", done=True)
        )
    )

    assert updated.title.value == "Actualizada"
    assert updated.done is True


def test_update_task_handler_raises_when_task_does_not_exist() -> None:
    repository = FakeTaskRepository()
    update_handler = UpdateTaskHandler(repository)

    with pytest.raises(TaskNotFoundError):
        asyncio.run(update_handler.execute(UpdateTaskCommand(task_id=999, done=True)))


def test_delete_task_handler_removes_existing_task() -> None:
    repository = FakeTaskRepository()
    create_handler = CreateTaskHandler(repository)
    delete_handler = DeleteTaskHandler(repository)

    created = asyncio.run(create_handler.execute(CreateTaskCommand(title="Eliminar")))
    asyncio.run(delete_handler.execute(DeleteTaskCommand(task_id=created.id)))

    remaining = asyncio.run(repository.list())
    assert remaining == []


def test_delete_task_handler_raises_when_task_does_not_exist() -> None:
    repository = FakeTaskRepository()
    delete_handler = DeleteTaskHandler(repository)

    with pytest.raises(TaskNotFoundError):
        asyncio.run(delete_handler.execute(DeleteTaskCommand(task_id=321)))
