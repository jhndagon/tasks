import pytest

from app.domain.task.value_objects import TaskTitle


def test_task_title_normalizes_whitespace() -> None:
    title = TaskTitle("  aprender fastapi  ")
    assert title.value == "aprender fastapi"


def test_task_title_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        TaskTitle("   ")


def test_task_title_rejects_values_longer_than_255() -> None:
    with pytest.raises(ValueError, match="cannot exceed 255"):
        TaskTitle("a" * 256)
