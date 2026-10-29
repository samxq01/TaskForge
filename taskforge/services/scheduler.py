"""Dependency-aware task scheduling and eligibility evaluation service (CO5)."""

from __future__ import annotations

from typing import Any, Optional

from taskforge.models import Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


class SchedulerService:
    """Evaluates task execution eligibility and identifies blocked tasks based on graph dependencies.
    
    A task is considered 'eligible' for work if:
        1. It is in 'Pending' status.
        2. All of its prerequisite tasks have achieved 'Completed' status.
        
    If any prerequisite task is still 'Pending' or 'In Progress', the task is 'blocked'.
    """

    def __init__(self, storage: TaskStorage, dependency_service: DependencyService) -> None:
        """Initialize the scheduler service.
        
        Args:
            storage: Persistent TaskStorage interface.
            dependency_service: DependencyService managing the graph and relationships.
        """
        self.storage = storage
        self.dependency_service = dependency_service

    def is_task_eligible(self, task_id: int) -> bool:
        """Determine whether a specific task is eligible for execution.
        
        Args:
            task_id: ID of the task to evaluate.
            
        Returns:
            True if the task exists, is Pending, and all prerequisites are Completed.
            False if blocked, already completed, or non-existent.
        """
        task = self.storage.get_task(task_id)
        if task is None or task.status != TaskStatus.PENDING.value:
            return False

        prereqs = self.dependency_service.get_prerequisites(task_id)
        return all(p.status == TaskStatus.COMPLETED.value for p in prereqs)

    def get_eligible_pending_tasks(self) -> list[Task]:
        """Retrieve all Pending tasks whose prerequisites are completely satisfied.
        
        Returns:
            List of eligible Task instances, ordered by priority DESC, created_at ASC, id ASC.
        """
        all_pending = self.storage.list_tasks(status=TaskStatus.PENDING.value)
        eligible: list[Task] = []

        for task in all_pending:
            assert task.id is not None
            prereqs = self.dependency_service.get_prerequisites(task.id)
            if all(p.status == TaskStatus.COMPLETED.value for p in prereqs):
                eligible.append(task)

        return eligible

    def get_blocked_tasks(self) -> list[tuple[Task, list[Task]]]:
        """Retrieve all Pending or In Progress tasks that are blocked by uncompleted prerequisites.
        
        Returns:
            List of tuples: (blocked_task, list_of_incomplete_prerequisite_tasks).
        """
        tasks = self.storage.list_tasks()
        blocked_list: list[tuple[Task, list[Task]]] = []

        for task in tasks:
            if task.status == TaskStatus.COMPLETED.value:
                continue
            assert task.id is not None
            prereqs = self.dependency_service.get_prerequisites(task.id)
            incomplete = [p for p in prereqs if p.status != TaskStatus.COMPLETED.value]
            if incomplete:
                blocked_list.append((task, incomplete))

        return blocked_list

    def get_task_eligibility_report(self, task_id: int) -> Optional[dict[str, Any]]:
        """Generate a detailed diagnostic report on a task's readiness and blockers.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            Dictionary with readiness details, or None if task does not exist.
        """
        task = self.storage.get_task(task_id)
        if task is None:
            return None

        prereqs = self.dependency_service.get_prerequisites(task_id)
        completed_prereqs = [p for p in prereqs if p.status == TaskStatus.COMPLETED.value]
        blocking_prereqs = [p for p in prereqs if p.status != TaskStatus.COMPLETED.value]

        return {
            "task": task,
            "status": task.status,
            "is_eligible": task.status == TaskStatus.PENDING.value and len(blocking_prereqs) == 0,
            "total_prerequisites": len(prereqs),
            "completed_prerequisites": completed_prereqs,
            "blocking_prerequisites": blocking_prereqs,
        }
