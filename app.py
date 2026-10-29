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
from taskforge.ui.theme import inject_anthracite_theme, render_brand_lockup
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
        render_brand_lockup()

        st.markdown(
            '<div class="pt-eyebrow" style="margin-top: 0.5rem;">Navigation Directory</div>',
            unsafe_allow_html=True,
        )

        nav_options = [
            "📊 Overview",
            "📋 Tasks",
            "🧠 Schedule & Risks",
            "🔗 Dependencies",
            "⏱️ Project Timeline",
            "🔬 Technical Labs: Algorithm Benchmarks",
            "🧮 Technical Labs: Structure Evaluation",
            "🌲 Technical Labs: BST Deadline Index",
        ]

        if "nav_view" not in st.session_state or st.session_state.nav_view not in nav_options:
            st.session_state.nav_view = nav_options[0]

        selected_idx = nav_options.index(st.session_state.nav_view)

        view_choice = st.radio(
            "Select Module",
            options=nav_options,
            index=selected_idx,
            key="sidebar_nav_choice",
            label_visibility="collapsed",
            help="Navigate across all Course Outcome modules (CO1–CO5).",
        )
        st.session_state.nav_view = view_choice

        st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            '<div class="pt-eyebrow">Academic Roadmap</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div style="font-size: 0.82rem; color: #475569; line-height: 1.6; font-family: 'JetBrains Mono', monospace;">
<div><span style="color: #2563EB;">●</span> CO1 Linear Structures &bull; Verified</div>
<div><span style="color: #2563EB;">●</span> CO2 Hash Storage &bull; Verified</div>
<div><span style="color: #2563EB;">●</span> CO3 Search & Sort Lab &bull; Verified</div>
<div><span style="color: #2563EB;">●</span> CO4 BST Task Index &bull; Verified</div>
<div><span style="color: #2563EB;">●</span> CO5 Graph & Critical Path &bull; Verified</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            '<div class="pt-eyebrow">Demonstration Suite</div>',
            unsafe_allow_html=True,
        )
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

        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase;">
                TASKFORGE<span style="color: #2563EB;">•</span> v2.0<br>
                POTADOT PRODUCT EXPERIENCE
            </div>
            """,
            unsafe_allow_html=True,
        )

    return view_choice


def main() -> None:
    """Main application routine."""
    st.set_page_config(
        page_title="TaskForge — Intelligent Task Scheduling System",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_anthracite_theme()

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

    if current_view == "📊 Overview":
        render_dashboard(
            storage,
            undo_manager=undo_manager,
            queue_service=queue_service,
            scheduler_service=scheduler_service,
            risk_analyzer=risk_analyzer,
            dep_service=dep_service,
            index_service=index_service,
            hash_index=hash_index,
            cp_service=cp_service,
        )
    elif current_view == "📋 Tasks":
        render_history_view(storage, undo_manager, queue_service)
    elif current_view == "🧠 Schedule & Risks":
        render_scheduling_view(storage, scheduler_service, risk_analyzer, queue_service)
    elif current_view == "🔗 Dependencies":
        render_dependency_view(storage, dep_service, scheduler_service, queue_service)
    elif current_view == "⏱️ Project Timeline":
        render_planning_view(storage, cp_service, what_if_simulator)
    elif current_view == "🔬 Technical Labs: Algorithm Benchmarks":
        render_dsa_performance_lab()
    elif current_view == "🧮 Technical Labs: Structure Evaluation":
        render_structure_evaluation_view(storage, hash_index)
    elif current_view == "🌲 Technical Labs: BST Deadline Index":
        render_tree_view(storage, index_service)


if __name__ == "__main__":
    main()
