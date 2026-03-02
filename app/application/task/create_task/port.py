from typing import Protocol

from app.application.task.create_task.command import CreateTaskCommand
from app.domain.task.entity import Task


class ICreateTaskUseCase(Protocol):
    async def execute(self, command: CreateTaskCommand) -> Task:
        ...
