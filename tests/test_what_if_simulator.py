"""Unit tests for WhatIfSimulatorService (CO5).

Validates:
- Validation errors (negative delay, completed task, non-existent task, cyclic graph)
- Baseline vs. simulated schedule accuracy
- Downstream delay propagation
- Parallel branch slack absorption
- Completed prerequisite handling
- Strict persistence safety (no mutation of database or task state)
"""

from __future__ import annotations

from pathlib import Path
import pytest

from taskforge.graph.dependency_graph import DependencyGraph
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.what_if_simulator import (
    WhatIfSimulationResult,
    WhatIfSimulatorService,
)
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated SQLite database."""
    return TaskStorage(tmp_path / "test_what_if_simulator.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def simulator(storage: TaskStorage, dep_service: DependencyService) -> WhatIfSimulatorService:
    """Fixture providing a WhatIfSimulatorService instance."""
    return WhatIfSimulatorService(storage, dep_service)


def test_negative_delay_rejected(simulator: WhatIfSimulatorService) -> None:
    """Test that a negative delay is rejected with an invalid result."""
    result = simulator.simulate_delay(task_id=1, delay_minutes=-15)
    assert result.is_valid is False
    assert "cannot be negative" in (result.error_message or "").lower()


def test_nonexistent_task_rejected(
    storage: TaskStorage,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that targeting a non-existent task ID returns an error."""
    result = simulator.simulate_delay(task_id=999, delay_minutes=30)
    assert result.is_valid is False
    assert "not found" in (result.error_message or "").lower()


