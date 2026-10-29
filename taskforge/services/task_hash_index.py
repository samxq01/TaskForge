"""Task-ID hash indexing service using custom HashTable (CO2)."""

from __future__ import annotations

from typing import Any, Optional

from taskforge.models import Task
from taskforge.storage import TaskStorage
from taskforge.structures.hash_table import HashTable


class TaskHashIndexService:
    """Provides rapid O(1) average-case task lookup by primary key ID using a custom HashTable.
    
    Academic Objectives (CO2):
        - Indexes persistent SQLite task records into an in-memory custom Hash Table.
        - Provides constant-time average task retrieval without repeated database round-trips.
        - Synchronizes with SQLite after task mutations (create, edit, delete, undo, redo).
        - Exposes bucket and collision metrics for educational evaluation.
    """

    def __init__(self, storage: TaskStorage, initial_capacity: int = 32) -> None:
        """Initialize the task hash index with persistent storage.
        
        Args:
            storage: Persistent TaskStorage interface.
            initial_capacity: Starting bucket array size. Default: 32.
        """
        self.storage = storage
        self._initial_capacity = initial_capacity
        self._table: HashTable[int, Task] = HashTable(initial_capacity=initial_capacity)
        self.rebuild_index()

    def rebuild_index(self) -> int:
        """Synchronize the in-memory hash table with all current SQLite task records.
        
        Returns:
            The total number of tasks indexed.
        """
        self._table.clear()
        tasks = self.storage.list_tasks()

        for task in tasks:
            if task.id is not None:
                self._table.insert(task.id, task)

        return self._table.size()

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID in O(1) average time.
        
        Args:
            task_id: Unique task identifier.
            
        Returns:
            The Task instance if indexed, or None if absent.
        """
        return self._table.get(task_id)

    def get_task_with_comparisons(self, task_id: int) -> tuple[Optional[Task], int]:
        """Retrieve task by ID and report key comparisons performed in bucket chain.
        
        Args:
            task_id: Unique task identifier.
            
        Returns:
            Tuple of (Task_or_None, comparison_count).
        """
        return self._table.get_with_comparisons(task_id)

    def contains_task(self, task_id: int) -> bool:
        """Check whether a task ID is indexed in the hash table.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            True if task is present, False otherwise.
        """
        return self._table.contains(task_id)

    def size(self) -> int:
        """Return the count of indexed tasks."""
        return self._table.size()

    def get_statistics(self) -> dict[str, Any]:
        """Retrieve collision, bucket, and load factor diagnostics."""
        return self._table.collision_stats()

    def get_raw_hash_table(self) -> HashTable[int, Task]:
        """Expose the underlying HashTable instance for UI bucket visualization."""
        return self._table
