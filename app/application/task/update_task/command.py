from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateTaskCommand:
    task_id: int
    title: str | None = None
    done: bool | None = None
