from app.application.task.update_task.command import UpdateTaskCommand
from app.application.task.update_task.port import IUpdateTaskUseCase
from app.domain.task.entity import Task
from app.domain.task.errors import TaskNotFoundError
from app.domain.task.repository import ITaskRepository
from app.domain.task.value_objects import TaskTitle


class UpdateTaskHandler(IUpdateTaskUseCase):
    def __init__(self, repository: ITaskRepository) -> None:
        self.repository = repository

    async def execute(self, command: UpdateTaskCommand) -> Task:
        task = await self.repository.get_by_id(command.task_id)
        if task is None:
            raise TaskNotFoundError(command.task_id)

        if command.title is not None:
            task.rename(TaskTitle(command.title))
        if command.done is True:
            task.mark_done()
        if command.done is False:
            task.mark_undone()

        return await self.repository.save(task)
