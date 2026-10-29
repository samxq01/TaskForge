"""Unit tests for the custom BinarySearchTree data structure."""

import pytest

from taskforge.structures.bst import BinarySearchTree, TreeNode


def test_empty_bst() -> None:
    """An empty BST has size 0, height -1, and returns empty traversals."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    assert bst.is_empty() is True
    assert bst.size() == 0
    assert len(bst) == 0
    assert bst.height() == -1
    assert bst.root is None
    assert bst.search(10) is None
    assert bst.contains(10) is False
    assert bst.inorder_traversal() == []
    assert bst.preorder_traversal() == []
    assert bst.postorder_traversal() == []


def test_insert_single_node() -> None:
    """Inserting a single node establishes root and size 1."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    bst.insert(50, "root_val")
    assert bst.is_empty() is False
    assert bst.size() == 1
    assert bst.height() == 0
    assert bst.root is not None
    assert bst.root.key == 50
    assert bst.root.value == "root_val"
    assert bst.search(50) == "root_val"
    assert bst.contains(50) is True


def test_insert_multiple_and_search() -> None:
    """Inserting multiple keys builds a proper BST structure accessible via search."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    # Tree shape:
    #        50
    #      /    \
    #     30     70
    #    /  \   /  \
    #   20  40 60  80
    keys = [50, 30, 70, 20, 40, 60, 80]
    for k in keys:
        bst.insert(k, f"val_{k}")

    assert bst.size() == 7
    assert bst.height() == 2

    # Verify search for all inserted keys
    for k in keys:
        assert bst.search(k) == f"val_{k}"

    # Search for missing keys
    assert bst.search(999) is None
    assert bst.search(25) is None


def test_inorder_traversal_sorted_order() -> None:
    """Inorder traversal (Left, Root, Right) must return values in sorted key order."""
    bst: BinarySearchTree[int, int] = BinarySearchTree()
    for k in [40, 20, 60, 10, 30, 50, 70]:
        bst.insert(k, k * 2)

    # Inorder keys must be 10, 20, 30, 40, 50, 60, 70
    expected_values = [20, 40, 60, 80, 100, 120, 140]
    assert bst.inorder_traversal() == expected_values

    entries = bst.inorder_entries()
    assert [e[0] for e in entries] == [10, 20, 30, 40, 50, 60, 70]


def test_preorder_traversal() -> None:
    """Preorder traversal visits Root, Left, Right."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    #       4
    #      / \
    #     2   5
    #    / \
    #   1   3
    for k in [4, 2, 1, 3, 5]:
        bst.insert(k, str(k))

    assert bst.preorder_traversal() == ["4", "2", "1", "3", "5"]


def test_postorder_traversal() -> None:
    """Postorder traversal visits Left, Right, Root."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    #       4
    #      / \
    #     2   5
    #    / \
    #   1   3
    for k in [4, 2, 1, 3, 5]:
        bst.insert(k, str(k))

    assert bst.postorder_traversal() == ["1", "3", "2", "5", "4"]


def test_duplicate_key_updates_value() -> None:
    """Inserting an exact existing key updates the payload in-place without incrementing size."""
    bst: BinarySearchTree[str, int] = BinarySearchTree()
    bst.insert("k1", 100)
    bst.insert("k2", 200)
    assert bst.size() == 2

    # Insert k1 with updated value
    bst.insert("k1", 999)
    assert bst.size() == 2
    assert bst.search("k1") == 999
    assert bst.search("k2") == 200


def test_deletion_leaf_node() -> None:
    """Case 1: Deleting a leaf node cleanly removes it."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    for k in [50, 30, 70, 20]:
        bst.insert(k, str(k))

    assert bst.delete(20) is True
    assert bst.size() == 3
    assert bst.search(20) is None
    assert bst.inorder_traversal() == ["30", "50", "70"]


def test_deletion_single_child_node() -> None:
    """Case 2: Deleting a node with one child splices child to parent."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    for k in [50, 30, 20]:  # 30 has only left child (20)
        bst.insert(k, str(k))

    assert bst.delete(30) is True
    assert bst.size() == 2
    assert bst.search(30) is None
    assert bst.inorder_traversal() == ["20", "50"]


def test_deletion_two_children_node() -> None:
    """Case 3: Deleting a node with two children replaces it with in-order successor."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    #       50
    #      /  \
    #     30   70
    #    /  \
    #   20  40
    for k in [50, 30, 70, 20, 40]:
        bst.insert(k, str(k))

    # Delete 30 (has two children: 20 and 40). Successor is 40.
    assert bst.delete(30) is True
    assert bst.size() == 4
    assert bst.search(30) is None
    assert bst.inorder_traversal() == ["20", "40", "50", "70"]


def test_deletion_root() -> None:
    """Deleting the root node with two children preserves BST properties."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    for k in [50, 30, 70, 60, 80]:
        bst.insert(k, str(k))

    assert bst.delete(50) is True
    assert bst.size() == 4
    assert bst.search(50) is None
    assert bst.inorder_traversal() == ["30", "60", "70", "80"]


def test_deletion_missing_key() -> None:
    """Deleting a key not in the tree returns False and preserves size."""
    bst: BinarySearchTree[int, str] = BinarySearchTree()
    bst.insert(10, "val")
    assert bst.delete(999) is False
    assert bst.size() == 1


def test_skewed_tree_ascending() -> None:
    """Inserting keys in strictly ascending order forms a right-skewed tree."""
    bst: BinarySearchTree[int, int] = BinarySearchTree()
    for k in [1, 2, 3, 4, 5]:
        bst.insert(k, k)

    assert bst.size() == 5
    assert bst.height() == 4  # Degenerate chain
    assert bst.inorder_traversal() == [1, 2, 3, 4, 5]
    assert bst.search(3) == 3


def test_skewed_tree_descending() -> None:
    """Inserting keys in strictly descending order forms a left-skewed tree."""
    bst: BinarySearchTree[int, int] = BinarySearchTree()
    for k in [5, 4, 3, 2, 1]:
        bst.insert(k, k)

    assert bst.size() == 5
    assert bst.height() == 4  # Degenerate chain
    assert bst.inorder_traversal() == [1, 2, 3, 4, 5]
    assert bst.search(2) == 2


def test_clear_tree() -> None:
    """Clearing a tree resets root to None and size to 0."""
    bst: BinarySearchTree[int, int] = BinarySearchTree()
    bst.insert(10, 10)
    bst.insert(20, 20)
    bst.clear()
    assert bst.is_empty() is True
    assert bst.size() == 0
    assert bst.root is None
