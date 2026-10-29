"""Main dashboard view for task management with custom DSA searching, sorting, and Potadot product showcases."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import streamlit as st

from taskforge.algorithms.searching import binary_search, linear_search
from taskforge.algorithms.sorting import (
    insertion_sort,
    merge_sort,
    task_deadline_key,
    task_id_key,
    task_priority_deadline_key,
    task_priority_key,
)
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import CriticalPathService
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import DeadlineRiskAnalyzer
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage
from taskforge.ui.task_manager import (
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    render_add_task_form,
    render_edit_task_form,
)
from taskforge.ui.theme import (
    render_editorial_hero,
    render_metric_strip,
    render_pill,
    render_section_header,
)


def _format_duration(minutes: int) -> str:
    """Format duration into human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours}h {rem}m" if rem else f"{hours}h"


def _priority_badge(priority: int) -> str:
    """Return a Potadot-styled semantic pill for priority value."""
    if priority == Priority.URGENT.value:
        return render_pill("Urgent (P4)", variant="coral")
    elif priority == Priority.HIGH.value:
        return render_pill("High (P3)", variant="amber")
    elif priority == Priority.MEDIUM.value:
        return render_pill("Medium (P2)", variant="blue")
    return render_pill("Low (P1)", variant="muted")


def _status_badge(status: str) -> str:
    """Return a Potadot-styled semantic pill for status."""
    if status == TaskStatus.COMPLETED.value:
        return render_pill("Completed", variant="lime")
    elif status == TaskStatus.IN_PROGRESS.value:
        return render_pill("In Progress", variant="blue")
    return render_pill("Pending", variant="muted")


def render_summary_metrics(storage: TaskStorage, dep_service: Optional[DependencyService] = None) -> None:
    """Render top metric strip for total, pending, in-progress, completed, overdue, and blocked tasks."""
    counts = storage.count_tasks()
    overdue_val = counts["overdue"]
    overdue_caption = f"{overdue_val} past due" if overdue_val > 0 else "All deadlines current"

    blocked_count = 0
    if dep_service is not None:
        graph = dep_service.get_graph()
        all_tasks = storage.list_tasks()
        completed_ids = {t.id for t in all_tasks if t.status == TaskStatus.COMPLETED.value}
        for t in all_tasks:
            if t.status == TaskStatus.PENDING.value and t.id is not None:
                prereqs = graph.get_prerequisites(t.id)
                if any(p not in completed_ids for p in prereqs):
                    blocked_count += 1

    metrics_list = [
        {"label": "Total Tasks", "value": counts["total"], "caption": "Persistent SQLite"},
        {"label": "Pending Queue", "value": counts["pending"], "caption": "FIFO Arrival Sequence"},
        {"label": "In Progress", "value": counts["in_progress"], "caption": "Active Processing"},
        {"label": "Completed", "value": counts["completed"], "caption": "Prereqs Satisfied"},
        {"label": "Overdue", "value": overdue_val, "caption": overdue_caption},
    ]

    if blocked_count > 0:
        metrics_list.append({"label": "Blocked Tasks", "value": blocked_count, "caption": "Awaiting Prereqs"})

    render_metric_strip(metrics_list)


