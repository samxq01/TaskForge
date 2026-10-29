"""Integration tests connecting custom searching and sorting algorithms with TaskForge tasks."""

from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.algorithms.searching import binary_search, linear_search
from taskforge.algorithms.sorting import (
    insertion_sort,
    merge_sort,
    task_deadline_key,
    task_id_key,
    task_priority_deadline_key,
    task_priority_key,
)
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.undo_manager import UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated SQLite database."""
    return TaskStorage(tmp_path / "integration_dsa.db")


def test_task_search_and_sort_integration(storage: TaskStorage) -> None:
    """Verify that tasks retrieved from SQLite can be sorted and searched using custom algorithms
    without modifying database records or producing side-effects.
    """
    now = datetime(2026, 10, 29, 12, 0)
    t1 = storage.create_task(
        Task(title="Alpha", priority=Priority.LOW.value, due_date=now + timedelta(days=2))
    )
    t2 = storage.create_task(
        Task(title="Beta", priority=Priority.URGENT.value, due_date=now + timedelta(days=1))
    )
    t3 = storage.create_task(
        Task(title="Gamma", priority=Priority.HIGH.value, due_date=None)
    )

    tasks = storage.list_tasks()
    assert len(tasks) == 3

    # 1. Sort by Priority descending using custom Merge Sort
    res_prio = merge_sort(tasks, key=task_priority_key)
    assert [t.priority for t in res_prio.items] == [4, 3, 1]
    assert [t.title for t in res_prio.items] == ["Beta", "Gamma", "Alpha"]

    # 2. Sort by Deadline ascending using custom Insertion Sort
    res_deadline = insertion_sort(tasks, key=task_deadline_key)
    assert [t.title for t in res_deadline.items] == ["Beta", "Alpha", "Gamma"]

    # 3. Prepare data for Binary Search by sorting by Task ID
    sorted_by_id = merge_sort(tasks, key=task_id_key).items

    # 4. Search by Task ID using Binary Search
    target_id = t2.id
    assert target_id is not None
    search_res = binary_search(sorted_by_id, target=target_id, key=task_id_key)
    assert search_res.found is True
    assert search_res.item is not None
    assert search_res.item.title == "Beta"

    # 5. Search by title using Linear Search
    search_title = linear_search(tasks, target="Gamma", key=lambda t: t.title)
    assert search_title.found is True
    assert search_title.item is not None
    assert search_title.item.id == t3.id

    # 6. Verify SQLite records remained completely unchanged
    db_tasks = storage.list_tasks()
    assert len(db_tasks) == 3
    t1_fresh = storage.get_task(t1.id)  # type: ignore
    assert t1_fresh is not None
    assert t1_fresh.title == "Alpha"
    assert t1_fresh.priority == 1
