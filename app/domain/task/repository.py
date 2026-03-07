from __future__ import annotations

from typing import Protocol

from app.domain.task.entity import Task
from app.domain.task.value_objects import TaskTitle


class ITaskRepository(Protocol):
    async def create(self, *, title: TaskTitle) -> Task:
        ...

    async def list(self, *, done: bool | None = None) -> list[Task]:
        ...

    async def get_by_id(self, task_id: int) -> Task | None:
        ...

    async def save(self, task: Task) -> Task:
        ...

    async def delete(self, task: Task) -> None:
        ...
