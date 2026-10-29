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


def draw_critical_path_gantt(result: CriticalPathResult) -> plt.Figure:
    """Render a Gantt-style timeline visualization of earliest task schedules."""
    fig, ax = plt.subplots(figsize=(10, max(4.0, len(result.schedule_details) * 0.55)), dpi=120)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    tasks_ordered = [result.schedule_details[tid] for tid in result.topological_order if tid in result.schedule_details]
    if not tasks_ordered:
        ax.text(0.5, 0.5, "No tasks to display", color="#8b949e", ha="center", va="center")
        return fig

    y_positions = list(range(len(tasks_ordered)))[::-1]

    for y, item in zip(y_positions, tasks_ordered):
        t = item.task
        start = item.earliest_start
        duration = max(1, item.duration_minutes)
        is_crit = item.is_on_critical_path

        bar_color = "#e53935" if is_crit else "#1e88e5"
        edge_color = "#ff8a80" if is_crit else "#90caf9"

        # Draw task duration bar
        rect = patches.Rectangle(
            (start, y - 0.25),
            duration,
            0.5,
            linewidth=1.5,
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
            color="#ffffff",
            fontsize=9,
            fontweight="bold" if is_crit else "normal",
            ha="center",
            va="center",
            zorder=4,
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"#{item.task.id}" for item in tasks_ordered], color="#c9d1d9", fontsize=9)
    ax.set_xlabel("Elapsed Timeline (Minutes from Project Start)", color="#c9d1d9", fontsize=10, labelpad=8)
    ax.tick_params(colors="#8b949e", which="both")
    ax.grid(axis="x", color="#30363d", linestyle="--", alpha=0.7)

    # Vertical line at total duration
    if result.total_duration_minutes > 0:
        ax.axvline(
            result.total_duration_minutes,
            color="#ff5252",
            linestyle="-.",
            linewidth=1.8,
            label=f"Project Finish: {result.total_duration_minutes}m",
            zorder=2,
        )

    ax.set_xlim(-5, max(result.total_duration_minutes + 15, 60))
    ax.set_ylim(-1, len(tasks_ordered))

    legend_elements = [
        patches.Patch(facecolor="#e53935", edgecolor="#ff8a80", label="Critical Path Task"),
        patches.Patch(facecolor="#1e88e5", edgecolor="#90caf9", label="Non-Critical (Has Slack)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#21262d", edgecolor="#30363d", labelcolor="#c9d1d9")
    plt.tight_layout()
    return fig


def draw_what_if_comparison_chart(sim_result: WhatIfSimulationResult) -> plt.Figure:
    """Render a side-by-side timeline comparison of Baseline vs Simulated schedules."""
    fig, ax = plt.subplots(figsize=(10, max(4.0, len(sim_result.impacts) * 0.7)), dpi=120)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#161b22")

    if not sim_result.impacts:
        ax.text(0.5, 0.5, "No incomplete tasks simulated", color="#8b949e", ha="center", va="center")
        return fig

    impacts = sim_result.impacts[::-1]
    y_positions = list(range(len(impacts)))

    for y, imp in zip(y_positions, impacts):
        # Baseline bar (top half)
        b_rect = patches.Rectangle(
            (imp.baseline_start, y + 0.05),
            imp.duration_minutes,
            0.3,
            linewidth=1,
            edgecolor="#64b5f6",
            facecolor="#1565c0",
            alpha=0.75,
            zorder=3,
        )
        ax.add_patch(b_rect)

        # Simulated bar (bottom half)
        sim_color = "#ff7043" if imp.is_affected else "#4caf50"
        sim_edge = "#ffab91" if imp.is_affected else "#81c784"

        s_rect = patches.Rectangle(
            (imp.simulated_start, y - 0.35),
            imp.duration_minutes,
            0.3,
            linewidth=1.2,
            edgecolor=sim_edge,
            facecolor=sim_color,
            alpha=0.9,
            zorder=3,
        )
        ax.add_patch(s_rect)

        # Task title on the side
        marker = " ⚠️ Delayed" if imp.is_affected else ""
        ax.text(
            max(imp.baseline_finish, imp.simulated_finish) + 5,
            y,
            f"#{imp.task_id} {imp.task_title[:18]}{marker}",
            color="#ffab91" if imp.is_affected else "#c9d1d9",
            fontsize=8.5,
            va="center",
            zorder=4,
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"#{imp.task_id}" for imp in impacts], color="#c9d1d9", fontsize=9)
    ax.set_xlabel("Remaining Timeline (Minutes)", color="#c9d1d9", fontsize=10, labelpad=8)
    ax.tick_params(colors="#8b949e", which="both")
    ax.grid(axis="x", color="#30363d", linestyle="--", alpha=0.7)

    max_x = max(
        sim_result.simulated_project_duration,
        sim_result.baseline_project_duration,
        30,
    )
    ax.set_xlim(-5, max_x + 50)
    ax.set_ylim(-1, len(impacts))

    legend_elements = [
        patches.Patch(facecolor="#1565c0", edgecolor="#64b5f6", label="Baseline Schedule"),
        patches.Patch(facecolor="#ff7043", edgecolor="#ffab91", label="Simulated (Shifted)"),
        patches.Patch(facecolor="#4caf50", edgecolor="#81c784", label="Simulated (Unchanged)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#21262d", edgecolor="#30363d", labelcolor="#c9d1d9")
    plt.tight_layout()
    return fig


def render_planning_view(
    storage: TaskStorage,
    critical_path_service: CriticalPathService,
    what_if_simulator: WhatIfSimulatorService,
) -> None:
    """Render the Critical Path Analyzer & What-If Schedule Simulator page."""
    st.subheader("🗺️ Critical Path & What-If Planning (CO5)")
    st.markdown(
        "Model project timelines, compute the longest dependency chain (Critical Path), "
        "and simulate task delays in-memory with **guaranteed persistence safety**."
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
        st.markdown("### 🎯 Critical Path Analysis (DAG Longest Path)")
        st.caption(
            "Identifies the sequence of dependent tasks that determines minimum project duration. "
            "Computed via dynamic programming over Kahn's topological sort."
        )

        col_act1, col_act2 = st.columns([1, 4])
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

        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Project Duration", result.total_duration_formatted)
        m2.metric("Critical Path Length", f"{len(result.critical_path_ids)} tasks")
        m3.metric("Total Project Tasks", len(all_tasks))
        pct = (len(result.critical_path_ids) / len(all_tasks) * 100) if all_tasks else 0
        m4.metric("Critical Task Ratio", f"{pct:.0f}%")

        st.markdown("---")

        # Visual Critical Path Chain
        if result.critical_path_tasks:
            path_display = " &nbsp;➔&nbsp; ".join(
                f"<span style='background-color:#b71c1c; padding:3px 8px; border-radius:4px; font-weight:bold;'>#{t.id} {t.title} ({t.duration}m)</span>"
                for t in result.critical_path_tasks
            )
            st.markdown(
                f"""
                <div style="background-color: rgba(229, 57, 53, 0.12); border-left: 5px solid #e53935; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #ff8a80;">🎯 Critical Dependency Chain:</h4>
                    <div style="font-size: 14px; color: #ffffff; line-height: 1.8;">{path_display}</div>
                    <p style="margin: 10px 0 0 0; color: #b0bec5; font-size: 13px;"><em>💡 Impact:</em> {result.explanation}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("ℹ️ No tasks available to establish a critical path.")

        # Timeline Chart
        if result.schedule_details:
            st.markdown("#### 📊 Project Earliest Schedule (Gantt)")
            fig = draw_critical_path_gantt(result)
            st.pyplot(fig)
            plt.close(fig)

        # Schedule Table
        if result.schedule_details:
            st.markdown("#### 📋 Earliest Start & Finish Schedule Table")
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
                            "Duration": f"{t.duration} min",
                            "Earliest Start": f"{item.earliest_start} min",
                            "Earliest Finish": f"{item.earliest_finish} min",
                            "Critical Path?": "🔴 Critical" if item.is_on_critical_path else "⚪ Slack",
                            "Predecessor": f"#{item.predecessor_id}" if item.predecessor_id is not None else "None (Root)",
                        }
                    )
            st.dataframe(table_data, use_container_width=True, hide_index=True)

        # Algorithmic Complexity Expander
        with st.expander("🔬 Algorithm Mechanics: DAG Longest Path Dynamic Programming", expanded=False):
            st.markdown(
                r"""
                **How the Critical Path is Computed:**
                1. **Topological Order:** Tasks are processed in order of Kahn's Algorithm ($O(V + E)$).
                2. **Recurrence Relation:**
                   $$\text{Earliest Start}(v) = \max_{u \in \text{prereqs}(v)} \text{Earliest Finish}(u)$$
                   $$\text{Earliest Finish}(v) = \text{Earliest Start}(v) + \text{Duration}(v)$$
                3. **Project Duration:** $\max_{v \in V} \text{Earliest Finish}(v)$.
                4. **Backtracking:** The path is reconstructed by following predecessor pointers from the task achieving maximum finish back to the root.
                5. **Parallel Tasks:** Independent tasks run concurrently; only the longest prerequisite branch determines completion time.
                """
            )

    # ------------------------------------------------------------------
    # TAB 2: What-If Schedule Simulator
    # ------------------------------------------------------------------
    with tab_sim:
        st.markdown("### 🔮 What-If Schedule Simulator")
        st.caption(
            "Hypothetically delay an incomplete task to assess downstream ripple effects and project completion delays. "
            "Evaluates slack absorption across parallel branches."
        )

        # Safety Banner
        st.info(
            "🛡️ **Simulation Only — Saved Task Data Will Not Change.**\n\n"
            "This simulation runs entirely in memory on isolated calculation models. "
            "No database records, deadlines, durations, dependencies, or undo histories are modified."
        )

        incomplete_tasks = [t for t in storage.list_tasks() if t.status != TaskStatus.COMPLETED.value and t.id is not None]

        if not incomplete_tasks:
            st.success("🎉 All tasks in the project are already Completed! Nothing to simulate.")
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
                st.error(f"🚨 Simulation Error: {sim_res.error_message}")
                return

            # Display Simulation Metrics
            st.markdown("---")
            m_b, m_s, m_diff, m_aff = st.columns(4)
            m_b.metric("Baseline Remaining Time", format_duration(sim_res.baseline_project_duration))
            m_s.metric("Simulated Remaining Time", format_duration(sim_res.simulated_project_duration))

            if sim_res.project_delay_increase > 0:
                m_diff.metric(
                    "Project Delay Impact",
                    f"+{sim_res.project_delay_increase} min",
                    delta=f"-{sim_res.project_delay_increase}m delay",
                    delta_color="inverse",
                )
            else:
                m_diff.metric(
                    "Project Delay Impact",
                    "+0 min (Absorbed)",
                    delta="Slack absorbed",
                    delta_color="normal",
                )

            m_aff.metric("Downstream Affected", f"{len(sim_res.affected_task_ids)} tasks")

            # Result Explanation Callout
            if sim_res.project_delay_increase > 0:
                st.warning(f"⚠️ **Schedule Impact:** {sim_res.explanation}")
            else:
                st.success(f"🟢 **No Project Delay:** {sim_res.explanation}")

            # Gantt / Timeline Comparison Chart
            st.markdown("#### 📊 Schedule Comparison Timeline (Baseline vs Simulated)")
            fig_comp = draw_what_if_comparison_chart(sim_res)
            st.pyplot(fig_comp)
            plt.close(fig_comp)

            # Comparison Table
            st.markdown("#### 📋 Detailed Task Impact Comparison")
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
                        "Impact": "🔴 Shifted" if imp.is_affected else "🟢 Unchanged",
                    }
                )

            st.dataframe(comp_table, use_container_width=True, hide_index=True)
