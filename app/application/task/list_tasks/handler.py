from app.application.task.list_tasks.port import IListTasksUseCase
from app.application.task.list_tasks.query import ListTasksQuery
from app.domain.task.entity import Task
from app.domain.task.repository import ITaskRepository


class ListTasksHandler(IListTasksUseCase):
    def __init__(self, repository: ITaskRepository) -> None:
        self.repository = repository

    async def execute(self, query: ListTasksQuery) -> list[Task]:
        return await self.repository.list(done=query.done)
