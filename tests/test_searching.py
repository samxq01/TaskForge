"""Unit tests for manual searching algorithms (Linear Search and Binary Search)."""

from datetime import datetime
import pytest

from taskforge.algorithms.searching import SearchResult, binary_search, linear_search
from taskforge.models import Task


def test_linear_search_empty() -> None:
    """Searching an empty collection returns found=False and comparisons=0."""
    res = linear_search([], 42)
    assert res.found is False
    assert res.index == -1
    assert res.item is None
    assert res.comparisons == 0


def test_linear_search_single_item() -> None:
    """Linear search handles a single item collection properly."""
    res_found = linear_search([10], 10)
    assert res_found.found is True
    assert res_found.index == 0
    assert res_found.item == 10
    assert res_found.comparisons == 1

    res_missing = linear_search([10], 99)
    assert res_missing.found is False
    assert res_missing.index == -1
    assert res_missing.comparisons == 1


def test_linear_search_positions() -> None:
    """Linear search finds items at first, middle, last positions, or missing."""
    items = ["apple", "banana", "cherry", "date", "elderberry"]

    # First position (best case: 1 comparison)
    r1 = linear_search(items, "apple")
    assert r1.found is True
    assert r1.index == 0
    assert r1.comparisons == 1

    # Middle position
    r2 = linear_search(items, "cherry")
    assert r2.found is True
    assert r2.index == 2
    assert r2.comparisons == 3

    # Last position (worst case found: n comparisons)
    r3 = linear_search(items, "elderberry")
    assert r3.found is True
    assert r3.index == 4
    assert r3.comparisons == 5

    # Not found (worst case not found: n comparisons)
    r4 = linear_search(items, "fig")
    assert r4.found is False
    assert r4.index == -1
    assert r4.comparisons == 5


def test_linear_search_duplicates_deterministic() -> None:
    """Linear search deterministically returns the first match for duplicate values."""
    data = [5, 20, 10, 20, 30, 20]
    res = linear_search(data, 20)
    assert res.found is True
    assert res.index == 1
    assert res.comparisons == 2


def test_linear_search_preserves_input() -> None:
    """Linear search must never mutate the input sequence."""
    original = [10, 30, 20, 50, 40]
    clone = list(original)
    linear_search(original, 20)
    assert original == clone


def test_linear_search_with_task_objects() -> None:
    """Linear search on Task objects using key function (e.g. task ID)."""
    tasks = [
        Task(id=101, title="Task A"),
        Task(id=202, title="Task B"),
        Task(id=303, title="Task C"),
    ]
    res = linear_search(tasks, target=202, key=lambda t: t.id)
    assert res.found is True
    assert res.index == 1
    assert res.item is not None
    assert res.item.title == "Task B"


# ---------------- BINARY SEARCH TESTS ----------------

def test_binary_search_empty() -> None:
    """Binary search on an empty sequence returns not found."""
    res = binary_search([], 50)
    assert res.found is False
    assert res.index == -1
    assert res.comparisons == 0


def test_binary_search_single_item() -> None:
    """Binary search handles single element sorted list."""
    res_found = binary_search([42], 42)
    assert res_found.found is True
    assert res_found.index == 0
    assert res_found.item == 42
    assert res_found.comparisons >= 1

    res_missing = binary_search([42], 100)
    assert res_missing.found is False
    assert res_missing.index == -1


def test_binary_search_positions() -> None:
    """Binary search locates elements in pre-sorted sequence."""
    sorted_data = [10, 20, 30, 40, 50, 60, 70]

    # First item
    r_first = binary_search(sorted_data, 10)
    assert r_first.found is True
    assert r_first.index == 0

    # Middle item (40)
    r_mid = binary_search(sorted_data, 40)
    assert r_mid.found is True
    assert r_mid.index == 3

    # Last item
    r_last = binary_search(sorted_data, 70)
    assert r_last.found is True
    assert r_last.index == 6

    # Missing item
    r_absent = binary_search(sorted_data, 25)
    assert r_absent.found is False
    assert r_absent.index == -1


def test_binary_search_logarithmic_comparisons() -> None:
    """Binary search comparisons must be bounded by ceil(log2(n)) + 1."""
    sorted_1000 = list(range(1000))
    res = binary_search(sorted_1000, 789)
    assert res.found is True
    assert res.index == 789
    # log2(1000) ~ 10. Comparisons should not exceed 15
    assert res.comparisons <= 15


def test_binary_search_duplicates_deterministic() -> None:
    """Binary search deterministically returns the first match for duplicate keys."""
    sorted_dups = [5, 10, 20, 20, 20, 30, 40]
    res = binary_search(sorted_dups, 20)
    assert res.found is True
    assert res.index == 2  # First occurrence of 20
    assert res.item == 20


def test_binary_search_preserves_input() -> None:
    """Binary search does not modify the input collection."""
    sorted_items = [1, 3, 5, 7, 9]
    clone = list(sorted_items)
    binary_search(sorted_items, 5)
    assert sorted_items == clone


def test_binary_search_with_tasks() -> None:
    """Binary search on tasks sorted by ID."""
    tasks = [
        Task(id=10, title="T10"),
        Task(id=20, title="T20"),
        Task(id=30, title="T30"),
        Task(id=40, title="T40"),
    ]
    res = binary_search(tasks, target=30, key=lambda t: t.id)
    assert res.found is True
    assert res.index == 2
    assert res.item is not None
    assert res.item.title == "T30"
