from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateTaskCommand:
    task_id: int
    title: str | None = None
    done: bool | None = None
