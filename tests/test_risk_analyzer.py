"""Comprehensive unit tests for DeadlineRiskAnalyzer (CO1 + CO5).

Verifies deterministic rule-based deadline risk evaluation across all 5
categories, boundary conditions, and aggregate summaries.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import (
    DeadlineRiskAnalyzer,
    RiskCategory,
)
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated TaskStorage database."""
    return TaskStorage(tmp_path / "test_risk_analyzer.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def risk_analyzer(storage: TaskStorage, dep_service: DependencyService) -> DeadlineRiskAnalyzer:
    """Fixture providing a DeadlineRiskAnalyzer."""
    return DeadlineRiskAnalyzer(storage, dep_service)


def test_completed_task_is_always_categorized_completed(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 1: Completed status takes priority even if deadline is passed."""
    now = datetime(2026, 10, 30, 12, 0)
    # Task deadline was yesterday, but status is completed
    task = storage.create_task(
        Task(
            title="Finished Task",
            status=TaskStatus.COMPLETED.value,
            duration=45,
            due_date=now - timedelta(days=1),
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.COMPLETED
    assert assessment.is_blocked is False
    assert "already completed" in assessment.explanation


def test_overdue_task_detection(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 2: Incomplete task with due_date <= current_time is Overdue."""
    now = datetime(2026, 10, 30, 12, 0)
    task = storage.create_task(
        Task(
            title="Late Submission",
            status=TaskStatus.PENDING.value,
            duration=30,
            due_date=now - timedelta(hours=2),
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.OVERDUE
    assert assessment.time_remaining_minutes == -120.0
    assert assessment.slack_minutes == -150.0
    assert "expired" in assessment.explanation.lower() or "overdue" in assessment.explanation.lower()


def test_at_risk_due_to_insufficient_time(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 3: Task with available time < duration is At Risk."""
    now = datetime(2026, 10, 30, 12, 0)
    # Due in 30 minutes, but duration is 60 minutes
    task = storage.create_task(
        Task(
            title="Heavy Workload",
            status=TaskStatus.PENDING.value,
            duration=60,
            due_date=now + timedelta(minutes=30),
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.AT_RISK
    assert assessment.is_blocked is False
    assert assessment.time_remaining_minutes == 30.0
    assert assessment.slack_minutes == -30.0
    assert "insufficient time" in assessment.explanation.lower()


def test_at_risk_due_to_incomplete_prerequisite(
    storage: TaskStorage,
    dep_service: DependencyService,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 3: Task blocked by incomplete prerequisite is At Risk even with ample time."""
    now = datetime(2026, 10, 30, 12, 0)
    prereq = storage.create_task(
        Task(
            title="Backend Setup",
            status=TaskStatus.PENDING.value,
            duration=20,
        )
    )
    # Dependent has deadline 5 days away and 30m duration (plenty of time)
    dependent = storage.create_task(
        Task(
            title="Frontend UI",
            status=TaskStatus.PENDING.value,
            duration=30,
            due_date=now + timedelta(days=5),
        )
    )
    assert prereq.id is not None and dependent.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, dependent.id)

    assessment = risk_analyzer.analyze_task(dependent, current_time=now)
    assert assessment.category == RiskCategory.AT_RISK
    assert assessment.is_blocked is True
    assert len(assessment.blocking_prerequisites) == 1
    assert assessment.blocking_prerequisites[0].id == prereq.id
    assert "blocked by 1 incomplete prerequisite" in assessment.explanation.lower()


def test_at_risk_blocked_task_without_deadline(
    storage: TaskStorage,
    dep_service: DependencyService,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 3: Task without deadline is At Risk if blocked by prerequisites."""
    now = datetime(2026, 10, 30, 12, 0)
    prereq = storage.create_task(Task(title="P", status=TaskStatus.IN_PROGRESS.value, duration=10))
    dependent = storage.create_task(Task(title="D", status=TaskStatus.PENDING.value, duration=10, due_date=None))
    assert prereq.id is not None and dependent.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, dependent.id)

    assessment = risk_analyzer.analyze_task(dependent, current_time=now)
    assert assessment.category == RiskCategory.AT_RISK
    assert assessment.is_blocked is True
    assert assessment.has_deadline is False


def test_unscheduled_task(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 4: Incomplete task with no deadline and no blocking prereqs is Unscheduled."""
    now = datetime(2026, 10, 30, 12, 0)
    task = storage.create_task(
        Task(
            title="Someday Task",
            status=TaskStatus.PENDING.value,
            duration=40,
            due_date=None,
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.UNSCHEDULED
    assert assessment.has_deadline is False
    assert assessment.is_blocked is False
    assert assessment.slack_minutes is None
    assert "no deadline" in assessment.explanation.lower()


def test_safe_task_evaluation(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test precedence 5: Incomplete task with sufficient time and no blocking prereqs is Safe."""
    now = datetime(2026, 10, 30, 12, 0)
    # Due in 120 minutes, duration is 30 minutes (buffer = +90m)
    task = storage.create_task(
        Task(
            title="Comfortable Task",
            status=TaskStatus.PENDING.value,
            duration=30,
            due_date=now + timedelta(minutes=120),
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.SAFE
    assert assessment.is_blocked is False
    assert assessment.has_deadline is True
    assert assessment.time_remaining_minutes == 120.0
    assert assessment.slack_minutes == 90.0
    assert "sufficient time remaining" in assessment.explanation.lower()


def test_exact_feasibility_boundary_is_safe(
    storage: TaskStorage,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test boundary condition: Available time exactly equals duration (slack = 0) is Safe."""
    now = datetime(2026, 10, 30, 12, 0)
    # Available time = exactly 60 minutes, duration = 60 minutes
    task = storage.create_task(
        Task(
            title="Exact Cutoff Task",
            status=TaskStatus.PENDING.value,
            duration=60,
            due_date=now + timedelta(minutes=60),
        )
    )

    assessment = risk_analyzer.analyze_task(task, current_time=now)
    assert assessment.category == RiskCategory.SAFE
    assert assessment.time_remaining_minutes == 60.0
    assert assessment.slack_minutes == 0.0


def test_blocked_overdue_task_flagged_both_overdue_and_blocked(
    storage: TaskStorage,
    dep_service: DependencyService,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test that an overdue task that also has blocked prerequisites is Overdue with is_blocked=True."""
    now = datetime(2026, 10, 30, 12, 0)
    prereq = storage.create_task(Task(title="Prereq", status=TaskStatus.PENDING.value, duration=15))
    overdue_task = storage.create_task(
        Task(
            title="Overdue Blocked",
            status=TaskStatus.PENDING.value,
            duration=30,
            due_date=now - timedelta(hours=1),
        )
    )
    assert prereq.id is not None and overdue_task.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, overdue_task.id)

    assessment = risk_analyzer.analyze_task(overdue_task, current_time=now)
    assert assessment.category == RiskCategory.OVERDUE
    assert assessment.is_blocked is True
    assert len(assessment.blocking_prerequisites) == 1


def test_analyze_all_summary_aggregation(
    storage: TaskStorage,
    dep_service: DependencyService,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Test analyze_all produces accurate counts across all 5 categories and blocked flag."""
    now = datetime(2026, 10, 30, 12, 0)

    # 1. Completed
    storage.create_task(Task(title="T1", status=TaskStatus.COMPLETED.value, duration=20))
    # 2. Overdue
    storage.create_task(Task(title="T2", status=TaskStatus.PENDING.value, duration=30, due_date=now - timedelta(hours=1)))
    # 3. At Risk (Insufficient time: 10m left, 30m duration)
    storage.create_task(Task(title="T3", status=TaskStatus.PENDING.value, duration=30, due_date=now + timedelta(minutes=10)))
    # 4. Unscheduled
    t4 = storage.create_task(Task(title="T4", status=TaskStatus.PENDING.value, duration=25, due_date=None))
    # 5. Safe
    storage.create_task(Task(title="T5", status=TaskStatus.PENDING.value, duration=15, due_date=now + timedelta(days=2)))
    # 6. At Risk (Blocked dependent)
    t6 = storage.create_task(Task(title="T6", status=TaskStatus.PENDING.value, duration=20, due_date=now + timedelta(days=3)))

    assert t4.id is not None and t6.id is not None
    dep_service.rebuild()
    dep_service.add_dependency(t4.id, t6.id)

    summary = risk_analyzer.analyze_all(current_time=now)

    assert summary.total_tasks == 6
    assert summary.completed_count == 1
    assert summary.overdue_count == 1
    assert summary.at_risk_count == 2  # T3 (insufficient time) and T6 (blocked by T4)
    assert summary.unscheduled_count == 1  # T4
    assert summary.safe_count == 1  # T5
    assert summary.blocked_count == 1  # T6 is blocked

    # Verify filtering helpers
    assert len(summary.get_by_category(RiskCategory.AT_RISK)) == 2
    assert len(summary.get_by_category("Overdue")) == 1
    assert len(summary.get_blocked()) == 1
