"""Unit tests for custom Heap-based PriorityQueue data structure (CO1, CO5)."""

from datetime import datetime, timedelta
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.structures.priority_queue import (
    EmptyPriorityQueueError,
    PriorityQueue,
    make_task_ranking_key,
)


def test_empty_priority_queue() -> None:
    """Test initial empty state of PriorityQueue."""
    pq: PriorityQueue[str, int] = PriorityQueue()
    assert pq.size() == 0
    assert pq.is_empty() is True
    assert pq.to_list() == []

    with pytest.raises(EmptyPriorityQueueError, match="Cannot pop"):
        pq.pop()

    with pytest.raises(EmptyPriorityQueueError, match="Cannot peek"):
        pq.peek()


def test_push_and_peek() -> None:
    """Test pushing items and peeking the highest priority."""
    pq: PriorityQueue[str, int] = PriorityQueue()
    pq.push("task_c", 30)
    assert pq.size() == 1
    assert pq.is_empty() is False
    assert pq.peek() == "task_c"

    # Push item with higher priority (smaller value in Min-Heap)
    pq.push("task_a", 10)
    assert pq.size() == 2
    assert pq.peek() == "task_a"
    assert pq.peek_with_priority() == ("task_a", 10)


def test_push_and_pop_min_heap_ordering() -> None:
    """Test that items are popped in strictly ascending order of priority keys."""
    pq: PriorityQueue[str, int] = PriorityQueue()
    items = [("three", 3), ("one", 1), ("four", 4), ("one_half", 2), ("zero", 0)]

    for payload, priority in items:
        pq.push(payload, priority)

    assert pq.size() == 5
    popped = [pq.pop() for _ in range(5)]
    assert popped == ["zero", "one", "one_half", "three", "four"]
    assert pq.is_empty() is True


def test_repeated_and_equal_priorities_fifo_tiebreak() -> None:
    """Test that equal priority keys preserve insertion sequence."""
    pq: PriorityQueue[str, int] = PriorityQueue()
    pq.push("item_1", 5)
    pq.push("item_2", 5)
    pq.push("item_3", 5)

    assert pq.pop() == "item_1"
    assert pq.pop() == "item_2"
    assert pq.pop() == "item_3"


def test_clear_and_reuse() -> None:
    """Test clearing and re-using the priority queue."""
    pq: PriorityQueue[str, int] = PriorityQueue()
    pq.push("a", 1)
    pq.push("b", 2)
    assert pq.size() == 2

    pq.clear()
    assert pq.size() == 0
    assert pq.is_empty() is True

    pq.push("c", 10)
    assert pq.size() == 1
    assert pq.pop() == "c"


def test_large_random_heap_operations() -> None:
    """Test heap invariant integrity under large numbers of insertions and removals."""
    pq: PriorityQueue[int, int] = PriorityQueue()
    import random
    rng = random.Random(42)
    values = [rng.randint(-500, 500) for _ in range(300)]

    for v in values:
        pq.push(v, v)

    assert pq.size() == 300
    expected_sorted = sorted(values)
    actual_popped = [pq.pop() for _ in range(300)]
    assert actual_popped == expected_sorted
    assert pq.is_empty() is True


def test_make_task_ranking_key_priority_ordering() -> None:
    """Test that make_task_ranking_key enforces the 5-tier scheduling ranking policy."""
    now = datetime(2026, 10, 30, 12, 0)

    # 1. Higher Priority beats Lower Priority regardless of deadline
    urgent_task = Task(id=1, title="Urgent", priority=Priority.URGENT.value, duration=100, due_date=now + timedelta(days=5))
    high_task = Task(id=2, title="High", priority=Priority.HIGH.value, duration=30, due_date=now + timedelta(hours=1))
    assert make_task_ranking_key(urgent_task) < make_task_ranking_key(high_task)

    # 2. Same Priority: Task with deadline beats task without deadline
    med_with_due = Task(id=3, title="Med Due", priority=Priority.MEDIUM.value, duration=60, due_date=now + timedelta(days=2))
    med_no_due = Task(id=4, title="Med No Due", priority=Priority.MEDIUM.value, duration=60, due_date=None)
    assert make_task_ranking_key(med_with_due) < make_task_ranking_key(med_no_due)

    # 3. Same Priority with deadline: Earlier deadline beats later deadline
    due_tomorrow = Task(id=5, title="Due Tomorrow", priority=Priority.HIGH.value, duration=60, due_date=now + timedelta(days=1))
    due_next_week = Task(id=6, title="Due Next Week", priority=Priority.HIGH.value, duration=60, due_date=now + timedelta(days=7))
    assert make_task_ranking_key(due_tomorrow) < make_task_ranking_key(due_next_week)

    # 4. Same Priority and Deadline: Shorter duration beats longer duration
    short_task = Task(id=7, title="Short", priority=Priority.HIGH.value, duration=30, due_date=now + timedelta(days=1))
    long_task = Task(id=8, title="Long", priority=Priority.HIGH.value, duration=120, due_date=now + timedelta(days=1))
    assert make_task_ranking_key(short_task) < make_task_ranking_key(long_task)

    # 5. Same Priority, Deadline, Duration: Lower Task ID beats higher Task ID
    id_lower = Task(id=10, title="ID 10", priority=Priority.LOW.value, duration=45, due_date=now + timedelta(days=1))
    id_higher = Task(id=20, title="ID 20", priority=Priority.LOW.value, duration=45, due_date=now + timedelta(days=1))
    assert make_task_ranking_key(id_lower) < make_task_ranking_key(id_higher)
