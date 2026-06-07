from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.task.create_task.command import CreateTaskCommand
from app.application.task.create_task.port import ICreateTaskUseCase
from app.application.task.delete_task.command import DeleteTaskCommand
from app.application.task.delete_task.port import IDeleteTaskUseCase
from app.application.task.list_tasks.port import IListTasksUseCase
from app.application.task.list_tasks.query import ListTasksQuery
from app.application.task.update_task.command import UpdateTaskCommand
from app.application.task.update_task.port import IUpdateTaskUseCase
from app.domain.task.errors import TaskNotFoundError
from app.infrastructure.config.container import (
    get_create_task_use_case,
    get_delete_task_use_case,
    get_list_tasks_use_case,
    get_update_task_use_case,
)
from app.infrastructure.http.rest.schemas.task_schema import TaskCreateRequest, TaskResponse, TaskUpdateRequest

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskController:
    def __init__(
        self,
        create_task_use_case: ICreateTaskUseCase,
        list_tasks_use_case: IListTasksUseCase,
        update_task_use_case: IUpdateTaskUseCase,
        delete_task_use_case: IDeleteTaskUseCase,
    ) -> None:
        self.create_task_use_case = create_task_use_case
        self.list_tasks_use_case = list_tasks_use_case
        self.update_task_use_case = update_task_use_case
        self.delete_task_use_case = delete_task_use_case

    async def list_tasks(
        self,
        *,
        done: Optional[bool] = None,
        title_contains: Optional[str] = None,
        title_starts_with: Optional[str] = None,
    ) -> list[TaskResponse]:
        tasks = await self.list_tasks_use_case.execute(
            ListTasksQuery(
                done=done,
                title_contains=title_contains,
                title_starts_with=title_starts_with,
            )
        )
        return [TaskResponse.from_domain(task) for task in tasks]

    async def create_task(self, payload: TaskCreateRequest) -> TaskResponse:
        try:
            task = await self.create_task_use_case.execute(CreateTaskCommand(title=payload.title))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
        return TaskResponse.from_domain(task)

    async def update_task(self, task_id: int, payload: TaskUpdateRequest) -> TaskResponse:
        try:
            task = await self.update_task_use_case.execute(
                UpdateTaskCommand(task_id=task_id, title=payload.title, done=payload.done)
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
        except TaskNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse.from_domain(task)

    async def delete_task(self, task_id: int) -> None:
        try:
            await self.delete_task_use_case.execute(DeleteTaskCommand(task_id=task_id))
        except TaskNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


def get_task_controller(
    create_task_use_case: Annotated[ICreateTaskUseCase, Depends(get_create_task_use_case)],
    list_tasks_use_case: Annotated[IListTasksUseCase, Depends(get_list_tasks_use_case)],
    update_task_use_case: Annotated[IUpdateTaskUseCase, Depends(get_update_task_use_case)],
    delete_task_use_case: Annotated[IDeleteTaskUseCase, Depends(get_delete_task_use_case)],
) -> TaskController:
    return TaskController(
        create_task_use_case=create_task_use_case,
        list_tasks_use_case=list_tasks_use_case,
        update_task_use_case=update_task_use_case,
        delete_task_use_case=delete_task_use_case,
    )


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    controller: Annotated[TaskController, Depends(get_task_controller)],
    done: Optional[bool] = None,
    title_contains: Optional[str] = None,
    title_starts_with: Optional[str] = None,
) -> list[TaskResponse]:
    return await controller.list_tasks(
        done=done,
        title_contains=title_contains,
        title_starts_with=title_starts_with,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    controller: Annotated[TaskController, Depends(get_task_controller)],
) -> TaskResponse:
    return await controller.create_task(payload)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    controller: Annotated[TaskController, Depends(get_task_controller)],
) -> TaskResponse:
    return await controller.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    controller: Annotated[TaskController, Depends(get_task_controller)],
) -> None:
    await controller.delete_task(task_id)
