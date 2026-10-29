"""Dependency management service synchronizing directed graph structure with SQLite persistence (CO5)."""

from __future__ import annotations

from typing import Optional

from taskforge.graph.dependency_graph import (
    CycleDetectedError,
    DependencyGraph,
    InvalidDependencyError,
)
from taskforge.models import Task
from taskforge.storage import TaskStorage


class DependencyService:
    """Coordinates task dependency relationships between SQLite storage and an in-memory DependencyGraph.
    
    Ensures that all graph modifications are validated (preventing self-dependencies,
    non-existent tasks, and circular dependencies) before persisting to the database.
    """

    def __init__(self, storage: TaskStorage) -> None:
        """Initialize the dependency service and build the in-memory graph.
        
        Args:
            storage: Persistent TaskStorage interface.
        """
        self.storage = storage
        self._graph = DependencyGraph()
        self.rebuild()

    def rebuild(self) -> None:
        """Synchronize the in-memory graph with all tasks and dependencies in SQLite.
        
        Ensures isolated tasks (tasks with 0 dependencies) are also registered as nodes.
        """
        self._graph.clear()

        # Register all existing tasks as nodes
        tasks = self.storage.list_tasks()
        for task in tasks:
            if task.id is not None:
                self._graph.add_node(task.id)

        # Register all directed dependency edges
        dependencies = self.storage.get_dependencies()
        for prereq_id, dep_id in dependencies:
            self._graph.add_edge(prereq_id, dep_id)

    def get_graph(self) -> DependencyGraph:
        """Return the underlying in-memory DependencyGraph instance."""
        return self._graph

    def add_dependency(self, prerequisite_id: int, dependent_id: int) -> None:
        """Validate and persist a directed dependency from prerequisite to dependent (prereq -> dependent).
        
        Args:
            prerequisite_id: ID of the prerequisite task (must complete first).
            dependent_id: ID of the dependent task (depends on prerequisite).
            
        Raises:
            InvalidDependencyError: If self-dependency or non-existent task ID is specified.
            CycleDetectedError: If adding the dependency would introduce a circular graph cycle.
        """
        if prerequisite_id == dependent_id:
            raise InvalidDependencyError(
                f"Self-dependency rejected: Task {prerequisite_id} cannot depend on itself."
            )

        prereq_task = self.storage.get_task(prerequisite_id)
        if prereq_task is None:
            raise InvalidDependencyError(f"Prerequisite task ID {prerequisite_id} does not exist.")

        dep_task = self.storage.get_task(dependent_id)
        if dep_task is None:
            raise InvalidDependencyError(f"Dependent task ID {dependent_id} does not exist.")

        # Ensure both nodes are in graph
        self._graph.add_node(prerequisite_id)
        self._graph.add_node(dependent_id)

        # If already exists, return cleanly
        if self._graph.has_edge(prerequisite_id, dependent_id):
            return

        # Pre-validate cycle prevention: would prereq -> dependent close a cycle?
        if self._graph.would_create_cycle(prerequisite_id, dependent_id):
            raise CycleDetectedError(
                f"Circular dependency rejected: Task {dependent_id} already leads to Task {prerequisite_id}. "
                f"Adding this dependency would cause a deadlock cycle."
            )

        # Persist to SQLite
        self.storage.add_dependency(prerequisite_id, dependent_id)

        # Update in-memory graph
        self._graph.add_edge(prerequisite_id, dependent_id)

    def remove_dependency(self, prerequisite_id: int, dependent_id: int) -> bool:
        """Remove a directed dependency from persistent storage and the in-memory graph.
        
        Args:
            prerequisite_id: ID of prerequisite task.
            dependent_id: ID of dependent task.
            
        Returns:
            True if removed, False if no such dependency existed.
        """
        db_removed = self.storage.remove_dependency(prerequisite_id, dependent_id)
        self._graph.remove_edge(prerequisite_id, dependent_id)
        return db_removed

    def get_prerequisites(self, task_id: int) -> list[Task]:
        """Retrieve all prerequisite Task objects that must be completed before task_id can start.
        
        Args:
            task_id: Dependent task ID.
            
        Returns:
            List of prerequisite Task model instances.
        """
        prereq_ids = self._graph.get_prerequisites(task_id)
        tasks: list[Task] = []
        for pid in prereq_ids:
            task = self.storage.get_task(pid)
            if task is not None:
                tasks.append(task)
        return tasks

    def get_dependents(self, task_id: int) -> list[Task]:
        """Retrieve all Task objects that depend on the completion of task_id.
        
        Args:
            task_id: Prerequisite task ID.
            
        Returns:
            List of dependent Task model instances.
        """
        dep_ids = self._graph.get_dependents(task_id)
        tasks: list[Task] = []
        for did in dep_ids:
            task = self.storage.get_task(did)
            if task is not None:
                tasks.append(task)
        return tasks

    def get_topological_order(self) -> list[Task]:
        """Compute the global linear execution order of tasks respecting dependencies.
        
        Returns:
            List of Task instances in valid topological order.
            
        Raises:
            CycleDetectedError: If a cycle exists in the graph.
        """
        order_ids = self._graph.topological_sort()
        tasks: list[Task] = []
        for tid in order_ids:
            task = self.storage.get_task(tid)
            if task is not None:
                tasks.append(task)
        return tasks

    def run_bfs(self, start_task_id: int) -> list[Task]:
        """Perform Breadth-First Search traversal from start_task_id.
        
        Returns:
            List of reachable Task instances in BFS discovery order.
        """
        order_ids = self._graph.bfs(start_task_id)
        tasks: list[Task] = []
        for tid in order_ids:
            task = self.storage.get_task(tid)
            if task is not None:
                tasks.append(task)
        return tasks

    def run_dfs(self, start_task_id: int) -> list[Task]:
        """Perform Depth-First Search traversal from start_task_id.
        
        Returns:
            List of reachable Task instances in DFS order.
        """
        order_ids = self._graph.dfs(start_task_id)
        tasks: list[Task] = []
        for tid in order_ids:
            task = self.storage.get_task(tid)
            if task is not None:
                tasks.append(task)
        return tasks

    def is_acyclic(self) -> bool:
        """Check whether the active dependency graph is acyclic."""
        return self._graph.is_acyclic()

    def detect_cycle(self) -> tuple[bool, list[int]]:
        """Run cycle detection on the active dependency graph."""
        return self._graph.detect_cycle()
