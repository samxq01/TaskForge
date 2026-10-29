"""Custom generic Queue data structure implementing FIFO (First-In, First-Out)."""

from __future__ import annotations

from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class EmptyQueueError(IndexError):
    """Raised when attempting to dequeue or peek an empty queue."""
    pass


class _Node(Generic[T]):
    """Internal singly-linked node for the Queue implementation."""

    __slots__ = ("value", "next")

    def __init__(self, value: T, next_node: Optional[_Node[T]] = None) -> None:
        self.value: T = value
        self.next: Optional[_Node[T]] = next_node


class Queue(Generic[T]):
    """A generic FIFO (First-In, First-Out) queue data structure.
    
    This implementation uses a singly-linked list with head and tail pointers
    to achieve guaranteed O(1) enqueue and dequeue operations without relying
    on `collections.deque` or experiencing O(n) list pop(0) penalties.
    
    Time Complexity:
        - enqueue(item): O(1)
        - dequeue(): O(1)
        - peek(): O(1)
        - is_empty(): O(1)
        - size(): O(1)
        
    Space Complexity:
        - O(n) where n is the number of queued elements.
    """

    def __init__(self) -> None:
        """Initialize an empty queue."""
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size: int = 0

    def enqueue(self, item: T) -> None:
        """Add an element to the rear of the queue.
        
        Args:
            item: Element to enqueue.
            
        Complexity:
            O(1).
        """
        new_node = _Node(item)
        if self._tail is None:
            # Queue was empty
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def dequeue(self) -> T:
        """Remove and return the element at the front of the queue.
        
        Returns:
            The front element (the oldest enqueued item).
            
        Raises:
            EmptyQueueError: If the queue is empty.
            
        Complexity:
            O(1).
        """
        if self.is_empty():
            raise EmptyQueueError("Cannot dequeue from an empty queue.")
        assert self._head is not None

        item = self._head.value
        self._head = self._head.next
        if self._head is None:
            # Queue became empty
            self._tail = None
        self._size -= 1
        return item

    def peek(self) -> T:
        """Return the element at the front of the queue without removing it.
        
        Returns:
            The front element.
            
        Raises:
            EmptyQueueError: If the queue is empty.
            
        Complexity:
            O(1).
        """
        if self.is_empty():
            raise EmptyQueueError("Cannot peek into an empty queue.")
        assert self._head is not None
        return self._head.value

    def is_empty(self) -> bool:
        """Check whether the queue is empty.
        
        Returns:
            True if empty, False otherwise.
            
        Complexity:
            O(1).
        """
        return self._size == 0

    def size(self) -> int:
        """Return the number of elements in the queue.
        
        Returns:
            Total element count.
            
        Complexity:
            O(1).
        """
        return self._size

    def to_list(self) -> list[T]:
        """Return a snapshot of queued elements in FIFO order (front to rear).
        
        This enables safe inspection of the queue state for the UI without
        permitting internal node alteration or dequeuing.
        
        Returns:
            List of items ordered from front to rear.
            
        Complexity:
            O(n) where n is the number of queued elements.
        """
        result: list[T] = []
        curr = self._head
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        return result

    def clear(self) -> None:
        """Remove all elements from the queue."""
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        """Enable standard Python len() function."""
        return self.size()

    def __bool__(self) -> bool:
        """Truthy if queue has elements, Falsy if empty."""
        return not self.is_empty()

    def __repr__(self) -> str:
        """Human-readable representation of queue."""
        front_val = self._head.value if self._head else None
        return f"Queue(size={self._size}, front={front_val})"
