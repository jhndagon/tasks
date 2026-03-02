from app.application.task.create_task.command import CreateTaskCommand
from app.application.task.create_task.port import ICreateTaskUseCase
from app.domain.task.entity import Task
from app.domain.task.repository import ITaskRepository
from app.domain.task.value_objects import TaskTitle


class CreateTaskHandler(ICreateTaskUseCase):
    def __init__(self, repository: ITaskRepository) -> None:
        self.repository = repository

    async def execute(self, command: CreateTaskCommand) -> Task:
        return await self.repository.create(title=TaskTitle(command.title))
