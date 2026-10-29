"""Comprehensive test suite for TaskForge FastAPI local integration layer."""

from __future__ import annotations

from datetime import datetime, timedelta
import os
import pytest
from starlette.testclient import TestClient

from taskforge.api.dependencies import ServiceContainer, set_service_container
from taskforge.api.main import create_app
from taskforge.models import Priority, Task, TaskStatus


@pytest.fixture
def client(tmp_path):
    """Provide a TestClient connected to an isolated test SQLite database."""
    test_db = str(tmp_path / "test_api.db")
    container = ServiceContainer(test_db)
    set_service_container(container)

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client, container


def test_health_check(client):
    tc, _ = client
    response = tc.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "TaskForge"


def test_empty_overview(client):
    tc, _ = client
    response = tc.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["pending_tasks"] == 0
    assert data["completed_tasks"] == 0
    assert data["can_undo"] is False


def test_task_crud_lifecycle(client):
    tc, container = client

    # 1. Create Task
    create_payload = {
        "title": "Architect API Layer",
        "priority": 3,
        "duration": 45,
        "status": "Pending",
        "description": "Design FastAPI adapter for TaskForge",
    }
    res = tc.post("/api/tasks", json=create_payload)
    assert res.status_code == 201
    task_data = res.json()
    assert task_data["id"] > 0
    assert task_data["title"] == "Architect API Layer"
    task_id = task_data["id"]

    # 2. Get Task
    res_get = tc.get(f"/api/tasks/{task_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == task_id

    # 3. Update Task
    update_payload = {
        "title": "Architect API Layer (Updated)",
        "priority": 4,
        "status": "In Progress",
    }
    res_patch = tc.patch(f"/api/tasks/{task_id}", json=update_payload)
    assert res_patch.status_code == 200
    assert res_patch.json()["title"] == "Architect API Layer (Updated)"
    assert res_patch.json()["priority"] == 4
    assert res_patch.json()["status"] == "In Progress"

    # 4. List Tasks
    res_list = tc.get("/api/tasks?status=In Progress")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 5. Delete Task
    res_del = tc.delete(f"/api/tasks/{task_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # 6. Verify Deletion
    res_after = tc.get(f"/api/tasks/{task_id}")
    assert res_after.status_code == 404


def test_queue_and_undo_redo(client):
    tc, container = client

    # Create two tasks
    t1 = tc.post("/api/tasks", json={"title": "Task 1", "priority": 2}).json()
    t2 = tc.post("/api/tasks", json={"title": "Task 2", "priority": 3}).json()

    # Queue status
    q_res = tc.get("/api/queue")
    assert q_res.status_code == 200
    assert q_res.json()["queue_size"] == 2
    assert q_res.json()["head_task"]["id"] == t1["id"]

    # Process next
    proc_res = tc.post("/api/queue/process-next")
    assert proc_res.status_code == 200
    assert proc_res.json()["success"] is True
    assert proc_res.json()["processed_task"]["id"] == t1["id"]
    assert proc_res.json()["remaining_queue_size"] == 1

    # Undo processing
    undo_res = tc.post("/api/history/undo")
    assert undo_res.status_code == 200
    assert undo_res.json()["success"] is True

    # Redo processing
    redo_res = tc.post("/api/history/redo")
    assert redo_res.status_code == 200
    assert redo_res.json()["success"] is True


def test_dependencies_and_cycle_rejection(client):
    tc, container = client

    # Create 3 tasks
    t1 = tc.post("/api/tasks", json={"title": "Task A"}).json()["id"]
    t2 = tc.post("/api/tasks", json={"title": "Task B"}).json()["id"]
    t3 = tc.post("/api/tasks", json={"title": "Task C"}).json()["id"]

    # Add dependencies: A -> B and B -> C
    res_dep1 = tc.post("/api/dependencies", json={"prerequisite_id": t1, "dependent_id": t2})
    assert res_dep1.status_code == 201

    res_dep2 = tc.post("/api/dependencies", json={"prerequisite_id": t2, "dependent_id": t3})
    assert res_dep2.status_code == 201

    # Attempt circular dependency: C -> A
    res_cycle = tc.post("/api/dependencies", json={"prerequisite_id": t3, "dependent_id": t1})
    assert res_cycle.status_code == 400
    assert "circular" in res_cycle.json()["detail"].lower() or "cycle" in res_cycle.json()["detail"].lower()

    # Get graph
    graph_res = tc.get("/api/dependencies")
    assert graph_res.status_code == 200
    assert graph_res.json()["is_cyclic"] is False
    assert graph_res.json()["topological_order"] == [t1, t2, t3]

    # BFS and DFS
    bfs_res = tc.post("/api/dependencies/bfs", json={"start_task_id": t1})
    assert bfs_res.status_code == 200
    assert bfs_res.json()["visited_sequence"] == [t1, t2, t3]

    # Remove dependency
    del_dep = tc.request("DELETE", "/api/dependencies", json={"prerequisite_id": t1, "dependent_id": t2})
    assert del_dep.status_code == 200


def test_algorithms_benchmarks(client):
    tc, _ = client

    # Search benchmark
    search_res = tc.post("/api/benchmarks/searching", json={"dataset_size": 200, "scenario": "middle"})
    assert search_res.status_code == 200
    s_data = search_res.json()
    assert s_data["dataset_size"] == 200
    assert s_data["linear_comparisons"] > 0
    assert s_data["binary_comparisons"] > 0

    # Sort benchmark
    sort_res = tc.post("/api/benchmarks/sorting", json={"dataset_size": 100, "distribution": "random"})
    assert sort_res.status_code == 200
    sort_data = sort_res.json()
    assert sort_data["dataset_size"] == 100
    assert sort_data["insertion_comparisons"] > 0
    assert sort_data["merge_comparisons"] > 0


def test_tree_and_hash_table(client):
    tc, _ = client

    # Create task with deadline
    now = datetime.now()
    tc.post("/api/tasks", json={"title": "Tree Task", "due_date": (now + timedelta(days=2)).isoformat()})

    # Tree overview
    tree_res = tc.get("/api/tree/overview")
    assert tree_res.status_code == 200
    assert tree_res.json()["total_nodes"] == 1

    # Hash table stats
    hash_stats = tc.get("/api/hash-table/stats")
    assert hash_stats.status_code == 200
    assert hash_stats.json()["size"] == 1

    # Evaluation
    eval_res = tc.post("/api/data-structure-evaluation", json={"dataset_size": 50, "scenario": "hit"})
    assert eval_res.status_code == 200
    assert len(eval_res.json()["results"]) == 3


def test_scheduling_and_critical_path(client):
    tc, _ = client

    t1 = tc.post("/api/tasks", json={"title": "Prep Foundation", "duration": 60, "priority": 3}).json()["id"]
    t2 = tc.post("/api/tasks", json={"title": "Build Structure", "duration": 120, "priority": 4}).json()["id"]

    tc.post("/api/dependencies", json={"prerequisite_id": t1, "dependent_id": t2})

    # Smart scheduling: t1 is eligible, t2 is blocked
    sched_res = tc.get("/api/scheduling/recommendations")
    assert sched_res.status_code == 200
    sched_data = sched_res.json()
    assert sched_data["eligible_count"] == 1
    assert sched_data["blocked_count"] == 1
    assert sched_data["recommendation"]["task"]["id"] == t1

    # Critical path: 60 + 120 = 180 min
    cp_res = tc.get("/api/planning/critical-path")
    assert cp_res.status_code == 200
    cp_data = cp_res.json()
    assert cp_data["total_duration_minutes"] == 180
    assert cp_data["critical_path_ids"] == [t1, t2]

    # What-If Simulation: delay t1 by 30 mins
    what_if_res = tc.post("/api/planning/what-if", json={"task_id": t1, "delay_minutes": 30})
    assert what_if_res.status_code == 200
    wi_data = what_if_res.json()
    assert wi_data["baseline_project_duration"] == 180
    assert wi_data["simulated_project_duration"] == 210
    assert wi_data["project_delay_increase"] == 30
    assert wi_data["is_persistent"] is False

    # Check persistence safety: verify t1 duration in database is still 60
    t1_check = tc.get(f"/api/tasks/{t1}").json()
    assert t1_check["duration"] == 60
