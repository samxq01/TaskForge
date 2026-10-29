"""TaskForge — Intelligent Task Scheduling and Dependency Management System.

Entrypoint for Streamlit web application.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage
from taskforge.ui.dashboard import render_dashboard
from taskforge.ui.history_view import render_history_view


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


def get_queue_service(storage: TaskStorage, undo_manager: UndoManager) -> TaskQueueService:
    """Initialize or retrieve TaskQueueService singleton."""
    if "queue_service" not in st.session_state:
        st.session_state.queue_service = TaskQueueService(storage, undo_manager)
    return st.session_state.queue_service


def load_sample_tasks(
    storage: TaskStorage, undo_manager: UndoManager, queue_service: TaskQueueService
) -> None:
    """Seed initial sample tasks for demonstration and viva testing."""
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

    for task in sample_data:
        created = storage.create_task(task)
        assert created.id is not None
        undo_manager.record_action(
            action_type=ActionType.CREATE,
            task_id=created.id,
            after_state=created,
        )

    queue_service.refresh()


def render_sidebar(
    storage: TaskStorage, undo_manager: UndoManager, queue_service: TaskQueueService
) -> str:
    """Render the sidebar with navigation, phase status, and demonstration tools."""
    with st.sidebar:
        st.title("⚡ TaskForge")
        st.caption("College DSA Micro-Project • CO1 Active")

        st.markdown("### 📌 Navigation")
        view_choice = st.radio(
            "Select Module",
            options=[
                "📋 Task Dashboard & Registry",
                "🔄 Task Processing & History (CO1)",
            ],
            index=0,
            help="Navigate between Phase 01 Dashboard and Phase 02 CO1 Processing & History.",
        )

        st.markdown("---")
        st.markdown("### 🗺️ Project Roadmap")
        st.markdown(
            """
- 🟢 **Phase 01:** Foundation & Tasks *(Complete)*
- 🟢 **Phase 02:** Stack, Queue & Undo/Redo (CO1) *(Active)*
- 🔒 **Phase 03:** Searching & Sorting Lab (CO3)
- 🔒 **Phase 04:** BST Deadline Index (CO4)
- 🔒 **Phase 05:** Dependency Graph & Visual Map (CO5)
- 🔒 **Phase 06:** Hash Table & Storage Lab (CO2)
- 🔒 **Phase 07:** Smart Auto-Scheduler
- 🔒 **Phase 08:** Critical Path & Simulator
- 🔒 **Phase 09:** Final Polish & Integration
            """
        )

        st.markdown("---")
        st.markdown("### 🛠️ Demonstration Tools")
        if st.button("🌱 Load Sample Tasks", use_container_width=True):
            load_sample_tasks(storage, undo_manager, queue_service)
            st.success("Sample tasks loaded & recorded in history!")
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
                st.warning("Erase all stored tasks?")
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button("Yes, Clear", type="primary", use_container_width=True):
                        for t in storage.list_tasks():
                            assert t.id is not None
                            storage.delete_task(t.id)
                        undo_manager.clear()
                        queue_service.refresh()
                        st.session_state.confirm_clear_all = False
                        st.success("All tasks and history cleared.")
                        st.rerun()
                with col_n:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_clear_all = False
                        st.rerun()

        st.markdown("---")
        st.caption("TaskForge v0.2.0 • Phase 02 (CO1)")

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
    queue_service = get_queue_service(storage, undo_manager)

    current_view = render_sidebar(storage, undo_manager, queue_service)

    st.title("⚡ TaskForge — Task Management & Scheduling System")

    if current_view == "📋 Task Dashboard & Registry":
        st.markdown(
            "Manage tasks with persistent SQLite storage, real-time metrics, and instant **Undo/Redo** capabilities."
        )
        render_dashboard(storage, undo_manager=undo_manager, queue_service=queue_service)
    else:
        render_history_view(storage, undo_manager, queue_service)


if __name__ == "__main__":
    main()
