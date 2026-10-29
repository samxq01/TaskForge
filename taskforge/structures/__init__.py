"""Custom data structures implemented for TaskForge."""

from taskforge.structures.bst import BinarySearchTree, TreeNode
from taskforge.structures.queue import EmptyQueueError, Queue
from taskforge.structures.stack import EmptyStackError, Stack

__all__ = [
    "Stack",
    "EmptyStackError",
    "Queue",
    "EmptyQueueError",
    "BinarySearchTree",
    "TreeNode",
]