def render_dashboard(
    storage: TaskStorage,
    undo_manager: Optional[UndoManager] = None,
    queue_service: Optional[TaskQueueService] = None,
    scheduler_service: Optional[SchedulerService] = None,
    risk_analyzer: Optional[DeadlineRiskAnalyzer] = None,
    dep_service: Optional[DependencyService] = None,
    index_service: Optional[TaskIndexService] = None,
    hash_index: Optional[TaskHashIndexService] = None,
    cp_service: Optional[CriticalPathService] = None,
) -> None:
    """Render the full TaskForge dashboard inspired by Potadot's professional product experience."""
    counts = storage.count_tasks()
    now = datetime.now()

    # -------------------------------------------------------------------------
    # 1. OPENING PRODUCT HERO
    # -------------------------------------------------------------------------
    render_editorial_hero(
        eyebrow="INTELLIGENT TASK SCHEDULING SYSTEM",
        headline="Good to see you.",
        subhead="Your tasks, deadlines, and project progress — all in one place.",
        meta_tags=[
            ("TOTAL WORK", f"{counts['total']} Items"),
            ("IN PROGRESS", f"{counts.get('in_progress', 0)} Active"),
            ("COMPLETED", f"{counts.get('completed', 0)} Done"),
            ("OVERDUE", f"{counts.get('overdue', 0)} Past Due"),
            ("BLOCKED", f"{counts.get('blocked', 0)} Waiting"),
        ],
    )

    # Quick Navigation / Action Bar directly below Hero
    col_act1, col_act2, col_act3, _ = st.columns([2, 2.4, 2.2, 3.4])
    with col_act1:
        if st.button("➕ Create Task", key="hero_create_btn", use_container_width=True, type="primary"):
            st.session_state["expand_add_form"] = True
    with col_act2:
        if st.button("⚡ Open Schedule", key="hero_schedule_btn", use_container_width=True):
            st.session_state["nav_view"] = "🧠 Schedule & Risks"
            st.rerun()
    with col_act3:
        if st.button("🔬 Technical Labs", key="hero_labs_btn", use_container_width=True):
            st.session_state["nav_view"] = "🔬 Technical Labs: Algorithm Benchmarks"
            st.rerun()

    st.write("")

    # -------------------------------------------------------------------------
    # 2. PROJECT OVERVIEW METRICS
    # -------------------------------------------------------------------------
    render_summary_metrics(storage, dep_service=dep_service)

    # -------------------------------------------------------------------------
    # 3. WORKSPACE HIGHLIGHTS (RECOMMENDED TASK & UPCOMING DEADLINES)
    # -------------------------------------------------------------------------
    col_rec, col_deadlines = st.columns([6, 5])

    # Left Column: Recommended Next Task from Smart Auto-Scheduler
    with col_rec:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">
                ⚡ Recommended Next Task (Smart Auto-Scheduler)
            </div>
            """,
            unsafe_allow_html=True,
        )

        rec_task_item = None
        if scheduler_service is not None:
            schedule_res = scheduler_service.get_smart_schedule()
            if schedule_res.is_valid and schedule_res.ranked_tasks:
                rec_task_item = schedule_res.ranked_tasks[0]

        if rec_task_item is not None:
            rec_task = rec_task_item.task
            assert rec_task.id is not None
            dl_display = rec_task.formatted_deadline if rec_task.due_date else "No deadline"
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 1.2rem 1.4rem; box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08); margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                        <span class="tf-pill tf-pill-blue">RANK #{rec_task_item.rank} &bull; TOP PRIORITY</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #2563EB; font-weight: 600;">{_priority_badge(rec_task.priority)}</span>
                    </div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">
                        #{rec_task.id}: {rec_task.title}
                    </div>
                    <div style="font-size: 0.86rem; color: #475569; margin-bottom: 0.6rem; line-height: 1.45;">
                        {rec_task.description or 'Ready for immediate dispatch — all dependencies satisfied.'}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; border-top: 1px solid #EFF6FF; padding-top: 0.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                        <span>🗓️ Due: <strong style="color: #0F172A;">{dl_display}</strong></span>
                        <span>⏱️ Duration: <strong style="color: #0F172A;">{_format_duration(rec_task.duration)}</strong></span>
                        <span>🧩 Prereqs: <strong style="color: #10B981;">Satisfied</strong></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.4rem; color: #64748B; font-size: 0.88rem; margin-bottom: 0.8rem;">
                    <strong style="color: #0F172A;">All caught up!</strong><br>
                    No pending tasks are awaiting dispatch or all pending items are currently blocked by uncompleted prerequisites.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Right Column: Upcoming Deadlines & Risks
    with col_deadlines:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">
                🗓️ Upcoming Deadlines & Chronology
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_tasks_raw = storage.list_tasks()
        pending_with_deadlines = [t for t in all_tasks_raw if t.due_date is not None and t.status != TaskStatus.COMPLETED.value]
        sorted_by_dl = merge_sort(pending_with_deadlines, key=task_deadline_key).items if pending_with_deadlines else []

        if not sorted_by_dl:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.4rem; color: #64748B; font-size: 0.88rem; margin-bottom: 0.8rem;">
                    No pending deadlines scheduled. Create tasks with due dates to activate BST indexing and risk tracking.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            top_dl = sorted_by_dl[:3]
            dl_html = ""
            for t in top_dl:
                is_ov = t.is_overdue(as_of=now)
                status_color = "#EF4444" if is_ov else "#2563EB"
                badge = '<span class="tf-pill tf-pill-coral">OVERDUE</span>' if is_ov else f'<span style="font-family: JetBrains Mono; font-size: 0.72rem; color: #64748B;">{t.formatted_deadline}</span>'
                dl_html += f"""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.55rem 0; border-bottom: 1px solid #F1F5F9;">
                    <div>
                        <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: {status_color}; font-size: 0.84rem;">#{t.id}</span>
                        <strong style="color: #0F172A; font-size: 0.88rem; margin-left: 0.4rem;">{t.title}</strong>
                    </div>
                    <div>{badge}</div>
                </div>
                """
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem 1.3rem; margin-bottom: 0.8rem;">
                    {dl_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. EXPLORE TASKFORGE (INTERACTIVE PRODUCT SHOWCASE MODULES)
    # -------------------------------------------------------------------------
    render_section_header(
        eyebrow="WORKSPACE CAPABILITIES & INTERACTIVE MODULES",
        title="Explore TaskForge Systems",
        subtitle="Live architectural previews of the underlying custom data structures, graph algorithms, and planning engines.",
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    # Module 01: Task Operations (CO1)
    with col_m1:
        q_head = queue_service.peek_next_task() if queue_service else None
        head_label = f"#{q_head.id} {q_head.title[:15]}..." if q_head else "Queue Empty"
        undo_cnt = len(undo_manager.get_undo_history()) if undo_manager else 0
        st.markdown(
            f"""
            <div class="pt-preview-card">
                <div class="pt-preview-number">MODULE 01 &bull; CO1</div>
                <div class="pt-preview-title">Task Operations</div>
                <div class="pt-preview-desc">FIFO Queue dispatching and dual-stack transactional history.</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                    Queue Head: <strong style="color: #2563EB;">{head_label}</strong><br>
                    Undo Depth: <strong style="color: #0F172A;">{undo_cnt}</strong> actions
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Task Queue ➔", key="mod_queue_btn", use_container_width=True):
            st.session_state["nav_view"] = "📋 Tasks"
            st.rerun()

    # Module 02: DSA Laboratory (CO3 + CO4 + CO2)
    with col_m2:
        bst_nodes = index_service.get_tree_size() if index_service else 0
        bst_height = index_service.get_tree_height() if index_service else 0
        hash_entries = hash_index.size() if hash_index else 0
        st.markdown(
            f"""
            <div class="pt-preview-card">
                <div class="pt-preview-number">TECHNICAL LABS</div>
                <div class="pt-preview-title">Algorithm Labs</div>
                <div class="pt-preview-desc">High-precision benchmarks and BST deadline index.</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                    BST Size / Height: <strong style="color: #2563EB;">{bst_nodes} / {bst_height}</strong><br>
                    Hash Entries: <strong style="color: #0F172A;">{hash_entries}</strong> items
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Algorithm Labs ➔", key="mod_labs_btn", use_container_width=True):
            st.session_state["nav_view"] = "🔬 Technical Labs: Algorithm Benchmarks"
            st.rerun()

    # Module 03: Dependency Planning (CO5)
    with col_m3:
        graph_nodes = 0
        graph_edges = 0
        is_dag_str = "Acyclic"
        if dep_service:
            g = dep_service.get_graph()
            graph_nodes = g.node_count()
            graph_edges = g.edge_count()
            is_dag_str = "Acyclic DAG" if g.is_acyclic() else "Cycle Alert"
        st.markdown(
            f"""
            <div class="pt-preview-card">
                <div class="pt-preview-number">CORE CAPABILITY</div>
                <div class="pt-preview-title">Dependency Map</div>
                <div class="pt-preview-desc">Directed Acyclic Graph execution flow and cycle detection.</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                    DAG Nodes / Edges: <strong style="color: #2563EB;">{graph_nodes} / {graph_edges}</strong><br>
                    Graph State: <strong style="color: #10B981;">{is_dag_str}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Dependency Map ➔", key="mod_dep_btn", use_container_width=True):
            st.session_state["nav_view"] = "🔗 Dependencies"
            st.rerun()

    # Module 04: Intelligent Scheduling (CO1 + CO5)
    with col_m4:
        cp_dur = 0
        if cp_service:
            cp_res = cp_service.calculate_critical_path()
            if cp_res.is_valid:
                cp_dur = cp_res.total_duration_minutes
        st.markdown(
            f"""
            <div class="pt-preview-card">
                <div class="pt-preview-number">CORE CAPABILITY</div>
                <div class="pt-preview-title">Project Timeline & Critical Path</div>
                <div class="pt-preview-desc">Determine longest project chains and simulate delay impacts.</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                    Critical Path Time: <strong style="color: #2563EB;">{cp_dur}m</strong> ({_format_duration(cp_dur)})<br>
                    Simulation: <strong style="color: #0F172A;">In-Memory Safe</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Planning Studio ➔", key="mod_cp_btn", use_container_width=True):
            st.session_state["nav_view"] = "⏱️ Project Timeline"
            st.rerun()

    st.markdown("<hr style='margin: 1.5rem 0 1.2rem 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. TASK REGISTRY & WORKSPACE MANAGEMENT
    # -------------------------------------------------------------------------
    render_section_header(
        eyebrow="WORK REGISTRY & SEARCH",
        title="Task Inventory & Algorithmic Sorting",
        subtitle="Search, filter, and sort tasks using custom O(n log n) Merge Sort or O(n²) Insertion Sort.",
    )

    # Quick Undo/Redo Action Strip
    if undo_manager is not None:
        col_undo, col_redo, col_status = st.columns([2.5, 2.5, 5])
        with col_undo:
            peek_u = undo_manager.peek_undo()
            undo_text = f"↩ Undo: {peek_u.summary}" if peek_u else "↩ Undo (Stack Empty)"
            if st.button(undo_text, disabled=not undo_manager.can_undo(), key="quick_undo", use_container_width=True):
                try:
                    act = undo_manager.undo(storage)
                    if queue_service:
                        queue_service.refresh()
                    st.success(f"Undone: {act.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Undo error: {err}")

        with col_redo:
            peek_r = undo_manager.peek_redo()
            redo_text = f"↪ Redo: {peek_r.summary}" if peek_r else "↪ Redo (Stack Empty)"
            if st.button(redo_text, disabled=not undo_manager.can_redo(), key="quick_redo", use_container_width=True):
                try:
                    act = undo_manager.redo(storage)
                    if queue_service:
                        queue_service.refresh()
                    st.success(f"Redone: {act.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Redo error: {err}")

        with col_status:
            undo_count = len(undo_manager.get_undo_history())
            redo_count = len(undo_manager.get_redo_history())
            st.markdown(
                f"""
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; padding-top: 0.55rem;">
                    Dual-Stack History: <strong style="color: #0F172A;">{undo_count}</strong> Undoable &bull; <strong style="color: #0F172A;">{redo_count}</strong> Redoable
                </div>
                """,
                unsafe_allow_html=True,
            )

    # State variables for editing and deleting
    if "editing_task_id" not in st.session_state:
        st.session_state.editing_task_id = None
    if "deleting_task_id" not in st.session_state:
        st.session_state.deleting_task_id = None

    # Handle Edit View if active
    if st.session_state.editing_task_id is not None:
        task_to_edit = storage.get_task(st.session_state.editing_task_id)
        if task_to_edit:
            def on_updated() -> None:
                st.session_state.editing_task_id = None
                if queue_service:
                    queue_service.refresh()
                st.rerun()

            def on_cancel() -> None:
                st.session_state.editing_task_id = None
                st.rerun()

            render_edit_task_form(storage, task_to_edit, on_updated, on_cancel, undo_manager=undo_manager)
            st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
        else:
            st.session_state.editing_task_id = None

    # Add Task Form
    def on_created() -> None:
        if queue_service:
            queue_service.refresh()
        st.rerun()

    render_add_task_form(storage, on_created, undo_manager=undo_manager)

    # Filter Controls
    col_search, col_status_f, col_priority_f, col_reset = st.columns([3, 2, 2, 1])

    with col_search:
        search_query = st.text_input(
            "Search Title or Description",
            value=st.session_state.get("filter_search", ""),
            placeholder="Search keywords...",
            key="input_search",
        )

    with col_status_f:
        status_filter_options = ["All"] + STATUS_OPTIONS
        selected_status = st.selectbox(
            "Filter by Status",
            options=status_filter_options,
            index=0,
            key="input_status_filter",
        )

    with col_priority_f:
        priority_filter_options = ["All"] + [opt[1] for opt in PRIORITY_OPTIONS]
        selected_priority_label = st.selectbox(
            "Filter by Priority",
            options=priority_filter_options,
            index=0,
            key="input_priority_filter",
        )

    with col_reset:
        st.write("")
        st.write("")
        if st.button("Reset Filters", use_container_width=True):
            st.session_state.input_search = ""
            st.session_state.input_status_filter = "All"
            st.session_state.input_priority_filter = "All"
            st.rerun()

    # Custom Sorting Controls (CO3 Demonstration)
    col_sort_mode, col_sort_algo = st.columns([3, 2])
    with col_sort_mode:
        sort_mode = st.selectbox(
            "Sort Order (Manual Algorithm):",
            options=[
                ("db_default", "Default Database Order (Status, Priority, ID)"),
                ("deadline_asc", "Deadline Ascending (Earliest First, No Deadline Last)"),
                ("priority_desc", "Priority Descending (Urgent to Low)"),
                ("priority_deadline", "Priority & Deadline Combined (Tie-break by ID)"),
                ("id_asc", "Task ID Ascending (Binary Search Order)"),
            ],
            format_func=lambda x: x[1],
            index=0,
            key="dashboard_sort_mode",
        )[0]

    with col_sort_algo:
        sort_algo = st.selectbox(
            "Sorting Algorithm:",
            options=["Merge Sort (O(n log n))", "Insertion Sort (O(n²))"],
            index=0,
            key="dashboard_sort_algo",
        )

    # Determine filter query values
    status_param = None if selected_status == "All" else selected_status
    priority_param = None
    if selected_priority_label != "All":
        priority_param = next(
            (opt[0] for opt in PRIORITY_OPTIONS if opt[1] == selected_priority_label), None
        )

    # Fetch filtered tasks from SQLite
    tasks = storage.list_tasks(
        status=status_param,
        priority=priority_param,
        search=search_query if search_query.strip() else None,
    )

    # Apply manual sorting algorithm to in-memory tasks
    sort_metrics_str = ""
    if tasks and sort_mode != "db_default":
        sort_fn = merge_sort if "Merge" in sort_algo else insertion_sort

        if sort_mode == "deadline_asc":
            sort_result = sort_fn(tasks, key=task_deadline_key)
        elif sort_mode == "priority_desc":
            sort_result = sort_fn(tasks, key=task_priority_key)
        elif sort_mode == "priority_deadline":
            sort_result = sort_fn(tasks, key=task_priority_deadline_key)
        elif sort_mode == "id_asc":
            sort_result = sort_fn(tasks, key=task_id_key)
        else:
            sort_result = None

        if sort_result is not None:
            tasks = sort_result.items
            sort_metrics_str = f"&bull; Sorted with <strong style='color: #2563EB;'>{sort_algo.split()[0]} {sort_algo.split()[1]}</strong>: <strong>{sort_result.comparisons}</strong> comparisons, <strong>{sort_result.shifts}</strong> shifts."

    # Search Demonstration by ID (Binary Search vs Linear Search)
    with st.expander("🔎 Algorithm Search Demonstration (Lookup by Task ID)", expanded=False):
        col_s_id, col_s_mode, col_s_btn = st.columns([2, 2, 1])
        with col_s_id:
            search_task_id = st.number_input("Target Task ID", min_value=1, step=1, value=1)
        with col_s_mode:
            search_method = st.radio("Search Algorithm:", ["Binary Search (O(log n))", "Linear Search (O(n))"], horizontal=True)
        with col_s_btn:
            st.write("")
            st.write("")
            run_search_clicked = st.button("Search Task", use_container_width=True)

        if run_search_clicked:
            all_current_tasks = storage.list_tasks()
            if not all_current_tasks:
                st.warning("No tasks available to search.")
            else:
                if "Binary" in search_method:
                    sorted_tasks = merge_sort(all_current_tasks, key=task_id_key).items
                    s_res = binary_search(sorted_tasks, target=search_task_id, key=task_id_key)
                    if s_res.found and s_res.item:
                        st.success(f"✅ Found #{s_res.item.id} '{s_res.item.title}' in **{s_res.comparisons}** comparison(s) using **Binary Search**! (Index: {s_res.index})")
                    else:
                        st.info(f"ℹ️ Task ID #{search_task_id} not found (determined in {s_res.comparisons} comparisons).")
                else:
                    s_res = linear_search(all_current_tasks, target=search_task_id, key=task_id_key)
                    if s_res.found and s_res.item:
                        st.success(f"✅ Found #{s_res.item.id} '{s_res.item.title}' in **{s_res.comparisons}** comparison(s) using **Linear Search**! (Index: {s_res.index})")
                    else:
                        st.info(f"ℹ️ Task ID #{search_task_id} not found (scanned all {s_res.comparisons} tasks).")

    # Active Deletion Confirmation Alert
    if st.session_state.deleting_task_id is not None:
        task_to_del = storage.get_task(st.session_state.deleting_task_id)
        if task_to_del:
            st.warning(f"⚠️ Are you sure you want to permanently delete Task #{task_to_del.id}: **{task_to_del.title}**?")
            col_conf1, col_conf2 = st.columns([1, 1])
            with col_conf1:
                if st.button("🚨 Yes, Delete Task", key=f"confirm_del_{task_to_del.id}", type="primary", use_container_width=True):
                    if undo_manager is not None and task_to_del.id is not None:
                        undo_manager.record_action(
                            action_type=ActionType.DELETE,
                            task_id=task_to_del.id,
                            before_state=task_to_del,
                            after_state=None,
                        )
                    storage.delete_task(task_to_del.id)  # type: ignore
                    st.session_state.deleting_task_id = None
                    if queue_service:
                        queue_service.refresh()
                    st.success(f"Task #{task_to_del.id} deleted. (Undoable)")
                    st.rerun()
            with col_conf2:
                if st.button("Cancel", key="cancel_del", use_container_width=True):
                    st.session_state.deleting_task_id = None
                    st.rerun()
            st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        else:
            st.session_state.deleting_task_id = None

    # Render Task List
    if not tasks:
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 2.2rem; text-align: center; color: #64748B;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; color: #0F172A; margin-bottom: 0.35rem;">No tasks match the active criteria.</div>
                <div>Create a new task above or click 'Reset Filters' to view the full registry.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; margin-bottom: 0.8rem;">
                Showing <strong style="color: #0F172A;">{len(tasks)}</strong> task(s) {sort_metrics_str}
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_cards, tab_table = st.tabs(["🗂️ Task Registry Cards", "📋 Data Table View"])

        with tab_cards:
            for task in tasks:
                assert task.id is not None
                with st.container(border=True):
                    col_main, col_meta, col_actions = st.columns([6, 3, 2])

                    with col_main:
                        p_badge = _priority_badge(task.priority)
                        s_badge = _status_badge(task.status)
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.35rem;">
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #2563EB;">#{task.id}</span>
                                {p_badge}
                                {s_badge}
                            </div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">{task.title}</div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if task.description:
                            st.markdown(
                                f"""<div style="font-size: 0.85rem; color: #64748B; line-height: 1.45;">{task.description}</div>""",
                                unsafe_allow_html=True,
                            )

                    with col_meta:
                        st.markdown(
                            "<div style=\"font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.35rem;\">DEADLINE & DURATION</div>",
                            unsafe_allow_html=True,
                        )
                        if task.due_date is None:
                            dl_html = "<span style='color: #94A3B8; font-size: 0.84rem;'>No deadline</span>"
                        elif task.is_overdue(as_of=now):
                            dl_html = f"<span style='color: #EF4444; font-weight: 600; font-family: JetBrains Mono; font-size: 0.84rem;'>⚠️ {task.formatted_deadline} (Overdue)</span>"
                        else:
                            dl_html = f"<span style='color: #0F172A; font-family: JetBrains Mono; font-size: 0.84rem;'>🗓️ {task.formatted_deadline}</span>"

                        dur_html = f"<span style='font-family: JetBrains Mono; color: #64748B; font-size: 0.82rem;'>⏱️ {_format_duration(task.duration)}</span>"
                        st.markdown(f"<div>{dl_html}</div><div style='margin-top: 0.25rem;'>{dur_html}</div>", unsafe_allow_html=True)

                    with col_actions:
                        st.markdown("<div style=\"height: 0.3rem;\"></div>", unsafe_allow_html=True)
                        if st.button("✏️ Edit", key=f"btn_edit_{task.id}", help="Edit this task", use_container_width=True):
                            st.session_state.editing_task_id = task.id
                            st.session_state.deleting_task_id = None
                            st.rerun()
                        if st.button("🗑️ Delete", key=f"btn_del_{task.id}", help="Delete this task", use_container_width=True):
                            st.session_state.deleting_task_id = task.id
                            st.session_state.editing_task_id = None
                            st.rerun()

        with tab_table:
            table_rows = []
            for t in tasks:
                is_ov = t.is_overdue(as_of=now) if t.due_date else False
                table_rows.append({
                    "ID": f"#{t.id}",
                    "Title": t.title,
                    "Priority": t.priority_label,
                    "Status": t.status,
                    "Deadline": t.formatted_deadline if t.due_date else "None",
                    "Duration": _format_duration(t.duration),
                    "Overdue": "⚠️ Past Due" if is_ov else "Current",
                })
            st.dataframe(table_rows, use_container_width=True, hide_index=True)
