"""Custom generic Heap-based Priority Queue implementation (CO1, CO5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")
P = TypeVar("P")


class EmptyPriorityQueueError(IndexError):
    """Raised when attempting to pop or peek from an empty priority queue."""
    pass


class _HeapNode(Generic[T, P]):
    """Internal heap node holding item payload, comparable priority, and insertion sequence."""

    __slots__ = ("item", "priority", "entry_id")

    def __init__(self, item: T, priority: P, entry_id: int) -> None:
        self.item: T = item
        self.priority: P = priority
        self.entry_id: int = entry_id

    def __lt__(self, other: _HeapNode[T, P]) -> bool:
        if self.priority == other.priority:
            # Deterministic FIFO tie-breaking on identical priority keys
            return self.entry_id < other.entry_id
        return self.priority < other.priority  # type: ignore[operator]

    def __repr__(self) -> str:
        return f"_HeapNode(priority={self.priority!r}, item={self.item!r})"


class PriorityQueue(Generic[T, P]):
    """A custom generic binary Min-Heap priority queue.
    
    Academic Objectives (CO1, CO5):
        - Pure Python manual binary heap implementation without standard `heapq`.
        - Sift-up and sift-down mechanics maintaining the heap-order property.
        - Guarantees O(log n) push and pop, and O(1) peek.
        - Deterministic tie-breaking on identical priorities using monotonic entry sequence.
        - Powers the TaskForge Smart Auto-Scheduler ranking policy.
        
    Complexity:
        - push(item, priority): O(log n)
        - pop(): O(log n)
        - peek(): O(1)
        - size(): O(1)
        - is_empty(): O(1)
        - Space: O(n)
    """

    def __init__(self) -> None:
        """Initialize an empty priority queue."""
        self._heap: list[_HeapNode[T, P]] = []
        self._entry_counter: int = 0

    def push(self, item: T, priority: P) -> None:
        """Add an item with a comparable priority key into the heap.
        
        Args:
            item: Payload data.
            priority: Comparable priority key (smaller values pop first in Min-Heap).
        """
        node = _HeapNode(item=item, priority=priority, entry_id=self._entry_counter)
        self._entry_counter += 1
        self._heap.append(node)
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> T:
        """Remove and return the highest-priority (minimum key) item.
        
        Returns:
            The payload of the minimum heap node.
            
        Raises:
            EmptyPriorityQueueError: If the queue is empty.
        """
        item, _ = self.pop_with_priority()
        return item

    def pop_with_priority(self) -> tuple[T, P]:
        """Remove and return the highest-priority item along with its priority key.
        
        Returns:
            Tuple of (item, priority).
            
        Raises:
            EmptyPriorityQueueError: If the queue is empty.
        """
        if not self._heap:
            raise EmptyPriorityQueueError("Cannot pop from an empty PriorityQueue.")

        # Swap root with last element
        min_node = self._heap[0]
        last_node = self._heap.pop()

        if self._heap:
            self._heap[0] = last_node
            self._sift_down(0)

        return min_node.item, min_node.priority

    def peek(self) -> T:
        """Inspect the highest-priority item without removing it.
        
        Returns:
            The payload of the minimum heap node.
            
        Raises:
            EmptyPriorityQueueError: If the queue is empty.
        """
        item, _ = self.peek_with_priority()
        return item

    def peek_with_priority(self) -> tuple[T, P]:
        """Inspect the highest-priority item and its priority key without removing it.
        
        Returns:
            Tuple of (item, priority).
            
        Raises:
            EmptyPriorityQueueError: If the queue is empty.
        """
        if not self._heap:
            raise EmptyPriorityQueueError("Cannot peek into an empty PriorityQueue.")
        return self._heap[0].item, self._heap[0].priority

    def size(self) -> int:
        """Return the number of elements currently stored in the priority queue."""
        return len(self._heap)

    def is_empty(self) -> bool:
        """Return True if the priority queue contains no items."""
        return len(self._heap) == 0

    def clear(self) -> None:
        """Reset the priority queue to an empty state."""
        self._heap.clear()
        self._entry_counter = 0

    def to_list(self) -> list[tuple[T, P]]:
        """Return a shallow snapshot copy of heap nodes as (item, priority) pairs."""
        return [(node.item, node.priority) for node in self._heap]

    def _sift_up(self, index: int) -> None:
        """Move node at index upward until the heap invariant is restored."""
        curr = index
        while curr > 0:
            parent = (curr - 1) // 2
            if self._heap[curr] < self._heap[parent]:
                self._heap[curr], self._heap[parent] = self._heap[parent], self._heap[curr]
                curr = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        """Move node at index downward until the heap invariant is restored."""
        curr = index
        n = len(self._heap)

        while True:
            left = 2 * curr + 1
            right = 2 * curr + 2
            smallest = curr

            if left < n and self._heap[left] < self._heap[smallest]:
                smallest = left

            if right < n and self._heap[right] < self._heap[smallest]:
                smallest = right

            if smallest != curr:
                self._heap[curr], self._heap[smallest] = self._heap[smallest], self._heap[curr]
                curr = smallest
            else:
                break


def make_task_ranking_key(task: Any, insertion_seq: int = 0) -> tuple[int, int, datetime, int, int, int]:
    """Generate a deterministic ranking key tuple for task scheduling in a Min-Heap.
    
    Ranking Policy:
        1. Higher priority first: Urgent (4) -> High (3) -> Medium (2) -> Low (1).
           Implemented via `-task.priority` so higher priority yields a smaller tuple value.
        2. Tasks with deadlines precede unscheduled tasks of comparable priority:
           `has_deadline_flag`: 0 if task has deadline, 1 if no deadline.
        3. Earlier deadline first among tasks with deadlines:
           `normalized_deadline`: exact timestamp or `datetime.max` if unscheduled.
        4. Shorter estimated duration first as tie-breaker:
           `task.duration` in minutes.
        5. Lower task ID first as final task-level tie-breaker:
           `task.id`.
        6. Monotonic insertion sequence as internal guard against payload comparison.
        
    Args:
        task: Task instance to rank.
        insertion_seq: Monotonic counter.
        
    Returns:
        A fully comparable 6-tuple.
    """
    priority_val = -int(task.priority)
    has_deadline = 0 if task.due_date is not None else 1
    deadline_val = task.due_date if task.due_date is not None else datetime.max
    duration_val = int(task.duration)
    task_id_val = int(task.id) if task.id is not None else 0

    return (priority_val, has_deadline, deadline_val, duration_val, task_id_val, insertion_seq)
