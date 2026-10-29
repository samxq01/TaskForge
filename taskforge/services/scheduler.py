"""Dependency-aware task scheduling and Smart Auto-Scheduler service (CO1, CO5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage
from taskforge.structures.priority_queue import PriorityQueue, make_task_ranking_key


@dataclass
class RankedTaskRecommendation:
    """Represents a single ranked task recommendation produced by the priority queue heap."""

    rank: int
    task: Task
    ranking_key: tuple
    explanation: str


@dataclass
class SmartScheduleResult:
    """Complete diagnostic and ranking result from the Smart Auto-Scheduler."""

    is_valid: bool
    error_message: Optional[str]
    recommended_task: Optional[Task]
    recommendation_reason: Optional[str]
    ranked_tasks: list[RankedTaskRecommendation]
    total_tasks_count: int
    eligible_count: int
    blocked_count: int
    in_progress_count: int
    completed_count: int
    blocked_tasks_info: list[tuple[Task, list[Task]]] = field(default_factory=list)


class SchedulerService:
    """Evaluates task execution eligibility and derives priority-ranked scheduling recommendations.
    
    Academic Objectives (CO1, CO5):
        - Enforces strict graph-based prerequisite readiness (CO5).
        - Excludes In-Progress, Completed, and Blocked tasks from new work dispatching.
        - Employs a custom binary Min-Heap Priority Queue to rank eligible tasks (CO1).
        - Generates explainable, deterministic recommendations based on Priority, Deadline, Duration, and Task ID.
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
        
        A task is eligible if:
            1. It exists and is in Pending status.
            2. Every direct prerequisite task has status == 'Completed'.
            
        Args:
            task_id: Task identifier.
            
        Returns:
            True if ready to start, False otherwise.
        """
        task = self.storage.get_task(task_id)
        if task is None or task.status != TaskStatus.PENDING.value:
            return False

        prereqs = self.dependency_service.get_prerequisites(task_id)
        return all(p.status == TaskStatus.COMPLETED.value for p in prereqs)

    def get_eligible_pending_tasks(self) -> list[Task]:
        """Retrieve all Pending tasks whose prerequisites are completely satisfied.
        
        Returns:
            List of eligible Task instances.
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

    def _generate_explanation(self, task: Task, all_eligible: list[Task]) -> str:
        """Formulate a human-readable explanation justifying the task's rank."""
        other_tasks = [t for t in all_eligible if t.id != task.id]
        if not other_tasks:
            return f"Sole eligible task ready to start ({task.priority_label} priority; all prerequisites satisfied)."

        reasons: list[str] = []

        # Compare priority
        max_other_priority = max(t.priority for t in other_tasks)
        if task.priority > max_other_priority:
            reasons.append(f"Highest priority ({task.priority_label}) among eligible tasks")
        elif task.priority == max_other_priority:
            reasons.append(f"Top-tier priority ({task.priority_label})")

        # Compare deadline
        same_priority_others = [t for t in other_tasks if t.priority == task.priority]
        if same_priority_others:
            if task.due_date is not None:
                others_with_due = [t for t in same_priority_others if t.due_date is not None]
                if not others_with_due:
                    reasons.append("has an active deadline while peers are unscheduled")
                else:
                    min_other_due = min(t.due_date for t in others_with_due)
                    if task.due_date < min_other_due:
                        reasons.append(f"earliest deadline ({task.due_date.strftime('%b %d, %H:%M')})")
                    elif task.due_date == min_other_due:
                        # Tie-breaker: duration
                        min_other_dur = min(t.duration for t in others_with_due if t.due_date == task.due_date)
                        if task.duration < min_other_dur:
                            reasons.append(f"shorter estimated duration ({task.duration}m)")
                        else:
                            reasons.append(f"lower task ID (#{task.id}) tie-breaker")
            else:
                reasons.append("unscheduled; ranked by duration & ID")

        if not reasons:
            return "Eligible for execution; all prerequisites completed."

        return "; ".join(reasons) + "."

    def get_smart_schedule(self, rebuild: bool = True) -> SmartScheduleResult:
        """Derive the priority-ranked task schedule using the custom Heap PriorityQueue.
        
        Args:
            rebuild: Whether to synchronize graph with SQLite storage first. Defaults to True.

        Returns:
            SmartScheduleResult containing the recommended task and ranked sequence.
        """
        # Synchronize graph with SQLite if requested
        if rebuild:
            self.dependency_service.rebuild()
        graph = self.dependency_service.get_graph()

        # Step 1: Validate graph acyclicity
        has_cycle, cycle_path = graph.detect_cycle()
        if has_cycle:
            cycle_desc = " ➔ ".join(map(str, cycle_path))
            return SmartScheduleResult(
                is_valid=False,
                error_message=f"Circular dependency detected ({cycle_desc}). Scheduling aborted.",
                recommended_task=None,
                recommendation_reason=None,
                ranked_tasks=[],
                total_tasks_count=self.storage.count_tasks()["total"],
                eligible_count=0,
                blocked_count=0,
                in_progress_count=0,
                completed_count=0,
            )

        # Step 2: Extract current status counts
        counts = self.storage.count_tasks()
        all_eligible = self.get_eligible_pending_tasks()
        blocked_info = self.get_blocked_tasks()

        if not all_eligible:
            reason = "No eligible pending tasks."
            if counts["pending"] > 0:
                reason = "All pending tasks are currently blocked by incomplete prerequisites."
            elif counts["total"] == 0:
                reason = "No tasks exist in the database."
            elif counts["total"] == counts["completed"]:
                reason = "All project tasks are already completed!"

            return SmartScheduleResult(
                is_valid=True,
                error_message=None,
                recommended_task=None,
                recommendation_reason=reason,
                ranked_tasks=[],
                total_tasks_count=counts["total"],
                eligible_count=0,
                blocked_count=len(blocked_info),
                in_progress_count=counts["in_progress"],
                completed_count=counts["completed"],
                blocked_tasks_info=blocked_info,
            )

        # Step 3: Populate custom binary Min-Heap PriorityQueue
        pq: PriorityQueue[Task, tuple] = PriorityQueue()
        for idx, task in enumerate(all_eligible):
            key = make_task_ranking_key(task, insertion_seq=idx)
            pq.push(task, key)

        # Step 4: Extract ranked order strictly via heap pop
        ranked_list: list[RankedTaskRecommendation] = []
        rank_pos = 1

        while not pq.is_empty():
            task, key = pq.pop_with_priority()
            explanation = self._generate_explanation(task, all_eligible)
            ranked_list.append(
                RankedTaskRecommendation(
                    rank=rank_pos,
                    task=task,
                    ranking_key=key,
                    explanation=explanation,
                )
            )
            rank_pos += 1

        recommended = ranked_list[0].task if ranked_list else None
        recommended_reason = ranked_list[0].explanation if ranked_list else None

        return SmartScheduleResult(
            is_valid=True,
            error_message=None,
            recommended_task=recommended,
            recommendation_reason=recommended_reason,
            ranked_tasks=ranked_list,
            total_tasks_count=counts["total"],
            eligible_count=len(all_eligible),
            blocked_count=len(blocked_info),
            in_progress_count=counts["in_progress"],
            completed_count=counts["completed"],
            blocked_tasks_info=blocked_info,
        )
