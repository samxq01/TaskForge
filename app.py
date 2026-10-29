"""TaskForge — Intelligent Task Scheduling and Dependency Management System.

Entrypoint for Streamlit web application.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.storage import TaskStorage
from taskforge.ui.dashboard import render_dashboard


def get_storage() -> TaskStorage:
    """Initialize or retrieve persistent TaskStorage singleton."""
    if "storage" not in st.session_state:
        st.session_state.storage = TaskStorage("taskforge.db")
    return st.session_state.storage


def load_sample_tasks(storage: TaskStorage) -> None:
    """Seed initial sample tasks for demonstration and testing."""
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
        storage.create_task(task)


def render_sidebar(storage: TaskStorage) -> None:
    """Render the sidebar with navigation, phase status, and database utilities."""
    with st.sidebar:
        st.title("⚡ TaskForge")
        st.caption("College DSA Micro-Project")

        st.markdown("### 📌 Navigation")
        st.radio(
            "Select Module",
            options=["📋 Task Dashboard (Active)"],
            index=0,
            disabled=True,
            help="Phase 01 enables Task Management. Further modules unlock in subsequent phases.",
        )

        st.markdown("---")
        st.markdown("### 🗺️ Project Roadmap")
        st.markdown(
            """
- 🟢 **Phase 01:** Foundation & Tasks *(Current)*
- 🔒 **Phase 02:** Stack, Queue & Undo/Redo (CO1)
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
            load_sample_tasks(storage)
            st.success("Sample tasks loaded!")
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
                        # Delete all tasks individually to preserve referential safety
                        for t in storage.list_tasks():
                            assert t.id is not None
                            storage.delete_task(t.id)
                        st.session_state.confirm_clear_all = False
                        st.success("All tasks cleared.")
                        st.rerun()
                with col_n:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_clear_all = False
                        st.rerun()

        st.markdown("---")
        st.caption("TaskForge v0.1.0 • Phase 01 Foundation")


def main() -> None:
    """Main application routine."""
    st.set_page_config(
        page_title="TaskForge — Intelligent Task Scheduling System",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    storage = get_storage()
    render_sidebar(storage)

    st.title("⚡ TaskForge — Task Management & Scheduling System")
    st.markdown(
        "A rigorous, real-world task management application powered by **Data Structures and Algorithms (DSA)**."
    )

    render_dashboard(storage)


if __name__ == "__main__":
    main()
