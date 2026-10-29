"""Unit tests for manual sorting algorithms (Insertion Sort and Merge Sort) and Task sorting rules."""

from datetime import datetime, timedelta
import random
import pytest

from taskforge.algorithms.sorting import (
    SortResult,
    insertion_sort,
    merge_sort,
    task_deadline_key,
    task_id_key,
    task_priority_deadline_key,
    task_priority_key,
)
from taskforge.models import Priority, Task


@pytest.mark.parametrize("sort_fn", [insertion_sort, merge_sort])
def test_sort_empty_and_single(sort_fn) -> None:
    """Sorting empty or single-item lists works without error."""
    res_empty = sort_fn([])
    assert res_empty.items == []
    assert res_empty.comparisons == 0

    res_single = sort_fn([42])
    assert res_single.items == [42]


@pytest.mark.parametrize("sort_fn", [insertion_sort, merge_sort])
def test_sort_numbers_basic(sort_fn) -> None:
    """Sorting numbers produces correct ascending order and matches Python sorted()."""
    data = [64, 34, 25, 12, 22, 11, 90, -5, 0, 12]
    res = sort_fn(data)
    assert res.items == sorted(data)
    # Verify input collection was not mutated
    assert data == [64, 34, 25, 12, 22, 11, 90, -5, 0, 12]


@pytest.mark.parametrize("sort_fn", [insertion_sort, merge_sort])
def test_sort_reverse_flag(sort_fn) -> None:
    """Sorting with reverse=True produces descending order."""
    data = [5, 1, 9, 3, 7]
    res = sort_fn(data, reverse=True)
    assert res.items == [9, 7, 5, 3, 1]


@pytest.mark.parametrize("sort_fn", [insertion_sort, merge_sort])
def test_sort_already_sorted_and_reversed(sort_fn) -> None:
    """Sorting handles already sorted and reverse-sorted input."""
    sorted_input = [1, 2, 3, 4, 5]
    res1 = sort_fn(sorted_input)
    assert res1.items == [1, 2, 3, 4, 5]

    reverse_input = [5, 4, 3, 2, 1]
    res2 = sort_fn(reverse_input)
    assert res2.items == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("sort_fn", [insertion_sort, merge_sort])
def test_sort_stability(sort_fn) -> None:
    """Algorithms must be stable: preserve relative order of elements with equal keys."""
    # Pairs of (key, original_order)
    items = [(2, "first_2"), (1, "first_1"), (2, "second_2"), (1, "second_1"), (2, "third_2")]
    res = sort_fn(items, key=lambda x: x[0])

    expected = [(1, "first_1"), (1, "second_1"), (2, "first_2"), (2, "second_2"), (2, "third_2")]
    assert res.items == expected


# ---------------- TASK SPECIFIC SORTING TESTS ----------------

def test_task_deadline_sorting() -> None:
    """Deadline ascending: earliest deadline first, tasks without deadline at the end."""
    now = datetime(2026, 10, 29, 12, 0)
    t1 = Task(id=1, title="No Deadline 1", due_date=None)
    t2 = Task(id=2, title="Tomorrow", due_date=now + timedelta(days=1))
    t3 = Task(id=3, title="Today", due_date=now)
    t4 = Task(id=4, title="No Deadline 2", due_date=None)

    tasks = [t1, t2, t3, t4]

    for sort_fn in [insertion_sort, merge_sort]:
        res = sort_fn(tasks, key=task_deadline_key)
        ordered_ids = [t.id for t in res.items]
        # t3 (today) -> t2 (tomorrow) -> t1 (no deadline, id=1) -> t4 (no deadline, id=4)
        assert ordered_ids == [3, 2, 1, 4]


def test_task_priority_sorting() -> None:
    """Priority descending: Urgent (4), High (3), Medium (2), Low (1)."""
    t1 = Task(id=1, title="Low", priority=Priority.LOW.value)
    t2 = Task(id=2, title="Urgent", priority=Priority.URGENT.value)
    t3 = Task(id=3, title="Medium", priority=Priority.MEDIUM.value)
    t4 = Task(id=4, title="High", priority=Priority.HIGH.value)

    tasks = [t1, t2, t3, t4]

    for sort_fn in [insertion_sort, merge_sort]:
        res = sort_fn(tasks, key=task_priority_key)
        ordered_priorities = [t.priority for t in res.items]
        assert ordered_priorities == [4, 3, 2, 1]


def test_task_priority_and_deadline_tie_breaking() -> None:
    """Priority descending, then earliest deadline, then task ID."""
    now = datetime(2026, 10, 29, 12, 0)

    # Priority 3, earlier deadline
    t_high_early = Task(id=10, title="High Early", priority=3, due_date=now + timedelta(days=1))
    # Priority 3, later deadline
    t_high_late = Task(id=20, title="High Late", priority=3, due_date=now + timedelta(days=3))
    # Priority 4, late deadline (higher priority wins over deadline)
    t_urg_late = Task(id=30, title="Urgent Late", priority=4, due_date=now + timedelta(days=5))
    # Priority 3, no deadline (comes after priority 3 with deadline)
    t_high_none = Task(id=40, title="High No Deadline", priority=3, due_date=None)

    tasks = [t_high_late, t_high_none, t_urg_late, t_high_early]

    for sort_fn in [insertion_sort, merge_sort]:
        res = sort_fn(tasks, key=task_priority_deadline_key)
        ordered_ids = [t.id for t in res.items]
        # Expected:
        # 1. t_urg_late (priority 4)
        # 2. t_high_early (priority 3, day 1)
        # 3. t_high_late (priority 3, day 3)
        # 4. t_high_none (priority 3, no deadline)
        assert ordered_ids == [30, 10, 20, 40]


def test_task_id_sorting() -> None:
    """Sorting tasks by ID ascending for Binary Search preparation."""
    tasks = [
        Task(id=50, title="T50"),
        Task(id=10, title="T10"),
        Task(id=30, title="T30"),
        Task(id=20, title="T20"),
    ]
    for sort_fn in [insertion_sort, merge_sort]:
        res = sort_fn(tasks, key=task_id_key)
        assert [t.id for t in res.items] == [10, 20, 30, 50]
