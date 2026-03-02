from datetime import datetime

from app.domain.task.entity import Task
from app.domain.task.value_objects import TaskTitle


def test_task_entity_can_be_renamed_and_toggle_done_state() -> None:
    task = Task.reconstitute(
        id=1,
        title=TaskTitle("Inicial"),
        done=False,
        created_at=datetime(2026, 3, 2, 12, 0, 0),
    )

    task.rename(TaskTitle("Renombrada"))
    task.mark_done()

    assert task.title.value == "Renombrada"
    assert task.done is True

    task.mark_undone()
    assert task.done is False
