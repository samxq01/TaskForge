"""TaskForge — Intelligent Task Scheduling and Dependency Management System.

Entrypoint for Streamlit web application.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import CriticalPathService
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import DeadlineRiskAnalyzer
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.services.what_if_simulator import WhatIfSimulatorService
from taskforge.storage import TaskStorage
from taskforge.ui.dashboard import render_dashboard
from taskforge.ui.dependency_view import render_dependency_view
from taskforge.ui.dsa_labs import render_dsa_performance_lab
from taskforge.ui.history_view import render_history_view
from taskforge.ui.planning_view import render_planning_view
from taskforge.ui.scheduling_view import render_scheduling_view
from taskforge.ui.structure_evaluation_view import render_structure_evaluation_view
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


def get_hash_index_service(storage: TaskStorage) -> TaskHashIndexService:
    """Initialize or retrieve TaskHashIndexService singleton (CO2)."""
    if "hash_index" not in st.session_state:
        st.session_state.hash_index = TaskHashIndexService(storage)
    return st.session_state.hash_index


def get_risk_analyzer_service(storage: TaskStorage, dep_service: DependencyService) -> DeadlineRiskAnalyzer:
    """Initialize or retrieve DeadlineRiskAnalyzer singleton (CO1 + CO5)."""
    if "risk_analyzer" not in st.session_state:
        st.session_state.risk_analyzer = DeadlineRiskAnalyzer(storage, dep_service)
    return st.session_state.risk_analyzer


def get_critical_path_service(storage: TaskStorage, dep_service: DependencyService) -> CriticalPathService:
    """Initialize or retrieve CriticalPathService singleton (CO5)."""
    if "cp_service" not in st.session_state:
        st.session_state.cp_service = CriticalPathService(storage, dep_service)
    return st.session_state.cp_service


def get_what_if_simulator_service(storage: TaskStorage, dep_service: DependencyService) -> WhatIfSimulatorService:
    """Initialize or retrieve WhatIfSimulatorService singleton (CO5)."""
    if "what_if_simulator" not in st.session_state:
        st.session_state.what_if_simulator = WhatIfSimulatorService(storage, dep_service)
    return st.session_state.what_if_simulator


def load_sample_tasks(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
    index_service: TaskIndexService,
    dep_service: DependencyService,
    hash_index: TaskHashIndexService,
) -> bool:
    """Seed initial sample tasks and realistic dependencies for demonstration and viva testing.
    
    Returns True if sample tasks were newly seeded, False if already loaded.
    """
    existing_tasks = storage.list_tasks()
    existing_titles = {t.title for t in existing_tasks}
    if "Setup Database Schema & Models" in existing_titles and "Construct BST Deadline Index" in existing_titles:
        return False

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
    hash_index.rebuild_index()
    return True


def render_sidebar(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
    index_service: TaskIndexService,
    dep_service: DependencyService,
    hash_index: TaskHashIndexService,
) -> str:
    """Render the sidebar with navigation, phase status, and demonstration tools."""
    with st.sidebar:
        st.title("⚡ TaskForge")
        st.caption("College DSA Micro-Project • CO1, CO2, CO3, CO4, CO5 Active")

        st.markdown("### 📌 Navigation")
        view_choice = st.radio(
            "Select Module",
            options=[
                "📋 Task Dashboard & Registry",
                "🔄 Task Processing & History (CO1)",
                "🧠 Smart Scheduling & Deadline Risks (CO1 + CO5)",
                "🗺️ Critical Path & What-If Planning (CO5)",
                "🧮 Data Structure Evaluation (CO2)",
                "🔬 DSA Performance Lab (CO3)",
                "🌲 BST Task Index (CO4)",
                "🔗 Dependency Map (CO5)",
            ],
            index=0,
            help="Navigate across all Course Outcome modules (CO1–CO5).",
        )

        st.markdown("---")
        st.markdown("### 🗺️ Project Roadmap")
        st.markdown(
            """
- 🟢 **Phase 01:** Foundation & Tasks *(Complete)*
- 🟢 **Phase 02:** Stack, Queue & Undo/Redo (CO1) *(Complete)*
- 🟢 **Phase 03:** Searching & Sorting Lab (CO3) *(Complete)*
- 🟢 **Phase 04:** BST Deadline Index (CO4) *(Complete)*
- 🟢 **Phase 05:** Dependency Graph & Visual Map (CO5) *(Complete)*
- 🟢 **Phase 06:** Hash Table & Storage Lab (CO2) *(Complete)*
- 🟢 **Phase 07:** Smart Auto-Scheduler & Risk Analyzer (CO1 + CO5) *(Complete)*
- 🟢 **Phase 08:** Critical Path & What-If Planning (CO5) *(Complete)*
- 🟢 **Phase 09:** Final Integration & CO Validation *(Complete)*
            """
        )

        st.markdown("---")
        st.markdown("### 🛠️ Demonstration Tools")
        if st.button("🌱 Load Sample Tasks", use_container_width=True):
            loaded = load_sample_tasks(storage, undo_manager, queue_service, index_service, dep_service, hash_index)
            if loaded:
                st.success("Sample tasks, dependencies & hash index loaded!")
            else:
                st.info("Sample demonstration tasks are already present in the database.")
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
                        hash_index.rebuild_index()
                        st.session_state.confirm_clear_all = False
                        st.success("All tasks, dependencies, queue, BST, and Hash index cleared.")
                        st.rerun()
                with col_n:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_clear_all = False
                        st.rerun()

        st.markdown("---")
        st.caption("TaskForge v1.0.0 • Micro-Project (CO1–CO5 Complete)")

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
    risk_analyzer = get_risk_analyzer_service(storage, dep_service)
    cp_service = get_critical_path_service(storage, dep_service)
    what_if_simulator = get_what_if_simulator_service(storage, dep_service)
    queue_service = get_queue_service(storage, undo_manager, dep_service)
    index_service = get_index_service(storage)
    hash_index = get_hash_index_service(storage)

    current_view = render_sidebar(
        storage=storage,
        undo_manager=undo_manager,
        queue_service=queue_service,
        index_service=index_service,
        dep_service=dep_service,
        hash_index=hash_index,
    )

    st.title("⚡ TaskForge — Task Management & Scheduling System")

    if current_view == "📋 Task Dashboard & Registry":
        st.markdown(
            "Manage tasks with persistent SQLite storage, real-time metrics, custom sorting, and instant **Undo/Redo**."
        )
        render_dashboard(storage, undo_manager=undo_manager, queue_service=queue_service)
    elif current_view == "🔄 Task Processing & History (CO1)":
        render_history_view(storage, undo_manager, queue_service)
    elif current_view == "🧠 Smart Scheduling & Deadline Risks (CO1 + CO5)":
        render_scheduling_view(storage, scheduler_service, risk_analyzer, queue_service)
    elif current_view == "🗺️ Critical Path & What-If Planning (CO5)":
        render_planning_view(storage, cp_service, what_if_simulator)
    elif current_view == "🧮 Data Structure Evaluation (CO2)":
        render_structure_evaluation_view(storage, hash_index)
    elif current_view == "🔬 DSA Performance Lab (CO3)":
        render_dsa_performance_lab()
    elif current_view == "🌲 BST Task Index (CO4)":
        render_tree_view(storage, index_service)
    elif current_view == "🔗 Dependency Map (CO5)":
        render_dependency_view(storage, dep_service, scheduler_service, queue_service)


if __name__ == "__main__":
    main()
