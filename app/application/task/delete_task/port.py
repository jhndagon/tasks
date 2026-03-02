from typing import Protocol

from app.application.task.delete_task.command import DeleteTaskCommand


class IDeleteTaskUseCase(Protocol):
    async def execute(self, command: DeleteTaskCommand) -> None:
        ...
