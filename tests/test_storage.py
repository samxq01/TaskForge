"""Integration tests for TaskForge SQLite storage."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing a fresh isolated SQLite TaskStorage."""
    db_file = tmp_path / "test_tasks.db"
    return TaskStorage(db_file)


def test_init_db_creates_table(storage: TaskStorage) -> None:
    """Ensure database table and indexes are created successfully."""
    counts = storage.count_tasks()
    assert counts == {"total": 0, "pending": 0, "in_progress": 0, "completed": 0, "overdue": 0}


def test_create_and_get_task(storage: TaskStorage) -> None:
    """Test inserting a new task and retrieving it by primary key ID."""
    task = Task(
        title="Write unit tests",
        description="Cover all CRUD paths",
        priority=Priority.HIGH.value,
        duration=60,
        due_date=datetime(2026, 12, 1, 10, 0, 0),
    )
    created = storage.create_task(task)
    assert created.id is not None
    assert created.id > 0

    retrieved = storage.get_task(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Write unit tests"
    assert retrieved.description == "Cover all CRUD paths"
    assert retrieved.priority == 3
    assert retrieved.duration == 60
    assert retrieved.status == "Pending"
    assert retrieved.due_date == datetime(2026, 12, 1, 10, 0, 0)


def test_get_nonexistent_task(storage: TaskStorage) -> None:
    """Retrieving a non-existent task returns None."""
    assert storage.get_task(9999) is None


def test_update_task(storage: TaskStorage) -> None:
    """Test updating existing task fields."""
    task = Task(title="Initial Title", duration=30)
    created = storage.create_task(task)
    task_id = created.id
    assert task_id is not None

    created.title = "Updated Title"
    created.priority = Priority.URGENT.value
    created.duration = 45
    created.status = TaskStatus.IN_PROGRESS.value
    created.due_date = datetime(2026, 11, 20, 15, 0, 0)

    updated = storage.update_task(created)
    assert updated.title == "Updated Title"
    assert updated.priority == 4
    assert updated.status == "In Progress"

    # Verify persistence by reading afresh
    fresh = storage.get_task(task_id)
    assert fresh is not None
    assert fresh.title == "Updated Title"
    assert fresh.priority == 4
    assert fresh.duration == 45
    assert fresh.status == "In Progress"
    assert fresh.due_date == datetime(2026, 11, 20, 15, 0, 0)


def test_update_nonexistent_task(storage: TaskStorage) -> None:
    """Updating a non-existent task raises ValueError."""
    ghost = Task(id=8888, title="Ghost Task")
    with pytest.raises(ValueError, match="does not exist"):
        storage.update_task(ghost)


def test_delete_task(storage: TaskStorage) -> None:
    """Test deleting an existing task and verifying removal."""
    task = Task(title="Task to Delete")
    created = storage.create_task(task)
    task_id = created.id
    assert task_id is not None

    assert storage.delete_task(task_id) is True
    assert storage.get_task(task_id) is None

    # Deleting again returns False
    assert storage.delete_task(task_id) is False


def test_list_tasks_filtering_and_search(storage: TaskStorage) -> None:
    """Test listing tasks with status, priority, and text search filters."""
    t1 = storage.create_task(
        Task(title="Design Database", description="SQLite schema setup", priority=4, status="Completed")
    )
    t2 = storage.create_task(
        Task(title="Build Streamlit UI", description="Design interactive widgets", priority=3, status="In Progress")
    )
    t3 = storage.create_task(
        Task(title="Write Documentation", description="CO mapping and guides", priority=2, status="Pending")
    )
    t4 = storage.create_task(
        Task(title="Review Algorithms", description="Verify data structures", priority=3, status="Pending")
    )

    # All tasks
    all_tasks = storage.list_tasks()
    assert len(all_tasks) == 4

    # Status filter
    pending_tasks = storage.list_tasks(status="Pending")
    assert len(pending_tasks) == 2
    assert {t.title for t in pending_tasks} == {"Write Documentation", "Review Algorithms"}

    # Priority filter
    high_priority = storage.list_tasks(priority=3)
    assert len(high_priority) == 2
    assert {t.title for t in high_priority} == {"Build Streamlit UI", "Review Algorithms"}

    # Search filter (title match)
    doc_search = storage.list_tasks(search="Documentation")
    assert len(doc_search) == 1
    assert doc_search[0].title == "Write Documentation"

    # Search filter (description match)
    schema_search = storage.list_tasks(search="schema")
    assert len(schema_search) == 1
    assert schema_search[0].title == "Design Database"

    # Combined filters
    combined = storage.list_tasks(status="Pending", priority=3)
    assert len(combined) == 1
    assert combined[0].title == "Review Algorithms"


def test_count_tasks_metrics(storage: TaskStorage) -> None:
    """Verify aggregate task counts including overdue tasks."""
    now = datetime(2026, 10, 29, 12, 0, 0)
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    # 1. Pending + Overdue
    storage.create_task(Task(title="Overdue Pending", due_date=yesterday, status="Pending"))
    # 2. In Progress + Overdue
    storage.create_task(Task(title="Overdue In Progress", due_date=yesterday, status="In Progress"))
    # 3. Completed + Past deadline (should NOT be counted as overdue)
    storage.create_task(Task(title="Completed Past", due_date=yesterday, status="Completed"))
    # 4. In Progress + Future deadline (not overdue)
    storage.create_task(Task(title="Active Normal", due_date=tomorrow, status="In Progress"))
    # 5. Pending + No deadline (not overdue)
    storage.create_task(Task(title="Unscheduled Pending", due_date=None, status="Pending"))

    metrics = storage.count_tasks(as_of=now)
    assert metrics["total"] == 5
    assert metrics["pending"] == 2
    assert metrics["in_progress"] == 2
    assert metrics["completed"] == 1
    assert metrics["overdue"] == 2


def test_persistence_across_instances(tmp_path: Path) -> None:
    """Verify data persists when a new TaskStorage instance connects to the same file."""
    db_file = tmp_path / "persistent.db"

    # Instance 1: write data
    storage1 = TaskStorage(db_file)
    task1 = storage1.create_task(Task(title="Persistent Task 1", priority=4, duration=45))
    task2 = storage1.create_task(Task(title="Persistent Task 2", priority=2, duration=15))

    # Instance 2: read and verify data
    storage2 = TaskStorage(db_file)
    tasks = storage2.list_tasks()
    assert len(tasks) == 2
    titles = [t.title for t in tasks]
    assert "Persistent Task 1" in titles
    assert "Persistent Task 2" in titles

    # Modify in instance 2
    t1 = storage2.get_task(task1.id)  # type: ignore
    assert t1 is not None
    t1.status = TaskStatus.COMPLETED.value
    storage2.update_task(t1)

    # Re-read in fresh instance 3
    storage3 = TaskStorage(db_file)
    fresh_t1 = storage3.get_task(task1.id)  # type: ignore
    assert fresh_t1 is not None
    assert fresh_t1.status == "Completed"
