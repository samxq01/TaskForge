"""Full integration tests for task dependencies, scheduling eligibility, and FIFO queue (CO1, CO5)."""

from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated TaskStorage instance."""
    return TaskStorage(tmp_path / "test_dep_integration.db")


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Provide an UndoManager instance."""
    return UndoManager()


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Provide a DependencyService instance."""
    return DependencyService(storage)


@pytest.fixture
def scheduler(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Provide a SchedulerService instance."""
    return SchedulerService(storage, dep_service)


@pytest.fixture
def queue_service(storage: TaskStorage, undo_mgr: UndoManager, dep_service: DependencyService) -> TaskQueueService:
    """Provide a TaskQueueService instance."""
    return TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)


def test_dependency_aware_queue_processing_lifecycle(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    queue_service: TaskQueueService,
) -> None:
    """Test that blocked tasks cannot enter the queue until prerequisites complete."""
    # Create 3 tasks: T1 -> T2 -> T3
    t1 = storage.create_task(Task(title="Step 1: DB Schema", priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="Step 2: API Endpoints", priority=Priority.MEDIUM.value, duration=45))
    t3 = storage.create_task(Task(title="Step 3: Frontend UI", priority=Priority.LOW.value, duration=60))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)
    dep_service.add_dependency(t2.id, t3.id)

    # Refresh queue
    queue_service.refresh()

    # Only T1 should be in the queue because T2 and T3 are blocked!
    assert queue_service.size() == 1
    assert queue_service.peek_next_task().id == t1.id  # type: ignore

    # Process T1 to In Progress
    processed1 = queue_service.process_next_task()
    assert processed1 is not None and processed1.id == t1.id
    assert processed1.status == TaskStatus.IN_PROGRESS.value

    # Queue should now be empty (T1 is in progress; T2 and T3 are still pending but blocked)
    queue_service.refresh()
    assert queue_service.is_empty() is True

    # Complete T1
    t1.status = TaskStatus.COMPLETED.value
    storage.update_task(t1)

    # Refresh queue: now T2 is unblocked and should be queued!
    queue_service.refresh()
    assert queue_service.size() == 1
    assert queue_service.peek_next_task().id == t2.id  # type: ignore

    # Process T2
    processed2 = queue_service.process_next_task()
    assert processed2 is not None and processed2.id == t2.id

    # Complete T2
    t2.status = TaskStatus.COMPLETED.value
    storage.update_task(t2)

    # Refresh queue: now T3 is unblocked and should be queued!
    queue_service.refresh()
    assert queue_service.size() == 1
    assert queue_service.peek_next_task().id == t3.id  # type: ignore

    # Process T3
    processed3 = queue_service.process_next_task()
    assert processed3 is not None and processed3.id == t3.id
    assert queue_service.size() == 0


def test_undo_task_processing_preserves_dependency_state(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
    queue_service: TaskQueueService,
) -> None:
    """Test that undoing a task processing step safely restores pending status and queue."""
    t1 = storage.create_task(Task(title="Initial Work", priority=Priority.HIGH.value, duration=20))
    assert t1.id is not None
    dep_service.rebuild()
    queue_service.refresh()

    assert queue_service.size() == 1
    # Process
    processed = queue_service.process_next_task()
    assert processed is not None
    assert storage.get_task(t1.id).status == TaskStatus.IN_PROGRESS.value  # type: ignore
    assert queue_service.size() == 0

    # Undo
    undo_mgr.undo(storage)
    assert storage.get_task(t1.id).status == TaskStatus.PENDING.value  # type: ignore

    # Refresh queue
    queue_service.refresh()
    assert queue_service.size() == 1
    assert queue_service.peek_next_task().id == t1.id  # type: ignore
