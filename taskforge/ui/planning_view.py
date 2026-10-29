"""Planning View UI: Critical Path Analyzer and What-If Schedule Simulator (CO5).

Provides interactive tools to:
1. Identify the longest dependency chain (Critical Path) and calculate total project duration.
2. Simulate hypothetical task delays in-memory with zero mutation of persistent data.
"""

from __future__ import annotations

from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import streamlit as st

from taskforge.models import Task, TaskStatus
from taskforge.services.critical_path import (
    CriticalPathResult,
    CriticalPathService,
    format_duration,
)
from taskforge.services.what_if_simulator import (
    WhatIfSimulationResult,
    WhatIfSimulatorService,
)
from taskforge.storage import TaskStorage
from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_BRAND,
    COLOR_CORAL,
    COLOR_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    render_metric_strip,
    render_pill,
    render_section_header,
    style_potadot_ax,
)


def draw_critical_path_gantt(result: CriticalPathResult) -> plt.Figure:
    """Render a Gantt-style timeline visualization of earliest task schedules in light mode."""
    fig, ax = plt.subplots(figsize=(10, max(4.0, len(result.schedule_details) * 0.52)), dpi=120)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    tasks_ordered = [result.schedule_details[tid] for tid in result.topological_order if tid in result.schedule_details]
    if not tasks_ordered:
        ax.text(0.5, 0.5, "No tasks to display", color="#64748B", ha="center", va="center")
        return fig

    y_positions = list(range(len(tasks_ordered)))[::-1]

    for y, item in zip(y_positions, tasks_ordered):
        t = item.task
        start = item.earliest_start
        duration = max(1, item.duration_minutes)
        is_crit = item.is_on_critical_path

        bar_color = "#EF4444" if is_crit else "#93C5FD"
        edge_color = "#DC2626" if is_crit else "#3B82F6"

        # Draw task duration bar
        rect = patches.Rectangle(
            (start, y - 0.22),
            duration,
            0.44,
            linewidth=1.2,
            edgecolor=edge_color,
            facecolor=bar_color,
            alpha=0.9,
            zorder=3,
        )
        ax.add_patch(rect)

        # Label inside or beside bar
        label_text = f"#{t.id} {t.title} ({duration}m)"
        ax.text(
            start + duration / 2,
            y,
            label_text,
            color="#FFFFFF" if is_crit else "#0F172A",
            fontsize=8.5,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=4,
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"#{item.task.id}" for item in tasks_ordered], color="#475569", fontsize=8.5)
    style_potadot_ax(ax, title="Project Earliest Start / Finish Timeline", xlabel="Elapsed Minutes from Project Inception", ylabel="Tasks")

    # Vertical line at total duration
    if result.total_duration_minutes > 0:
        ax.axvline(
            result.total_duration_minutes,
            color="#2563EB",
            linestyle="-.",
            linewidth=1.8,
            label=f"Project Finish: {result.total_duration_minutes}m",
            zorder=2,
        )

    ax.set_xlim(-5, max(result.total_duration_minutes + 15, 60))
    ax.set_ylim(-1, len(tasks_ordered))

    legend_elements = [
        patches.Patch(facecolor="#EF4444", edgecolor="#DC2626", label="Critical Path Task (Zero Float)"),
        patches.Patch(facecolor="#93C5FD", edgecolor="#3B82F6", label="Non-Critical (Has Slack)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#FFFFFF", edgecolor="#E2E8F0", labelcolor="#0F172A", fontsize=8.5)
    plt.tight_layout()
    return fig


def draw_what_if_comparison_chart(sim_result: WhatIfSimulationResult) -> plt.Figure:
    """Render a side-by-side timeline comparison of Baseline vs Simulated schedules in light mode."""
    fig, ax = plt.subplots(figsize=(10, max(4.0, len(sim_result.impacts) * 0.65)), dpi=120)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    if not sim_result.impacts:
        ax.text(0.5, 0.5, "No incomplete tasks simulated", color="#64748B", ha="center", va="center")
        return fig

    impacts = sim_result.impacts[::-1]
    y_positions = list(range(len(impacts)))

    for y, imp in zip(y_positions, impacts):
        # Baseline bar (top half)
        b_rect = patches.Rectangle(
            (imp.baseline_start, y + 0.05),
            imp.duration_minutes,
            0.28,
            linewidth=1,
            edgecolor="#3B82F6",
            facecolor="#93C5FD",
            alpha=0.85,
            zorder=3,
        )
        ax.add_patch(b_rect)

        # Simulated bar (bottom half)
        sim_color = "#FCA5A5" if imp.is_affected else "#A7F3D0"
        sim_edge = "#EF4444" if imp.is_affected else "#10B981"

        s_rect = patches.Rectangle(
            (imp.simulated_start, y - 0.33),
            imp.duration_minutes,
            0.28,
            linewidth=1.2,
            edgecolor=sim_edge,
            facecolor=sim_color,
            alpha=0.9,
            zorder=3,
        )
        ax.add_patch(s_rect)

        # Task title on the side
        marker = " ⚠ Delayed" if imp.is_affected else ""
        ax.text(
            max(imp.baseline_finish, imp.simulated_finish) + 5,
            y,
            f"#{imp.task_id} {imp.task_title[:18]}{marker}",
            color="#EF4444" if imp.is_affected else "#475569",
            fontsize=8.2,
            fontweight="bold" if imp.is_affected else "normal",
            va="center",
            zorder=4,
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"#{imp.task_id}" for imp in impacts], color="#475569", fontsize=8.5)
    style_potadot_ax(ax, title="Remaining Timeline Comparison (Baseline vs Simulated)", xlabel="Remaining Minutes", ylabel="Tasks")

    max_x = max(
        sim_result.simulated_project_duration,
        sim_result.baseline_project_duration,
        30,
    )
    ax.set_xlim(-5, max_x + 50)
    ax.set_ylim(-1, len(impacts))

    legend_elements = [
        patches.Patch(facecolor="#93C5FD", edgecolor="#3B82F6", label="Baseline Schedule"),
        patches.Patch(facecolor="#FCA5A5", edgecolor="#EF4444", label="Simulated (Shifted Downstream)"),
        patches.Patch(facecolor="#A7F3D0", edgecolor="#10B981", label="Simulated (Slack Absorbed / Unchanged)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#FFFFFF", edgecolor="#E2E8F0", labelcolor="#0F172A", fontsize=8.5)
    plt.tight_layout()
    return fig


def render_planning_view(
    storage: TaskStorage,
    critical_path_service: CriticalPathService,
    what_if_simulator: WhatIfSimulatorService,
) -> None:
    """Render the Critical Path Analyzer & What-If Schedule Simulator page."""
    render_section_header(
        eyebrow="COURSE OUTCOME 5 (CO5) • CRITICAL PATH & SIMULATION",
        title="Critical Path Analyzer & What-If Planning Studio",
        subtitle="Model project completion timelines, identify the longest dependency chain via DAG dynamic programming, and simulate delay ripple effects in-memory with guaranteed database persistence safety.",
    )

    tab_cp, tab_sim = st.tabs(
        [
            "⛓️ Critical Path Analyzer",
            "🔮 What-If Schedule Simulator",
        ]
    )

    # ------------------------------------------------------------------
    # TAB 1: Critical Path Analyzer
    # ------------------------------------------------------------------
    with tab_cp:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Critical Path Analysis (DAG Longest Path)
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Identifies the sequence of dependent tasks that strictly dictates total project duration. Computed via single-pass dynamic programming over Kahn's topological sort.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_act1, _ = st.columns([2, 5])
        with col_act1:
            if st.button("🔄 Recalculate Critical Path", type="primary", use_container_width=True):
                st.rerun()

        result = critical_path_service.calculate_critical_path()

        if not result.is_valid:
            st.error(
                f"🚨 **Critical Path Analysis Aborted!**\n\n"
                f"{result.error_message}\n\n"
                f"*Action Required: Resolve the circular dependency in the **🔗 Dependency Map (CO5)**.*"
            )
            return

        all_tasks = storage.list_tasks()
        pct = (len(result.critical_path_ids) / len(all_tasks) * 100) if all_tasks else 0

        render_metric_strip([
            {"label": "Total Project Duration", "value": result.total_duration_formatted, "caption": "Minimum Completion Time"},
            {"label": "Critical Path Tasks", "value": f"{len(result.critical_path_ids)} tasks", "caption": "Longest Predecessor Chain"},
            {"label": "Total Tasks", "value": str(len(all_tasks)), "caption": "Persistent Project Tasks"},
            {"label": "Critical Task Ratio", "value": f"{pct:.0f}%", "caption": "Constrained Proportion"},
        ])

        # Visual Critical Path Chain
        if result.critical_path_tasks:
            path_display = " &nbsp;➔&nbsp; ".join(
                f"<span style='background-color:#FEF2F2; border: 1px solid #FECACA; padding:4px 10px; border-radius:4px; font-weight:600; font-family: JetBrains Mono; color: #B91C1C;'>#{t.id} {t.title} ({t.duration}m)</span>"
                for t in result.critical_path_tasks
            )
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #EF4444; padding: 1.2rem 1.4rem; border-radius: 8px; margin-bottom: 1.4rem; box-shadow: 0 1px 3px rgba(239,68,68,0.06);">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #EF4444; font-weight: 700; margin-bottom: 0.4rem;">
                        ● Critical Dependency Chain (Zero Float)
                    </div>
                    <div style="font-size: 0.95rem; color: #0F172A; line-height: 1.9; margin-bottom: 0.6rem;">{path_display}</div>
                    <div style="font-size: 0.86rem; color: #475569; border-top: 1px solid #F1F5F9; padding-top: 0.6rem;">
                        <strong style="color: #0F172A;">Algorithmic Assessment:</strong> {result.explanation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No tasks available to establish a critical path.")

        # Timeline Chart
        if result.schedule_details:
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.6rem;">Project Earliest Schedule Timeline (Gantt)</div>', unsafe_allow_html=True)
            fig = draw_critical_path_gantt(result)
            st.pyplot(fig)
            plt.close(fig)

        # Schedule Table
        if result.schedule_details:
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 1.2rem 0 0.6rem 0;">Earliest Start & Finish Schedule Table</div>', unsafe_allow_html=True)
            table_data = []
            for tid in result.topological_order:
                if tid in result.schedule_details:
                    item = result.schedule_details[tid]
                    t = item.task
                    table_data.append(
                        {
                            "Task ID": t.id,
                            "Title": t.title,
                            "Priority": t.priority_label,
                            "Status": t.status,
                            "Duration": f"{t.duration}m",
                            "Earliest Start": f"{item.earliest_start}m",
                            "Earliest Finish": f"{item.earliest_finish}m",
                            "Critical Path?": "Critical (Zero Slack)" if item.is_on_critical_path else "Non-Critical (Float)",
                            "Dominant Predecessor": f"#{item.predecessor_id}" if item.predecessor_id is not None else "None (Root)",
                        }
                    )
            st.dataframe(table_data, use_container_width=True, hide_index=True)

        # Algorithmic Complexity Expander
        with st.expander("🔬 Algorithm Mechanics: DAG Longest Path Dynamic Programming", expanded=False):
            st.markdown(
                r"""
                **How the Critical Path is Computed:**
                1. **Topological Order:** Tasks are sorted using Kahn's Algorithm ($O(V + E)$).
                2. **Recurrence Relation:**
                   $$\text{Earliest Start}(v) = \max_{u \in \text{prereqs}(v)} \text{Earliest Finish}(u)$$
                   $$\text{Earliest Finish}(v) = \text{Earliest Start}(v) + \text{Duration}(v)$$
                3. **Project Duration:** $\max_{v \in V} \text{Earliest Finish}(v)$.
                4. **Backtracking:** Follows dominant predecessor pointers backwards from terminal max finish task.
                5. **Parallel Tasks:** Independent branches execute concurrently; shorter parallel branches possess slack float.
                """
            )

    # ------------------------------------------------------------------
    # TAB 2: What-If Schedule Simulator
    # ------------------------------------------------------------------
    with tab_sim:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                What-If Schedule Simulator
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Hypothetically delay an incomplete task to assess downstream ripple effects and project completion delays.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Safety Banner
        st.markdown(
            """
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 1rem 1.3rem; margin-bottom: 1.4rem; font-size: 0.88rem; color: #0F172A; box-shadow: 0 1px 3px rgba(37,99,235,0.06);">
                <strong style="color: #2563EB;">● Strict Persistence Safety Guaranteed:</strong> This simulation runs strictly on in-memory deep copies. Persistent SQLite records, deadlines, durations, dependencies, and undo histories remain 100% unaltered.
            </div>
            """,
            unsafe_allow_html=True,
        )

        incomplete_tasks = [t for t in storage.list_tasks() if t.status != TaskStatus.COMPLETED.value and t.id is not None]

        if not incomplete_tasks:
            st.success("All tasks in the project are already Completed. Nothing to simulate.")
            return

        col_sel1, col_sel2 = st.columns([2, 2])
        with col_sel1:
            task_options = {t.id: f"#{t.id} {t.title} ({t.duration}m) [{t.status}]" for t in incomplete_tasks if t.id is not None}
            selected_id = st.selectbox(
                "Select Incomplete Task to Delay:",
                options=list(task_options.keys()),
                format_func=lambda tid: task_options[tid],
                key="what_if_selected_task",
            )
        with col_sel2:
            col_val, col_unit = st.columns([2, 1])
            with col_val:
                delay_input = st.number_input(
                    "Additional Delay:",
                    min_value=0,
                    value=30,
                    step=15,
                    key="what_if_delay_val",
                )
            with col_unit:
                unit = st.selectbox("Unit:", options=["Minutes", "Hours"], index=0, key="what_if_unit")

        delay_minutes = int(delay_input * 60) if unit == "Hours" else int(delay_input)

        if st.button("🚀 Run What-If Simulation", type="primary", use_container_width=True):
            sim_res = what_if_simulator.simulate_delay(
                task_id=selected_id,
                delay_minutes=delay_minutes,
            )

            if not sim_res.is_valid:
                st.error(f"Simulation Error: {sim_res.error_message}")
                return

            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            render_metric_strip([
                {"label": "Baseline Remaining", "value": format_duration(sim_res.baseline_project_duration), "caption": "Unshifted Schedule"},
                {"label": "Simulated Remaining", "value": format_duration(sim_res.simulated_project_duration), "caption": "Post-Delay Timeline"},
                {"label": "Project Delay Impact", "value": f"+{sim_res.project_delay_increase}m" if sim_res.project_delay_increase > 0 else "+0m", "caption": "Net Project Extension"},
                {"label": "Downstream Affected", "value": f"{len(sim_res.affected_task_ids)} tasks", "caption": "Propagated Delays"},
            ])

            if sim_res.project_delay_increase > 0:
                st.markdown(
                    f"""
                    <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 1.2rem; font-size: 0.88rem; color: #B91C1C;">
                        <strong>⚠ Schedule Impact:</strong> {sim_res.explanation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 4px solid #10B981; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 1.2rem; font-size: 0.88rem; color: #047857;">
                        <strong>● Slack Absorbed:</strong> {sim_res.explanation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Gantt / Timeline Comparison Chart
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.6rem;">Schedule Comparison Timeline (Baseline vs Simulated)</div>', unsafe_allow_html=True)
            fig_comp = draw_what_if_comparison_chart(sim_res)
            st.pyplot(fig_comp)
            plt.close(fig_comp)

            # Comparison Table
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 1.2rem 0 0.6rem 0;">Detailed Task Impact Comparison</div>', unsafe_allow_html=True)
            comp_table = []
            for imp in sim_res.impacts:
                comp_table.append(
                    {
                        "Task ID": imp.task_id,
                        "Title": imp.task_title,
                        "Status": imp.status,
                        "Duration": f"{imp.duration_minutes}m",
                        "Baseline Start": f"{imp.baseline_start}m",
                        "Baseline Finish": f"{imp.baseline_finish}m",
                        "Simulated Start": f"{imp.simulated_start}m",
                        "Simulated Finish": f"{imp.simulated_finish}m",
                        "Start Shift": f"+{imp.start_delay_minutes}m" if imp.start_delay_minutes > 0 else "0m",
                        "Finish Shift": f"+{imp.finish_delay_minutes}m" if imp.finish_delay_minutes > 0 else "0m",
                        "Impact State": "Shifted" if imp.is_affected else "Unchanged (Slack)",
                    }
                )

            st.dataframe(comp_table, use_container_width=True, hide_index=True)
