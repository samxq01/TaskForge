"""Unit tests for custom DependencyGraph data structure and graph algorithms (CO5)."""

import pytest

from taskforge.graph.dependency_graph import (
    CycleDetectedError,
    DependencyGraph,
    InvalidDependencyError,
)


def test_empty_graph() -> None:
    """Test initial empty state of DependencyGraph."""
    graph = DependencyGraph()
    assert graph.node_count() == 0
    assert graph.edge_count() == 0
    assert graph.get_nodes() == []
    assert graph.get_edges() == []
    assert graph.is_acyclic() is True
    assert graph.topological_sort() == []
    assert graph.bfs(1) == []
    assert graph.dfs(1) == []


def test_add_and_remove_nodes() -> None:
    """Test adding and removing nodes explicitly."""
    graph = DependencyGraph()
    graph.add_node(10)
    graph.add_node(20)
    graph.add_node(10)  # Duplicate idempotent

    assert graph.node_count() == 2
    assert graph.has_node(10) is True
    assert graph.has_node(20) is True
    assert graph.has_node(30) is False
    assert graph.get_nodes() == [10, 20]

    assert graph.remove_node(10) is True
    assert graph.has_node(10) is False
    assert graph.node_count() == 1
    assert graph.remove_node(99) is False


def test_add_and_remove_edges() -> None:
    """Test adding and removing directed edges."""
    graph = DependencyGraph()
    # 1 -> 2 (Task 2 depends on Task 1)
    graph.add_edge(1, 2)
    assert graph.has_node(1) is True
    assert graph.has_node(2) is True
    assert graph.has_edge(1, 2) is True
    assert graph.has_edge(2, 1) is False
    assert graph.edge_count() == 1
    assert graph.get_edges() == [(1, 2)]

    # Adding edge again is idempotent
    graph.add_edge(1, 2)
    assert graph.edge_count() == 1

    assert graph.remove_edge(1, 2) is True
    assert graph.has_edge(1, 2) is False
    assert graph.edge_count() == 0
    assert graph.remove_edge(1, 2) is False


def test_self_dependency_rejected() -> None:
    """Test that self-dependencies raise InvalidDependencyError."""
    graph = DependencyGraph()
    with pytest.raises(InvalidDependencyError, match="Self-dependency detected"):
        graph.add_edge(5, 5)


def test_prerequisites_and_dependents() -> None:
    """Test retrieving in-neighbors (prerequisites) and out-neighbors (dependents)."""
    graph = DependencyGraph()
    # Task 3 depends on Task 1 and Task 2
    # Task 4 depends on Task 3
    graph.add_edge(1, 3)
    graph.add_edge(2, 3)
    graph.add_edge(3, 4)

    assert graph.get_prerequisites(3) == [1, 2]
    assert graph.get_prerequisites(1) == []
    assert graph.get_dependents(3) == [4]
    assert graph.get_dependents(1) == [3]
    assert graph.get_neighbors(1) == [3]

    assert graph.in_degree(3) == 2
    assert graph.out_degree(3) == 1
    assert graph.in_degree(1) == 0
    assert graph.out_degree(1) == 1


def test_has_path() -> None:
    """Test directed path reachability."""
    graph = DependencyGraph()
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(3, 4)
    graph.add_node(5)  # Isolated

    assert graph.has_path(1, 4) is True
    assert graph.has_path(1, 3) is True
    assert graph.has_path(4, 1) is False  # Directed
    assert graph.has_path(1, 5) is False
    assert graph.has_path(1, 1) is True


def test_would_create_cycle() -> None:
    """Test cycle pre-validation logic."""
    graph = DependencyGraph()
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)

    # 1 -> 2 -> 3
    # Adding 3 -> 1 would create 1 -> 2 -> 3 -> 1
    assert graph.would_create_cycle(3, 1) is True
    assert graph.would_create_cycle(1, 1) is True
    # Adding 1 -> 3 or 3 -> 4 is safe
    assert graph.would_create_cycle(1, 3) is False
    assert graph.would_create_cycle(3, 4) is False


def test_bfs_traversal() -> None:
    """Test Breadth-First Search traversal with custom Queue."""
    graph = DependencyGraph()
    # Tree-like structure
    # 1 -> 2, 1 -> 3
    # 2 -> 4, 3 -> 5
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(3, 5)

    order = graph.bfs(1)
    # Level 0: 1; Level 1: 2, 3; Level 2: 4, 5
    assert order == [1, 2, 3, 4, 5]


def test_dfs_traversal() -> None:
    """Test Depth-First Search traversal with custom Stack."""
    graph = DependencyGraph()
    # 1 -> 2, 1 -> 3
    # 2 -> 4
    # 3 -> 5
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(3, 5)

    order = graph.dfs(1)
    # DFS explores branch 1 -> 2 -> 4 first, then 3 -> 5
    assert order == [1, 2, 4, 3, 5]


def test_detect_cycle_acyclic() -> None:
    """Test cycle detection on a Directed Acyclic Graph (DAG)."""
    graph = DependencyGraph()
    # Diamond graph: 1 -> 2 -> 4, 1 -> 3 -> 4
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(3, 4)

    has_cycle, cycle_path = graph.detect_cycle()
    assert has_cycle is False
    assert cycle_path == []
    assert graph.is_acyclic() is True


def test_detect_cycle_cyclic() -> None:
    """Test cycle detection when a circular dependency is present."""
    graph = DependencyGraph()
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(3, 1)

    has_cycle, cycle_path = graph.detect_cycle()
    assert has_cycle is True
    # Cycle path should form a loop e.g. [1, 2, 3, 1] or similar rotation
    assert len(cycle_path) == 4
    assert cycle_path[0] == cycle_path[-1]
    assert graph.is_acyclic() is False


def test_topological_sort_linear() -> None:
    """Test Kahn's algorithm on a linear dependency chain."""
    graph = DependencyGraph()
    # 1 -> 2 -> 3 -> 4
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(3, 4)

    assert graph.topological_sort() == [1, 2, 3, 4]


def test_topological_sort_diamond() -> None:
    """Test Kahn's algorithm on a diamond DAG."""
    graph = DependencyGraph()
    # 1 -> 2 -> 4
    # 1 -> 3 -> 4
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(3, 4)

    order = graph.topological_sort()
    assert order.index(1) < order.index(2)
    assert order.index(1) < order.index(3)
    assert order.index(2) < order.index(4)
    assert order.index(3) < order.index(4)
    # Deterministic tie-breaking selects 2 before 3
    assert order == [1, 2, 3, 4]


def test_topological_sort_disconnected_dag() -> None:
    """Test Kahn's algorithm on disconnected components."""
    graph = DependencyGraph()
    # Component 1: 10 -> 20
    # Component 2: 5 -> 15
    graph.add_edge(10, 20)
    graph.add_edge(5, 15)

    order = graph.topological_sort()
    # Nodes with in-degree 0: [5, 10]
    assert order == [5, 10, 15, 20]


def test_topological_sort_raises_cycle_error() -> None:
    """Test that topological sort raises CycleDetectedError on cyclic graphs."""
    graph = DependencyGraph()
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(3, 1)

    with pytest.raises(CycleDetectedError, match="circular dependency"):
        graph.topological_sort()
