"""End-to-end integration tests for Phase 02 (Stack, Queue, Undo/Redo)."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


def test_full_phase2_integration_workflow(tmp_path: Path) -> None:
    """Execute the complete Phase 02 integration sequence:
    1. Create task, record action, verify persistence.
    2. Undo creation, verify task removed.
    3. Redo creation, verify original ID restored.
    4. Process next pending task, verify status becomes In Progress.
    5. Undo processing, verify status reverts to Pending.
    6. Redo processing, verify status becomes In Progress again.
    """
    storage = TaskStorage(tmp_path / "integration_p2.db")
    undo_mgr = UndoManager()
    queue_svc = TaskQueueService(storage, undo_mgr)

    # 1. Create task through storage and record action
    task = Task(title="Integration Task", priority=Priority.HIGH.value, duration=60)
    created = storage.create_task(task)
    task_id = created.id
    assert task_id is not None
    undo_mgr.record_action(
        action_type=ActionType.CREATE,
        task_id=task_id,
        after_state=created,
    )
    assert storage.get_task(task_id) is not None

    # 2. Undo creation
    undo_mgr.undo(storage)
    assert storage.get_task(task_id) is None

    # 3. Redo creation -> same ID restored
    undo_mgr.redo(storage)
    restored = storage.get_task(task_id)
    assert restored is not None
    assert restored.id == task_id
    assert restored.title == "Integration Task"

    # Refresh queue
    queue_svc.refresh()
    assert queue_svc.size() == 1
    assert queue_svc.peek_next_task().id == task_id  # type: ignore

    # 4. Process the next pending task
    processed = queue_svc.process_next_task()
    assert processed is not None
    assert processed.id == task_id
    assert processed.status == TaskStatus.IN_PROGRESS.value

    # Verify database reflects In Progress
    db_task = storage.get_task(task_id)
    assert db_task is not None
    assert db_task.status == "In Progress"
    assert queue_svc.size() == 0

    # 5. Undo processing action
    assert undo_mgr.can_undo() is True
    undo_mgr.undo(storage)
    reverted_task = storage.get_task(task_id)
    assert reverted_task is not None
    assert reverted_task.status == "Pending"

    # Queue refresh reflects restored pending task
    queue_svc.refresh()
    assert queue_svc.size() == 1

    # 6. Redo processing action
    assert undo_mgr.can_redo() is True
    undo_mgr.redo(storage)
    final_task = storage.get_task(task_id)
    assert final_task is not None
    assert final_task.status == "In Progress"

    queue_svc.refresh()
    assert queue_svc.size() == 0
