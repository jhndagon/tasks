from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: int
