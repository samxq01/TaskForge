"""Unit and integration tests for Undo/Redo manager and stack-based history."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.undo_manager import ActionType, NoHistoryError, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide a fresh isolated SQLite storage."""
    return TaskStorage(tmp_path / "test_undo.db")


@pytest.fixture
def manager() -> UndoManager:
    """Provide a fresh UndoManager."""
    return UndoManager()


def test_empty_manager_states(manager: UndoManager, storage: TaskStorage) -> None:
    """An empty UndoManager has can_undo=False, can_redo=False and raises on undo/redo."""
    assert manager.can_undo() is False
    assert manager.can_redo() is False
    assert manager.peek_undo() is None
    assert manager.peek_redo() is None
    assert manager.get_undo_history() == []
    assert manager.get_redo_history() == []

    with pytest.raises(NoHistoryError, match="No operations available to undo"):
        manager.undo(storage)

    with pytest.raises(NoHistoryError, match="No operations available to redo"):
        manager.redo(storage)


def test_undo_and_redo_task_creation(manager: UndoManager, storage: TaskStorage) -> None:
    """Creating a task, undoing creation, and redoing creation preserves original ID."""
    task = Task(title="Created Task", priority=Priority.HIGH.value, duration=45)
    created = storage.create_task(task)
    original_id = created.id
    assert original_id is not None

    manager.record_action(
        action_type=ActionType.CREATE,
        task_id=original_id,
        before_state=None,
        after_state=created,
    )

    assert manager.can_undo() is True
    assert manager.can_redo() is False
    assert storage.get_task(original_id) is not None

    # Undo creation -> task should be deleted from SQLite
    action_undone = manager.undo(storage)
    assert action_undone.task_id == original_id
    assert storage.get_task(original_id) is None
    assert manager.can_undo() is False
    assert manager.can_redo() is True

    # Redo creation -> task should be re-inserted with the EXACT SAME ID
    action_redone = manager.redo(storage)
    assert action_redone.task_id == original_id
    restored = storage.get_task(original_id)
    assert restored is not None
    assert restored.id == original_id
    assert restored.title == "Created Task"
    assert restored.priority == 3
    assert restored.duration == 45
    assert manager.can_undo() is True
    assert manager.can_redo() is False


def test_undo_and_redo_task_editing(manager: UndoManager, storage: TaskStorage) -> None:
    """Editing a task can be undone to previous state and redone to new state."""
    task = storage.create_task(Task(title="Initial Version", priority=2, duration=30))
    task_id = task.id
    assert task_id is not None

    # Snapshot before edit
    before_state = storage.get_task(task_id)

    # Apply edit in DB
    task.title = "Modified Version"
    task.priority = 4
    task.status = TaskStatus.IN_PROGRESS.value
    storage.update_task(task)
    after_state = storage.get_task(task_id)

    manager.record_action(
        action_type=ActionType.EDIT,
        task_id=task_id,
        before_state=before_state,
        after_state=after_state,
    )

    # Undo edit -> state reverts to 'Initial Version'
    manager.undo(storage)
    undone = storage.get_task(task_id)
    assert undone is not None
    assert undone.title == "Initial Version"
    assert undone.priority == 2
    assert undone.status == "Pending"

    # Redo edit -> state advances back to 'Modified Version'
    manager.redo(storage)
    redone = storage.get_task(task_id)
    assert redone is not None
    assert redone.title == "Modified Version"
    assert redone.priority == 4
    assert redone.status == "In Progress"


def test_undo_and_redo_task_deletion(manager: UndoManager, storage: TaskStorage) -> None:
    """Deleting a task can be undone to restore the full task with original ID."""
    due = datetime(2026, 12, 25, 18, 0, 0)
    task = storage.create_task(
        Task(
            title="Task To Delete",
            description="Important notes",
            priority=Priority.URGENT.value,
            duration=90,
            status=TaskStatus.IN_PROGRESS.value,
            due_date=due,
        )
    )
    task_id = task.id
    assert task_id is not None
    deleted_snapshot = storage.get_task(task_id)

    # Delete from database
    assert storage.delete_task(task_id) is True
    assert storage.get_task(task_id) is None

    # Record deletion
    manager.record_action(
        action_type=ActionType.DELETE,
        task_id=task_id,
        before_state=deleted_snapshot,
        after_state=None,
    )

    # Undo deletion -> task restored with original ID, timestamps, and fields
    manager.undo(storage)
    restored = storage.get_task(task_id)
    assert restored is not None
    assert restored.id == task_id
    assert restored.title == "Task To Delete"
    assert restored.description == "Important notes"
    assert restored.priority == 4
    assert restored.duration == 90
    assert restored.status == "In Progress"
    assert restored.due_date == due

    # Redo deletion -> task removed again
    manager.redo(storage)
    assert storage.get_task(task_id) is None


def test_new_action_clears_redo_history(manager: UndoManager, storage: TaskStorage) -> None:
    """Performing any new database mutation clears the redo stack."""
    t1 = storage.create_task(Task(title="Task 1"))
    assert t1.id is not None
    manager.record_action(ActionType.CREATE, t1.id, after_state=t1)

    # Undo creation -> 1 item on redo stack
    manager.undo(storage)
    assert manager.can_redo() is True

    # Now create a new task
    t2 = storage.create_task(Task(title="Task 2"))
    assert t2.id is not None
    manager.record_action(ActionType.CREATE, t2.id, after_state=t2)

    # Redo stack must now be cleared
    assert manager.can_redo() is False
    with pytest.raises(NoHistoryError):
        manager.redo(storage)


def test_clear_all_history(manager: UndoManager, storage: TaskStorage) -> None:
    """Calling clear() resets both undo and redo stacks."""
    t = storage.create_task(Task(title="Task"))
    assert t.id is not None
    manager.record_action(ActionType.CREATE, t.id, after_state=t)
    manager.clear()
    assert manager.can_undo() is False
    assert manager.can_redo() is False
