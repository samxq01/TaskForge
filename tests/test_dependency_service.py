"""Tests for DependencyService SQLite persistence and graph synchronization (CO5)."""

from pathlib import Path
import pytest

from taskforge.graph.dependency_graph import (
    CycleDetectedError,
    InvalidDependencyError,
)
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated SQLite TaskStorage instance."""
    return TaskStorage(tmp_path / "test_dep.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Provide a DependencyService initialized with storage."""
    return DependencyService(storage)


def test_add_and_get_dependencies(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test adding dependencies and verifying graph reflection."""
    t1 = storage.create_task(Task(title="Design DB", priority=Priority.HIGH.value, duration=60))
    t2 = storage.create_task(Task(title="Build API", priority=Priority.MEDIUM.value, duration=60))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    # Add dependency: t1 -> t2 (t2 depends on t1)
    dep_service.add_dependency(t1.id, t2.id)

    assert dep_service.get_graph().has_edge(t1.id, t2.id) is True
    assert storage.has_dependency(t1.id, t2.id) is True

    # Retrieve objects
    prereqs = dep_service.get_prerequisites(t2.id)
    assert len(prereqs) == 1
    assert prereqs[0].id == t1.id

    dependents = dep_service.get_dependents(t1.id)
    assert len(dependents) == 1
    assert dependents[0].id == t2.id


def test_self_dependency_rejected(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test that self-dependencies are rejected before reaching SQLite."""
    t1 = storage.create_task(Task(title="Self Task", priority=Priority.MEDIUM.value, duration=30))
    assert t1.id is not None

    with pytest.raises(InvalidDependencyError, match="Self-dependency rejected"):
        dep_service.add_dependency(t1.id, t1.id)

    assert storage.get_dependencies() == []


def test_nonexistent_task_dependency_rejected(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test that dependencies involving non-existent tasks are rejected."""
    t1 = storage.create_task(Task(title="Real Task", priority=Priority.LOW.value, duration=30))
    assert t1.id is not None

    with pytest.raises(InvalidDependencyError, match="does not exist"):
        dep_service.add_dependency(t1.id, 999)

    with pytest.raises(InvalidDependencyError, match="does not exist"):
        dep_service.add_dependency(888, t1.id)


def test_cycle_detection_rejection(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test that adding a dependency creating a cycle is aborted without polluting SQLite."""
    t1 = storage.create_task(Task(title="Task A", priority=Priority.HIGH.value, duration=30))
    t2 = storage.create_task(Task(title="Task B", priority=Priority.HIGH.value, duration=30))
    t3 = storage.create_task(Task(title="Task C", priority=Priority.HIGH.value, duration=30))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    # A -> B -> C
    dep_service.add_dependency(t1.id, t2.id)
    dep_service.add_dependency(t2.id, t3.id)

    # Attempting C -> A must be rejected!
    with pytest.raises(CycleDetectedError, match="Circular dependency rejected"):
        dep_service.add_dependency(t3.id, t1.id)

    # Verify C -> A was not persisted to SQLite
    assert storage.has_dependency(t3.id, t1.id) is False
    assert dep_service.get_graph().has_edge(t3.id, t1.id) is False
    assert dep_service.is_acyclic() is True


def test_remove_dependency(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test removing dependencies from storage and graph."""
    t1 = storage.create_task(Task(title="Prereq", priority=Priority.LOW.value, duration=20))
    t2 = storage.create_task(Task(title="Dependent", priority=Priority.LOW.value, duration=20))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)
    assert dep_service.remove_dependency(t1.id, t2.id) is True
    assert dep_service.get_graph().has_edge(t1.id, t2.id) is False
    assert storage.has_dependency(t1.id, t2.id) is False


def test_task_deletion_cascades_dependencies(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test that deleting a task removes its dependencies and cleans the graph."""
    t1 = storage.create_task(Task(title="Task 1", priority=Priority.LOW.value, duration=20))
    t2 = storage.create_task(Task(title="Task 2", priority=Priority.LOW.value, duration=20))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # Delete t1
    storage.delete_task(t1.id)
    dep_service.rebuild()

    assert storage.get_dependencies() == []
    assert dep_service.get_graph().has_node(t1.id) is False
    assert dep_service.get_graph().has_edge(t1.id, t2.id) is False


def test_topological_order_resolution(storage: TaskStorage, dep_service: DependencyService) -> None:
    """Test topological order returns Task models in valid sequence."""
    t1 = storage.create_task(Task(title="Init", priority=Priority.HIGH.value, duration=20))
    t2 = storage.create_task(Task(title="Middle", priority=Priority.MEDIUM.value, duration=20))
    t3 = storage.create_task(Task(title="Final", priority=Priority.LOW.value, duration=20))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)
    dep_service.add_dependency(t2.id, t3.id)

    order = dep_service.get_topological_order()
    titles = [t.title for t in order]
    assert titles == ["Init", "Middle", "Final"]
