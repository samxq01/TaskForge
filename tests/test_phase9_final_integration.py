"""Final comprehensive cross-phase integration tests (Workflows A to E) for Phase 09.

Validates the complete integration across all 8 previous phases:
- Workflow A: Task CRUD, dual-stack Undo/Redo, and exact ID preservation.
- Workflow B: Directed dependency constraints, eligibility filtering, and FIFO dispatching.
- Workflow C: Custom search/sort algorithms, BST deadline indexing, and Hash Table indexing.
- Workflow D: Min-Heap Smart Auto-Scheduler and deterministic Deadline Risk Analyzer.
- Workflow E: Critical Path DAG dynamic programming, What-If delay simulation, and persistence safety.
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.algorithms.searching import binary_search, linear_search
from taskforge.algorithms.sorting import insertion_sort, merge_sort
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import CriticalPathService
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import DeadlineRiskAnalyzer, RiskCategory
from taskforge.services.scheduler import SchedulerService
from taskforge.services.structure_evaluation import StructureEvaluationService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.services.what_if_simulator import WhatIfSimulatorService
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated SQLite database."""
    return TaskStorage(tmp_path / "test_phase9_final_integration.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Fixture providing an undo manager."""
    return UndoManager()


@pytest.fixture
def queue_service(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
) -> TaskQueueService:
    """Fixture providing a task queue service."""
    return TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)


@pytest.fixture
def bst_index(storage: TaskStorage) -> TaskIndexService:
    """Fixture providing a BST task index service."""
    return TaskIndexService(storage)


@pytest.fixture
def hash_index(storage: TaskStorage) -> TaskHashIndexService:
    """Fixture providing a hash table index service."""
    return TaskHashIndexService(storage)


