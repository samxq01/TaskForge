"""Unit and integration tests for TaskQueueService and FIFO processing."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide a fresh isolated SQLite storage."""
    return TaskStorage(tmp_path / "test_queue_svc.db")


@pytest.fixture
def manager() -> UndoManager:
    """Provide a fresh UndoManager."""
    return UndoManager()


@pytest.fixture
def service(storage: TaskStorage, manager: UndoManager) -> TaskQueueService:
    """Provide a TaskQueueService configured with storage and undo manager."""
    return TaskQueueService(storage, manager)


def test_empty_queue_service(service: TaskQueueService) -> None:
    """When no tasks exist, service reports empty and process_next_task returns None."""
    assert service.is_empty() is True
    assert service.size() == 0
    assert service.peek_next_task() is None
    assert service.process_next_task() is None


def test_fifo_ordering_by_created_at_and_id(storage: TaskStorage, service: TaskQueueService) -> None:
    """Tasks must be queued and processed in FIFO order by creation timestamp and ID."""
    t0 = datetime(2026, 10, 29, 10, 0, 0)

    task1 = Task(title="Task Alpha", status="Pending", created_at=t0)
    task2 = Task(title="Task Beta", status="Pending", created_at=t0 + timedelta(minutes=5))
    task3 = Task(title="Task Gamma", status="Pending", created_at=t0 + timedelta(minutes=10))

    storage.create_task(task1)
    storage.create_task(task2)
    storage.create_task(task3)

    service.refresh()
    assert service.size() == 3

    # FIFO check: Alpha first, then Beta, then Gamma
    first = service.process_next_task()
    assert first is not None
    assert first.title == "Task Alpha"
    assert first.status == "In Progress"

    second = service.process_next_task()
    assert second is not None
    assert second.title == "Task Beta"
    assert second.status == "In Progress"

    third = service.process_next_task()
    assert third is not None
    assert third.title == "Task Gamma"
    assert third.status == "In Progress"

    assert service.is_empty() is True


def test_non_pending_tasks_excluded(storage: TaskStorage, service: TaskQueueService) -> None:
    """Tasks that are already 'In Progress' or 'Completed' are not queued."""
    storage.create_task(Task(title="Pending 1", status="Pending"))
    storage.create_task(Task(title="Active 1", status="In Progress"))
    storage.create_task(Task(title="Done 1", status="Completed"))
    storage.create_task(Task(title="Pending 2", status="Pending"))

    service.refresh()
    assert service.size() == 2
    tasks = service.get_queue_tasks()
    titles = [t.title for t in tasks]
    assert titles == ["Pending 1", "Pending 2"]


def test_processing_creates_undoable_action(
    storage: TaskStorage, manager: UndoManager, service: TaskQueueService
) -> None:
    """Processing a task creates an undoable edit action that reverts status to Pending."""
    t = storage.create_task(Task(title="Task To Process", status="Pending"))
    task_id = t.id
    assert task_id is not None

    service.refresh()
    assert service.size() == 1

    processed = service.process_next_task()
    assert processed is not None
    assert processed.status == "In Progress"

    # SQLite record should now be In Progress
    in_db = storage.get_task(task_id)
    assert in_db is not None
    assert in_db.status == "In Progress"

    # Queue should now be empty
    assert service.size() == 0

    # Undo the processing action
    assert manager.can_undo() is True
    manager.undo(storage)

    # SQLite record should revert to Pending
    reverted = storage.get_task(task_id)
    assert reverted is not None
    assert reverted.status == "Pending"

    # Refresh queue -> task reappears in queue!
    service.refresh()
    assert service.size() == 1
    assert service.peek_next_task().id == task_id  # type: ignore

    # Redo the processing action
    manager.redo(storage)
    redone = storage.get_task(task_id)
    assert redone is not None
    assert redone.status == "In Progress"

    service.refresh()
    assert service.size() == 0
