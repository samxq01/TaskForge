"""Task Processing and Stack/Queue History UI for Course Outcome 1 (CO1)."""

from __future__ import annotations

import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import Action, ActionType, NoHistoryError, UndoManager
from taskforge.storage import TaskStorage
from taskforge.ui.theme import render_metric_strip, render_pill, render_section_header


def render_history_view(
    storage: TaskStorage,
    undo_manager: UndoManager,
    queue_service: TaskQueueService,
) -> None:
    """Render the CO1 demonstration interface: Stack-based Undo/Redo and FIFO Queue processing."""
    render_section_header(
        eyebrow="COURSE OUTCOME 1 (CO1) • LINEAR DATA STRUCTURES",
        title="Task Processing & Dual-Stack History Lab",
        subtitle="Practical implementation of custom linear data structures: LIFO Stack for transactional undo/redo and FIFO Queue for arrival-order execution dispatching.",
    )

    # Always ensure the queue matches fresh database state
    queue_service.refresh()

    tab_queue, tab_undo_redo, tab_concepts = st.tabs(
        ["📋 FIFO Pending Queue", "⏪ LIFO Undo / Redo Stacks", "💡 Viva DSA Concepts"]
    )

    # ---------------- TAB 1: FIFO QUEUE ----------------
    with tab_queue:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Deterministic FIFO Task Dispatching
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1rem;">
                Pending tasks queued in strict chronological arrival sequence (<code>created_at ASC, id ASC</code>).
            </div>
            """,
            unsafe_allow_html=True,
        )

        next_task = queue_service.peek_next_task()
        head_caption = f"#{next_task.id} {next_task.title}" if next_task else "Queue Empty"

        render_metric_strip([
            {"label": "Pending Queue Size", "value": f"{queue_service.size()} tasks", "caption": "Singly-Linked List"},
            {"label": "Head of Queue", "value": f"#{next_task.id}" if next_task else "None", "caption": head_caption},
            {"label": "Queue Complexity", "value": "O(1) Enq / Deq", "caption": "Explicit Tail Pointer"},
        ])

        if next_task:
            st.markdown(
                f"""
                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 1.2rem 1.4rem; margin-bottom: 1.2rem; box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08);">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #2563EB; font-weight: 700; margin-bottom: 0.3rem;">
                        ● Next at Head of Queue (FIFO Dispatch)
                    </div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">
                        Task #{next_task.id}: {next_task.title}
                    </div>
                    <div style="font-size: 0.86rem; color: #475569;">
                        Priority: <strong style="color: #0F172A;">{next_task.priority_label}</strong> &bull; Duration: <strong style="color: #0F172A;">{next_task.duration}m</strong> &bull; Enqueued: <span style="font-family: JetBrains Mono;">{next_task.created_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.2rem 1.4rem; margin-bottom: 1.2rem; color: #64748B; font-size: 0.88rem;">
                    Queue is currently empty. No pending tasks ready to process.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Action: Process Next Task
        btn_disabled = queue_service.is_empty()
        if st.button("⚡ Process Next Task (FIFO Dequeue)", type="primary", disabled=btn_disabled, use_container_width=True):
            processed = queue_service.process_next_task()
            if processed:
                st.success(f"✅ Dequeued and advanced Task #{processed.id} '{processed.title}' to **In Progress**! (Action recorded in Undo Stack)")
                st.rerun()

        st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.6rem;">Queue Sequence (Front to Rear)</div>',
            unsafe_allow_html=True,
        )

        queue_tasks = queue_service.get_queue_tasks()
        if not queue_tasks:
            st.markdown("<span style='color: #94A3B8; font-size: 0.88rem;'>No pending tasks in queue. All tasks are In Progress or Completed.</span>", unsafe_allow_html=True)
        else:
            queue_data = [
                {
                    "Queue Pos": "🟢 HEAD (Next)" if idx == 1 else f"#{idx}",
                    "Task ID": f"#{task.id}",
                    "Title": task.title,
                    "Priority": task.priority_label,
                    "Duration": f"{task.duration}m",
                    "Enqueued At": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for idx, task in enumerate(queue_tasks, start=1)
            ]
            st.dataframe(queue_data, use_container_width=True, hide_index=True)

    # ---------------- TAB 2: LIFO UNDO / REDO ----------------
    with tab_undo_redo:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Reversible Operations via Dual LIFO Stacks
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1rem;">
                Every creation, modification, deletion, and queue dispatch pushes a reversible action onto the Undo Stack.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_u_btn, col_r_btn = st.columns(2)

        peek_u = undo_manager.peek_undo()
        peek_r = undo_manager.peek_redo()

        with col_u_btn:
            undo_label = f"↩ Undo: {peek_u.summary}" if peek_u else "↩ Undo (Stack Empty)"
            if st.button(undo_label, disabled=not undo_manager.can_undo(), use_container_width=True, type="secondary"):
                try:
                    action = undo_manager.undo(storage)
                    queue_service.refresh()
                    st.success(f"Undone: {action.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to undo: {err}")

        with col_r_btn:
            redo_label = f"↪ Redo: {peek_r.summary}" if peek_r else "↪ Redo (Stack Empty)"
            if st.button(redo_label, disabled=not undo_manager.can_redo(), use_container_width=True, type="secondary"):
                try:
                    action = undo_manager.redo(storage)
                    queue_service.refresh()
                    st.success(f"Redone: {action.summary}")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to redo: {err}")

        st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)

        col_undo_view, col_redo_view = st.columns(2)

        with col_undo_view:
            undo_items = undo_manager.get_undo_history()
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.1rem 1.3rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem;">
                        📚 Undo Stack (LIFO)
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                        Stack Depth: <strong style="color: #2563EB;">{len(undo_items)}</strong> (Top = Most recent action)
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if not undo_items:
                st.markdown("<span style='color: #94A3B8; font-size: 0.85rem;'>Undo stack is empty.</span></div>", unsafe_allow_html=True)
            else:
                for idx, act in enumerate(undo_items):
                    prefix = "<strong style='color: #2563EB;'>[TOP]</strong>" if idx == 0 else f"<span style='color: #94A3B8;'>[{idx + 1}]</span>"
                    st.markdown(
                        f"""
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; padding: 0.35rem 0; border-bottom: 1px solid #F1F5F9;">
                            {prefix} <strong>{act.action_type.value}</strong>: <span style="color: #475569;">{act.summary}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        with col_redo_view:
            redo_items = undo_manager.get_redo_history()
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.1rem 1.3rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem;">
                        📚 Redo Stack (LIFO)
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #475569; margin-bottom: 0.8rem;">
                        Stack Depth: <strong style="color: #2563EB;">{len(redo_items)}</strong> (Top = Next action to reapply)
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if not redo_items:
                st.markdown("<span style='color: #94A3B8; font-size: 0.85rem;'>Redo stack is empty.</span></div>", unsafe_allow_html=True)
            else:
                for idx, act in enumerate(redo_items):
                    prefix = "<strong style='color: #2563EB;'>[TOP]</strong>" if idx == 0 else f"<span style='color: #94A3B8;'>[{idx + 1}]</span>"
                    st.markdown(
                        f"""
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; padding: 0.35rem 0; border-bottom: 1px solid #F1F5F9;">
                            {prefix} <strong>{act.action_type.value}</strong>: <span style="color: #475569;">{act.summary}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        if undo_items or redo_items:
            st.write("")
            if st.button("🧹 Clear Undo/Redo History", use_container_width=True):
                undo_manager.clear()
                st.success("Undo/Redo history cleared.")
                st.rerun()

    # ---------------- TAB 3: VIVA CONCEPTS ----------------
    with tab_concepts:
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.6rem 1.8rem; margin-top: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;">
                    Academic Viva Walkthrough: LIFO vs FIFO Theoretical Design
                </div>
                
                <h4 style="color: #2563EB; margin-top: 1.2rem;">1. Stack Data Structure (LIFO: Last In, First Out)</h4>
                <ul style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                    <li><strong>Definition:</strong> Elements are pushed and popped strictly from the same end, designated as the <em>Top</em>.</li>
                    <li><strong>TaskForge Use-Case:</strong> Dual-Stack <em>Undo/Redo</em> transactional history.
                        <ul>
                            <li>Every state mutation in SQLite pushes an inverse command onto the <code>Undo Stack</code>.</li>
                            <li>Pressing <strong>Undo</strong> pops the top action, inverts its mutation in SQLite, and pushes it onto the <code>Redo Stack</code>.</li>
                            <li>Pressing <strong>Redo</strong> pops the action from <code>Redo Stack</code>, reapplies the forward mutation, and pushes it back onto <code>Undo Stack</code>.</li>
                            <li>Any new write mutation strictly purges the <code>Redo Stack</code> to maintain linear timeline consistency.</li>
                        </ul>
                    </li>
                    <li><strong>Time Complexity:</strong> <code>push</code>: $O(1)$ amortized &bull; <code>pop</code>: $O(1)$ &bull; <code>peek</code>: $O(1)$</li>
                </ul>

                <hr style="margin: 1.2rem 0; border-color: #E2E8F0;">

                <h4 style="color: #2563EB; margin-top: 1.2rem;">2. Queue Data Structure (FIFO: First In, First Out)</h4>
                <ul style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                    <li><strong>Definition:</strong> Elements are appended at the <em>Rear (Tail)</em> and removed from the <em>Front (Head)</em>.</li>
                    <li><strong>TaskForge Use-Case:</strong> Starvation-free, deterministic pending task processing.</li>
                    <li><strong>Custom Linked Implementation:</strong> Manually implemented using a singly-linked list with explicit <code>head</code> and <code>tail</code> pointers, avoiding the $O(n)$ shifting penalty of Python <code>list.pop(0)</code> and eliminating external reliance on <code>collections.deque</code>.</li>
                    <li><strong>Time Complexity:</strong> <code>enqueue</code>: $O(1)$ &bull; <code>dequeue</code>: $O(1)$ &bull; <code>peek</code>: $O(1)$</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
