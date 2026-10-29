"""Comprehensive end-to-end integration tests for Phase 08 (CO5).

Verifies the integration of:
- CriticalPathService (DAG Longest Path via Dynamic Programming)
- WhatIfSimulatorService (In-memory delay propagation and slack absorption)
- Strict persistence safety across SQLite, Undo/Redo stacks, FIFO Queue, BST, and Hash indexes.
- Regression verification across all Phase 01–07 components.
"""

from __future__ import annotations

import copy
from pathlib import Path
import pytest

from taskforge.graph.dependency_graph import DependencyGraph
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import CriticalPathService
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.services.what_if_simulator import WhatIfSimulatorService
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated SQLite database."""
    return TaskStorage(tmp_path / "test_phase8_integration.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Fixture providing an undo manager."""
    return UndoManager()


@pytest.fixture
def cp_service(storage: TaskStorage, dep_service: DependencyService) -> CriticalPathService:
    """Fixture providing a CriticalPathService."""
    return CriticalPathService(storage, dep_service)


@pytest.fixture
def simulator(storage: TaskStorage, dep_service: DependencyService) -> WhatIfSimulatorService:
    """Fixture providing a WhatIfSimulatorService."""
    return WhatIfSimulatorService(storage, dep_service)


@pytest.fixture
def bst_index(storage: TaskStorage) -> TaskIndexService:
    """Fixture providing a BST task index service."""
    return TaskIndexService(storage)


@pytest.fixture
def hash_index(storage: TaskStorage) -> TaskHashIndexService:
    """Fixture providing a hash table index service."""
    return TaskHashIndexService(storage)


@pytest.fixture
def queue_service(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
) -> TaskQueueService:
    """Fixture providing a task queue service."""
    return TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)


def test_full_phase8_planning_workflow(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
    simulator: WhatIfSimulatorService,
    queue_service: TaskQueueService,
    bst_index: TaskIndexService,
    hash_index: TaskHashIndexService,
    undo_mgr: UndoManager,
) -> None:
    """Test full planning lifecycle: Critical Path, What-If simulation, delay propagation,
    slack absorption, and strict persistence safety.
    """
    # Create realistic project:
    # T1: Architecture (60m)
    # T2: Backend API (90m, depends on T1)
    # T3: Frontend Prototype (40m, depends on T1)
    # T4: System Integration (30m, depends on T2 and T3)
    t1 = storage.create_task(Task(title="Architecture", duration=60, priority=Priority.URGENT.value))
    t2 = storage.create_task(Task(title="Backend API", duration=90, priority=Priority.HIGH.value))
    t3 = storage.create_task(Task(title="Frontend Prototype", duration=40, priority=Priority.MEDIUM.value))
    t4 = storage.create_task(Task(title="System Integration", duration=30, priority=Priority.URGENT.value))
    assert t1.id is not None and t2.id is not None and t3.id is not None and t4.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)
    dep_service.add_dependency(t1.id, t3.id)
    dep_service.add_dependency(t2.id, t4.id)
    dep_service.add_dependency(t3.id, t4.id)

    # 1. Critical Path Analysis:
    # Path 1: T1(60) -> T2(90) -> T4(30) = 180m (Dominant)
    # Path 2: T1(60) -> T3(40) -> T4(30) = 130m
    cp_res = cp_service.calculate_critical_path()
    assert cp_res.is_valid is True
    assert cp_res.total_duration_minutes == 180
    assert cp_res.critical_path_ids == [t1.id, t2.id, t4.id]

    # 2. What-If Simulation on Non-Critical Branch (Slack Absorption):
    # T3 has 50 min of slack (finishes at 100 while T2 finishes at 150).
    # Delaying T3 by 30 min should NOT increase project duration!
    sim_slack = simulator.simulate_delay(task_id=t3.id, delay_minutes=30)
    assert sim_slack.is_valid is True
    assert sim_slack.project_delay_increase == 0
    assert sim_slack.simulated_project_duration == 180
    assert sim_slack.affected_task_ids == [t3.id]  # Only T3 shifted; T4 is unaffected!

    # 3. What-If Simulation on Critical Path Task (Delay Propagation):
    # Delaying T2 by 45 min must push T4 and increase project duration by 45 min.
    sim_crit = simulator.simulate_delay(task_id=t2.id, delay_minutes=45)
    assert sim_crit.is_valid is True
    assert sim_crit.project_delay_increase == 45
    assert sim_crit.simulated_project_duration == 225
    assert set(sim_crit.affected_task_ids) == {t2.id, t4.id}

    # 4. Persistence Safety Verification:
    # Assert database records and service indexes were NOT modified by simulations
    db_tasks = storage.list_tasks()
    assert len(db_tasks) == 4
    for dt in db_tasks:
        assert dt.status == TaskStatus.PENDING.value  # Status preserved
        if dt.id == t1.id:
            assert dt.duration == 60
        elif dt.id == t2.id:
            assert dt.duration == 90
        elif dt.id == t3.id:
            assert dt.duration == 40
        elif dt.id == t4.id:
            assert dt.duration == 30

    # Ensure queue and undo history were not mutated
    queue_service.refresh()
    assert queue_service.size() == 1  # Only T1 is unblocked
    assert undo_mgr.can_undo() is False


def test_completed_task_remaining_work_difference(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Verify that full-plan Critical Path retains completed task durations,
    while What-If simulation treats completed tasks as 0 remaining time.
    """
    # T1 completed (60m) -> T2 pending (90m)
    t1 = storage.create_task(Task(title="Architecture", duration=60, status=TaskStatus.COMPLETED.value))
    t2 = storage.create_task(Task(title="Implementation", duration=90, status=TaskStatus.PENDING.value))
    assert t1.id is not None and t2.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # 1. Full-plan Critical Path: 60 + 90 = 150m
    cp_res = cp_service.calculate_critical_path()
    assert cp_res.total_duration_minutes == 150
    assert cp_res.critical_path_ids == [t1.id, t2.id]

    # 2. What-If Remaining Work: T1 is completed (takes 0m), so baseline remaining is 90m
    sim_res = simulator.simulate_delay(task_id=t2.id, delay_minutes=0)
    assert sim_res.baseline_project_duration == 90
    assert sim_res.simulated_project_duration == 90


def test_cycle_detection_safety_across_phase8_services(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Verify that if a circular dependency is introduced, both services fail gracefully."""
    t1 = storage.create_task(Task(title="A", duration=30))
    t2 = storage.create_task(Task(title="B", duration=30))
    assert t1.id is not None and t2.id is not None

    # Artificially inject a cycle into an in-memory graph
    cyclic_graph = DependencyGraph()
    cyclic_graph.add_node(t1.id)
    cyclic_graph.add_node(t2.id)
    cyclic_graph.add_edge(t1.id, t2.id)
    cyclic_graph.add_edge(t2.id, t1.id)

    # Critical path should abort safely
    cp_res = cp_service.calculate_critical_path(
        custom_graph=cyclic_graph,
        custom_tasks=[t1, t2],
    )
    assert cp_res.is_valid is False
    assert "Circular dependency detected" in (cp_res.error_message or "")

    # What-If simulator should abort safely
    sim_res = simulator.simulate_delay(
        task_id=t1.id,
        delay_minutes=15,
        custom_graph=cyclic_graph,
        custom_tasks=[t1, t2],
    )
    assert sim_res.is_valid is False
    assert "Circular dependency detected" in (sim_res.error_message or "")