@pytest.fixture
def scheduler(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Fixture providing a Smart Auto-Scheduler service."""
    return SchedulerService(storage, dep_service)


@pytest.fixture
def risk_analyzer(storage: TaskStorage, dep_service: DependencyService) -> DeadlineRiskAnalyzer:
    """Fixture providing a Deadline Risk Analyzer."""
    return DeadlineRiskAnalyzer(storage, dep_service)


@pytest.fixture
def cp_service(storage: TaskStorage, dep_service: DependencyService) -> CriticalPathService:
    """Fixture providing a CriticalPathService."""
    return CriticalPathService(storage, dep_service)


@pytest.fixture
def simulator(storage: TaskStorage, dep_service: DependencyService) -> WhatIfSimulatorService:
    """Fixture providing a WhatIfSimulatorService."""
    return WhatIfSimulatorService(storage, dep_service)


def test_workflow_a_task_management_and_history(
    storage: TaskStorage,
    undo_mgr: UndoManager,
) -> None:
    """Workflow A: Task creation, editing, undo, redo, deletion, and exact ID preservation."""
    # 1. Create a task
    t = storage.create_task(
        Task(
            title="Initial Task",
            description="Created for Workflow A",
            priority=Priority.MEDIUM.value,
            duration=45,
            status=TaskStatus.PENDING.value,
        )
    )
    assert t.id is not None
    original_id = t.id
    undo_mgr.record_action(ActionType.CREATE, task_id=original_id, after_state=copy.copy(t))

    # 2. Edit task
    before_edit = copy.copy(t)
    t.title = "Updated Task Title"
    t.priority = Priority.URGENT.value
    t.duration = 60
    storage.update_task(t)
    undo_mgr.record_action(
        ActionType.EDIT,
        task_id=original_id,
        before_state=before_edit,
        after_state=copy.copy(t),
    )

    db_edited = storage.get_task(original_id)
    assert db_edited is not None
    assert db_edited.title == "Updated Task Title"
    assert db_edited.priority == Priority.URGENT.value

    # 3. Undo edit
    assert undo_mgr.can_undo() is True
    undo_mgr.undo(storage)
    db_undone = storage.get_task(original_id)
    assert db_undone is not None
    assert db_undone.title == "Initial Task"
    assert db_undone.priority == Priority.MEDIUM.value

    # 4. Redo edit
    assert undo_mgr.can_redo() is True
    undo_mgr.redo(storage)
    db_redone = storage.get_task(original_id)
    assert db_redone is not None
    assert db_redone.title == "Updated Task Title"

    # 5. Delete task
    before_del = copy.copy(db_redone)
    storage.delete_task(original_id)
    assert storage.get_task(original_id) is None
    undo_mgr.record_action(ActionType.DELETE, task_id=original_id, before_state=before_del)

    # 6. Undo deletion -> verify exact ID and attributes restored
    assert undo_mgr.can_undo() is True
    undo_mgr.undo(storage)
    db_restored = storage.get_task(original_id)
    assert db_restored is not None
    assert db_restored.id == original_id
    assert db_restored.title == "Updated Task Title"
    assert db_restored.priority == Priority.URGENT.value


def test_workflow_b_dependencies_and_fifo_processing(
    storage: TaskStorage,
    dep_service: DependencyService,
    queue_service: TaskQueueService,
) -> None:
    """Workflow B: Dependencies, blocked status exclusion, and FIFO task dispatching."""
    # Create 3 tasks: T1 (prereq), T2 (dependent on T1), T3 (independent)
    t1 = storage.create_task(Task(title="Prerequisite Task", duration=30))
    t2 = storage.create_task(Task(title="Blocked Dependent", duration=40))
    t3 = storage.create_task(Task(title="Independent Task", duration=25))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # Queue should only contain eligible tasks: [T1, T3]. T2 is blocked!
    queue_service.refresh()
    queued_tasks = queue_service.get_queue_tasks()
    queued_ids = [t.id for t in queued_tasks]
    assert t1.id in queued_ids
    assert t3.id in queued_ids
    assert t2.id not in queued_ids

    # Dispatch first task in FIFO order (T1 was created first)
    dispatched_1 = queue_service.process_next_task()
    assert dispatched_1 is not None
    assert dispatched_1.id == t1.id
    assert dispatched_1.status == TaskStatus.IN_PROGRESS.value

    # Complete T1
    dispatched_1.status = TaskStatus.COMPLETED.value
    storage.update_task(dispatched_1)
    dep_service.rebuild()

    # Now T2 is unblocked and becomes eligible!
    queue_service.refresh()
    new_queued_ids = [t.id for t in queue_service.get_queue_tasks()]
    assert t2.id in new_queued_ids


def test_workflow_c_algorithms_and_indexes(
    storage: TaskStorage,
    bst_index: TaskIndexService,
    hash_index: TaskHashIndexService,
) -> None:
    """Workflow C: Custom search, sort, BST deadline indexing, and Hash Table indexing."""
    now = datetime(2026, 10, 30, 12, 0)
    t_early = storage.create_task(Task(title="Alpha", priority=Priority.LOW.value, due_date=now + timedelta(days=1)))
    t_mid = storage.create_task(Task(title="Beta", priority=Priority.URGENT.value, due_date=now + timedelta(days=3)))
    t_late = storage.create_task(Task(title="Gamma", priority=Priority.HIGH.value, due_date=now + timedelta(days=5)))
    assert t_early.id is not None and t_mid.id is not None and t_late.id is not None

    tasks = storage.list_tasks()

    # 1. Custom Linear Search
    match_linear = linear_search(tasks, "Beta", key=lambda t: t.title)
    assert match_linear.found is True
    assert match_linear.item is not None
    assert match_linear.item.id == t_mid.id

    # 2. Custom Binary Search (on pre-sorted list by title)
    sorted_by_title = merge_sort(tasks, key=lambda t: t.title).items
    match_binary = binary_search(sorted_by_title, "Gamma", key=lambda t: t.title)
    assert match_binary.found is True
    assert match_binary.item is not None
    assert match_binary.item.id == t_late.id

    # 3. Custom Insertion Sort by Priority DESC
    sorted_by_priority = insertion_sort(tasks, key=lambda t: t.priority, reverse=True).items
    assert [t.id for t in sorted_by_priority] == [t_mid.id, t_late.id, t_early.id]

    # 4. BST Deadline Index
    bst_index.rebuild()
    inorder_tasks = bst_index.get_deadline_ordered_tasks()
    # Inorder traversal must match chronological deadline order
    assert [t.id for t in inorder_tasks] == [t_early.id, t_mid.id, t_late.id]

    # 5. Hash Table Index
    hash_index.rebuild_index()
    retrieved_beta, comp_count = hash_index.get_task_with_comparisons(t_mid.id)
    assert retrieved_beta is not None
    assert retrieved_beta.title == "Beta"
    assert comp_count >= 1

    # Multi-Structure Evaluation Service
    eval_service = StructureEvaluationService()
    comparison_results = eval_service.run_evaluation(dataset=tasks, scenario="early", repetitions=5)
    assert len(comparison_results) == 3
    for res in comparison_results:
        assert res.result_found is True


def test_workflow_d_smart_scheduling_and_risk(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    risk_analyzer: DeadlineRiskAnalyzer,
) -> None:
    """Workflow D: Min-Heap Smart Auto-Scheduler and deterministic Deadline Risk Analyzer."""
    now = datetime(2026, 10, 30, 9, 0)
    prereq = storage.create_task(
        Task(title="Foundation", priority=Priority.LOW.value, duration=30, due_date=now + timedelta(days=2))
    )
    blocked_urgent = storage.create_task(
        Task(title="Urgent Feature", priority=Priority.URGENT.value, duration=60, due_date=now + timedelta(hours=2))
    )
    assert prereq.id is not None and blocked_urgent.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, blocked_urgent.id)

    # 1. Initial Smart Schedule: Only prereq is eligible; blocked_urgent is excluded
    sched_1 = scheduler.get_smart_schedule()
    assert sched_1.is_valid is True
    assert sched_1.recommended_task is not None
    assert sched_1.recommended_task.id == prereq.id
    assert sched_1.blocked_count == 1

    # 2. Deadline Risk Analysis: blocked_urgent must be At Risk with is_blocked=True
    risk_1 = risk_analyzer.analyze_task(blocked_urgent, current_time=now)
    assert risk_1.category == RiskCategory.AT_RISK
    assert risk_1.is_blocked is True

    # 3. Complete the prerequisite
    prereq.status = TaskStatus.COMPLETED.value
    storage.update_task(prereq)
    dep_service.rebuild()

    # 4. Refreshed Smart Schedule: blocked_urgent is now eligible and top recommended!
    sched_2 = scheduler.get_smart_schedule()
    assert sched_2.recommended_task is not None
    assert sched_2.recommended_task.id == blocked_urgent.id
    assert sched_2.blocked_count == 0


def test_workflow_e_critical_path_and_simulation(
    storage: TaskStorage,
    dep_service: DependencyService,
    cp_service: CriticalPathService,
    simulator: WhatIfSimulatorService,
) -> None:
    """Workflow E: Critical Path calculation, What-If simulation, and persistence safety."""
    # Graph: A(60) -> B(40) -> D(30), A(60) -> C(90) -> D(30)
    tA = storage.create_task(Task(title="A", duration=60))
    tB = storage.create_task(Task(title="B", duration=40))
    tC = storage.create_task(Task(title="C", duration=90))
    tD = storage.create_task(Task(title="D", duration=30))
    assert tA.id is not None and tB.id is not None and tC.id is not None and tD.id is not None

    dep_service.rebuild()
    dep_service.add_dependency(tA.id, tB.id)
    dep_service.add_dependency(tA.id, tC.id)
    dep_service.add_dependency(tB.id, tD.id)
    dep_service.add_dependency(tC.id, tD.id)

    # 1. Critical Path is A -> C -> D = 180 min
    cp_res = cp_service.calculate_critical_path()
    assert cp_res.is_valid is True
    assert cp_res.total_duration_minutes == 180
    assert cp_res.critical_path_ids == [tA.id, tC.id, tD.id]

    # 2. Simulation on parallel non-critical branch (slack absorption)
    sim_slack = simulator.simulate_delay(task_id=tB.id, delay_minutes=25)
    assert sim_slack.is_valid is True
    assert sim_slack.project_delay_increase == 0  # Delay absorbed!
    assert sim_slack.simulated_project_duration == 180
    assert sim_slack.affected_task_ids == [tB.id]

    # 3. Simulation on critical task
    sim_crit = simulator.simulate_delay(task_id=tC.id, delay_minutes=30)
    assert sim_crit.is_valid is True
    assert sim_crit.project_delay_increase == 30
    assert sim_crit.simulated_project_duration == 210
    assert set(sim_crit.affected_task_ids) == {tC.id, tD.id}

    # 4. Strict persistence safety check: assert zero database or model changes
    db_tasks = storage.list_tasks()
    for dt in db_tasks:
        if dt.id == tA.id:
            assert dt.duration == 60
        elif dt.id == tB.id:
            assert dt.duration == 40
        elif dt.id == tC.id:
            assert dt.duration == 90
        elif dt.id == tD.id:
            assert dt.duration == 30
