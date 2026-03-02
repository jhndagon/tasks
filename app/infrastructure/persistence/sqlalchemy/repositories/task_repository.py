from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.task.entity import Task
from app.domain.task.errors import TaskNotFoundError
from app.domain.task.repository import ITaskRepository
from app.domain.task.value_objects import TaskTitle
from app.infrastructure.persistence.sqlalchemy.mappers.task_mapper import TaskMapper
from app.infrastructure.persistence.sqlalchemy.models.task_model import TaskModel


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, title: TaskTitle) -> Task:
        db_task = TaskModel(title=title.value, done=False)
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return TaskMapper.to_domain(db_task)

    async def list(self) -> list[Task]:
        result = await self.session.execute(select(TaskModel).order_by(TaskModel.id.asc()))
        return [TaskMapper.to_domain(item) for item in result.scalars().all()]

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.session.execute(select(TaskModel).where(TaskModel.id == task_id))
        db_task = result.scalar_one_or_none()
        if db_task is None:
            return None
        return TaskMapper.to_domain(db_task)

    async def save(self, task: Task) -> Task:
        result = await self.session.execute(select(TaskModel).where(TaskModel.id == task.id))
        db_task = result.scalar_one_or_none()
        if db_task is None:
            raise TaskNotFoundError(task.id)

        db_task.title = task.title.value
        db_task.done = task.done

        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return TaskMapper.to_domain(db_task)

    async def delete(self, task: Task) -> None:
        result = await self.session.execute(select(TaskModel).where(TaskModel.id == task.id))
        db_task = result.scalar_one_or_none()
        if db_task is None:
            raise TaskNotFoundError(task.id)

        await self.session.delete(db_task)
        await self.session.commit()
