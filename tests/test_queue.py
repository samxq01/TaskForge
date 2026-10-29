"""Unit tests for the custom Queue data structure."""

import pytest

from taskforge.structures.queue import EmptyQueueError, Queue


def test_empty_queue_properties() -> None:
    """An initialized queue must be empty and have size 0."""
    queue: Queue[int] = Queue()
    assert queue.is_empty() is True
    assert queue.size() == 0
    assert len(queue) == 0
    assert bool(queue) is False
    assert queue.to_list() == []


def test_enqueue_and_peek() -> None:
    """Enqueueing elements updates size and peek reflects the front element."""
    queue: Queue[str] = Queue()
    queue.enqueue("first")
    assert queue.is_empty() is False
    assert queue.size() == 1
    assert queue.peek() == "first"

    queue.enqueue("second")
    assert queue.size() == 2
    assert queue.peek() == "first"  # Front remains unchanged


def test_fifo_order_dequeue() -> None:
    """Elements must be dequeued in arrival order (FIFO)."""
    queue: Queue[int] = Queue()
    for item in [100, 200, 300]:
        queue.enqueue(item)

    assert queue.dequeue() == 100
    assert queue.dequeue() == 200
    assert queue.dequeue() == 300
    assert queue.is_empty() is True


def test_dequeue_empty_queue_raises_error() -> None:
    """Dequeuing an empty queue must raise EmptyQueueError."""
    queue: Queue[int] = Queue()
    with pytest.raises(EmptyQueueError, match="Cannot dequeue from an empty queue"):
        queue.dequeue()


def test_peek_empty_queue_raises_error() -> None:
    """Peeking an empty queue must raise EmptyQueueError."""
    queue: Queue[int] = Queue()
    with pytest.raises(EmptyQueueError, match="Cannot peek into an empty queue"):
        queue.peek()


def test_to_list_inspection_safety() -> None:
    """to_list() returns items in FIFO order (front to rear) safely."""
    queue: Queue[str] = Queue()
    queue.enqueue("front")
    queue.enqueue("middle")
    queue.enqueue("rear")

    items = queue.to_list()
    assert items == ["front", "middle", "rear"]

    # Mutating returned snapshot does not corrupt queue
    items.pop(0)
    assert queue.size() == 3
    assert queue.peek() == "front"


def test_clear_queue() -> None:
    """Clearing a queue resets it to an empty state."""
    queue: Queue[int] = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.clear()
    assert queue.is_empty() is True
    assert queue.size() == 0


def test_interleaved_enqueue_dequeue() -> None:
    """Interleaving enqueue and dequeue maintains FIFO consistency."""
    queue: Queue[int] = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() == 1

    queue.enqueue(3)
    queue.enqueue(4)
    assert queue.dequeue() == 2
    assert queue.dequeue() == 3
    assert queue.dequeue() == 4
    assert queue.is_empty() is True
