"""TaskForge — Intelligent Task Scheduling and Dependency Management System.

Entrypoint for Streamlit web application.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage
from taskforge.ui.dashboard import render_dashboard
from taskforge.ui.dependency_view import render_dependency_view
from taskforge.ui.dsa_labs import render_dsa_performance_lab
from taskforge.ui.history_view import render_history_view
from taskforge.ui.tree_view import render_tree_view


def get_storage() -> TaskStorage:
    """Initialize or retrieve persistent TaskStorage singleton."""
    if "storage" not in st.session_state:
        st.session_state.storage = TaskStorage("taskforge.db")
    return st.session_state.storage


def get_undo_manager() -> UndoManager:
    """Initialize or retrieve session-local UndoManager singleton."""
    if "undo_manager" not in st.session_state:
        st.session_state.undo_manager = UndoManager()
    return st.session_state.undo_manager


def get_dependency_service(storage: TaskStorage) -> DependencyService:
    """Initialize or retrieve DependencyService singleton."""
    if "dep_service" not in st.session_state:
        st.session_state.dep_service = DependencyService(storage)
    return st.session_state.dep_service


def get_scheduler_service(storage: TaskStorage, dep_service: DependencyService) -> SchedulerService:
    """Initialize or retrieve SchedulerService singleton."""
    if "scheduler_service" not in st.session_state:
        st.session_state.scheduler_service = SchedulerService(storage, dep_service)
    return st.session_state.scheduler_service


def get_queue_service(
    storage: TaskStorage,
    undo_manager: UndoManager,
    dep_service: DependencyService,
) -> TaskQueueService:
    """Initialize or retrieve TaskQueueService singleton."""
    if "queue_service" not in st.session_state:
        st.session_state.queue_service = TaskQueueService(
            storage=storage,
            undo_manager=undo_manager,
            dependency_service=dep_service,
        )
    return st.session_state.queue_service


def get_index_service(storage: TaskStorage) -> TaskIndexService:
    """Initialize or retrieve TaskIndexService singleton."""
    if "index_service" not in st.session_state:
        st.session_state.index_service = TaskIndexService(storage)
    return st.session_state.index_service


def load_sample_tasks(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
    index_service: TaskIndexService,
    dep_service: DependencyService,
) -> None:
    """Seed initial sample tasks and realistic dependencies for demonstration and viva testing."""
    now = datetime.now()
    sample_data = [
        Task(
            title="Setup Database Schema & Models",
            description="Initialize SQLite schema and typed dataclass models",
            priority=Priority.URGENT.value,
            duration=45,
            status=TaskStatus.COMPLETED.value,
            due_date=now - timedelta(hours=2),
        ),
        Task(
            title="Implement Undo/Redo Stacks",
            description="CO1: Linear data structures with custom Stack implementation",
            priority=Priority.HIGH.value,
            duration=90,
            status=TaskStatus.IN_PROGRESS.value,
            due_date=now + timedelta(days=1),
        ),
        Task(
            title="Build Searching & Sorting Lab",
            description="CO3: Benchmark linear vs binary search and insertion vs merge sort",
            priority=Priority.HIGH.value,
            duration=120,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(days=2),
        ),
        Task(
            title="Construct BST Deadline Index",
            description="CO4: Tree structure for logarithmic deadline search and inorder traversal",
            priority=Priority.MEDIUM.value,
            duration=60,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(days=3),
        ),
        Task(
            title="Implement Dependency Graph & Topological Sort",
            description="CO5: Graph adjacency list, cycle detection, and BFS/DFS traversal",
            priority=Priority.URGENT.value,
            duration=150,
            status=TaskStatus.PENDING.value,
            due_date=now + timedelta(days=4),
        ),
        Task(
            title="Draft Viva Presentation & Demo Script",
            description="Prepare explanation slides for Course Outcomes and algorithm complexity",
            priority=Priority.LOW.value,
            duration=30,
            status=TaskStatus.PENDING.value,
            due_date=None,  # Intentionally no deadline
        ),
    ]

    created_ids: list[int] = []
    for task in sample_data:
        created = storage.create_task(task)
        assert created.id is not None
        created_ids.append(created.id)
        undo_manager.record_action(
            action_type=ActionType.CREATE,
            task_id=created.id,
            after_state=created,
        )

    # Establish realistic dependency relationships:
    # Task 1 (DB) is prerequisite for Task 2 (Undo/Redo) and Task 3 (Searching/Sorting)
    # Task 2 is prerequisite for Task 4 (BST)
    # Task 3 & Task 4 are prerequisites for Task 5 (Dependency Graph)
    # Task 5 is prerequisite for Task 6 (Viva Presentation)
    if len(created_ids) >= 6:
        dep_service.rebuild()
        try:
            dep_service.add_dependency(created_ids[0], created_ids[1])
            dep_service.add_dependency(created_ids[0], created_ids[2])
            dep_service.add_dependency(created_ids[1], created_ids[3])
            dep_service.add_dependency(created_ids[2], created_ids[4])
            dep_service.add_dependency(created_ids[3], created_ids[4])
            dep_service.add_dependency(created_ids[4], created_ids[5])
        except Exception:
            pass

    dep_service.rebuild()
    queue_service.refresh()
    index_service.rebuild()


def render_sidebar(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
    index_service: TaskIndexService,
    dep_service: DependencyService,
) -> str:
    """Render the sidebar with navigation, phase status, and demonstration tools."""
    with st.sidebar:
        st.title("⚡ TaskForge")
        st.caption("College DSA Micro-Project • CO1, CO3, CO4, CO5 Active")

        st.markdown("### 📌 Navigation")
        view_choice = st.radio(
            "Select Module",
            options=[
                "📋 Task Dashboard & Registry",
                "🔄 Task Processing & History (CO1)",
                "🔬 DSA Performance Lab (CO3)",
                "🌲 BST Task Index (CO4)",
                "🔗 Dependency Map (CO5)",
            ],
            index=0,
            help="Navigate across Phase 01 (Dashboard), Phase 02 (CO1), Phase 03 (CO3), Phase 04 (CO4), and Phase 05 (CO5).",
        )

        st.markdown("---")
        st.markdown("### 🗺️ Project Roadmap")
        st.markdown(
            """
