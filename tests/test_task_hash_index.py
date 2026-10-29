"""Tests for TaskHashIndexService connecting custom HashTable with SQLite storage (CO2)."""

from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated SQLite TaskStorage instance."""
    return TaskStorage(tmp_path / "test_hash_index.db")


@pytest.fixture
def hash_index(storage: TaskStorage) -> TaskHashIndexService:
    """Provide a TaskHashIndexService initialized with storage."""
    return TaskHashIndexService(storage)


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Provide an UndoManager instance."""
    return UndoManager()


def test_empty_task_hash_index(hash_index: TaskHashIndexService) -> None:
    """Test initial empty state of the task hash index."""
    assert hash_index.size() == 0
    assert hash_index.get_task(1) is None
    assert hash_index.contains_task(1) is False
    stats = hash_index.get_statistics()
    assert stats["size"] == 0
    assert stats["occupied_buckets"] == 0


def test_rebuild_and_get_tasks(storage: TaskStorage, hash_index: TaskHashIndexService) -> None:
    """Test populating tasks in SQLite and rebuilding the hash index."""
    t1 = storage.create_task(Task(title="Task 1", priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="Task 2", priority=Priority.LOW.value, duration=45))
    assert t1.id is not None and t2.id is not None

    indexed_count = hash_index.rebuild_index()
    assert indexed_count == 2
    assert hash_index.size() == 2

    # Verify retrieval
    retrieved1 = hash_index.get_task(t1.id)
    assert retrieved1 is not None
    assert retrieved1.title == "Task 1"
    assert retrieved1.priority == Priority.HIGH.value

    retrieved2, comps = hash_index.get_task_with_comparisons(t2.id)
    assert retrieved2 is not None
    assert retrieved2.title == "Task 2"
    assert comps >= 1

    # Verify missing task
    assert hash_index.get_task(999) is None
    assert hash_index.contains_task(999) is False


def test_index_consistency_across_mutations_and_undo_redo(
    storage: TaskStorage,
    hash_index: TaskHashIndexService,
    undo_mgr: UndoManager,
) -> None:
    """Test index synchronization through mutations and undo/redo cycles."""
    # 1. Create task
    task = storage.create_task(Task(title="Original Work", priority=Priority.MEDIUM.value, duration=20))
    assert task.id is not None
    undo_mgr.record_action(ActionType.CREATE, task_id=task.id, after_state=task)
    hash_index.rebuild_index()

    assert hash_index.contains_task(task.id) is True
    assert hash_index.get_task(task.id).title == "Original Work"  # type: ignore

    # 2. Update task
    task.title = "Updated Work"
    storage.update_task(task)
    hash_index.rebuild_index()
    assert hash_index.get_task(task.id).title == "Updated Work"  # type: ignore

    # 3. Delete task
    before_del = storage.get_task(task.id)
    storage.delete_task(task.id)
    undo_mgr.record_action(ActionType.DELETE, task_id=task.id, before_state=before_del)
    hash_index.rebuild_index()

    assert hash_index.contains_task(task.id) is False
    assert hash_index.get_task(task.id) is None

    # 4. Undo deletion -> task restored with exact original ID
    undo_mgr.undo(storage)
    hash_index.rebuild_index()
    assert hash_index.contains_task(task.id) is True
    restored = hash_index.get_task(task.id)
    assert restored is not None
    assert restored.title == "Updated Work"

    # 5. Redo deletion
    undo_mgr.redo(storage)
    hash_index.rebuild_index()
    assert hash_index.contains_task(task.id) is False
