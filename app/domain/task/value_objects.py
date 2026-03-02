from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskTitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Task title cannot be empty")
        if len(normalized) > 255:
            raise ValueError("Task title cannot exceed 255 characters")
        object.__setattr__(self, "value", normalized)
