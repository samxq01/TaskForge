"""End-to-end integration tests for Phase 06: Hash Table & Data Structure Evaluation (CO2)."""

from pathlib import Path
import pytest

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.structure_evaluation import (
    StructureEvaluationService,
    generate_evaluation_dataset,
)
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage


@pytest.fixture
def storage(tmp_path: Path) -> TaskStorage:
    """Provide an isolated TaskStorage instance."""
    return TaskStorage(tmp_path / "test_phase6_integration.db")


@pytest.fixture
def undo_mgr() -> UndoManager:
    """Provide an UndoManager instance."""
    return UndoManager()


@pytest.fixture
def dep_service(storage: TaskStorage) -> DependencyService:
    """Provide a DependencyService instance."""
    return DependencyService(storage)


@pytest.fixture
def queue_service(storage: TaskStorage, undo_mgr: UndoManager, dep_service: DependencyService) -> TaskQueueService:
    """Provide a TaskQueueService instance."""
    return TaskQueueService(storage, undo_manager=undo_mgr, dependency_service=dep_service)


@pytest.fixture
def bst_index(storage: TaskStorage) -> TaskIndexService:
    """Provide Phase 04 BST deadline index service."""
    return TaskIndexService(storage)


@pytest.fixture
def hash_index(storage: TaskStorage) -> TaskHashIndexService:
    """Provide Phase 06 Task-ID hash index service."""
    return TaskHashIndexService(storage)


def test_full_phase6_task_hash_index_and_regression_workflow(
    storage: TaskStorage,
    undo_mgr: UndoManager,
    dep_service: DependencyService,
    queue_service: TaskQueueService,
    bst_index: TaskIndexService,
    hash_index: TaskHashIndexService,
) -> None:
    """Verify that custom hash indexing integrates seamlessly with earlier phase features."""
    # 1. Create a set of tasks
    t1 = storage.create_task(Task(title="Architecture Spec", priority=Priority.URGENT.value, duration=45))
    t2 = storage.create_task(Task(title="Implement HashTable", priority=Priority.HIGH.value, duration=60))
    t3 = storage.create_task(Task(title="Benchmark Lab", priority=Priority.MEDIUM.value, duration=90))
    assert t1.id is not None and t2.id is not None and t3.id is not None

    # Track creation in undo manager
    for t in [t1, t2, t3]:
        undo_mgr.record_action(ActionType.CREATE, task_id=t.id, after_state=t)

    # Rebuild all indices
    hash_index.rebuild_index()
    bst_index.rebuild()
    dep_service.rebuild()
    queue_service.refresh()

    # 2. Verify Hash Index lookup
    assert hash_index.size() == 3
    found_t2 = hash_index.get_task(t2.id)
    assert found_t2 is not None
    assert found_t2.title == "Implement HashTable"

    # 3. Add graph dependency: t1 -> t2
    dep_service.add_dependency(t1.id, t2.id)
    queue_service.refresh()

    # In queue, t2 is blocked by t1, so only t1 and t3 are queued
    queued_ids = [t.id for t in queue_service.get_queue_tasks()]
    assert t1.id in queued_ids
    assert t3.id in queued_ids
    assert t2.id not in queued_ids

    # 4. Mutate task t2
    t2.title = "Implement HashTable & Chaining"
    storage.update_task(t2)
    hash_index.rebuild_index()
    assert hash_index.get_task(t2.id).title == "Implement HashTable & Chaining"  # type: ignore

    # 5. Delete task t3
    storage.delete_task(t3.id)
    undo_mgr.record_action(ActionType.DELETE, task_id=t3.id, before_state=t3)
    hash_index.rebuild_index()
    assert hash_index.contains_task(t3.id) is False
    assert hash_index.size() == 2

    # 6. Undo deletion
    undo_mgr.undo(storage)
    hash_index.rebuild_index()
    assert hash_index.contains_task(t3.id) is True
    assert hash_index.size() == 3

    # 7. Run Data Structure Evaluation on synthetic workload
    eval_service = StructureEvaluationService()
    dataset = generate_evaluation_dataset(size=50, seed=77)
    results = eval_service.run_evaluation(dataset, scenario="middle", repetitions=25)
    assert len(results) == 3

    # All three structures must return the identical matched task
    list_res, hash_res, bst_res = results
    assert list_res.result_found == hash_res.result_found == bst_res.result_found is True
    assert list_res.result_task_id == hash_res.result_task_id == bst_res.result_task_id

    # 8. Verify Phase 04 BST deadline index remains completely functional and ordered
    inorder_entries = bst_index.get_inorder_entries()
    assert len(inorder_entries) == 3
    # Verify Phase 05 graph remains intact
    assert dep_service.get_graph().has_edge(t1.id, t2.id) is True