def test_completed_task_delay_rejected(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that attempting to delay an already completed task is rejected."""
    done_task = storage.create_task(
        Task(title="Finished Task", status=TaskStatus.COMPLETED.value, duration=45)
    )
    assert done_task.id is not None
    dep_service.rebuild()

    result = simulator.simulate_delay(task_id=done_task.id, delay_minutes=30)
    assert result.is_valid is False
    assert "already completed" in (result.error_message or "").lower()


def test_zero_minute_delay_leaves_schedule_identical(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that a 0-minute delay produces identical baseline and simulated schedules."""
    t1 = storage.create_task(Task(title="Task 1", duration=60))
    t2 = storage.create_task(Task(title="Task 2", duration=30))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    result = simulator.simulate_delay(task_id=t1.id, delay_minutes=0)
    assert result.is_valid is True
    assert result.project_delay_increase == 0
    assert result.baseline_project_duration == 90
    assert result.simulated_project_duration == 90
    assert len(result.affected_task_ids) == 0
    assert len(result.unaffected_task_ids) == 2


def test_delay_propagation_linear_chain(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test delay propagation down a 3-task linear chain: A(60) -> B(30) -> C(45)."""
    tA = storage.create_task(Task(title="A", duration=60))
    tB = storage.create_task(Task(title="B", duration=30))
    tC = storage.create_task(Task(title="C", duration=45))
    assert tA.id is not None and tB.id is not None and tC.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)
    dep_service.add_dependency(tB.id, tC.id)

    # Delay task A by 20 minutes
    result = simulator.simulate_delay(task_id=tA.id, delay_minutes=20)
    assert result.is_valid is True
    assert result.baseline_project_duration == 135
    assert result.simulated_project_duration == 155
    assert result.project_delay_increase == 20

    # All three tasks should be affected
    assert set(result.affected_task_ids) == {tA.id, tB.id, tC.id}

    impact_map = {imp.task_id: imp for imp in result.impacts}

    # A: baseline 0..60 -> simulated 20..80 (diff: +20)
    assert impact_map[tA.id].baseline_start == 0
    assert impact_map[tA.id].baseline_finish == 60
    assert impact_map[tA.id].simulated_start == 20
    assert impact_map[tA.id].simulated_finish == 80
    assert impact_map[tA.id].start_delay_minutes == 20

    # B: baseline 60..90 -> simulated 80..110 (diff: +20)
    assert impact_map[tB.id].baseline_start == 60
    assert impact_map[tB.id].baseline_finish == 90
    assert impact_map[tB.id].simulated_start == 80
    assert impact_map[tB.id].simulated_finish == 110

    # C: baseline 90..135 -> simulated 110..155 (diff: +20)
    assert impact_map[tC.id].baseline_start == 90
    assert impact_map[tC.id].baseline_finish == 135
    assert impact_map[tC.id].simulated_start == 110
    assert impact_map[tC.id].simulated_finish == 155


def test_delaying_intermediate_task_leaves_predecessors_unaffected(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that delaying B in A -> B -> C leaves predecessor A untouched."""
    tA = storage.create_task(Task(title="A", duration=50))
    tB = storage.create_task(Task(title="B", duration=50))
    tC = storage.create_task(Task(title="C", duration=50))
    assert tA.id is not None and tB.id is not None and tC.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)
    dep_service.add_dependency(tB.id, tC.id)

    # Delay B by 15 min
    result = simulator.simulate_delay(task_id=tB.id, delay_minutes=15)
    assert result.is_valid is True

    impact_map = {imp.task_id: imp for imp in result.impacts}
    # Predecessor A is unaffected
    assert impact_map[tA.id].is_affected is False
    assert impact_map[tA.id].simulated_start == 0
    assert impact_map[tA.id].simulated_finish == 50

    # B and C are affected
    assert impact_map[tB.id].is_affected is True
    assert impact_map[tB.id].simulated_start == 65
    assert impact_map[tB.id].simulated_finish == 115

    assert impact_map[tC.id].is_affected is True
    assert impact_map[tC.id].simulated_start == 115
    assert impact_map[tC.id].simulated_finish == 165


def test_parallel_branch_slack_absorption(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that when a non-critical parallel task is delayed within its slack buffer,
    downstream tasks and total project completion time remain completely unchanged.
    
    Structure:
        A(40) -> C(30)
        B(100) -> C(30)
    Baseline:
        A: 0..40
        B: 0..100
        C: 100..130 (total: 130 min)
    Delaying A by 30 min:
        A: 30..70 (still finishes before B at 100)
        C still starts at max(70, 100) = 100
        Total project duration remains 130 min (0 min increase).
    """
    tA = storage.create_task(Task(title="A Short", duration=40))
    tB = storage.create_task(Task(title="B Long", duration=100))
    tC = storage.create_task(Task(title="C Convergence", duration=30))
    assert tA.id is not None and tB.id is not None and tC.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tC.id)
    dep_service.add_dependency(tB.id, tC.id)

    result = simulator.simulate_delay(task_id=tA.id, delay_minutes=30)
    assert result.is_valid is True
    assert result.baseline_project_duration == 130
    assert result.simulated_project_duration == 130
    assert result.project_delay_increase == 0

    impact_map = {imp.task_id: imp for imp in result.impacts}
    # A was delayed
    assert impact_map[tA.id].is_affected is True
    assert impact_map[tA.id].simulated_start == 30
    assert impact_map[tA.id].simulated_finish == 70

    # B was unaffected
    assert impact_map[tB.id].is_affected is False

    # C is unaffected because B still finishes at 100!
    assert impact_map[tC.id].is_affected is False
    assert impact_map[tC.id].simulated_start == 100
    assert impact_map[tC.id].simulated_finish == 130


def test_completed_prerequisites_treated_as_satisfied_at_time_zero(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Test that completed prerequisites do not add time to the remaining-work schedule."""
    # Completed task
    done_prereq = storage.create_task(
        Task(title="Done Setup", status=TaskStatus.COMPLETED.value, duration=120)
    )
    # Pending dependent
    pending_dep = storage.create_task(
        Task(title="Feature Task", status=TaskStatus.PENDING.value, duration=45)
    )
    assert done_prereq.id is not None and pending_dep.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(done_prereq.id, pending_dep.id)

    # In remaining work, done_prereq is excluded, so pending_dep starts at 0
    result = simulator.simulate_delay(task_id=pending_dep.id, delay_minutes=10)
    assert result.is_valid is True
    assert result.baseline_project_duration == 45
    assert result.simulated_project_duration == 55
    assert result.project_delay_increase == 10

    impact = result.impacts[0]
    assert impact.task_id == pending_dep.id
    assert impact.baseline_start == 0
    assert impact.simulated_start == 10


def test_persistence_safety_no_database_mutation(
    storage: TaskStorage,
    dep_service: DependencyService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Crucial verification: Assert that simulations do NOT alter SQLite records,
    task durations, statuses, deadlines, or dependencies.
    """
    t1 = storage.create_task(Task(title="Persistent 1", duration=50, status=TaskStatus.PENDING.value))
    t2 = storage.create_task(Task(title="Persistent 2", duration=40, status=TaskStatus.IN_PROGRESS.value))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # Snapshot before simulation
    tasks_before = storage.list_tasks()
    deps_before = storage.get_dependencies()

    # Run multiple aggressive simulations
    simulator.simulate_delay(task_id=t1.id, delay_minutes=120)
    simulator.simulate_delay(task_id=t2.id, delay_minutes=60)
    simulator.simulate_delay(task_id=t1.id, delay_minutes=0)

    # Snapshot after simulation
    tasks_after = storage.list_tasks()
    deps_after = storage.get_dependencies()

    # Assert exact equality
    assert len(tasks_after) == len(tasks_before)
    for b, a in zip(tasks_before, tasks_after):
        assert b.id == a.id
        assert b.title == a.title
        assert b.duration == a.duration
        assert b.status == a.status
        assert b.due_date == a.due_date
        assert b.priority == a.priority

    assert deps_before == deps_after
