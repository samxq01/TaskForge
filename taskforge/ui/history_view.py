"""Task Processing and Stack/Queue History UI for Course Outcome 1 (CO1)."""

from __future__ import annotations

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import Action, ActionType, NoHistoryError, UndoManager
from taskforge.storage import TaskStorage


def render_history_view(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
) -> None:
    """Render the CO1 demonstration interface: Stack-based Undo/Redo and FIFO Queue processing."""
    st.markdown("## 🔄 Task Processing & History Lab (CO1)")
    st.markdown(
        """
        > **Course Outcome 1 (CO1):** *Develop efficient solutions using stack and/or queue data structures.*
        
        This module demonstrates real-world application of linear data structures:
        - **Custom Stack (LIFO):** Powers dual Undo and Redo operations across task creation, editing, and deletion.
        - **Custom Queue (FIFO):** Guarantees fair, arrival-based task dispatching without starvation.
        """
    )

    # Always ensure the queue matches fresh database state
    queue_service.refresh()

    tab_queue, tab_undo_redo, tab_concepts = st.tabs(
        ["📋 FIFO Pending Queue", "⏪ LIFO Undo / Redo Stacks", "💡 Viva DSA Concepts"]
    )

    # ---------------- TAB 1: FIFO QUEUE ----------------
    with tab_queue:
        st.markdown("### 🏃 Deterministic FIFO Task Processing")
        st.caption(
            "Tasks with status **Pending** are queued by arrival order (`created_at ASC`, tie-break: `id ASC`)."
        )

        col_q1, col_q2 = st.columns([1, 2])
        with col_q1:
            st.metric("Pending Queue Size", f"{queue_service.size()} tasks")
        with col_q2:
            next_task = queue_service.peek_next_task()
            if next_task:
                st.info(f"👉 **Next at Head of Queue:** #{next_task.id} — **{next_task.title}** (Priority: {next_task.priority_label}, {next_task.duration}m)")
            else:
                st.info("ℹ️ Queue is currently empty. No pending tasks to process.")

        # Action: Process Next Task
        btn_disabled = queue_service.is_empty()
        if st.button("⚡ Process Next Task (FIFO Dequeue)", type="primary", disabled=btn_disabled, use_container_width=True):
            processed = queue_service.process_next_task()
            if processed:
                st.success(f"✅ Dequeued and advanced Task #{processed.id} '{processed.title}' to **In Progress**! (Action recorded in Undo Stack)")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📦 Current Queue Contents (Front to Rear)")

        queue_tasks = queue_service.get_queue_tasks()
        if not queue_tasks:
            st.caption("No pending tasks in queue. All tasks are In Progress or Completed.")
        else:
            q_cols = st.columns([1, 1, 4, 2, 2, 3])
            q_cols[0].markdown("**Pos**")
            q_cols[1].markdown("**ID**")
            q_cols[2].markdown("**Title**")
            q_cols[3].markdown("**Priority**")
            q_cols[4].markdown("**Duration**")
            q_cols[5].markdown("**Enqueued Time**")
            st.markdown("<hr style='margin: 0.3rem 0;'>", unsafe_allow_html=True)

            for idx, task in enumerate(queue_tasks, start=1):
                cols = st.columns([1, 1, 4, 2, 2, 3])
                badge = "🥇 Front" if idx == 1 else f"#{idx}"
                cols[0].write(badge)
                cols[1].write(f"#{task.id}")
                cols[2].write(task.title)
                cols[3].write(task.priority_label)
                cols[4].write(f"{task.duration}m")
                cols[5].write(task.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                st.markdown("<hr style='margin: 0.2rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # ---------------- TAB 2: LIFO UNDO / REDO ----------------
    with tab_undo_redo:
        st.markdown("### ⏪ Reversible Operations via Dual LIFO Stacks")
        st.caption(
            "Every database creation, modification, deletion, and queue processing action is pushed onto the Undo Stack."
        )

        col_u_btn, col_r_btn = st.columns(2)

        peek_u = undo_manager.peek_undo()
        peek_r = undo_manager.peek_redo()

        with col_u_btn:
            undo_label = f"↩️ Undo: {peek_u.summary}" if peek_u else "↩️ Undo (Empty)"
            if st.button(undo_label, disabled=not undo_manager.can_undo(), use_container_width=True, type="secondary"):
                try:
                    action = undo_manager.undo(storage)
                    queue_service.refresh()
                    st.success(f"Undone: {action.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to undo: {err}")

        with col_r_btn:
            redo_label = f"↪️ Redo: {peek_r.summary}" if peek_r else "↪️ Redo (Empty)"
            if st.button(redo_label, disabled=not undo_manager.can_redo(), use_container_width=True, type="secondary"):
                try:
                    action = undo_manager.redo(storage)
                    queue_service.refresh()
                    st.success(f"Redone: {action.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to redo: {err}")

        st.markdown("---")

        col_undo_view, col_redo_view = st.columns(2)

        with col_undo_view:
            st.markdown("#### 📚 Undo Stack (LIFO)")
            undo_items = undo_manager.get_undo_history()
            st.caption(f"Stack size: **{len(undo_items)}** (Top = Most recent action)")
            if not undo_items:
                st.info("Undo stack is empty.")
            else:
                for idx, act in enumerate(undo_items):
                    prefix = "🔝 [TOP]" if idx == 0 else f"[{idx + 1}]"
                    icon = "➕" if act.action_type == ActionType.CREATE else ("✏️" if act.action_type == ActionType.EDIT else "🗑️")
                    st.markdown(f"- **{prefix}** {icon} `{act.action_type.value}`: {act.summary}")

        with col_redo_view:
            st.markdown("#### 📚 Redo Stack (LIFO)")
            redo_items = undo_manager.get_redo_history()
            st.caption(f"Stack size: **{len(redo_items)}** (Top = Next action to reapply)")
            if not redo_items:
                st.info("Redo stack is empty.")
            else:
                for idx, act in enumerate(redo_items):
                    prefix = "🔝 [TOP]" if idx == 0 else f"[{idx + 1}]"
                    icon = "➕" if act.action_type == ActionType.CREATE else ("✏️" if act.action_type == ActionType.EDIT else "🗑️")
                    st.markdown(f"- **{prefix}** {icon} `{act.action_type.value}`: {act.summary}")

        if undo_items or redo_items:
            if st.button("🧹 Clear Undo/Redo History", use_container_width=True):
                undo_manager.clear()
                st.success("Undo/Redo history cleared.")
                st.rerun()

    # ---------------- TAB 3: VIVA CONCEPTS ----------------
    with tab_concepts:
        st.markdown("### 🎓 Academic Viva Walkthrough: LIFO vs FIFO")
        st.markdown(
            """
            #### 1. Stack Data Structure (LIFO: Last In, First Out)
            - **Definition:** Elements are added and removed from the same end, called the **Top**.
            - **TaskForge Use-Case:** Dual-stack **Undo/Redo** manager.
              - When a task mutation happens, it is pushed onto the `Undo Stack`.
              - Pressing **Undo** pops the top action, inverts its mutation in SQLite, and pushes it onto the `Redo Stack`.
              - Pressing **Redo** pops the top action from `Redo Stack`, reapplies the forward mutation in SQLite, and pushes it back to `Undo Stack`.
              - Performing any new operation clears the `Redo Stack` to maintain temporal consistency.
            - **Complexity:**
              - `push`: $O(1)$ amortized
              - `pop`: $O(1)$
              - `peek`: $O(1)$
            
            ---
            
            #### 2. Queue Data Structure (FIFO: First In, First Out)
            - **Definition:** Elements are inserted at the **Rear (Tail)** and extracted from the **Front (Head)**.
            - **TaskForge Use-Case:** **Deterministic Pending Task Processing**.
              - Avoids starvation by dispatching the oldest created task first.
              - Does not use `list.pop(0)` ($O(n)$) or Python's `collections.deque`.
              - Implemented manually using a **singly-linked list** with head and tail pointers to achieve guaranteed $O(1)$ enqueue and $O(1)$ dequeue operations.
            - **Complexity:**
              - `enqueue`: $O(1)$
              - `dequeue`: $O(1)$
              - `peek`: $O(1)$
            """
        )
