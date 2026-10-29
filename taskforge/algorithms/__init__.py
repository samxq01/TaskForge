"""Custom searching and sorting algorithms implemented for TaskForge."""

from taskforge.algorithms.searching import SearchResult, binary_search, linear_search
from taskforge.algorithms.sorting import (
    SortResult,
    insertion_sort,
    merge_sort,
    task_deadline_key,
    task_id_key,
    task_priority_deadline_key,
    task_priority_key,
)

__all__ = [
    "SearchResult",
    "linear_search",
    "binary_search",
    "SortResult",
    "insertion_sort",
    "merge_sort",
    "task_deadline_key",
    "task_priority_key",
    "task_priority_deadline_key",
    "task_id_key",
]
