"""Main dashboard view for task management."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
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


def render_dashboard(storage: TaskStorage) -> None:
    """Render the full Phase 01 TaskForge dashboard."""
    # Summary Metrics
    render_summary_metrics(storage)
    st.markdown("---")

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
                st.rerun()

            def on_cancel() -> None:
                st.session_state.editing_task_id = None
                st.rerun()

            render_edit_task_form(storage, task_to_edit, on_updated, on_cancel)
            st.markdown("---")
        else:
            st.session_state.editing_task_id = None

    # Add Task Form
    def on_created() -> None:
        st.rerun()

    render_add_task_form(storage, on_created)

    st.markdown("### 🔍 Task Registry & Filters")

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
        st.write("")  # Vertical spacing
        st.write("")
        if st.button("Reset Filters", use_container_width=True):
            st.session_state.input_search = ""
            st.session_state.input_status_filter = "All"
            st.session_state.input_priority_filter = "All"
            st.rerun()

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

    now = datetime.now()

    # Active Deletion Confirmation Alert
    if st.session_state.deleting_task_id is not None:
        task_to_del = storage.get_task(st.session_state.deleting_task_id)
        if task_to_del:
            st.warning(f"⚠️ Are you sure you want to permanently delete Task #{task_to_del.id}: **{task_to_del.title}**?")
            col_conf1, col_conf2 = st.columns([1, 1])
            with col_conf1:
                if st.button("🚨 Yes, Delete Task", key=f"confirm_del_{task_to_del.id}", type="primary", use_container_width=True):
                    storage.delete_task(task_to_del.id)  # type: ignore
                    st.session_state.deleting_task_id = None
                    st.success(f"Task #{task_to_del.id} deleted.")
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
        st.caption(f"Showing **{len(tasks)}** task(s)")

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
