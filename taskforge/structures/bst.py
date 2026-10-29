"""Custom generic Binary Search Tree (BST) implementation for TaskForge (CO4)."""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TreeNode(Generic[K, V]):
    """Represents a single node within a Binary Search Tree.
    
    Attributes:
        key: A comparable key used to position the node in the BST.
        value: The payload/value associated with the key (e.g. Task object).
        left: Pointer to the left child node (containing keys strictly less than this node's key).
        right: Pointer to the right child node (containing keys strictly greater than this node's key).
    """

    __slots__ = ("key", "value", "left", "right")

    def __init__(
        self,
        key: K,
        value: V,
        left: Optional[TreeNode[K, V]] = None,
        right: Optional[TreeNode[K, V]] = None,
    ) -> None:
        self.key: K = key
        self.value: V = value
        self.left: Optional[TreeNode[K, V]] = left
        self.right: Optional[TreeNode[K, V]] = right

    def is_leaf(self) -> bool:
        """Return True if this node has no children."""
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"TreeNode(key={self.key!r})"


class BinarySearchTree(Generic[K, V]):
    """A generic, un-balanced Binary Search Tree (BST).
    
    Guarantees the BST Invariant:
        For every node N, all keys in N's left subtree are strictly less than N.key,
        and all keys in N's right subtree are strictly greater than N.key.
        
    Duplicate Policy:
        If an exact key match is inserted, this implementation updates the associated
        value in place without increasing the tree size, ensuring 1:1 key-to-node mapping.
        For TaskForge, composite keys include task IDs (deadline, id) so duplicate
        deadlines occupy distinct nodes.
        
    Complexity:
        - Search: O(log n) average case, O(n) worst case (skewed tree).
        - Insert: O(log n) average case, O(n) worst case.
        - Delete: O(log n) average case, O(n) worst case.
        - Traversals (Inorder, Preorder, Postorder): O(n) time, O(h) recursion space.
    """

    def __init__(self) -> None:
        """Initialize an empty Binary Search Tree."""
        self._root: Optional[TreeNode[K, V]] = None
        self._size: int = 0

    @property
    def root(self) -> Optional[TreeNode[K, V]]:
        """Direct reference to the root node (useful for visualization)."""
        return self._root

    def is_empty(self) -> bool:
        """Return True if the tree contains zero nodes."""
        return self._root is None

    def size(self) -> int:
        """Return the total number of unique keys/nodes currently in the tree."""
        return self._size

    def __len__(self) -> int:
        return self.size()

    def insert(self, key: K, value: V) -> None:
        """Insert a key-value pair into the BST.
        
        If the key already exists, updates its value.
        
        Args:
            key: Comparable key.
            value: Data payload.
        """
        if self._root is None:
            self._root = TreeNode(key, value)
            self._size = 1
            return

        curr = self._root
        while True:
            if key == curr.key:
                # Update existing key payload
                curr.value = value
                return
            elif key < curr.key:
                if curr.left is None:
                    curr.left = TreeNode(key, value)
                    self._size += 1
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = TreeNode(key, value)
                    self._size += 1
                    return
                curr = curr.right

    def search(self, key: K) -> Optional[V]:
        """Search for a key in the BST.
        
        Args:
            key: The key to locate.
            
        Returns:
            The associated value if found, or None if the key does not exist.
        """
        curr = self._root
        while curr is not None:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def contains(self, key: K) -> bool:
        """Check whether a key exists in the tree."""
        return self.search(key) is not None

    def delete(self, key: K) -> bool:
        """Remove a node by key from the BST using standard 3-case deletion.
        
        Cases:
            1. Node is a leaf: remove it directly.
            2. Node has one child: splice child to parent.
            3. Node has two children: replace with in-order successor (min of right subtree),
               then delete the in-order successor.
               
        Args:
            key: Key of the node to remove.
            
        Returns:
            True if a node was deleted, False if key was not found.
        """
        deleted = False

        def _delete_node(node: Optional[TreeNode[K, V]], target_key: K) -> Optional[TreeNode[K, V]]:
            nonlocal deleted
            if node is None:
                return None

            if target_key < node.key:
                node.left = _delete_node(node.left, target_key)
            elif target_key > node.key:
                node.right = _delete_node(node.right, target_key)
            else:
                # Target node found
                deleted = True
                # Case 1 & 2: 0 or 1 child
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left

                # Case 3: 2 children. Find in-order successor (minimum in right subtree)
                successor = node.right
                while successor.left is not None:
                    successor = successor.left

                # Copy successor data to current node
                node.key = successor.key
                node.value = successor.value

                # Delete successor node from right subtree
                node.right = _delete_node(node.right, successor.key)

            return node

        self._root = _delete_node(self._root, key)
        if deleted:
            self._size -= 1
        return deleted

    def inorder_traversal(self) -> list[V]:
        """Traverse the BST Inorder (Left -> Root -> Right).
        
        Returns:
            List of values sorted in strictly ascending order of keys.
        """
        values: list[V] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            _traverse(node.left)
            values.append(node.value)
            _traverse(node.right)

        _traverse(self._root)
        return values

    def preorder_traversal(self) -> list[V]:
        """Traverse the BST Preorder (Root -> Left -> Right).
        
        Returns:
            List of values in prefix order (useful for tree reconstruction).
        """
        values: list[V] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            values.append(node.value)
            _traverse(node.left)
            _traverse(node.right)

        _traverse(self._root)
        return values

    def postorder_traversal(self) -> list[V]:
        """Traverse the BST Postorder (Left -> Right -> Root).
        
        Returns:
            List of values in postfix order (useful for bottom-up cleanup).
        """
        values: list[V] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            _traverse(node.left)
            _traverse(node.right)
            values.append(node.value)

        _traverse(self._root)
        return values

    def inorder_entries(self) -> list[tuple[K, V]]:
        """Return list of (key, value) tuples visited in Inorder."""
        entries: list[tuple[K, V]] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            _traverse(node.left)
            entries.append((node.key, node.value))
            _traverse(node.right)

        _traverse(self._root)
        return entries

    def preorder_entries(self) -> list[tuple[K, V]]:
        """Return list of (key, value) tuples visited in Preorder."""
        entries: list[tuple[K, V]] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            entries.append((node.key, node.value))
            _traverse(node.left)
            _traverse(node.right)

        _traverse(self._root)
        return entries

    def postorder_entries(self) -> list[tuple[K, V]]:
        """Return list of (key, value) tuples visited in Postorder."""
        entries: list[tuple[K, V]] = []

        def _traverse(node: Optional[TreeNode[K, V]]) -> None:
            if node is None:
                return
            _traverse(node.left)
            _traverse(node.right)
            entries.append((node.key, node.value))

        _traverse(self._root)
        return entries

    def height(self) -> int:
        """Calculate the height/depth of the tree (-1 if empty, 0 for root only)."""
        def _calc_height(node: Optional[TreeNode[K, V]]) -> int:
            if node is None:
                return -1
            return 1 + max(_calc_height(node.left), _calc_height(node.right))

        return _calc_height(self._root)

    def clear(self) -> None:
        """Reset the BST to an empty state."""
        self._root = None
        self._size = 0
