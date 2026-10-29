"""Manual searching algorithm implementations for TaskForge (CO3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SearchResult(Generic[T]):
    """Encapsulates the outcome and performance metrics of a search operation.
    
    Attributes:
        found: True if a matching element was found, False otherwise.
        index: Zero-based index of the matching element in the sequence (-1 if not found).
        item: The matching item itself, or None if not found.
        comparisons: Number of key comparisons executed during the search.
    """
    found: bool
    index: int
    item: Optional[T]
    comparisons: int


def linear_search(
    sequence: Sequence[T],
    target: Any,
    key: Optional[Callable[[T], Any]] = None,
) -> SearchResult[T]:
    """Perform a manual Linear Search across a sequence.
    
    Examines each element sequentially from index 0 until a match is discovered
    or the end of the collection is reached. For sequences containing duplicates,
    it deterministically returns the first matching item.
    
    Time Complexity:
        - Best Case: O(1) [target is located at the first index]
        - Average Case: O(n)
        - Worst Case: O(n) [target is at the last index or absent]
        
    Auxiliary Space:
        - O(1) [no auxiliary memory allocated beyond the result object]
        
    Args:
        sequence: An iterable collection or list of items (remains unmutated).
        target: The target value to search for.
        key: Optional function to extract comparison key from an element (e.g. lambda t: t.id).
        
    Returns:
        SearchResult[T] containing found status, index, item, and comparison count.
    """
    comparisons = 0
    for idx, element in enumerate(sequence):
        comparisons += 1
        elem_key = key(element) if key is not None else element
        if elem_key == target:
            return SearchResult(
                found=True,
                index=idx,
                item=element,
                comparisons=comparisons,
            )

    return SearchResult(
        found=False,
        index=-1,
        item=None,
        comparisons=comparisons,
    )


def binary_search(
    sorted_sequence: Sequence[T],
    target: Any,
    key: Optional[Callable[[T], Any]] = None,
) -> SearchResult[T]:
    """Perform a manual iterative Binary Search across a pre-sorted sequence.
    
    IMPORTANT PRECONDITION:
        The input sequence MUST already be sorted in ascending order by the exact
        same key used for searching. Passing an unsorted sequence violates the
        fundamental invariant of Binary Search and produces invalid results.
        This function does NOT sort the data internally.
        
    For sequences with duplicate keys, this implementation continues searching
    the left partition to deterministically return the first occurrence.
    
    Time Complexity:
        - Best Case: O(1) [target matches the middle element immediately]
        - Average Case: O(log n)
        - Worst Case: O(log n)
        
    Auxiliary Space:
        - O(1) [iterative implementation maintains only pointer variables]
        
    Args:
        sorted_sequence: Sequence sorted in ascending order by the comparison key.
        target: The target value to search for.
        key: Optional extractor function to retrieve the key from an item.
        
    Returns:
        SearchResult[T] containing found status, index, item, and comparison count.
    """
    low = 0
    high = len(sorted_sequence) - 1
    comparisons = 0
    first_match_idx = -1

    while low <= high:
        mid = low + (high - low) // 2
        comparisons += 1
        mid_val = key(sorted_sequence[mid]) if key is not None else sorted_sequence[mid]

        if mid_val == target:
            first_match_idx = mid
            # Continue scanning the left sub-array to find the first occurrence
            high = mid - 1
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    if first_match_idx != -1:
        return SearchResult(
            found=True,
            index=first_match_idx,
            item=sorted_sequence[first_match_idx],
            comparisons=comparisons,
        )

    return SearchResult(
        found=False,
        index=-1,
        item=None,
        comparisons=comparisons,
    )
