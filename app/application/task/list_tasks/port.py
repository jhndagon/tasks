from typing import Protocol

from app.application.task.list_tasks.query import ListTasksQuery
from app.domain.task.entity import Task


class IListTasksUseCase(Protocol):
    async def execute(self, query: ListTasksQuery) -> list[Task]:
        ...
