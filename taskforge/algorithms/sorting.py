"""Manual sorting algorithm implementations and task key functions for TaskForge (CO3)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

from taskforge.models import Task

T = TypeVar("T")


@dataclass(frozen=True)
class SortResult(Generic[T]):
    """Encapsulates the result and performance statistics of a sorting operation.
    
    Attributes:
        items: Newly allocated sorted list (caller input was preserved).
        comparisons: Count of key comparison operations performed.
        shifts: Count of element movements, assignments, or merge placements.
    """
    items: list[T]
    comparisons: int
    shifts: int


# ---------------- TASK COMPARISON KEYS ----------------

def task_deadline_key(task: Task) -> tuple[int, datetime, int]:
    """Sort key for deadline ascending: earliest deadline first, tasks without deadline last.
    
    Tie-breaking: task ID ascending.
    """
    if task.due_date is not None:
        return (0, task.due_date, task.id or 0)
    return (1, datetime.max, task.id or 0)


def task_priority_key(task: Task) -> tuple[int, int]:
    """Sort key for priority descending: Urgent (4) down to Low (1).
    
    Tie-breaking: task ID ascending.
    """
    return (-task.priority, task.id or 0)


def task_priority_deadline_key(task: Task) -> tuple[int, int, datetime, int]:
    """Sort key combining priority descending, earliest deadline, and task ID.
    
    1. Higher priority first (-priority)
    2. Earliest deadline first (tasks with deadline before tasks without)
    3. Task ID ascending as final tie-breaker.
    """
    has_deadline_flag = 0 if task.due_date is not None else 1
    deadline_val = task.due_date if task.due_date is not None else datetime.max
    return (-task.priority, has_deadline_flag, deadline_val, task.id or 0)


def task_id_key(task: Task) -> int:
    """Sort key by task primary key ID ascending (useful for Binary Search preparation)."""
    return task.id if task.id is not None else 0


# ---------------- INSERTION SORT ----------------

def insertion_sort(
    items: Sequence[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
) -> SortResult[T]:
    """Perform a manual Insertion Sort on a sequence.
    
    Builds the sorted array one item at a time by repeatedly taking the next
    element and inserting it into its correct position among previously sorted items.
    
    Stability:
        Guaranteed STABLE (does not swap or shift elements with identical keys).
        
    Input Safety:
        Allocates a new working list copy; does NOT modify the caller-owned input.
        
    Time Complexity:
        - Best Case: O(n) [already sorted input requires only n - 1 comparisons]
        - Average Case: O(n^2)
        - Worst Case: O(n^2) [reverse sorted input]
        
    Auxiliary Space:
        - O(1) sorting auxiliary space (operating in-place on the returned O(n) copy).
        
    Args:
        items: Input sequence of comparable items.
        key: Function to extract comparison key.
        reverse: If True, sort in descending order.
        
    Returns:
        SortResult[T] with sorted items and operation metrics.
    """
    # Defensive copy: do not mutate caller's collection
    arr: list[T] = list(items)
    n = len(arr)
    comparisons = 0
    shifts = 0

    for i in range(1, n):
        current_item = arr[i]
        current_key = key(current_item) if key is not None else current_item
        j = i - 1

        while j >= 0:
            comparisons += 1
            prev_key = key(arr[j]) if key is not None else arr[j]

            # In ascending order, shift right if prev_key > current_key.
            # In descending order, shift right if prev_key < current_key.
            should_shift = (prev_key < current_key) if reverse else (prev_key > current_key)

            if should_shift:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break

        arr[j + 1] = current_item
        shifts += 1

    return SortResult(items=arr, comparisons=comparisons, shifts=shifts)


# ---------------- MERGE SORT ----------------

def merge_sort(
    items: Sequence[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
) -> SortResult[T]:
    """Perform a manual Merge Sort using a stable divide-and-conquer strategy.
    
    Recursively splits the sequence into halves, sorts each half, and merges
    the sorted sub-lists into a new ordered list.
    
    Stability:
        Guaranteed STABLE (during merge, left sub-array element is chosen first
        whenever keys are equal).
        
    Input Safety:
        Pure functional approach: returns a newly allocated sorted list;
        never mutates the caller-owned input sequence.
        
    Time Complexity:
        - Best Case: O(n log n)
        - Average Case: O(n log n)
        - Worst Case: O(n log n)
        
    Auxiliary Space:
        - O(n) auxiliary space for sub-array allocations during the merge phase.
        
    Args:
        items: Input sequence of items.
        key: Function to extract comparison key.
        reverse: If True, sort in descending order.
        
    Returns:
        SortResult[T] with sorted items, comparison count, and merge shift operations.
    """
    arr: list[T] = list(items)
    comparisons = 0
    shifts = 0

    def _sort(sub: list[T]) -> list[T]:
        nonlocal comparisons, shifts
        if len(sub) <= 1:
            return sub

        mid = len(sub) // 2
        left = _sort(sub[:mid])
        right = _sort(sub[mid:])

        # Merge step
        merged: list[T] = []
        i = 0
        j = 0
        len_l = len(left)
        len_r = len(right)

        while i < len_l and j < len_r:
            comparisons += 1
            key_l = key(left[i]) if key is not None else left[i]
            key_r = key(right[j]) if key is not None else right[j]

            # In ascending order, pick left if key_l <= key_r (maintains stability).
            # In descending order, pick left if key_l >= key_r (maintains stability).
            pick_left = (key_l >= key_r) if reverse else (key_l <= key_r)

            if pick_left:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
            shifts += 1

        # Append remaining elements
        while i < len_l:
            merged.append(left[i])
            i += 1
            shifts += 1

        while j < len_r:
            merged.append(right[j])
            j += 1
            shifts += 1

        return merged

    sorted_arr = _sort(arr)
    return SortResult(items=sorted_arr, comparisons=comparisons, shifts=shifts)
