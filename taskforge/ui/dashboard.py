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


def render_summary_metrics(storage: TaskStorage) -> None:
    """Render top metric cards for total, pending, in-progress, completed, and overdue tasks."""
    counts = storage.count_tasks()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="📋 Total Tasks", value=counts["total"])
    with col2:
        st.metric(label="⏳ Pending", value=counts["pending"])
    with col3:
        st.metric(label="⚙️ In Progress", value=counts["in_progress"])
    with col4:
        st.metric(label="✅ Completed", value=counts["completed"])
    with col5:
        overdue_val = counts["overdue"]
        delta_str = f"{overdue_val} past due" if overdue_val > 0 else "None"
        st.metric(
            label="⚠️ Overdue",
            value=overdue_val,
            delta=delta_str if overdue_val > 0 else None,
            delta_color="inverse",
        )


def _format_duration(minutes: int) -> str:
    """Format duration into human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours}h {rem}m" if rem else f"{hours}h"


def _priority_badge(priority: int) -> str:
    """Return an emoji and label for a priority value."""
    badges = {
        Priority.URGENT.value: "🔴 Urgent (P4)",
        Priority.HIGH.value: "🟠 High (P3)",
        Priority.MEDIUM.value: "🟡 Medium (P2)",
        Priority.LOW.value: "⚪ Low (P1)",
    }
    return badges.get(priority, f"P{priority}")


def _status_badge(status: str) -> str:
    """Return an emoji and label for status."""
    badges = {
        TaskStatus.PENDING.value: "⏳ Pending",
        TaskStatus.IN_PROGRESS.value: "⚙️ In Progress",
        TaskStatus.COMPLETED.value: "✅ Completed",
    }
    return badges.get(status, status)


def render_dashboard(
    storage: TaskStorage,
    undo_manager: Optional[UndoManager] = None,
    queue_service: Optional[TaskQueueService] = None,
) -> None:
    """Render the full TaskForge dashboard with CRUD operations, undo/redo, and custom sorting/searching."""
    # Summary Metrics
    render_summary_metrics(storage)
    st.markdown("---")

    # State variables for editing and deleting
    if "editing_task_id" not in st.session_state:
        st.session_state.editing_task_id = None
    if "deleting_task_id" not in st.session_state:
        st.session_state.deleting_task_id = None

    # Quick Undo/Redo Bar
    if undo_manager is not None:
        col_undo, col_redo, col_status = st.columns([2, 2, 4])
        with col_undo:
            peek_u = undo_manager.peek_undo()
            undo_text = f"↩️ Undo: {peek_u.summary}" if peek_u else "↩️ Undo (Empty)"
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
            redo_text = f"↪️ Redo: {peek_r.summary}" if peek_r else "↪️ Redo (Empty)"
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
            st.caption(f"📚 Stacks: **{undo_count}** Undoable action(s) | **{redo_count}** Redoable action(s)")

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
            st.markdown("---")
        else:
            st.session_state.editing_task_id = None

    # Add Task Form
    def on_created() -> None:
        if queue_service:
            queue_service.refresh()
        st.rerun()

    render_add_task_form(storage, on_created, undo_manager=undo_manager)

    st.markdown("### 🔍 Task Registry, Search & Custom Sorting (CO3)")

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
            "⚡ Sort Tasks By (Manual DSA Implementation):",
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
            sort_metrics_str = f"📊 Ordered using **{sort_algo.split()[0]} {sort_algo.split()[1]}**: **{sort_result.comparisons}** comparisons, **{sort_result.shifts}** shifts."

    # Search Demonstration by ID (Binary Search vs Linear Search)
    with st.expander("🔎 **Algorithm Search Demonstration (Lookup by Task ID)**", expanded=False):
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
                    # Binary search precondition: sort by task ID first
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
            st.markdown("---")
        else:
            st.session_state.deleting_task_id = None

    # Render Task List Table
    if not tasks:
        st.info("ℹ️ No tasks found matching the criteria. Create a new task above or reset filters.")
    else:
        st.caption(f"Showing **{len(tasks)}** task(s). {sort_metrics_str}")

        # Table header
        header_cols = st.columns([1, 4, 2, 3, 2, 2, 2])
        header_cols[0].markdown("**ID**")
        header_cols[1].markdown("**Title & Details**")
        header_cols[2].markdown("**Priority**")
        header_cols[3].markdown("**Deadline**")
        header_cols[4].markdown("**Duration**")
        header_cols[5].markdown("**Status**")
        header_cols[6].markdown("**Actions**")

        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

        for task in tasks:
            assert task.id is not None
            cols = st.columns([1, 4, 2, 3, 2, 2, 2])

            # ID
            cols[0].write(f"#{task.id}")

            # Title and description
            with cols[1]:
                st.markdown(f"**{task.title}**")
                if task.description:
                    st.caption(task.description)

            # Priority
            cols[2].write(_priority_badge(task.priority))

            # Deadline with overdue alert if applicable
            with cols[3]:
                if task.due_date is None:
                    st.write("No deadline")
                else:
                    if task.is_overdue(as_of=now):
                        st.markdown(f"🔴 **{task.formatted_deadline}** *(Overdue)*")
                    else:
                        st.write(task.formatted_deadline)

            # Duration
            cols[4].write(_format_duration(task.duration))

            # Status
            cols[5].write(_status_badge(task.status))

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

            st.markdown("<hr style='margin: 0.3rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
