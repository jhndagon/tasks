from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.task.entity import Task


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            title=task.title.value,
            done=task.done,
            created_at=task.created_at,
        )
