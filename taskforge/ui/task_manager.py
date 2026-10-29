"""Task creation, editing, and form management components."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Callable

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.storage import TaskStorage


PRIORITY_OPTIONS = [
    (Priority.URGENT.value, "Urgent (Priority 4)"),
    (Priority.HIGH.value, "High (Priority 3)"),
    (Priority.MEDIUM.value, "Medium (Priority 2)"),
    (Priority.LOW.value, "Low (Priority 1)"),
]

STATUS_OPTIONS = [
    TaskStatus.PENDING.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.COMPLETED.value,
]


def render_add_task_form(storage: TaskStorage, on_task_created: Callable[[], None]) -> None:
    """Render the form for creating a new task."""
    with st.expander("➕ **Add New Task**", expanded=False):
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                title = st.text_input(
                    "Task Title *",
                    placeholder="e.g. Implement Dijkstra Algorithm",
                    help="Short, meaningful title (required)",
                )
            with col2:
                priority = st.selectbox(
                    "Priority *",
                    options=[p[0] for p in PRIORITY_OPTIONS],
                    format_func=lambda val: next(opt[1] for opt in PRIORITY_OPTIONS if opt[0] == val),
                    index=2,  # Default: Medium (P2)
                )

            description = st.text_area(
                "Description",
                placeholder="Optional task details, requirements, or notes...",
                rows=2,
            )

            col3, col4, col5 = st.columns([2, 2, 2])
            with col3:
                has_deadline = st.checkbox("Set Deadline?", value=False)
                if has_deadline:
                    default_date = date.today() + timedelta(days=1)
                    due_d = st.date_input("Due Date", value=default_date)
                    due_t = st.time_input("Due Time", value=time(23, 59))
                    due_date = datetime.combine(due_d, due_t)
                else:
                    due_date = None

            with col4:
                duration = st.number_input(
                    "Estimated Duration (minutes) *",
                    min_value=1,
                    max_value=10080,
                    value=30,
                    step=5,
                    help="Must be a positive integer in minutes",
                )

            with col5:
                status = st.selectbox(
                    "Status *",
                    options=STATUS_OPTIONS,
                    index=0,  # Default: Pending
                )

            submitted = st.form_submit_button("Create Task", use_container_width=True)
            if submitted:
                if not title or not title.strip():
                    st.error("❌ Task title cannot be empty.")
                    return

                try:
                    new_task = Task(
                        title=title.strip(),
                        description=description.strip(),
                        priority=priority,
                        due_date=due_date,
                        duration=int(duration),
                        status=status,
                    )
                    created = storage.create_task(new_task)
                    st.success(f"✅ Task #{created.id} '{created.title}' created successfully!")
                    on_task_created()
                except ValueError as err:
                    st.error(f"❌ Validation error: {err}")
                except Exception as err:
                    st.error(f"❌ Failed to create task: {err}")


def render_edit_task_form(
    storage: TaskStorage,
    task: Task,
    on_task_updated: Callable[[], None],
    on_cancel: Callable[[], None],
) -> None:
    """Render the editing form for an existing task."""
    st.markdown(f"### ✏️ Editing Task #{task.id}: **{task.title}**")

    with st.form(f"edit_task_form_{task.id}"):
        col1, col2 = st.columns([3, 1])
        with col1:
            title = st.text_input("Task Title *", value=task.title)
        with col2:
            current_priority_idx = next(
                (i for i, opt in enumerate(PRIORITY_OPTIONS) if opt[0] == task.priority), 2
            )
            priority = st.selectbox(
                "Priority *",
                options=[p[0] for p in PRIORITY_OPTIONS],
                format_func=lambda val: next(opt[1] for opt in PRIORITY_OPTIONS if opt[0] == val),
                index=current_priority_idx,
            )

        description = st.text_area("Description", value=task.description or "", rows=2)

        col3, col4, col5 = st.columns([2, 2, 2])
        with col3:
            has_deadline = st.checkbox(
                "Has Deadline?",
                value=(task.due_date is not None),
                key=f"edit_has_deadline_{task.id}",
            )
            if has_deadline:
                initial_date = task.due_date.date() if task.due_date else date.today() + timedelta(days=1)
                initial_time = task.due_date.time() if task.due_date else time(23, 59)
                due_d = st.date_input("Due Date", value=initial_date, key=f"edit_date_{task.id}")
                due_t = st.time_input("Due Time", value=initial_time, key=f"edit_time_{task.id}")
                due_date = datetime.combine(due_d, due_t)
            else:
                due_date = None

        with col4:
            duration = st.number_input(
                "Estimated Duration (minutes) *",
                min_value=1,
                max_value=10080,
                value=int(task.duration),
                step=5,
                key=f"edit_duration_{task.id}",
            )

        with col5:
            current_status_idx = (
                STATUS_OPTIONS.index(task.status) if task.status in STATUS_OPTIONS else 0
            )
            status = st.selectbox(
                "Status *",
                options=STATUS_OPTIONS,
                index=current_status_idx,
                key=f"edit_status_{task.id}",
            )

        col_save, col_cancel = st.columns([1, 1])
        with col_save:
            submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if submitted:
            if not title or not title.strip():
                st.error("❌ Task title cannot be empty.")
                return

            try:
                task.title = title.strip()
                task.description = description.strip()
                task.priority = priority
                task.due_date = due_date
                task.duration = int(duration)
                task.status = status
                storage.update_task(task)
                st.success(f"✅ Task #{task.id} updated successfully!")
                on_task_updated()
            except ValueError as err:
                st.error(f"❌ Validation error: {err}")
            except Exception as err:
                st.error(f"❌ Failed to update task: {err}")

        if cancelled:
            on_cancel()
