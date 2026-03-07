from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ListTasksQuery:
    done: Optional[bool] = None
