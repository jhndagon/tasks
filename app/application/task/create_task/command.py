from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateTaskCommand:
    title: str
