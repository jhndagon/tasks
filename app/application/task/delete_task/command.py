from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeleteTaskCommand:
    task_id: int
