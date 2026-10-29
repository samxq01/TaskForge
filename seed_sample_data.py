"""Seed TaskForge SQLite database with rich sample tasks, deadlines, and dependencies."""

from datetime import datetime, timedelta
from taskforge.models import Priority, Task, TaskStatus
from taskforge.storage import TaskStorage
from taskforge.services.dependency_service import DependencyService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.undo_manager import UndoManager


def seed_database(db_path: str = "taskforge.db") -> None:
    storage = TaskStorage(db_path)
    undo_mgr = UndoManager()
    dep_service = DependencyService(storage)
    queue_service = TaskQueueService(storage, undo_mgr, dep_service)
    index_service = TaskIndexService(storage)
    hash_index = TaskHashIndexService(storage)

    # Clear existing tasks to ensure clean demo state
    for t in storage.list_tasks():
        if t.id is not None:
            storage.delete_task(t.id)

    undo_mgr.clear()
    dep_service.rebuild()

    now = datetime.now()

    sample_tasks = [
        Task(
            title="Setup Database Architecture & Schema",
            description="Initialize SQLite tables, indexed columns, and typed models.",
            priority=Priority.URGENT.value,
            duration=45,
            status=TaskStatus.COMPLETED.value,
            due_date=now - timedelta(days=1),
        ),
        Task(
            title="Implement User Authentication & Session Security",
            description="Build secure session tokens, password hashing, and role checks.",
            priority=Priority.HIGH.value,
            duration=90,
            status=TaskStatus.IN_PROGRESS.value,
            due_date=now + timedelta(days=1),
        ),
        Task(
            title="Build Core Task Scheduler Engine",
            description="Implement priority ranking and prerequisite feasibility checks.",
            priority=Priority.URGENT.value,
            duration=60,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(hours=14),
        ),
        Task(
            title="Construct Dependency Graph & Cycle Validator",
            description="Graph adjacency lists with Kahn's cycle prevention and topological ordering.",
            priority=Priority.HIGH.value,
            duration=120,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(days=2),
        ),
        Task(
            title="Interactive Dashboard & Critical Path Timeline",
            description="Build timeline Gantt breakdown and in-memory What-If simulation engine.",
            priority=Priority.MEDIUM.value,
            duration=150,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(days=4),
        ),
        Task(
            title="System Documentation & Viva Preparation",
            description="Finalize architecture diagrams, complexity tables, and demo scripts.",
            priority=Priority.LOW.value,
            duration=45,
            status=TaskStatus.PENDING.value,
            due_date=None,  # Unscheduled task
        ),
        Task(
            title="Audit Legacy Export Pipeline",
            description="Review deprecated data serialization formats and log output.",
            priority=Priority.URGENT.value,
            duration=30,
            status=TaskStatus.PENDING.value,
            due_date=now - timedelta(hours=3),  # Overdue task
        ),
    ]

    created_tasks = []
    for t in sample_tasks:
        created = storage.create_task(t)
        created_tasks.append(created)
        print(f"Created Task #{created.id}: {created.title} [{created.status}]")

    # Establish realistic dependencies:
    # Task 1 (DB) -> Task 2 (Auth) and Task 3 (Scheduler)
    # Task 2 (Auth) -> Task 4 (Graph)
    # Task 3 (Scheduler) & Task 4 (Graph) -> Task 5 (Timeline)
    # Task 5 (Timeline) -> Task 6 (Docs)
    t1, t2, t3, t4, t5, t6, t7 = created_tasks
    dep_service.rebuild()

    dep_service.add_dependency(t1.id, t2.id)
    dep_service.add_dependency(t1.id, t3.id)
    dep_service.add_dependency(t2.id, t4.id)
    dep_service.add_dependency(t3.id, t5.id)
    dep_service.add_dependency(t4.id, t5.id)
    dep_service.add_dependency(t5.id, t6.id)

    print("Dependencies established:")
    print(f"  #{t2.id} depends on #{t1.id} (Prerequisite met)")
    print(f"  #{t3.id} depends on #{t1.id} (Prerequisite met -> READY to dispatch)")
    print(f"  #{t4.id} depends on #{t2.id} (BLOCKED by in-progress #{t2.id})")
    print(f"  #{t5.id} depends on #{t3.id} & #{t4.id} (BLOCKED)")
    print(f"  #{t6.id} depends on #{t5.id} (BLOCKED)")

    # Rebuild all indices
    dep_service.rebuild()
    queue_service.refresh()
    index_service.rebuild()
    hash_index.rebuild_index()

    print("\nSample database seeded successfully!")
    print(f"Total tasks: {len(created_tasks)}")
    print(f"Database: {db_path}")


if __name__ == "__main__":
    seed_database()

