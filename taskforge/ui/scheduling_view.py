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
from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_CORAL,
    COLOR_LIME,
    COLOR_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    render_metric_strip,
    render_pill,
    render_section_header,
)


def render_scheduling_view(
    storage: TaskStorage,
    scheduler: SchedulerService,
    risk_analyzer: DeadlineRiskAnalyzer,
    queue_service: Optional[TaskQueueService] = None,
) -> None:
    """Render the Smart Scheduling & Deadline Risk Analyzer interface."""
    render_section_header(
        eyebrow="COURSE OUTCOMES 1 & 5 • SMART SCHEDULING & RISK",
        title="Smart Scheduling & Deadline Risk Studio",
        subtitle="Dynamically prioritize ready tasks using custom Binary Min-Heap Priority Queues and diagnose deadline bottlenecks with deterministic slack-time rule analysis.",
    )

    # Architectural Comparison Callout: FIFO vs Smart Heap
    with st.expander("💡 Architectural Insight: FIFO Dispatch Queue vs. Smart Heap Auto-Scheduler", expanded=False):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                """
                <div style="background-color: #171717; border: 1px solid #282828; border-radius: 3px; padding: 1.1rem 1.3rem;">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">
                        🔄 FIFO Processing Queue (Phase 02 & 05)
                    </div>
                    <ul style="color: #A6A49E; font-size: 0.85rem; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                        <li><strong>Data Structure:</strong> Custom Singly-Linked <code>Queue</code> ($O(1)$ operations).</li>
                        <li><strong>Strategy:</strong> Strict chronological arrival (<code>created_at ASC, id ASC</code>).</li>
                        <li><strong>Role:</strong> Fair, predictable background task dispatching without starvation.</li>
                        <li><strong>Behavior:</strong> Ignores priority and deadlines.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_c2:
            st.markdown(
                """
                <div style="background-color: #171717; border: 1px solid #282828; border-radius: 3px; padding: 1.1rem 1.3rem;">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #D7FF64; margin-bottom: 0.4rem;">
                        ⚡ Smart Heap Auto-Scheduler (Phase 07)
                    </div>
                    <ul style="color: #A6A49E; font-size: 0.85rem; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                        <li><strong>Data Structure:</strong> Custom Binary <code>PriorityQueue</code> ($O(\\log N)$ push/pop).</li>
                        <li><strong>Strategy:</strong> Multi-criteria tuple: <code>(-priority, has_deadline, deadline, duration, id)</code>.</li>
                        <li><strong>Role:</strong> Maximizes project throughput and business impact.</li>
                        <li><strong>Coexistence:</strong> Operates independently without corrupting persistent queue state.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
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
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Heap-Ranked Task Recommendations
            </div>
            <div style="font-size: 0.85rem; color: #A6A49E; margin-bottom: 1.2rem;">
                Eligible tasks (Pending status with all prerequisite dependencies satisfied) prioritized via Binary Min-Heap.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_act1, _ = st.columns([2, 5])
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

        render_metric_strip([
            {"label": "Total Tasks", "value": str(schedule_result.total_tasks_count), "caption": "Project Inventory"},
            {"label": "Eligible to Start", "value": str(schedule_result.eligible_count), "caption": "Heap Contenders"},
            {"label": "Blocked by Prereqs", "value": str(schedule_result.blocked_count), "caption": "Awaiting Ancestors"},
            {"label": "In Progress", "value": str(schedule_result.in_progress_count), "caption": "Active Work"},
            {"label": "Completed", "value": str(schedule_result.completed_count), "caption": "Finished Tasks"},
        ])

        # Top Recommendation Highlight
        if schedule_result.recommended_task:
            top = schedule_result.recommended_task
            due_str = top.due_date.strftime('%Y-%m-%d %H:%M') if top.due_date else 'No Deadline'
            st.markdown(
                f"""
                <div style="background-color: #1A1F16; border: 1px solid rgba(215, 255, 100, 0.4); border-radius: 3px; padding: 1.4rem 1.6rem; margin-bottom: 1.4rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #D7FF64; font-weight: 700; margin-bottom: 0.35rem;">
                        ● Top Recommended Task (#1 Rank in Min-Heap)
                    </div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.45rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.4rem;">
                        Task #{top.id}: {top.title}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #A6A49E; margin-bottom: 0.8rem;">
                        Priority: <strong style="color: #FFFFFF;">{top.priority_label}</strong> &bull; Duration: <strong style="color: #FFFFFF;">{top.duration}m</strong> &bull; Deadline: <strong style="color: #FFFFFF;">{due_str}</strong>
                    </div>
                    <div style="font-size: 0.88rem; color: #F3F1EB; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 0.75rem;">
                        <strong style="color: #D7FF64;">Algorithmic Justification:</strong> {schedule_result.recommendation_reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info(f"ℹ️ {schedule_result.recommendation_reason}")

        # Ranked Schedule List
        if schedule_result.ranked_tasks:
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.6rem;">Recommended Execution Sequence</div>', unsafe_allow_html=True)
            for idx, item in enumerate(schedule_result.ranked_tasks):
                t = item.task
                due_display = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else "No Deadline"
                st.markdown(
                    f"""
                    <div style="background-color: #1A1A1A; border: 1px solid #282828; padding: 10px 14px; border-radius: 3px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.95rem; font-weight: 600; color: #FFFFFF;">
                                <span style="font-family: JetBrains Mono; color: #D7FF64;">#{idx + 1}</span> &nbsp; Task #{t.id}: {t.title}
                            </span>
                            {render_pill(t.priority_label, variant='amber' if 'High' in t.priority_label or 'Urgent' in t.priority_label else 'muted')}
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #A6A49E; margin-top: 4px;">
                            Duration: {t.duration}m &bull; Deadline: {due_display} &bull; <em>{item.explanation}</em>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Blocked Tasks Expander
        if schedule_result.blocked_tasks_info:
            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            with st.expander(f"🔒 Blocked Tasks Waiting on Incomplete Prerequisites ({len(schedule_result.blocked_tasks_info)})", expanded=True):
                st.caption("These pending tasks are currently held back until their prerequisite tasks complete:")
                for b_info in schedule_result.blocked_tasks_info:
                    b_task: Task = b_info["task"]
                    blocking = b_info["blocking_prerequisites"]
                    b_prereq_str = ", ".join(f"#{p.id} '{p.title}' ({p.status})" for p in blocking)
                    st.markdown(
                        f"- <span style='font-family: JetBrains Mono; color: #F87171;'>#{b_task.id}</span> **{b_task.title}** ({b_task.priority_label}): Waiting on {b_prereq_str}",
                        unsafe_allow_html=True,
                    )

    # ---------------------------------------------------------
    # TAB 2: Deadline Risk Analyzer
    # ---------------------------------------------------------
    with tab_risk:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Deterministic Deadline Risk Analyzer
            </div>
            <div style="font-size: 0.85rem; color: #A6A49E; margin-bottom: 1.2rem;">
                Rule-based risk evaluation: Completed &gt; Overdue &gt; At Risk &gt; Unscheduled &gt; Safe. Evaluates <code>slack = (Time Remaining - Duration)</code> and incomplete dependencies.
            </div>
            """,
            unsafe_allow_html=True,
        )

        now = datetime.now()
        risk_summary = risk_analyzer.analyze_all(current_time=now)

        render_metric_strip([
            {"label": "Total Analyzed", "value": str(risk_summary.total_tasks), "caption": "Evaluated Tasks"},
            {"label": "Safe Buffer", "value": str(risk_summary.safe_count), "caption": "Slack > 0"},
            {"label": "At Risk", "value": str(risk_summary.at_risk_count), "caption": "Slack <= 0"},
            {"label": "Overdue", "value": str(risk_summary.overdue_count), "caption": "Past Deadline"},
            {"label": "Unscheduled", "value": str(risk_summary.unscheduled_count), "caption": "No Deadline"},
            {"label": "Blocked", "value": str(risk_summary.blocked_count), "caption": "Prereqs Pending"},
        ])

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            category_filter = st.selectbox(
                "Filter by Risk Category:",
                options=["All Categories", "Safe", "At Risk", "Overdue", "Unscheduled", "Completed"],
                index=0,
            )
        with col_f2:
            show_blocked_only = st.checkbox("Show Blocked Tasks Only", value=False)

        filtered_assessments = risk_summary.assessments
        if category_filter != "All Categories":
            filtered_assessments = [a for a in filtered_assessments if a.category.value == category_filter]
        if show_blocked_only:
            filtered_assessments = [a for a in filtered_assessments if a.is_blocked]

        if not filtered_assessments:
            st.info("No tasks match the active filters.")
        else:
            table_rows = []
            for a in filtered_assessments:
                t = a.task
                time_rem_str = f"{a.time_remaining_minutes:.0f}m" if a.time_remaining_minutes is not None else "—"
                slack_str = f"{a.slack_minutes:+.0f}m" if a.slack_minutes is not None else "—"
                due_str = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else "None"

                cat_display = {
                    RiskCategory.SAFE: "Safe",
                    RiskCategory.AT_RISK: "At Risk",
                    RiskCategory.OVERDUE: "Overdue",
                    RiskCategory.UNSCHEDULED: "Unscheduled",
                    RiskCategory.COMPLETED: "Completed",
                }.get(a.category, a.category.value)

                table_rows.append(
                    {
                        "ID": t.id,
                        "Title": t.title,
                        "Status": t.status,
                        "Priority": t.priority_label,
                        "Risk Category": cat_display,
                        "Deadline": due_str,
                        "Duration": f"{t.duration}m",
                        "Time Remaining": time_rem_str,
                        "Slack Buffer": slack_str,
                        "Blocked?": "Yes" if a.is_blocked else "No",
                        "Explanation": a.explanation,
                    }
                )

            st.dataframe(table_rows, use_container_width=True, hide_index=True)

        # Deep-Dive Inspector
        if risk_summary.assessments:
            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.6rem;">🔬 Task Risk Diagnostics Inspector</div>', unsafe_allow_html=True)
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
                        <div style="background-color: #171717; border: 1px solid #282828; border-radius: 3px; padding: 1rem 1.2rem; font-size: 0.85rem; color: #A6A49E; line-height: 1.6;">
                            <strong style="color: #FFFFFF;">Task Metadata:</strong><br>
                            &bull; Title: <strong style="color: #FFFFFF;">#{t.id} {t.title}</strong><br>
                            &bull; Status: <code>{t.status}</code> &bull; Priority: {t.priority_label}<br>
                            &bull; Duration: {t.duration} minutes<br>
                            &bull; Deadline: {t.due_date.strftime('%Y-%m-%d %H:%M') if t.due_date else 'None'}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_d2:
                    st.markdown(
                        f"""
                        <div style="background-color: #171717; border: 1px solid #282828; border-radius: 3px; padding: 1rem 1.2rem; font-size: 0.85rem; color: #A6A49E; line-height: 1.6;">
                            <strong style="color: #FFFFFF;">Slack Diagnostics:</strong><br>
                            &bull; Risk Category: <strong style="color: #D7FF64;">{sel.category.value}</strong><br>
                            &bull; Time Remaining: {f"{sel.time_remaining_minutes:.1f}m" if sel.time_remaining_minutes is not None else 'N/A'}<br>
                            &bull; Slack Buffer: {f"{sel.slack_minutes:+.1f}m" if sel.slack_minutes is not None else 'N/A'}<br>
                            &bull; Blocked by Prerequisites: {'Yes' if sel.is_blocked else 'No'}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"""
                    <div style="background-color: #1A1F16; border: 1px solid rgba(215, 255, 100, 0.3); border-radius: 3px; padding: 0.9rem 1.1rem; margin-top: 0.8rem; font-size: 0.85rem; color: #F3F1EB;">
                        <strong style="color: #D7FF64;">Diagnostic Justification:</strong> {sel.explanation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if sel.blocking_prerequisites:
                    st.warning(
                        f"🔒 Incomplete Prerequisites: {', '.join(f'#{p.id} {p.title} ({p.status})' for p in sel.blocking_prerequisites)}"
                    )
