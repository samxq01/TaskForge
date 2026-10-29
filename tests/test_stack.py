"""Unit tests for the custom Stack data structure."""

import pytest

from taskforge.structures.stack import EmptyStackError, Stack


def test_empty_stack_properties() -> None:
    """An initialized stack must be empty and have size 0."""
    stack: Stack[int] = Stack()
    assert stack.is_empty() is True
    assert stack.size() == 0
    assert len(stack) == 0
    assert bool(stack) is False
    assert stack.to_list() == []


def test_push_and_peek() -> None:
    """Pushing elements updates size and peek reflects the top element."""
    stack: Stack[str] = Stack()
    stack.push("alpha")
    assert stack.is_empty() is False
    assert stack.size() == 1
    assert stack.peek() == "alpha"

    stack.push("beta")
    assert stack.size() == 2
    assert stack.peek() == "beta"


def test_lifo_order_pop() -> None:
    """Elements must be popped in reverse order of insertion (LIFO)."""
    stack: Stack[int] = Stack()
    for item in [10, 20, 30]:
        stack.push(item)

    assert stack.pop() == 30
    assert stack.pop() == 20
    assert stack.pop() == 10
    assert stack.is_empty() is True


def test_pop_empty_stack_raises_error() -> None:
    """Popping an empty stack must raise EmptyStackError."""
    stack: Stack[int] = Stack()
    with pytest.raises(EmptyStackError, match="Cannot pop from an empty stack"):
        stack.pop()


def test_peek_empty_stack_raises_error() -> None:
    """Peeking into an empty stack must raise EmptyStackError."""
    stack: Stack[int] = Stack()
    with pytest.raises(EmptyStackError, match="Cannot peek into an empty stack"):
        stack.peek()


def test_to_list_inspection_safety() -> None:
    """to_list() returns bottom-to-top items and does not mutate internal stack."""
    stack: Stack[str] = Stack()
    stack.push("first")
    stack.push("second")
    stack.push("third")

    items = stack.to_list()
    assert items == ["first", "second", "third"]

    # Mutating returned list must not affect internal stack
    items.append("fourth")
    assert stack.size() == 3
    assert stack.peek() == "third"


def test_clear_stack() -> None:
    """Clearing a stack resets it to an empty state."""
    stack: Stack[int] = Stack()
    stack.push(1)
    stack.push(2)
    stack.clear()
    assert stack.is_empty() is True
    assert stack.size() == 0
