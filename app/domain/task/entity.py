from dataclasses import dataclass
from datetime import datetime

from app.domain.task.value_objects import TaskTitle


@dataclass
class Task:
    id: int
    title: TaskTitle
    done: bool
    created_at: datetime

    @classmethod
    def reconstitute(cls, *, id: int, title: TaskTitle, done: bool, created_at: datetime) -> "Task":
        return cls(id=id, title=title, done=done, created_at=created_at)

    def rename(self, title: TaskTitle) -> None:
        self.title = title

    def mark_done(self) -> None:
        self.done = True

    def mark_undone(self) -> None:
        self.done = False
