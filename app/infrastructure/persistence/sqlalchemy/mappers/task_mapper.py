from app.domain.task.entity import Task
from app.domain.task.value_objects import TaskTitle
from app.infrastructure.persistence.sqlalchemy.models.task_model import TaskModel


class TaskMapper:
    @staticmethod
    def to_domain(model: TaskModel) -> Task:
        return Task.reconstitute(
            id=model.id,
            title=TaskTitle(model.title),
            done=model.done,
            created_at=model.created_at,
        )
