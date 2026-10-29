"""Conversion helpers between TaskForge domain models and API schemas."""

from __future__ import annotations

from typing import Optional

from taskforge.api.schemas import TaskOut
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import format_duration
from taskforge.services.dependency_service import DependencyService


def task_to_schema(task: Task, dep_service: Optional[DependencyService] = None) -> TaskOut:
    """Convert an internal Task model instance into a typed TaskOut API schema."""
    is_ready = True
    prereqs_count = 0
    deps_count = 0

    if task.id is not None and dep_service is not None:
        try:
            prereqs = dep_service.get_prerequisites(task.id)
            prereqs_count = len(prereqs)
            is_ready = all(p.status == TaskStatus.COMPLETED.value for p in prereqs)
            deps = dep_service.get_dependents(task.id)
            deps_count = len(deps)
        except Exception:
            pass

    return TaskOut(
        id=task.id if task.id is not None else 0,
        title=task.title,
        priority=task.priority,
        priority_label=Priority.label(task.priority),
        duration=task.duration,
        duration_formatted=format_duration(task.duration),
        status=task.status,
        description=task.description,
        due_date=task.due_date,
        due_date_formatted=task.formatted_deadline if task.due_date else "No deadline",
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_ready=is_ready,
        prerequisites_count=prereqs_count,
        dependents_count=deps_count,
    )
