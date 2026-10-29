"""Unit tests for Smart Auto-Scheduler service and custom heap ranking (CO1, CO5)."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated TaskStorage instance."""
    return TaskStorage(tmp_path / "test_smart_scheduler.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Provide a DependencyService instance."""
    return DependencyService(storage)


@pytest.fixture
def scheduler(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Provide a SchedulerService instance."""
    return SchedulerService(storage, dep_service)


def test_smart_scheduler_empty_database(scheduler: SchedulerService) -> None:
    """Test smart scheduler output when database contains no tasks."""
    result = scheduler.get_smart_schedule()
    assert result.is_valid is True
    assert result.recommended_task is None
    assert result.ranked_tasks == []
    assert result.eligible_count == 0
    assert "No tasks exist" in (result.recommendation_reason or "")


def test_smart_scheduler_priority_and_deadline_ranking(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that higher priority and earlier deadline correctly order recommendations."""
    now = datetime(2026, 10, 30, 10, 0)

    # T1: Medium Priority, due in 1 day
    t1 = storage.create_task(Task(title="Medium Task", priority=Priority.MEDIUM.value, duration=60, due_date=now + timedelta(days=1)))
    # T2: Urgent Priority, due in 5 days
    t2 = storage.create_task(Task(title="Urgent Task", priority=Priority.URGENT.value, duration=45, due_date=now + timedelta(days=5)))
    # T3: High Priority, due in 2 hours
    t3 = storage.create_task(Task(title="High Urgent Due", priority=Priority.HIGH.value, duration=30, due_date=now + timedelta(hours=2)))
    # T4: High Priority, due in 10 hours
    t4 = storage.create_task(Task(title="High Later Due", priority=Priority.HIGH.value, duration=30, due_date=now + timedelta(hours=10)))

    dep_service.rebuild()
    result = scheduler.get_smart_schedule()

    assert result.is_valid is True
    assert len(result.ranked_tasks) == 4

    # Ranking expectation:
    # 1. Urgent (T2)
    # 2. High Earlier Due (T3)
    # 3. High Later Due (T4)
    # 4. Medium (T1)
    ranked_ids = [r.task.id for r in result.ranked_tasks]
    assert ranked_ids == [t2.id, t3.id, t4.id, t1.id]
    assert result.recommended_task is not None
    assert result.recommended_task.id == t2.id
    assert "Highest priority (Urgent" in result.ranked_tasks[0].explanation


def test_smart_scheduler_excludes_completed_in_progress_and_blocked(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that completed, in-progress, and blocked tasks are excluded from recommendations."""
    # Completed
    storage.create_task(Task(title="Done", status=TaskStatus.COMPLETED.value, priority=Priority.URGENT.value, duration=30))
    # In Progress
    storage.create_task(Task(title="Running", status=TaskStatus.IN_PROGRESS.value, priority=Priority.URGENT.value, duration=30))
    # Prerequisite (Pending)
    prereq = storage.create_task(Task(title="Prereq", status=TaskStatus.PENDING.value, priority=Priority.LOW.value, duration=15))
    # Blocked Dependent (Pending, Urgent)
    blocked = storage.create_task(Task(title="Blocked Urgent", status=TaskStatus.PENDING.value, priority=Priority.URGENT.value, duration=10))
    assert prereq.id is not None and blocked.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, blocked.id)

    result = scheduler.get_smart_schedule()
    assert result.is_valid is True
    # Only prereq should be eligible to start!
    assert len(result.ranked_tasks) == 1
    assert result.ranked_tasks[0].task.id == prereq.id
    assert result.blocked_count == 1
    assert result.completed_count == 1
    assert result.in_progress_count == 1


def test_smart_scheduler_detects_cycle_and_aborts_safely(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Test that if a cycle exists in the dependency graph, scheduling returns an error."""
    t1 = storage.create_task(Task(title="A", priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="B", priority=Priority.HIGH.value, duration=30))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    # Artificially simulate a cycle in the in-memory graph
    dep_service.get_graph().add_edge(t1.id, t2.id)
    dep_service.get_graph()._adj[t2.id].add(t1.id)
    dep_service.get_graph()._rev_adj[t1.id].add(t2.id)

    result = scheduler.get_smart_schedule(rebuild=False)
    assert result.is_valid is False
    assert result.recommended_task is None
    assert "Circular dependency detected" in (result.error_message or "")


def test_fifo_queue_order_distinct_from_smart_scheduler_order(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
) -> None:
    """Demonstrate that FIFO queue order coexists with heap-ranked smart recommendations."""
    now = datetime(2026, 10, 30, 12, 0)
    # T1 created first: Low priority
    t1 = storage.create_task(Task(title="Old Low Task", priority=Priority.LOW.value, duration=60, due_date=now + timedelta(days=10)))
    # T2 created second: Urgent priority
    t2 = storage.create_task(Task(title="New Urgent Task", priority=Priority.URGENT.value, duration=15, due_date=now + timedelta(hours=1)))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    undo_mgr = UndoManager()
    queue_service = TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)

    # 1. FIFO Queue: ordered by created_at ASC -> [T1, T2]
    fifo_tasks = queue_service.get_queue_tasks()
    assert [t.id for t in fifo_tasks] == [t1.id, t2.id]
    assert queue_service.peek_next_task().id == t1.id  # type: ignore

    # 2. Smart Scheduler: ordered by priority DESC, deadline ASC -> [T2, T1]
    schedule_result = scheduler.get_smart_schedule()
    assert [r.task.id for r in schedule_result.ranked_tasks] == [t2.id, t1.id]
    assert schedule_result.recommended_task.id == t2.id  # type: ignore

    # Proves FIFO dispatch and smart priority recommendations coexist without mutating each other
