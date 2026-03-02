from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.task.create_task.handler import CreateTaskHandler
from app.application.task.create_task.port import ICreateTaskUseCase
from app.application.task.delete_task.handler import DeleteTaskHandler
from app.application.task.delete_task.port import IDeleteTaskUseCase
from app.application.task.list_tasks.handler import ListTasksHandler
from app.application.task.list_tasks.port import IListTasksUseCase
from app.application.task.update_task.handler import UpdateTaskHandler
from app.application.task.update_task.port import IUpdateTaskUseCase
from app.domain.task.repository import ITaskRepository
from app.infrastructure.persistence.sqlalchemy.database import get_db_session
from app.infrastructure.persistence.sqlalchemy.repositories.task_repository import SQLAlchemyTaskRepository


def get_task_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ITaskRepository:
    return SQLAlchemyTaskRepository(session)


def get_create_task_use_case(
    repository: Annotated[ITaskRepository, Depends(get_task_repository)],
) -> ICreateTaskUseCase:
    return CreateTaskHandler(repository)


def get_list_tasks_use_case(
    repository: Annotated[ITaskRepository, Depends(get_task_repository)],
) -> IListTasksUseCase:
    return ListTasksHandler(repository)


def get_update_task_use_case(
    repository: Annotated[ITaskRepository, Depends(get_task_repository)],
) -> IUpdateTaskUseCase:
    return UpdateTaskHandler(repository)


def get_delete_task_use_case(
    repository: Annotated[ITaskRepository, Depends(get_task_repository)],
) -> IDeleteTaskUseCase:
    return DeleteTaskHandler(repository)
