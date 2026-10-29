"""Directed Dependency Graph data structure implementing BFS, DFS, cycle detection, and Kahn's topological sort (CO5)."""

from __future__ import annotations

from typing import Optional

from taskforge.structures.queue import Queue
from taskforge.structures.stack import Stack


class CycleDetectedError(ValueError):
    """Raised when a circular dependency is detected or when topological sorting fails on a cyclic graph."""
    pass


class InvalidDependencyError(ValueError):
    """Raised when an invalid dependency (e.g. self-loop or non-existent task) is encountered."""
    pass


class DependencyGraph:
    """A custom directed graph representing task dependencies using adjacency lists.
    
    Convention:
        An edge `A -> B` means Task B depends on Task A.
        Therefore, Task A is a prerequisite for Task B (Task A must be completed before Task B).
        
    Algorithms Implemented:
        - Breadth-First Search (BFS) using custom FIFO Queue (CO1, CO5).
        - Depth-First Search (DFS) using custom LIFO Stack (CO1, CO5).
        - Directed Cycle Detection using 3-color DFS state tracking.
        - Topological Sorting using Kahn's Algorithm with in-degree Queue processing.
        - Reachability / Path detection for pre-validation of dependencies.
        
    Complexity:
        - Add Node: O(1)
        - Remove Node: O(V + E)
        - Add Edge: O(1)
        - Remove Edge: O(1)
        - BFS Traversal: O(V + E) time, O(V) space
        - DFS Traversal: O(V + E) time, O(V) space
        - Cycle Detection: O(V + E) time, O(V) space
        - Kahn's Topological Sort: O(V + E) time, O(V) space
    """

    def __init__(self) -> None:
        """Initialize an empty directed dependency graph."""
        # _adj[u] = set of v such that u -> v (v depends on u; u is prerequisite of v)
        self._adj: dict[int, set[int]] = {}
        # _rev_adj[v] = set of u such that u -> v (u is prerequisite of v)
        self._rev_adj: dict[int, set[int]] = {}
        # Set of all registered nodes in the graph
        self._nodes: set[int] = set()

    def add_node(self, node: int) -> None:
        """Add a task node to the graph if not already present.
        
        Args:
            node: Unique task identifier.
        """
        if node not in self._nodes:
            self._nodes.add(node)
            self._adj[node] = set()
            self._rev_adj[node] = set()

    def remove_node(self, node: int) -> bool:
        """Remove a task node and all associated incoming and outgoing edges.
        
        Args:
            node: Task identifier to remove.
            
        Returns:
            True if the node was removed, False if it was not in the graph.
        """
        if node not in self._nodes:
            return False

        # Remove outgoing edges: node -> dependent
        for dep in list(self._adj.get(node, set())):
            self._rev_adj[dep].discard(node)

        # Remove incoming edges: prereq -> node
        for prereq in list(self._rev_adj.get(node, set())):
            self._adj[prereq].discard(node)

        self._adj.pop(node, None)
        self._rev_adj.pop(node, None)
        self._nodes.remove(node)
        return True

    def has_node(self, node: int) -> bool:
        """Check whether a node exists in the graph."""
        return node in self._nodes

    def get_nodes(self) -> list[int]:
        """Return a sorted list of all node IDs in the graph."""
        return sorted(self._nodes)

    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Return the total number of directed dependency edges in the graph."""
        return sum(len(deps) for deps in self._adj.values())

    def clear(self) -> None:
        """Reset the graph to an empty state."""
        self._adj.clear()
        self._rev_adj.clear()
        self._nodes.clear()

    def add_edge(self, prerequisite: int, dependent: int) -> None:
        """Add a directed dependency edge from prerequisite to dependent (prereq -> dependent).
        
        Args:
            prerequisite: ID of the prerequisite task (must complete first).
            dependent: ID of the dependent task (depends on prerequisite).
            
        Raises:
            InvalidDependencyError: If a task attempts to depend on itself.
        """
        if prerequisite == dependent:
            raise InvalidDependencyError(
                f"Self-dependency detected: Task {prerequisite} cannot depend on itself."
            )

        self.add_node(prerequisite)
        self.add_node(dependent)

        self._adj[prerequisite].add(dependent)
        self._rev_adj[dependent].add(prerequisite)

    def remove_edge(self, prerequisite: int, dependent: int) -> bool:
        """Remove a directed dependency edge between prerequisite and dependent.
        
        Args:
            prerequisite: ID of prerequisite task.
            dependent: ID of dependent task.
            
        Returns:
            True if the edge existed and was removed, False otherwise.
        """
        if (
            prerequisite in self._adj
            and dependent in self._adj[prerequisite]
        ):
            self._adj[prerequisite].discard(dependent)
            self._rev_adj[dependent].discard(prerequisite)
            return True
        return False

    def has_edge(self, prerequisite: int, dependent: int) -> bool:
        """Check whether a directed edge exists from prerequisite to dependent."""
        return (
            prerequisite in self._adj
            and dependent in self._adj[prerequisite]
        )

    def get_edges(self) -> list[tuple[int, int]]:
        """Return a sorted list of all directed dependency edges as (prerequisite, dependent)."""
        edges: list[tuple[int, int]] = []
        for prereq in sorted(self._adj.keys()):
            for dep in sorted(self._adj[prereq]):
                edges.append((prereq, dep))
        return edges

    def get_prerequisites(self, task_id: int) -> list[int]:
        """Return a sorted list of task IDs that must be completed before task_id can start.
        
        Args:
            task_id: Dependent task ID.
            
        Returns:
            Sorted list of prerequisite task IDs (in-neighbors).
        """
        return sorted(self._rev_adj.get(task_id, set()))

    def get_dependents(self, task_id: int) -> list[int]:
        """Return a sorted list of task IDs that directly depend on task_id.
        
        Args:
            task_id: Prerequisite task ID.
            
        Returns:
            Sorted list of dependent task IDs (out-neighbors).
        """
        return sorted(self._adj.get(task_id, set()))

    def get_neighbors(self, task_id: int) -> list[int]:
        """Alias for get_dependents, returning out-neighbors."""
        return self.get_dependents(task_id)

    def in_degree(self, task_id: int) -> int:
        """Return the in-degree of a task node (number of direct prerequisites)."""
        return len(self._rev_adj.get(task_id, set()))

    def out_degree(self, task_id: int) -> int:
        """Return the out-degree of a task node (number of direct dependents)."""
        return len(self._adj.get(task_id, set()))

    def has_path(self, start: int, target: int) -> bool:
        """Determine if a directed path exists from start to target.
        
        Uses BFS with custom Queue to explore reachable nodes.
        
        Args:
            start: Source task ID.
            target: Destination task ID.
            
        Returns:
            True if target is reachable from start, False otherwise.
        """
        if start not in self._nodes or target not in self._nodes:
            return False
        if start == target:
            return True

        queue: Queue[int] = Queue()
        visited: set[int] = {start}
        queue.enqueue(start)

        while not queue.is_empty():
            curr = queue.dequeue()
            if curr == target:
                return True
            for nxt in self._adj.get(curr, set()):
                if nxt not in visited:
                    if nxt == target:
                        return True
                    visited.add(nxt)
                    queue.enqueue(nxt)

        return False

    def would_create_cycle(self, prerequisite: int, dependent: int) -> bool:
        """Check whether adding an edge prerequisite -> dependent would induce a circular dependency.
        
        A cycle would be formed if:
        1. prerequisite == dependent (self-loop).
        2. A directed path already exists from dependent to prerequisite.
        
        Args:
            prerequisite: ID of proposed prerequisite.
            dependent: ID of proposed dependent.
            
        Returns:
            True if adding this edge would create a cycle, False otherwise.
        """
        if prerequisite == dependent:
            return True
        # If dependent can already reach prerequisite, adding prerequisite -> dependent creates a cycle
        return self.has_path(start=dependent, target=prerequisite)

    def bfs(self, start_node: int) -> list[int]:
        """Perform Breadth-First Search traversal starting from start_node.
        
        Explores reachable dependents level by level using the custom FIFO Queue
        from Phase 02 (`taskforge.structures.queue.Queue`).
        
        Args:
            start_node: Root task ID for traversal.
            
        Returns:
            List of visited task IDs in the exact order of discovery.
        """
        if start_node not in self._nodes:
            return []

        visited: set[int] = {start_node}
        traversal_order: list[int] = []
        queue: Queue[int] = Queue()
        queue.enqueue(start_node)

        while not queue.is_empty():
            curr = queue.dequeue()
            traversal_order.append(curr)

            # Deterministic exploration order: sort dependents ascending
            for neighbor in sorted(self._adj.get(curr, set())):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.enqueue(neighbor)

        return traversal_order

    def dfs(self, start_node: int) -> list[int]:
        """Perform Depth-First Search traversal starting from start_node.
        
        Explores paths deeply before backtracking using the custom LIFO Stack
        from Phase 02 (`taskforge.structures.stack.Stack`).
        
        Args:
            start_node: Root task ID for traversal.
            
        Returns:
            List of visited task IDs in the order they are popped/processed.
        """
        if start_node not in self._nodes:
            return []

        visited: set[int] = set()
        traversal_order: list[int] = []
        stack: Stack[int] = Stack()
        stack.push(start_node)

        while not stack.is_empty():
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                traversal_order.append(curr)

                # Push unvisited neighbors in reverse sorted order so that
                # the smallest neighbor is popped and explored first
                neighbors = sorted(self._adj.get(curr, set()), reverse=True)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.push(neighbor)

        return traversal_order

    def detect_cycle(self) -> tuple[bool, list[int]]:
        """Detect whether the graph contains any directed circular dependency.
        
        Uses 3-color Depth-First Search:
            - WHITE (0): Unvisited
            - GRAY (1): Currently in the active recursion call stack
            - BLACK (2): Completely explored
            
        Returns:
            A tuple of (has_cycle, cycle_path).
            If a cycle exists, has_cycle is True and cycle_path contains the sequence of nodes
            forming the cycle (e.g. [1, 2, 3, 1]). Otherwise, returns (False, []).
        """
        # 0 = WHITE, 1 = GRAY, 2 = BLACK
        color: dict[int, int] = {node: 0 for node in self._nodes}
        active_path: list[int] = []
        cycle_found: list[int] = []

        def dfs_visit(u: int) -> bool:
            color[u] = 1  # GRAY: enter recursion stack
            active_path.append(u)

            for v in sorted(self._adj.get(u, set())):
                if color[v] == 1:
                    # Back-edge detected! Reconstruct the cycle
                    cycle_start_idx = active_path.index(v)
                    cycle_found.extend(active_path[cycle_start_idx:] + [v])
                    return True
                if color[v] == 0:
                    if dfs_visit(v):
                        return True

            active_path.pop()
            color[u] = 2  # BLACK: finished
            return False

        for node in sorted(self._nodes):
            if color[node] == 0:
                if dfs_visit(node):
                    return True, cycle_found

        return False, []

    def is_acyclic(self) -> bool:
        """Return True if the graph is a Directed Acyclic Graph (DAG), False if it contains cycles."""
        has_cycle, _ = self.detect_cycle()
        return not has_cycle

    def topological_sort(self) -> list[int]:
        """Compute a valid linear execution order for all tasks using Kahn's Algorithm.
        
        Kahn's Algorithm:
            1. Compute in-degrees for all nodes.
            2. Enqueue all nodes with in-degree 0 into our custom Queue.
               To guarantee deterministic order, initial zero in-degree nodes are enqueued in ascending ID order.
            3. Dequeue a node, append to result order, and decrement in-degrees of its dependents.
            4. If any dependent's in-degree drops to 0, enqueue it.
            5. If the count of processed nodes does not match total nodes in the graph,
               a circular dependency exists.
               
        Returns:
            A list of task IDs in valid dependency-respecting topological order.
            
        Raises:
            CycleDetectedError: If the graph contains at least one cycle.
        """
        if not self._nodes:
            return []

        # 1. Compute in-degrees
        in_degrees: dict[int, int] = {node: len(self._rev_adj.get(node, set())) for node in self._nodes}

        # 2. Enqueue nodes with in-degree 0 using custom Queue
        queue: Queue[int] = Queue()
        for node in sorted(node for node, deg in in_degrees.items() if deg == 0):
            queue.enqueue(node)

        result: list[int] = []

        # 3. Process queue
        while not queue.is_empty():
            curr = queue.dequeue()
            result.append(curr)

            # Sort dependents for deterministic tie-breaking
            for dep in sorted(self._adj.get(curr, set())):
                in_degrees[dep] -= 1
                if in_degrees[dep] == 0:
                    queue.enqueue(dep)

        # 4. Check for cycle
        if len(result) != len(self._nodes):
            has_cycle, cycle_path = self.detect_cycle()
            cycle_desc = " -> ".join(map(str, cycle_path)) if cycle_path else "unknown cycle"
            raise CycleDetectedError(
                f"Graph contains a circular dependency ({cycle_desc}); topological sort is not possible."
            )

        return result