- 🟢 **Phase 01:** Foundation & Tasks *(Complete)*
- 🟢 **Phase 02:** Stack, Queue & Undo/Redo (CO1) *(Complete)*
- 🟢 **Phase 03:** Searching & Sorting Lab (CO3) *(Complete)*
- 🟢 **Phase 04:** BST Deadline Index (CO4) *(Complete)*
- 🟢 **Phase 05:** Dependency Graph & Visual Map (CO5) *(Active)*
- 🔒 **Phase 06:** Hash Table & Storage Lab (CO2)
- 🔒 **Phase 07:** Smart Auto-Scheduler
- 🔒 **Phase 08:** Critical Path & Simulator
- 🔒 **Phase 09:** Final Polish & Integration
            """
        )

        st.markdown("---")
        st.markdown("### 🛠️ Demonstration Tools")
        if st.button("🌱 Load Sample Tasks", use_container_width=True):
            load_sample_tasks(storage, undo_manager, queue_service, index_service, dep_service)
            st.success("Sample tasks & graph dependencies loaded!")
            st.rerun()

        counts = storage.count_tasks()
        if counts["total"] > 0:
            if "confirm_clear_all" not in st.session_state:
                st.session_state.confirm_clear_all = False

            if not st.session_state.confirm_clear_all:
                if st.button("🗑️ Clear All Tasks", use_container_width=True):
                    st.session_state.confirm_clear_all = True
                    st.rerun()
            else:
                st.warning("Erase all stored tasks and dependencies?")
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button("Yes, Clear", type="primary", use_container_width=True):
                        for t in storage.list_tasks():
                            assert t.id is not None
                            storage.delete_task(t.id)
                        undo_manager.clear()
                        dep_service.rebuild()
                        queue_service.refresh()
                        index_service.rebuild()
                        st.session_state.confirm_clear_all = False
                        st.success("All tasks, graph dependencies, queue, and BST index cleared.")
                        st.rerun()
                with col_n:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_clear_all = False
                        st.rerun()

        st.markdown("---")
        st.caption("TaskForge v0.5.0 • Phase 05 (CO5)")

    return view_choice


def main() -> None:
    """Main application routine."""
    st.set_page_config(
        page_title="TaskForge — Intelligent Task Scheduling System",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    storage = get_storage()
    undo_manager = get_undo_manager()
    dep_service = get_dependency_service(storage)
    scheduler_service = get_scheduler_service(storage, dep_service)
    queue_service = get_queue_service(storage, undo_manager, dep_service)
    index_service = get_index_service(storage)

    current_view = render_sidebar(storage, undo_manager, queue_service, index_service, dep_service)

    st.title("⚡ TaskForge — Task Management & Scheduling System")

    if current_view == "📋 Task Dashboard & Registry":
        st.markdown(
            "Manage tasks with persistent SQLite storage, real-time metrics, custom sorting, and instant **Undo/Redo**."
        )
        render_dashboard(storage, undo_manager=undo_manager, queue_service=queue_service)
    elif current_view == "🔄 Task Processing & History (CO1)":
        render_history_view(storage, undo_manager, queue_service)
    elif current_view == "🔬 DSA Performance Lab (CO3)":
        render_dsa_performance_lab()
    elif current_view == "🌲 BST Task Index (CO4)":
        render_tree_view(storage, index_service)
    elif current_view == "🔗 Dependency Map (CO5)":
        render_dependency_view(storage, dep_service, scheduler_service, queue_service)


if __name__ == "__main__":
    main()
