"""Main dashboard view for task management with custom DSA searching and sorting integration."""

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


def render_summary_metrics(storage: TaskStorage) -> None:
    """Render top metric strip for total, pending, in-progress, completed, and overdue tasks."""
    counts = storage.count_tasks()
    overdue_val = counts["overdue"]
    overdue_caption = f"{overdue_val} past due" if overdue_val > 0 else "All deadlines current"

    render_metric_strip([
        {"label": "Total Tasks", "value": counts["total"], "caption": "Persistent SQLite"},
        {"label": "Pending", "value": counts["pending"], "caption": "FIFO Queue Head"},
        {"label": "In Progress", "value": counts["in_progress"], "caption": "Active Processing"},
        {"label": "Completed", "value": counts["completed"], "caption": "Prereqs Satisfied"},
        {"label": "Overdue", "value": overdue_val, "caption": overdue_caption},
    ])


def _format_duration(minutes: int) -> str:
    """Format duration into human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours}h {rem}m" if rem else f"{hours}h"


def _priority_badge(priority: int) -> str:
    """Return an Anthracite-styled semantic pill for priority value."""
    if priority == Priority.URGENT.value:
        return render_pill("Urgent (P4)", variant="coral")
    elif priority == Priority.HIGH.value:
        return render_pill("High (P3)", variant="amber")
    elif priority == Priority.MEDIUM.value:
        return render_pill("Medium (P2)", variant="blue")
    return render_pill("Low (P1)", variant="muted")


def _status_badge(status: str) -> str:
    """Return an Anthracite-styled semantic pill for status."""
    if status == TaskStatus.COMPLETED.value:
        return render_pill("Completed", variant="lime")
    elif status == TaskStatus.IN_PROGRESS.value:
        return render_pill("In Progress", variant="blue")
    return render_pill("Pending", variant="muted")


def render_dashboard(
    storage: TaskStorage,
    undo_manager: Optional[UndoManager] = None,
    queue_service: Optional[TaskQueueService] = None,
) -> None:
    """Render the full TaskForge dashboard with CRUD operations, undo/redo, and custom sorting/searching."""
    counts = storage.count_tasks()

    # Editorial Hero Section
    render_editorial_hero(
        eyebrow="DIGITAL CRAFT • INTELLIGENT PLANNING",
        headline="Make every task count.",
        subhead="Your work, dependencies, and deadlines. One intelligent, deterministic planning system powered by pure data structures.",
        meta_tags=[
            ("TOTAL INVENTORY", f"{counts['total']} Items"),
            ("ARRIVAL QUEUE", f"{counts['pending']} Pending"),
            ("STORAGE ENGINE", "SQLite ACID Persistence"),
        ],
    )

    # Top Metric Strip
    render_summary_metrics(storage)

    # State variables for editing and deleting
    if "editing_task_id" not in st.session_state:
        st.session_state.editing_task_id = None
    if "deleting_task_id" not in st.session_state:
        st.session_state.deleting_task_id = None

    # Quick Undo/Redo Action Strip
    if undo_manager is not None:
        col_undo, col_redo, col_status = st.columns([2, 2, 4])
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
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #A6A49E; padding-top: 0.55rem;">
                    Dual-Stack History: <strong style="color: #FFFFFF;">{undo_count}</strong> Undoable &bull; <strong style="color: #FFFFFF;">{redo_count}</strong> Redoable
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)

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
            st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)
        else:
            st.session_state.editing_task_id = None

    # Add Task Form
    def on_created() -> None:
        if queue_service:
            queue_service.refresh()
        st.rerun()

    render_add_task_form(storage, on_created, undo_manager=undo_manager)

    # Section Header for Work Registry
    render_section_header(
        eyebrow="WORK REGISTRY & SEARCH",
        title="Task Inventory & Algorithmic Sorting",
        subtitle="Filter and sort live tasks using manual O(n log n) Merge Sort or O(n²) Insertion Sort.",
    )

    # Filter Controls
    col_search, col_status, col_priority, col_reset = st.columns([3, 2, 2, 1])

    with col_search:
        search_query = st.text_input(
            "Search Title or Description",
            value=st.session_state.get("filter_search", ""),
            placeholder="Search keywords...",
            key="input_search",
        )

    with col_status:
        status_filter_options = ["All"] + STATUS_OPTIONS
        selected_status = st.selectbox(
            "Filter by Status",
            options=status_filter_options,
            index=0,
            key="input_status_filter",
        )

    with col_priority:
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
            sort_metrics_str = f"&bull; Ordered using <strong style='color: #D7FF64;'>{sort_algo.split()[0]} {sort_algo.split()[1]}</strong>: <strong>{sort_result.comparisons}</strong> comparisons, <strong>{sort_result.shifts}</strong> shifts."

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

    now = datetime.now()

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

    # Render Task List Table
    if not tasks:
        st.markdown(
            """
            <div style="background-color: #1B1B1B; border: 1px solid #2A2A2A; border-radius: 3px; padding: 2rem; text-align: center; color: #A6A49E;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; color: #FFFFFF; margin-bottom: 0.35rem;">No tasks match the active criteria.</div>
                <div>Create a new task above or click 'Reset Filters' to view the full registry.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #A6A49E; margin-bottom: 0.8rem;">
                Showing <strong style="color: #FFFFFF;">{len(tasks)}</strong> task(s) {sort_metrics_str}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Table header
        header_cols = st.columns([1, 4, 2, 3, 2, 2, 2])
        header_cols[0].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>ID</span>", unsafe_allow_html=True)
        header_cols[1].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Title & Details</span>", unsafe_allow_html=True)
        header_cols[2].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Priority</span>", unsafe_allow_html=True)
        header_cols[3].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Deadline</span>", unsafe_allow_html=True)
        header_cols[4].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Duration</span>", unsafe_allow_html=True)
        header_cols[5].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Status</span>", unsafe_allow_html=True)
        header_cols[6].markdown("<span style='font-family: JetBrains Mono; font-size: 0.75rem; text-transform: uppercase; color: #A6A49E;'>Actions</span>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0.4rem 0 0.8rem 0;'>", unsafe_allow_html=True)

        for task in tasks:
            assert task.id is not None
            cols = st.columns([1, 4, 2, 3, 2, 2, 2])

            # ID
            cols[0].markdown(f"<span style='font-family: JetBrains Mono; font-weight: 600; color: #D7FF64;'>#{task.id}</span>", unsafe_allow_html=True)

            # Title and description
            with cols[1]:
                st.markdown(f"<strong style='color: #FFFFFF; font-size: 0.95rem;'>{task.title}</strong>", unsafe_allow_html=True)
                if task.description:
                    st.caption(task.description)

            # Priority
            cols[2].markdown(_priority_badge(task.priority), unsafe_allow_html=True)

            # Deadline with overdue alert if applicable
            with cols[3]:
                if task.due_date is None:
                    st.markdown("<span style='color: #6E6D68; font-size: 0.85rem;'>No deadline</span>", unsafe_allow_html=True)
                else:
                    if task.is_overdue(as_of=now):
                        st.markdown(f"<span style='color: #F87171; font-weight: 600; font-family: JetBrains Mono; font-size: 0.85rem;'>⚠ {task.formatted_deadline}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #F3F1EB; font-family: JetBrains Mono; font-size: 0.85rem;'>{task.formatted_deadline}</span>", unsafe_allow_html=True)

            # Duration
            cols[4].markdown(f"<span style='font-family: JetBrains Mono; color: #A6A49E; font-size: 0.85rem;'>{_format_duration(task.duration)}</span>", unsafe_allow_html=True)

            # Status
            cols[5].markdown(_status_badge(task.status), unsafe_allow_html=True)

            # Action Buttons: Edit and Delete
            with cols[6]:
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button("✏️", key=f"btn_edit_{task.id}", help="Edit this task"):
                        st.session_state.editing_task_id = task.id
                        st.session_state.deleting_task_id = None
                        st.rerun()
                with action_col2:
                    if st.button("🗑️", key=f"btn_del_{task.id}", help="Delete this task"):
                        st.session_state.deleting_task_id = task.id
                        st.session_state.editing_task_id = None
                        st.rerun()

            st.markdown("<hr style='margin: 0.35rem 0; opacity: 0.4;'>", unsafe_allow_html=True)
