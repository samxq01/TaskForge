"""Integration tests connecting the custom BST with TaskForge SQLite storage and models (CO4)."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_index import (
    TaskIndexService,
    make_deadline_key,
    make_search_key,
)
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide a fresh SQLite storage instance."""
    return TaskStorage(tmp_path / "test_bst_integration.db")


@pytest.fixture
def index_service(storage: TaskStorage) -> TaskIndexService:
    """Provide a TaskIndexService instance."""
    return TaskIndexService(storage)


def test_make_deadline_key_ordering() -> None:
    """Verify composite key ordering rules:
    1. Tasks with deadline before tasks without deadline.
    2. Earlier deadline before later deadline.
    3. Equal deadlines tie-broken by task ID.
    4. Tasks without deadline tie-broken by task ID.
    """
    now = datetime(2026, 10, 29, 12, 0)

    t_early = Task(id=1, title="Early", due_date=now)
    t_late = Task(id=2, title="Late", due_date=now + timedelta(days=2))
    t_same_due_1 = Task(id=10, title="Same 1", due_date=now + timedelta(days=1))
    t_same_due_2 = Task(id=20, title="Same 2", due_date=now + timedelta(days=1))
    t_no_due_1 = Task(id=100, title="No Due 1", due_date=None)
    t_no_due_2 = Task(id=200, title="No Due 2", due_date=None)

    k_early = make_deadline_key(t_early)
    k_late = make_deadline_key(t_late)
    k_same_1 = make_deadline_key(t_same_due_1)
    k_same_2 = make_deadline_key(t_same_due_2)
    k_none_1 = make_deadline_key(t_no_due_1)
    k_none_2 = make_deadline_key(t_no_due_2)

    # Verify strict ascending order
    assert k_early < k_same_1 < k_same_2 < k_late < k_none_1 < k_none_2


def test_bst_index_rebuild_from_sqlite(storage: TaskStorage, index_service: TaskIndexService) -> None:
    """Verify building the BST index from SQLite records and extracting in deadline order."""
    now = datetime(2026, 10, 29, 12, 0)
    t_late = storage.create_task(Task(title="Late Task", due_date=now + timedelta(days=5)))
    t_none = storage.create_task(Task(title="Unscheduled Task", due_date=None))
    t_early = storage.create_task(Task(title="Early Task", due_date=now + timedelta(days=1)))

    index_service.rebuild()
    assert index_service.get_tree_size() == 3

    ordered = index_service.get_deadline_ordered_tasks()
    ordered_ids = [t.id for t in ordered]
    # Expected: t_early -> t_late -> t_none
    assert ordered_ids == [t_early.id, t_late.id, t_none.id]


def test_bst_search_by_deadline_and_id(storage: TaskStorage, index_service: TaskIndexService) -> None:
    """Searching for a task by its exact deadline composite key returns the correct Task."""
    now = datetime(2026, 11, 15, 10, 0)
    task = storage.create_task(Task(title="Find Me In Tree", due_date=now, priority=4))
    task_id = task.id
    assert task_id is not None

    index_service.rebuild()

    # Search existing
    found = index_service.search_by_deadline_and_id(now, task_id)
    assert found is not None
    assert found.id == task_id
    assert found.title == "Find Me In Tree"

    # Search non-existing
    missing = index_service.search_by_deadline_and_id(now, 9999)
    assert missing is None


def test_bst_index_consistency_across_mutations_and_undo_redo(
    storage: TaskStorage, index_service: TaskIndexService
) -> None:
    """Verify index consistency through task creation, editing, deletion, undo, and redo."""
    undo_mgr = UndoManager()
    now = datetime(2026, 10, 29, 12, 0)

    # 1. Create task
    t = storage.create_task(Task(title="Mutation Task", due_date=now + timedelta(days=2)))
    task_id = t.id
    assert task_id is not None
    undo_mgr.record_action(ActionType.CREATE, task_id, after_state=t)

    index_service.rebuild()
    assert index_service.get_tree_size() == 1
    assert index_service.search_by_task(t) is not None

    # 2. Undo creation
    undo_mgr.undo(storage)
    index_service.rebuild()
    assert index_service.get_tree_size() == 0
    assert index_service.search_by_task(t) is None

    # 3. Redo creation
    undo_mgr.redo(storage)
    index_service.rebuild()
    assert index_service.get_tree_size() == 1

    # 4. Edit task deadline
    before_edit = storage.get_task(task_id)
    assert before_edit is not None
    new_due = now - timedelta(days=1)
    t.due_date = new_due
    storage.update_task(t)
    undo_mgr.record_action(ActionType.EDIT, task_id, before_state=before_edit, after_state=t)

    index_service.rebuild()
    # Old deadline key should not exist, new deadline key should exist
    assert index_service.search_by_deadline_and_id(before_edit.due_date, task_id) is None
    assert index_service.search_by_deadline_and_id(new_due, task_id) is not None

    # 5. Delete task
    before_del = storage.get_task(task_id)
    storage.delete_task(task_id)
    undo_mgr.record_action(ActionType.DELETE, task_id, before_state=before_del)

    index_service.rebuild()
    assert index_service.get_tree_size() == 0

    # 6. Undo deletion -> task restored into tree
    undo_mgr.undo(storage)
    index_service.rebuild()
    assert index_service.get_tree_size() == 1
    restored = index_service.search_by_deadline_and_id(new_due, task_id)
    assert restored is not None
    assert restored.id == task_id


def test_bst_traversals_matching_tasks(storage: TaskStorage, index_service: TaskIndexService) -> None:
    """Preorder, Inorder, and Postorder entries match nodes in the tree."""
    now = datetime(2026, 10, 29, 12, 0)
    # Insert 3 tasks
    storage.create_task(Task(title="T1", due_date=now + timedelta(days=2)))
    storage.create_task(Task(title="T2", due_date=now + timedelta(days=1)))
    storage.create_task(Task(title="T3", due_date=now + timedelta(days=3)))

    index_service.rebuild()
    assert index_service.get_tree_size() == 3

    inorder = index_service.get_inorder_entries()
    preorder = index_service.get_preorder_entries()
    postorder = index_service.get_postorder_entries()

    assert len(inorder) == 3
    assert len(preorder) == 3
    assert len(postorder) == 3

    # Inorder is strictly sorted by deadline
    titles_inorder = [item[1].title for item in inorder]
    assert titles_inorder == ["T2", "T1", "T3"]
