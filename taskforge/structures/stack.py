"""Custom generic Stack data structure implementing LIFO (Last-In, First-Out)."""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class EmptyStackError(IndexError):
    """Raised when attempting to pop or peek an empty stack."""
    pass


class Stack(Generic[T]):
    """A generic LIFO (Last-In, First-Out) stack data structure.
    
    This implementation encapsulates an internal list container, exposing
    only standard stack operations to uphold data structure abstraction.
    
    Time Complexity:
        - push(item): O(1) amortized
        - pop(): O(1)
        - peek(): O(1)
        - is_empty(): O(1)
        - size(): O(1)
    
    Space Complexity:
        - O(n) where n is the number of elements in the stack.
    """

    def __init__(self) -> None:
        """Initialize an empty stack."""
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Add an element to the top of the stack.
        
        Args:
            item: Element to push onto the stack.
            
        Complexity:
            O(1) amortized.
        """
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the element at the top of the stack.
        
        Returns:
            The most recently pushed element.
            
        Raises:
            EmptyStackError: If the stack contains no elements.
            
        Complexity:
            O(1).
        """
        if self.is_empty():
            raise EmptyStackError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        """Return the element at the top of the stack without removing it.
        
        Returns:
            The element at the top of the stack.
            
        Raises:
            EmptyStackError: If the stack contains no elements.
            
        Complexity:
            O(1).
        """
        if self.is_empty():
            raise EmptyStackError("Cannot peek into an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check whether the stack contains any elements.
        
        Returns:
            True if empty, False otherwise.
            
        Complexity:
            O(1).
        """
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of elements in the stack.
        
        Returns:
            Total element count.
            
        Complexity:
            O(1).
        """
        return len(self._items)

    def to_list(self) -> list[T]:
        """Return a shallow copy of stack elements ordered from bottom to top.
        
        This enables safe inspection of the stack state without permitting
        accidental mutation of internal container structures.
        
        Returns:
            List of items from bottom (oldest) to top (newest).
        """
        return list(self._items)

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()

    def __len__(self) -> int:
        """Enable standard Python len() function."""
        return self.size()

    def __bool__(self) -> bool:
        """Truthy if stack has elements, Falsy if empty."""
        return not self.is_empty()

    def __repr__(self) -> str:
        """Human-readable representation of stack."""
        return f"Stack(size={self.size()}, top={self._items[-1] if self._items else None})"
