"""Tests for SchedulerService task eligibility and blocker diagnostics (CO5)."""

from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated TaskStorage instance."""
    return TaskStorage(tmp_path / "test_scheduler.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Provide a DependencyService instance."""
    return DependencyService(storage)


@pytest.fixture
def scheduler(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Provide a SchedulerService instance."""
    return SchedulerService(storage, dep_service)


def test_independent_pending_task_is_eligible(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that a pending task with no prerequisites is eligible immediately."""
    t1 = storage.create_task(Task(title="Free Task", priority=Priority.MEDIUM.value, duration=30))
    assert t1.id is not None
    dep_service.rebuild()

    assert scheduler.is_task_eligible(t1.id) is True
    eligible = scheduler.get_eligible_pending_tasks()
    assert len(eligible) == 1
    assert eligible[0].id == t1.id
    assert scheduler.get_blocked_tasks() == []


def test_dependent_task_blocked_by_pending_prerequisite(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that a task is blocked when its prerequisite is still pending."""
    t1 = storage.create_task(Task(title="Prereq", status=TaskStatus.PENDING.value, priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="Dependent", status=TaskStatus.PENDING.value, priority=Priority.HIGH.value, duration=30))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # t1 is eligible, t2 is blocked
    assert scheduler.is_task_eligible(t1.id) is True
    assert scheduler.is_task_eligible(t2.id) is False

    eligible = scheduler.get_eligible_pending_tasks()
    assert [t.id for t in eligible] == [t1.id]

    blocked = scheduler.get_blocked_tasks()
    assert len(blocked) == 1
    assert blocked[0][0].id == t2.id
    assert [p.id for p in blocked[0][1]] == [t1.id]


def test_dependent_task_unblocked_when_prerequisite_completed(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that completing a prerequisite unblocks the dependent task."""
    t1 = storage.create_task(Task(title="Prereq", status=TaskStatus.PENDING.value, priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="Dependent", status=TaskStatus.PENDING.value, priority=Priority.HIGH.value, duration=30))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # Mark t1 as Completed
    t1.status = TaskStatus.COMPLETED.value
    storage.update_task(t1)

    assert scheduler.is_task_eligible(t2.id) is True
    eligible = scheduler.get_eligible_pending_tasks()
    assert [t.id for t in eligible] == [t2.id]
    assert scheduler.get_blocked_tasks() == []


def test_multiple_prerequisites_all_must_be_completed(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that ALL prerequisites must complete for a task to be eligible."""
    t1 = storage.create_task(Task(title="P1", status=TaskStatus.COMPLETED.value, priority=Priority.HIGH.value, duration=20))
    t2 = storage.create_task(Task(title="P2", status=TaskStatus.IN_PROGRESS.value, priority=Priority.HIGH.value, duration=20))
    t3 = storage.create_task(Task(title="Dependent", status=TaskStatus.PENDING.value, priority=Priority.HIGH.value, duration=20))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t3.id)
    dep_service.add_dependency(t2.id, t3.id)

    # P1 is completed, but P2 is in progress -> t3 is still blocked
    assert scheduler.is_task_eligible(t3.id) is False

    report = scheduler.get_task_eligibility_report(t3.id)
    assert report is not None
    assert report["is_eligible"] is False
    assert report["total_prerequisites"] == 2
    assert len(report["completed_prerequisites"]) == 1
    assert [p.id for p in report["completed_prerequisites"]] == [t1.id]
    assert len(report["blocking_prerequisites"]) == 1
    assert [p.id for p in report["blocking_prerequisites"]] == [t2.id]

    # Now complete P2
    t2.status = TaskStatus.COMPLETED.value
    storage.update_task(t2)

    assert scheduler.is_task_eligible(t3.id) is True
