"""Deterministic rule-based deadline risk analyzer (CO1 + CO5).

Evaluates project tasks against time constraints, duration feasibility,
and prerequisite completion status without probabilistic or ML models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from taskforge.models import Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


class RiskCategory(str, Enum):
    """Mutually exclusive risk assessment categories."""

    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    AT_RISK = "At Risk"
    UNSCHEDULED = "Unscheduled"
    SAFE = "Safe"


@dataclass(frozen=True)
class TaskRiskAssessment:
    """Individual risk analysis assessment for a single task."""

    task: Task
    category: RiskCategory
    is_blocked: bool
    blocking_prerequisites: list[Task]
    has_deadline: bool
    time_remaining_minutes: Optional[float]
    duration_minutes: int
    slack_minutes: Optional[float]
    explanation: str

    @property
    def category_label(self) -> str:
        """String representation of the risk category."""
        return self.category.value


@dataclass(frozen=True)
class RiskAnalysisSummary:
    """Aggregated project-wide risk analysis metrics."""

    total_tasks: int
    completed_count: int
    overdue_count: int
    at_risk_count: int
    unscheduled_count: int
    safe_count: int
    blocked_count: int
    assessments: list[TaskRiskAssessment]
    evaluated_at: datetime

    def get_by_category(self, category: RiskCategory | str) -> list[TaskRiskAssessment]:
        """Filter assessments by risk category."""
        cat_val = category.value if isinstance(category, RiskCategory) else category
        return [a for a in self.assessments if a.category.value == cat_val]

    def get_blocked(self) -> list[TaskRiskAssessment]:
        """Retrieve all assessments currently blocked by incomplete prerequisites."""
        return [a for a in self.assessments if a.is_blocked]


class DeadlineRiskAnalyzer:
    """Deterministic, rule-based task deadline feasibility and prerequisite analyzer.
    
    Category Precedence:
        1. Completed   - Task is already marked completed.
        2. Overdue     - Task incomplete and due_date <= current_time.
        3. At Risk     - Task incomplete and (time_remaining < duration OR blocked by prerequisites).
        4. Unscheduled - Task incomplete, no due_date, and not blocked.
        5. Safe        - Task incomplete, due_date set, time_remaining >= duration, and not blocked.
    """

    def __init__(self, storage: TaskStorage, dependency_service: DependencyService) -> None:
        """Initialize analyzer with data storage and dependency service."""
        self.storage = storage
        self.dependency_service = dependency_service

    def analyze_task(
        self,
        task: Task,
        current_time: Optional[datetime] = None,
    ) -> TaskRiskAssessment:
        """Evaluate deadline feasibility and blocking prerequisites for a single task.
        
        Args:
            task: Task to evaluate.
            current_time: Reference timestamp for evaluation. Defaults to datetime.now().
            
        Returns:
            TaskRiskAssessment with deterministic risk categorization and explanation.
        """
        now = current_time or datetime.now()
        task_id = task.id

        # 1. Inspect prerequisites
        blocking_prereqs: list[Task] = []
        if task_id is not None:
            prereqs = self.dependency_service.get_prerequisites(task_id)
            blocking_prereqs = [p for p in prereqs if p.status != TaskStatus.COMPLETED.value]
        is_blocked = len(blocking_prereqs) > 0

        # Calculate time remaining and slack if deadline exists
        has_deadline = task.due_date is not None
        time_remaining_minutes: Optional[float] = None
        slack_minutes: Optional[float] = None

        if has_deadline and task.due_date is not None:
            t_due = task.due_date.replace(tzinfo=None) if task.due_date.tzinfo else task.due_date
            t_now = now.replace(tzinfo=None) if now.tzinfo else now
            time_remaining_minutes = (t_due - t_now).total_seconds() / 60.0
            slack_minutes = time_remaining_minutes - float(task.duration)

        # Precedence Rule 1: Completed
        if task.status == TaskStatus.COMPLETED.value:
            return TaskRiskAssessment(
                task=task,
                category=RiskCategory.COMPLETED,
                is_blocked=False,
                blocking_prerequisites=[],
                has_deadline=has_deadline,
                time_remaining_minutes=time_remaining_minutes,
                duration_minutes=task.duration,
                slack_minutes=slack_minutes,
                explanation="Task is already completed.",
            )

        # Precedence Rule 2: Overdue
        if has_deadline and time_remaining_minutes is not None and time_remaining_minutes <= 0:
            overdue_by = abs(time_remaining_minutes)
            due_str = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
            explanation = f"Deadline expired {overdue_by:.0f}m ago ({due_str}). Task is overdue."
            if is_blocked:
                prereq_names = ", ".join(f"'{p.title}'" for p in blocking_prereqs)
                explanation += f" Also blocked by {len(blocking_prereqs)} incomplete prerequisite(s): {prereq_names}."

            return TaskRiskAssessment(
                task=task,
                category=RiskCategory.OVERDUE,
                is_blocked=is_blocked,
                blocking_prerequisites=blocking_prereqs,
                has_deadline=has_deadline,
                time_remaining_minutes=time_remaining_minutes,
                duration_minutes=task.duration,
                slack_minutes=slack_minutes,
                explanation=explanation,
            )

        # Precedence Rule 3: At Risk
        # Triggered if available time < duration OR if blocked by incomplete prerequisites
        insufficient_time = (
            has_deadline
            and time_remaining_minutes is not None
            and time_remaining_minutes < float(task.duration)
        )

        if insufficient_time or is_blocked:
            reasons: list[str] = []
            if insufficient_time and time_remaining_minutes is not None and slack_minutes is not None:
                reasons.append(
                    f"Insufficient time remaining ({time_remaining_minutes:.0f}m available vs {task.duration}m duration; slack {slack_minutes:.0f}m)"
                )
            if is_blocked:
                prereq_names = ", ".join(f"'{p.title}'" for p in blocking_prereqs)
                reasons.append(
                    f"Blocked by {len(blocking_prereqs)} incomplete prerequisite(s): {prereq_names}"
                )

            explanation = "; ".join(reasons) + "."
            return TaskRiskAssessment(
                task=task,
                category=RiskCategory.AT_RISK,
                is_blocked=is_blocked,
                blocking_prerequisites=blocking_prereqs,
                has_deadline=has_deadline,
                time_remaining_minutes=time_remaining_minutes,
                duration_minutes=task.duration,
                slack_minutes=slack_minutes,
                explanation=explanation,
            )

        # Precedence Rule 4: Unscheduled
        if not has_deadline:
            return TaskRiskAssessment(
                task=task,
                category=RiskCategory.UNSCHEDULED,
                is_blocked=False,
                blocking_prerequisites=[],
                has_deadline=False,
                time_remaining_minutes=None,
                duration_minutes=task.duration,
                slack_minutes=None,
                explanation="No deadline assigned. Ready for execution (all prerequisites satisfied).",
            )

        # Precedence Rule 5: Safe
        assert time_remaining_minutes is not None and slack_minutes is not None
        return TaskRiskAssessment(
            task=task,
            category=RiskCategory.SAFE,
            is_blocked=False,
            blocking_prerequisites=[],
            has_deadline=True,
            time_remaining_minutes=time_remaining_minutes,
            duration_minutes=task.duration,
            slack_minutes=slack_minutes,
            explanation=(
                f"Sufficient time remaining ({time_remaining_minutes:.0f}m available vs {task.duration}m duration; "
                f"buffer +{slack_minutes:.0f}m) with all prerequisites satisfied."
            ),
        )

    def analyze_all(
        self,
        current_time: Optional[datetime] = None,
        rebuild_graph: bool = True,
    ) -> RiskAnalysisSummary:
        """Perform comprehensive deadline risk evaluation across all tasks in storage.
        
        Args:
            current_time: Reference timestamp for evaluation. Defaults to datetime.now().
            rebuild_graph: Whether to synchronize dependency graph with storage first.
            
        Returns:
            RiskAnalysisSummary with per-task assessments and aggregate counts.
        """
        now = current_time or datetime.now()
        if rebuild_graph:
            self.dependency_service.rebuild()

        tasks = self.storage.list_tasks()
        assessments: list[TaskRiskAssessment] = []

        completed_count = 0
        overdue_count = 0
        at_risk_count = 0
        unscheduled_count = 0
        safe_count = 0
        blocked_count = 0

        for task in tasks:
            assessment = self.analyze_task(task, current_time=now)
            assessments.append(assessment)

            if assessment.is_blocked:
                blocked_count += 1

            if assessment.category == RiskCategory.COMPLETED:
                completed_count += 1
            elif assessment.category == RiskCategory.OVERDUE:
                overdue_count += 1
            elif assessment.category == RiskCategory.AT_RISK:
                at_risk_count += 1
            elif assessment.category == RiskCategory.UNSCHEDULED:
                unscheduled_count += 1
            elif assessment.category == RiskCategory.SAFE:
                safe_count += 1

        return RiskAnalysisSummary(
            total_tasks=len(tasks),
            completed_count=completed_count,
            overdue_count=overdue_count,
            at_risk_count=at_risk_count,
            unscheduled_count=unscheduled_count,
            safe_count=safe_count,
            blocked_count=blocked_count,
            assessments=assessments,
            evaluated_at=now,
        )
