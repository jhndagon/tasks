from typing import Protocol

from app.application.task.update_task.command import UpdateTaskCommand
from app.domain.task.entity import Task


class IUpdateTaskUseCase(Protocol):
    async def execute(self, command: UpdateTaskCommand) -> Task:
        ...
