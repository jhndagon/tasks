from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ListTasksQuery:
    done: Optional[bool] = None
    title_contains: Optional[str] = None
    title_starts_with: Optional[str] = None
