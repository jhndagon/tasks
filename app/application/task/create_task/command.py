from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
