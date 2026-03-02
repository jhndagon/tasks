from app.application.task.delete_task.command import DeleteTaskCommand
from app.application.task.delete_task.port import IDeleteTaskUseCase
from app.domain.task.errors import TaskNotFoundError
from app.domain.task.repository import ITaskRepository


class DeleteTaskHandler(IDeleteTaskUseCase):
    def __init__(self, repository: ITaskRepository) -> None:
        self.repository = repository

    async def execute(self, command: DeleteTaskCommand) -> None:
        task = await self.repository.get_by_id(command.task_id)
        if task is None:
            raise TaskNotFoundError(command.task_id)
        await self.repository.delete(task)
