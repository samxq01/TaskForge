"""Comprehensive end-to-end integration tests for Phase 07 (CO1 + CO5).

Verifies the interplay among:
- Manual Min-Heap Priority Queue (CO1)
- Smart Auto-Scheduler (CO1 + CO5)
- Dependency Graph with cycle prevention (CO5)
- Deterministic Deadline Risk Analyzer
- FIFO Task Processing Queue and Undo/Redo stack manager
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import DeadlineRiskAnalyzer, RiskCategory
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Fixture providing an isolated SQLite database."""
    return TaskStorage(tmp_path / "test_phase7_integration.db")


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Fixture providing a dependency service."""
    return DependencyService(storage)


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Fixture providing an undo/redo manager."""
    return UndoManager()


@pytest.fixture
def scheduler(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Fixture providing a scheduler service."""
    return SchedulerService(storage, dep_service)


@pytest.fixture
def risk_analyzer(storage: TaskStorage, dep_service: DependencyService) -> DeadlineRiskAnalyzer:
    """Fixture providing a deadline risk analyzer."""
    return DeadlineRiskAnalyzer(storage, dep_service)


@pytest.fixture
def queue_service(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
) -> TaskQueueService:
    """Fixture providing a task queue service."""
    return TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)


def test_full_phase7_lifecycle_and_prerequisite_unblocking(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    risk_analyzer: DeadlineRiskAnalyzer,
    undo_mgr: UndoManager,
) -> None:
    """Verify that completing a prerequisite unlocks dependent tasks in both heap ranking and risk analysis."""
    now = datetime(2026, 10, 30, 9, 0)

    # 1. Create a foundational prerequisite task (Low priority, 30m, due tomorrow)
    t1 = storage.create_task(
        Task(
            title="Setup Database Schema",
            status=TaskStatus.PENDING.value,
            priority=Priority.LOW.value,
            duration=30,
            due_date=now + timedelta(days=1),
        )
    )
    # 2. Create a dependent urgent feature (Urgent priority, 60m, due in 3 hours)
    t2 = storage.create_task(
        Task(
            title="Implement Core API",
            status=TaskStatus.PENDING.value,
            priority=Priority.URGENT.value,
            duration=60,
            due_date=now + timedelta(hours=3),
        )
    )
    # 3. Create an independent high priority task (High priority, 45m, due in 5 hours)
    t3 = storage.create_task(
        Task(
            title="Design Frontend Wireframes",
            status=TaskStatus.PENDING.value,
            priority=Priority.HIGH.value,
            duration=45,
            due_date=now + timedelta(hours=5),
        )
    )

    assert t1.id is not None and t2.id is not None and t3.id is not None

    # Link: T1 -> T2
    dep_service.rebuild()
    dep_service.add_dependency(t1.id, t2.id)

    # --- Initial State Evaluation ---
    risk_summary_1 = risk_analyzer.analyze_all(current_time=now)
    assert risk_summary_1.total_tasks == 3
    assert risk_summary_1.blocked_count == 1  # T2 is blocked
    # T2 is At Risk because it is blocked by T1
    t2_assessment = [a for a in risk_summary_1.assessments if a.task.id == t2.id][0]
    assert t2_assessment.category == RiskCategory.AT_RISK
    assert t2_assessment.is_blocked is True

    # Scheduler recommendations:
    # T2 is blocked! Only T3 (High) and T1 (Low) are eligible.
    # Min-Heap ranking must recommend T3 first, then T1.
    schedule_1 = scheduler.get_smart_schedule()
    assert schedule_1.is_valid is True
    assert schedule_1.eligible_count == 2
    assert schedule_1.blocked_count == 1
    assert schedule_1.recommended_task is not None
    assert schedule_1.recommended_task.id == t3.id
    assert [r.task.id for r in schedule_1.ranked_tasks] == [t3.id, t1.id]

    # --- Step 2: Complete the Prerequisite Task (T1) ---
    t1.status = TaskStatus.COMPLETED.value
    storage.update_task(t1)
    dep_service.rebuild()

    # --- Post-Completion Evaluation ---
    risk_summary_2 = risk_analyzer.analyze_all(current_time=now)
    assert risk_summary_2.completed_count == 1
    assert risk_summary_2.blocked_count == 0  # No tasks blocked anymore!

    t2_assessment_post = [a for a in risk_summary_2.assessments if a.task.id == t2.id][0]
    assert t2_assessment_post.is_blocked is False
    assert t2_assessment_post.category == RiskCategory.SAFE

    # Smart Scheduler must now recommend T2 (Urgent priority) as #1!
    schedule_2 = scheduler.get_smart_schedule()
    assert schedule_2.is_valid is True
    assert schedule_2.eligible_count == 2  # T2 and T3 (T1 is completed)
    assert schedule_2.recommended_task is not None
    assert schedule_2.recommended_task.id == t2.id
    assert [r.task.id for r in schedule_2.ranked_tasks] == [t2.id, t3.id]


def test_undo_redo_interoperability_with_scheduling_and_risk(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    risk_analyzer: DeadlineRiskAnalyzer,
    undo_mgr: UndoManager,
) -> None:
    """Verify that undoing a task status change properly updates smart scheduling and risk status."""
    now = datetime(2026, 10, 30, 10, 0)
    prereq = storage.create_task(
        Task(title="Prereq Task", status=TaskStatus.PENDING.value, priority=Priority.MEDIUM.value, duration=30)
    )
    dep = storage.create_task(
        Task(title="Dependent Task", status=TaskStatus.PENDING.value, priority=Priority.URGENT.value, duration=30)
    )
    assert prereq.id is not None and dep.id is not None
    dep_service.rebuild()
    dep_service.add_dependency(prereq.id, dep.id)

    # Complete prereq with undo registration
    old_prereq_state = copy.copy(prereq)
    prereq.status = TaskStatus.COMPLETED.value
    storage.update_task(prereq)
    undo_mgr.record_action(
        action_type=ActionType.EDIT,
        task_id=prereq.id,
        before_state=old_prereq_state,
        after_state=copy.copy(prereq),
        summary=f"Complete '{prereq.title}'",
    )

    # With prereq completed, dep is eligible and recommended
    res_after_complete = scheduler.get_smart_schedule()
    assert res_after_complete.recommended_task is not None
    assert res_after_complete.recommended_task.id == dep.id

    # Now UNDO the completion
    assert undo_mgr.can_undo() is True
    undo_mgr.undo(storage)
    dep_service.rebuild()

    # Dep must be blocked again!
    res_after_undo = scheduler.get_smart_schedule()
    assert res_after_undo.recommended_task is not None
    assert res_after_undo.recommended_task.id == prereq.id  # Prereq is eligible, dep is blocked
    assert res_after_undo.blocked_count == 1

    risk_after_undo = risk_analyzer.analyze_task(dep, current_time=now)
    assert risk_after_undo.is_blocked is True
    assert risk_after_undo.category == RiskCategory.AT_RISK

    # REDO the completion
    assert undo_mgr.can_redo() is True
    undo_mgr.redo(storage)
    dep_service.rebuild()

    res_after_redo = scheduler.get_smart_schedule()
    assert res_after_redo.recommended_task is not None
    assert res_after_redo.recommended_task.id == dep.id
    assert res_after_redo.blocked_count == 0


def test_coexistence_of_fifo_queue_and_heap_scheduler(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    queue_service: TaskQueueService,
) -> None:
    """Verify that the FIFO execution queue remains intact and does not interfere with the Heap PriorityQueue."""
    # Create 3 tasks in order: T1 (Low), T2 (Medium), T3 (Urgent)
    t1 = storage.create_task(Task(title="First In, Low", priority=Priority.LOW.value, duration=15))
    t2 = storage.create_task(Task(title="Second In, Medium", priority=Priority.MEDIUM.value, duration=15))
    t3 = storage.create_task(Task(title="Third In, Urgent", priority=Priority.URGENT.value, duration=15))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    dep_service.rebuild()
    queue_service.refresh()

    # FIFO Queue preserves arrival order [T1, T2, T3]
    queue_list = queue_service.get_queue_tasks()
    assert [t.id for t in queue_list] == [t1.id, t2.id, t3.id]

    # Smart Scheduler ranks by priority [T3, T2, T1]
    schedule = scheduler.get_smart_schedule()
    assert [r.task.id for r in schedule.ranked_tasks] == [t3.id, t2.id, t1.id]

    # Dispatching from FIFO queue does not alter Heap logic
    dispatched = queue_service.process_next_task()
    assert dispatched is not None
    assert dispatched.id == t1.id  # FIFO correctly gave T1
    assert dispatched.status == TaskStatus.IN_PROGRESS.value

    # Smart Scheduler now excludes T1 (in progress) and ranks [T3, T2]
    schedule_after_dispatch = scheduler.get_smart_schedule()
    assert [r.task.id for r in schedule_after_dispatch.ranked_tasks] == [t3.id, t2.id]
    assert schedule_after_dispatch.in_progress_count == 1
