"""Task Indexing Service utilizing a custom Binary Search Tree (BST) for deadline ordering (CO4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from taskforge.models import Task
from taskforge.storage import TaskStorage
from taskforge.structures.bst import BinarySearchTree, TreeNode


def make_deadline_key(task: Task) -> tuple[int, datetime, int]:
    """Generate a composite key for deterministic deadline ordering in the BST.
    
    Structure:
        (has_no_deadline_flag, normalized_deadline, task_id)
        
    Properties:
        - Tasks with deadlines (flag=0) strictly precede tasks without deadlines (flag=1).
        - Earliest deadlines precede later deadlines.
        - Identical deadlines are deterministically tie-broken by unique task ID.
        - Tasks without deadlines are ordered deterministically by task ID.
    """
    has_no_deadline = 1 if task.due_date is None else 0
    normalized_deadline = task.due_date if task.due_date is not None else datetime.max
    task_id = task.id if task.id is not None else 0
    return (has_no_deadline, normalized_deadline, task_id)


def make_search_key(due_date: Optional[datetime], task_id: int) -> tuple[int, datetime, int]:
    """Generate the exact composite key for a given deadline and task ID."""
    has_no_deadline = 1 if due_date is None else 0
    normalized_deadline = due_date if due_date is not None else datetime.max
    return (has_no_deadline, normalized_deadline, task_id)


class TaskIndexService:
    """Manages an in-memory Binary Search Tree index over persistent SQLite task records.
    
    The BST indexes tasks according to their deadline composite key, allowing:
    - O(n) inorder retrieval of tasks in sorted deadline order.
    - O(log n) average-case search for tasks by composite key.
    - Full inspection of BST preorder, inorder, and postorder traversals.
    """

    def __init__(self, storage: TaskStorage) -> None:
        """Initialize the task index service with persistent storage.
        
        Args:
            storage: TaskStorage instance representing the SQLite persistence layer.
        """
        self.storage = storage
        self._bst: BinarySearchTree[tuple[int, datetime, int], Task] = BinarySearchTree()
        self.rebuild()

    def rebuild(self) -> None:
        """Reconstruct the entire BST from current SQLite task records.
        
        Ensures the tree index is synchronized with persistent database state,
        retaining SQLite as the durable source of truth.
        """
        self._bst.clear()
        # Fetch current tasks from SQLite
        all_tasks = self.storage.list_tasks()
        for task in all_tasks:
            key = make_deadline_key(task)
            self._bst.insert(key, task)

    def refresh(self) -> None:
        """Alias for rebuild to refresh the index after mutations."""
        self.rebuild()

    def get_deadline_ordered_tasks(self) -> list[Task]:
        """Retrieve all stored tasks in deadline order via BST inorder traversal.
        
        Complexity:
            O(n) where n is the number of indexed tasks.
            
        Returns:
            List of tasks ordered earliest deadline first, unscheduled last.
        """
        return self._bst.inorder_traversal()

    def search_by_deadline_and_id(self, due_date: Optional[datetime], task_id: int) -> Optional[Task]:
        """Search for a task using its deadline and primary key ID via BST search.
        
        Args:
            due_date: Target deadline (or None if unscheduled).
            task_id: Task identifier.
            
        Returns:
            The Task object if found in the BST, None otherwise.
        """
        key = make_search_key(due_date, task_id)
        return self._bst.search(key)

    def search_by_task(self, task: Task) -> Optional[Task]:
        """Search for a specific task instance in the BST."""
        key = make_deadline_key(task)
        return self._bst.search(key)

    def get_tree_size(self) -> int:
        """Return the number of nodes in the BST."""
        return self._bst.size()

    def get_tree_height(self) -> int:
        """Return the maximum depth/height of the BST."""
        return self._bst.height()

    def is_empty(self) -> bool:
        """Return True if the index contains zero tasks."""
        return self._bst.is_empty()

    def get_inorder_entries(self) -> list[tuple[tuple[int, datetime, int], Task]]:
        """Return (key, task) entries visited in Inorder traversal."""
        return self._bst.inorder_entries()

    def get_preorder_entries(self) -> list[tuple[tuple[int, datetime, int], Task]]:
        """Return (key, task) entries visited in Preorder traversal."""
        return self._bst.preorder_entries()

    def get_postorder_entries(self) -> list[tuple[tuple[int, datetime, int], Task]]:
        """Return (key, task) entries visited in Postorder traversal."""
        return self._bst.postorder_entries()

    def get_raw_bst(self) -> BinarySearchTree[tuple[int, datetime, int], Task]:
        """Expose raw BST instance for tree visualization and diagnostics."""
        return self._bst
