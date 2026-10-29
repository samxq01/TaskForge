"""Smart Scheduling & Deadline Risk Analyzer UI View (CO1 + CO5).

Demonstrates:
1. Heap-based Smart Auto-Scheduler using custom binary Min-Heap PriorityQueue.
2. Deterministic, rule-based Deadline Risk Analyzer.
3. Coexistence of FIFO dispatching and Heap priority ranking.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.risk_analyzer import (
    DeadlineRiskAnalyzer,
    RiskAnalysisSummary,
    RiskCategory,
    TaskRiskAssessment,
)
from taskforge.services.scheduler import RankedTaskRecommendation, SchedulerService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.storage import TaskStorage


def render_scheduling_view(
    storage: TaskStorage,
    scheduler: SchedulerService,
    risk_analyzer: DeadlineRiskAnalyzer,
    queue_service: Optional[TaskQueueService] = None,
) -> None:
    """Render the Smart Scheduling & Deadline Risk Analyzer interface."""
    st.subheader("🧠 Smart Scheduling & Deadline Risk Analyzer (CO1 + CO5)")
    st.markdown(
        "Leverage custom **Binary Min-Heap Priority Queues (CO1)** and "
        "**Directed Graph Traversal (CO5)** to dynamically prioritize ready tasks "
        "and diagnose deadline bottlenecks without heuristics or probabilistic models."
    )

    # Architectural Comparison Callout: FIFO vs Smart Heap
    with st.expander("💡 Architectural Insight: FIFO Dispatch Queue vs. Smart Heap Auto-Scheduler", expanded=False):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                """
                **🔄 FIFO Processing Queue (Phase 02 & 05)**
                - **Data Structure:** Custom Doubly-Linked / Circular `Queue` ($O(1)$ enqueue & dequeue).
                - **Strategy:** Strict arrival chronological order (`created_at ASC, id ASC`).
                - **Purpose:** Fair, predictable first-come-first-served background task dispatching.
                - **State:** Operates independently of priority attributes.
                """
            )
        with col_c2:
            st.markdown(
                r"""
                **⚡ Smart Heap Auto-Scheduler (Phase 07)**
                - **Data Structure:** Custom Generic Binary `PriorityQueue` (Min-Heap, $O(\log N)$ push/pop).
                - **Strategy:** Dynamic multi-criteria tuple: `(-priority, has_deadline, deadline, duration, id)`.
                - **Purpose:** Optimizes project throughput and business impact.
                - **Coexistence:** Reads SQLite independently; neither queue mutates or overwrites the other.
                """
            )

    tab_scheduler, tab_risk = st.tabs(
        [
            "⚡ Smart Auto-Scheduler (Heap Engine)",
            "🛡️ Deadline Risk Analyzer",
        ]
    )

    # ---------------------------------------------------------
    # TAB 1: Smart Auto-Scheduler
    # ---------------------------------------------------------
    with tab_scheduler:
        st.markdown("### 🎯 Heap-Ranked Task Recommendations")
        st.caption("Eligible tasks (Pending status with all prerequisites satisfied) ranked via Binary Min-Heap.")

        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            if st.button("🔄 Recalculate Schedule", type="primary", use_container_width=True):
                st.rerun()

        schedule_result = scheduler.get_smart_schedule()

        # Handle Circular Dependency Cycle
        if not schedule_result.is_valid:
            st.error(
                f"🚨 **Scheduling Deadlock Aborted!**\n\n"
                f"{schedule_result.error_message}\n\n"
                f"*Action Required: Open the **🔗 Dependency Map (CO5)** view to resolve or remove the circular dependency.*"
            )
            return

        # Metrics Row
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Project Tasks", schedule_result.total_tasks_count)
        m2.metric("Eligible to Start", schedule_result.eligible_count)
        m3.metric("Blocked by Prereqs", schedule_result.blocked_count)
        m4.metric("In Progress", schedule_result.in_progress_count)
        m5.metric("Completed", schedule_result.completed_count)

        st.markdown("---")

        # Top Recommendation Highlight
        if schedule_result.recommended_task:
            top = schedule_result.recommended_task
            st.markdown(
                f"""
                <div style="background-color: rgba(33, 150, 243, 0.1); border-left: 5px solid #2196f3; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 8px 0; color: #64b5f6;">🎯 Top Recommended Task: #{top.id} — {top.title}</h3>
                    <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Priority:</strong> <span style="color: #ff9800;">{top.priority_label}</span> &nbsp;|&nbsp; <strong>Duration:</strong> {top.duration} min &nbsp;|&nbsp; <strong>Due Date:</strong> {top.due_date.strftime('%Y-%m-%d %H:%M') if top.due_date else 'None'}</p>
                    <p style="margin: 0; color: #b0bec5; font-size: 13px;"><em>💡 Justification:</em> {schedule_result.recommendation_reason}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info(f"ℹ️ {schedule_result.recommendation_reason}")

        # Ranked Schedule List
        if schedule_result.ranked_tasks:
            st.markdown("#### 📋 Recommended Execution Sequence")
            for idx, item in enumerate(schedule_result.ranked_tasks):
                t = item.task
                due_display = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else "No Deadline"
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #1a2234; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #2d3748;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 15px; font-weight: bold; color: #ffffff;">
                                    <span style="color: #4fc3f7;">#{idx + 1}</span> &nbsp; Task #{t.id}: {t.title}
                                </span>
                                <span style="background-color: #2b394e; padding: 4px 10px; border-radius: 12px; font-size: 12px; color: #ffb74d;">
                                    {t.priority_label}
                                </span>
                            </div>
                            <div style="font-size: 12px; color: #90a4ae; margin-top: 4px;">
                                ⏱️ {t.duration} min &nbsp;•&nbsp; 📅 Due: {due_display} &nbsp;•&nbsp; 🔍 <em>{item.explanation}</em>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Blocked Tasks Expander
        if schedule_result.blocked_tasks_info:
            st.markdown("---")
            with st.expander(f"🔒 Blocked Tasks Waiting on Incomplete Prerequisites ({len(schedule_result.blocked_tasks_info)})", expanded=True):
                st.caption("These pending tasks are currently held back until their prerequisite tasks complete:")
                for b_info in schedule_result.blocked_tasks_info:
                    b_task: Task = b_info["task"]
                    blocking = b_info["blocking_prerequisites"]
                    b_prereq_str = ", ".join(f"#{p.id} '{p.title}' ({p.status})" for p in blocking)
                    st.markdown(
                        f"- **#{b_task.id} {b_task.title}** ({b_task.priority_label}): Waiting on {b_prereq_str}"
                    )

    # ---------------------------------------------------------
    # TAB 2: Deadline Risk Analyzer
    # ---------------------------------------------------------
    with tab_risk:
        st.markdown("### 🛡️ Deterministic Deadline Risk Analyzer")
        st.caption(
            "Rigorous rule-based risk evaluation: Completed > Overdue > At Risk > Unscheduled > Safe. "
            "Evaluates slack time = (Time Remaining - Duration) and incomplete prerequisite dependencies."
        )

        now = datetime.now()
        risk_summary = risk_analyzer.analyze_all(current_time=now)

        # Metric summary row
        c_tot, c_safe, c_risk, c_due, c_unsched, c_block = st.columns(6)
        c_tot.metric("Total Analyzed", risk_summary.total_tasks)
        c_safe.metric("🟢 Safe", risk_summary.safe_count)
        c_risk.metric("🟡 At Risk", risk_summary.at_risk_count)
        c_due.metric("🔴 Overdue", risk_summary.overdue_count)
        c_unsched.metric("⚪ Unscheduled", risk_summary.unscheduled_count)
        c_block.metric("🔒 Blocked", risk_summary.blocked_count)

        # Filter controls
        st.markdown("---")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            category_filter = st.selectbox(
                "Filter by Risk Category:",
                options=["All Categories", "Safe", "At Risk", "Overdue", "Unscheduled", "Completed"],
                index=0,
            )
        with col_f2:
            show_blocked_only = st.checkbox("Show Blocked Tasks Only", value=False)

        # Apply filters
        filtered_assessments = risk_summary.assessments
        if category_filter != "All Categories":
            filtered_assessments = [a for a in filtered_assessments if a.category.value == category_filter]
        if show_blocked_only:
            filtered_assessments = [a for a in filtered_assessments if a.is_blocked]

        # Table Display
        if not filtered_assessments:
            st.info("No tasks match the active filters.")
        else:
            table_rows = []
            for a in filtered_assessments:
                t = a.task
                time_rem_str = f"{a.time_remaining_minutes:.0f}m" if a.time_remaining_minutes is not None else "—"
                slack_str = f"{a.slack_minutes:+.0f}m" if a.slack_minutes is not None else "—"
                due_str = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else "None"

                # Emoji indicator for category
                cat_display = {
                    RiskCategory.SAFE: "🟢 Safe",
                    RiskCategory.AT_RISK: "🟡 At Risk",
                    RiskCategory.OVERDUE: "🔴 Overdue",
                    RiskCategory.UNSCHEDULED: "⚪ Unscheduled",
                    RiskCategory.COMPLETED: "✅ Completed",
                }.get(a.category, a.category.value)

                table_rows.append(
                    {
                        "ID": t.id,
                        "Title": t.title,
                        "Status": t.status,
                        "Priority": t.priority_label,
                        "Category": cat_display,
                        "Deadline": due_str,
                        "Duration": f"{t.duration}m",
                        "Time Remaining": time_rem_str,
                        "Slack (Buffer)": slack_str,
                        "Blocked?": "🔒 Yes" if a.is_blocked else "No",
                        "Diagnostic Explanation": a.explanation,
                    }
                )

            st.dataframe(
                table_rows,
                use_container_width=True,
                hide_index=True,
            )

        # Deep-Dive Inspector
        if risk_summary.assessments:
            st.markdown("---")
            st.markdown("#### 🔬 Task Risk Diagnostics Inspector")
            task_options = {a.task.id: a for a in risk_summary.assessments if a.task.id is not None}
            selected_id = st.selectbox(
                "Select a task to inspect in-depth calculations:",
                options=list(task_options.keys()),
                format_func=lambda tid: f"#{tid} — {task_options[tid].task.title} [{task_options[tid].category.value}]",
            )
            if selected_id:
                sel = task_options[selected_id]
                t = sel.task
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    st.markdown(
                        f"""
                        **Task Overview:**
                        - **Title:** #{t.id} {t.title}
                        - **Status:** `{t.status}`
                        - **Priority:** {t.priority_label}
                        - **Duration:** {t.duration} minutes
                        - **Deadline:** {t.due_date.strftime('%Y-%m-%d %H:%M') if t.due_date else 'None'}
                        """
                    )
                with col_d2:
                    st.markdown(
                        f"""
                        **Timing & Slack Diagnostics:**
                        - **Risk Category:** **{sel.category.value}**
                        - **Time Remaining:** {f"{sel.time_remaining_minutes:.1f} minutes" if sel.time_remaining_minutes is not None else 'N/A'}
                        - **Slack (Buffer):** {f"{sel.slack_minutes:+.1f} minutes" if sel.slack_minutes is not None else 'N/A'}
                        - **Blocked by Prerequisites:** {'Yes' if sel.is_blocked else 'No'}
                        """
                    )

                st.info(f"**Diagnostic Justification:** {sel.explanation}")

                if sel.blocking_prerequisites:
                    st.warning(
                        f"🔒 **Incomplete Prerequisites:** {', '.join(f'#{p.id} {p.title} ({p.status})' for p in sel.blocking_prerequisites)}"
                    )
