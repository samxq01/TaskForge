"""Comprehensive unit tests for CriticalPathService (CO5).

Validates longest-path dynamic programming over DAG topological order,
earliest start/finish calculations, tie-breaking, disconnected components,
and cycle rejection.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from taskforge.graph.dependency_graph import DependencyGraph
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import (
    CriticalPathResult,
    CriticalPathService,
    format_duration,
)
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated SQLite database."""
    return TaskStorage(tmp_path / "test_critical_path.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def cp_service(storage: TaskStorage, dep_service: DependencyService) -> CriticalPathService:
    """Fixture providing a CriticalPathService instance."""
    return CriticalPathService(storage, dep_service)


def test_format_duration() -> None:
    """Test format_duration helper utility."""
    assert format_duration(0) == "0 min (0h 00m)"
    assert format_duration(45) == "45 min (0h 45m)"
    assert format_duration(60) == "60 min (1h 00m)"
    assert format_duration(330) == "330 min (5h 30m)"


def test_empty_graph(cp_service: CriticalPathService) -> None:
    """Test critical path calculation on an empty project."""
    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 0
    assert result.critical_path_ids == []
    assert result.critical_path_tasks == []
    assert result.schedule_details == {}
    assert "no tasks" in result.explanation.lower()


def test_single_task_graph(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test critical path calculation with a single isolated task."""
    t1 = storage.create_task(Task(title="Solo Task", duration=75))
    assert t1.id is not None
    dep_service.rebuild()

    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 75
    assert result.critical_path_ids == [t1.id]
    assert len(result.critical_path_tasks) == 1
    assert result.schedule_details[t1.id].earliest_start == 0
    assert result.schedule_details[t1.id].earliest_finish == 75
    assert result.schedule_details[t1.id].is_on_critical_path is True


def test_linear_dependency_chain(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test critical path on a strictly linear sequence: A(40) -> B(50) -> C(60)."""
    tA = storage.create_task(Task(title="A", duration=40))
    tB = storage.create_task(Task(title="B", duration=50))
    tC = storage.create_task(Task(title="C", duration=60))
    assert tA.id is not None and tB.id is not None and tC.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)
    dep_service.add_dependency(tB.id, tC.id)

    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    # 40 + 50 + 60 = 150
    assert result.total_duration_minutes == 150
    assert result.critical_path_ids == [tA.id, tB.id, tC.id]

    assert result.schedule_details[tA.id].earliest_start == 0
    assert result.schedule_details[tA.id].earliest_finish == 40

    assert result.schedule_details[tB.id].earliest_start == 40
    assert result.schedule_details[tB.id].earliest_finish == 90

    assert result.schedule_details[tC.id].earliest_start == 90
    assert result.schedule_details[tC.id].earliest_finish == 150


def test_diamond_branching_graph_with_dominant_path(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test the exact specification example:
    A(120) -> B(90) -> D(30)
    A(120) -> C(180) -> D(30)
    Dominant critical path is A -> C -> D = 330 min.
    """
    tA = storage.create_task(Task(title="Task A", duration=120))
    tB = storage.create_task(Task(title="Task B", duration=90))
    tC = storage.create_task(Task(title="Task C", duration=180))
    tD = storage.create_task(Task(title="Task D", duration=30))
    assert tA.id is not None and tB.id is not None and tC.id is not None and tD.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)
    dep_service.add_dependency(tA.id, tC.id)
    dep_service.add_dependency(tB.id, tD.id)
    dep_service.add_dependency(tC.id, tD.id)

    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 330
    assert result.critical_path_ids == [tA.id, tC.id, tD.id]

    # Check timings
    # B: start=120, finish=210. (Not on critical path)
    assert result.schedule_details[tB.id].is_on_critical_path is False
    assert result.schedule_details[tB.id].earliest_start == 120
    assert result.schedule_details[tB.id].earliest_finish == 210

    # C: start=120, finish=300. (On critical path)
    assert result.schedule_details[tC.id].is_on_critical_path is True
    assert result.schedule_details[tC.id].earliest_start == 120
    assert result.schedule_details[tC.id].earliest_finish == 300

    # D: start=max(210, 300) = 300, finish=330.
    assert result.schedule_details[tD.id].is_on_critical_path is True
    assert result.schedule_details[tD.id].earliest_start == 300
    assert result.schedule_details[tD.id].earliest_finish == 330
    assert result.schedule_details[tD.id].predecessor_id == tC.id


def test_independent_disconnected_components(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test two disjoint components: Component 1 takes 100m, Component 2 takes 250m."""
    # Component 1: C1_1(50) -> C1_2(50) = 100
    c1_1 = storage.create_task(Task(title="C1_1", duration=50))
    c1_2 = storage.create_task(Task(title="C1_2", duration=50))

    # Component 2: C2_1(100) -> C2_2(150) = 250
    c2_1 = storage.create_task(Task(title="C2_1", duration=100))
    c2_2 = storage.create_task(Task(title="C2_2", duration=150))

    assert c1_1.id is not None and c1_2.id is not None and c2_1.id is not None and c2_2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(c1_1.id, c1_2.id)
    dep_service.add_dependency(c2_1.id, c2_2.id)

    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 250
    assert result.critical_path_ids == [c2_1.id, c2_2.id]


def test_isolated_long_task_determines_project_duration(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test when an isolated task has longer duration than a connected chain."""
    # Chain: A(30) -> B(40) = 70 min
    tA = storage.create_task(Task(title="A", duration=30))
    tB = storage.create_task(Task(title="B", duration=40))
    # Isolated task: Solo(180 min)
    tSolo = storage.create_task(Task(title="Solo Big Task", duration=180))

    assert tA.id is not None and tB.id is not None and tSolo.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)

    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 180
    assert result.critical_path_ids == [tSolo.id]


def test_equal_duration_paths_deterministic_tie_breaking(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test deterministic tie-breaking when two independent paths have identical duration."""
    t1 = storage.create_task(Task(title="Path 1", duration=100))
    t2 = storage.create_task(Task(title="Path 2", duration=100))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    result = cp_service.calculate_critical_path()
    assert result.is_valid is True
    assert result.total_duration_minutes == 100
    # Predictably selects smallest task ID: t1.id
    assert result.critical_path_ids == [min(t1.id, t2.id)]


def test_detect_cycle_aborts_critical_path(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test that a circular dependency safely halts critical path analysis."""
    t1 = storage.create_task(Task(title="Node 1", duration=30))
    t2 = storage.create_task(Task(title="Node 2", duration=30))
    assert t1.id is not None and t2.id is not None

    # Artificially create a cyclic graph in memory
    graph = DependencyGraph()
    graph.add_node(t1.id)
    graph.add_node(t2.id)
    graph.add_edge(t1.id, t2.id)
    graph.add_edge(t2.id, t1.id)

    result = cp_service.calculate_critical_path(
        custom_graph=graph,
        custom_tasks=[t1, t2],
    )
    assert result.is_valid is False
    assert result.critical_path_ids == []
    assert "Circular dependency detected" in (result.error_message or "")


def test_recalculate_after_updating_task_duration(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
) -> None:
    """Test that updating a task's duration immediately recalculates the critical path."""
    t1 = storage.create_task(Task(title="Task 1", duration=50))
    t2 = storage.create_task(Task(title="Task 2", duration=50))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    res1 = cp_service.calculate_critical_path()
    assert res1.total_duration_minutes == 100

    # Modify duration of t2 in SQLite
    t2.duration = 150
    storage.update_task(t2)

    res2 = cp_service.calculate_critical_path()
    assert res2.total_duration_minutes == 200
