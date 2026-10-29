"""Dependency Map and Graph Algorithms visualization UI view (CO5)."""

from __future__ import annotations

from typing import Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import streamlit as st

from taskforge.graph.dependency_graph import (
    CycleDetectedError,
    DependencyGraph,
    InvalidDependencyError,
)
from taskforge.models import Task, TaskStatus
from taskforge.services.dependency_service import DependencyService
from taskforge.services.scheduler import SchedulerService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.storage import TaskStorage
from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_BRAND,
    COLOR_CORAL,
    COLOR_EMERALD,
    COLOR_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    render_metric_strip,
    render_pill,
    render_section_header,
)


def compute_node_positions(
    graph: DependencyGraph,
    tasks_by_id: dict[int, Task],
) -> dict[int, tuple[float, float]]:
    """Compute 2D coordinates for graph nodes using topological layering.
    
    Places prerequisite nodes on the left and dependent nodes on the right.
    """
    nodes = graph.get_nodes()
    if not nodes:
        return {}

    layers: dict[int, int] = {}
    try:
        topo_order = graph.topological_sort()
        for node in topo_order:
            prereqs = graph.get_prerequisites(node)
            if not prereqs:
                layers[node] = 0
            else:
                layers[node] = max(layers.get(p, 0) for p in prereqs) + 1
    except CycleDetectedError:
        for i, node in enumerate(nodes):
            layers[node] = i % 4

    layer_groups: dict[int, list[int]] = {}
    for node, layer in layers.items():
        layer_groups.setdefault(layer, []).append(node)

    positions: dict[int, tuple[float, float]] = {}
    for layer, group in layer_groups.items():
        count = len(group)
        for idx, node in enumerate(group):
            x = float(layer) * 3.0
            y = -(idx - (count - 1) / 2.0) * 2.0
            positions[node] = (x, y)

    return positions


def draw_dependency_graph(
    graph: DependencyGraph,
    tasks_by_id: dict[int, Task],
    scheduler: SchedulerService,
) -> plt.Figure:
    """Render a directed graph visualization using Potadot clean light styling."""
    positions = compute_node_positions(graph, tasks_by_id)
    fig, ax = plt.subplots(figsize=(10, max(4.5, len(positions) * 0.7)), dpi=120)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    if not positions:
        ax.text(
            0.5, 0.5, "No tasks or dependencies in graph.\nAdd tasks and dependencies to visualize.",
            color="#64748B", fontsize=11, ha="center", va="center", transform=ax.transAxes
        )
        ax.axis("off")
        return fig

    # Draw directed edges (arrows)
    edges = graph.get_edges()
    for prereq, dep in edges:
        if prereq in positions and dep in positions:
            x1, y1 = positions[prereq]
            x2, y2 = positions[dep]
            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color="#94A3B8",
                    lw=1.8,
                    mutation_scale=14,
                    shrinkA=22,
                    shrinkB=22,
                    alpha=0.9,
                ),
            )

    # Status color map
    for node, (x, y) in positions.items():
        task = tasks_by_id.get(node)
        status = task.status if task else "Pending"
        is_eligible = scheduler.is_task_eligible(node)

        if status == TaskStatus.COMPLETED.value:
            node_color = "#10B981"
            border_color = "#047857"
            text_color = "#FFFFFF"
            status_text = "Completed"
        elif status == TaskStatus.IN_PROGRESS.value:
            node_color = "#2563EB"
            border_color = "#1D4ED8"
            text_color = "#FFFFFF"
            status_text = "In Progress"
        elif is_eligible:
            node_color = "#F8FAFC"
            border_color = "#2563EB"
            text_color = "#0F172A"
            status_text = "Eligible"
        else:
            node_color = "#FEF2F2"
            border_color = "#EF4444"
            text_color = "#991B1B"
            status_text = "Blocked"

        # Draw node circle
        circle = patches.Circle(
            (x, y),
            radius=0.52,
            facecolor=node_color,
            edgecolor=border_color,
            linewidth=2.0,
            zorder=3,
        )
        ax.add_patch(circle)

        # Node label (ID)
        ax.text(
            x, y + 0.04,
            f"#{node}",
            color=text_color,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=4,
        )

        # Status text inside or below circle
        status_sub_color = "#FFFFFF" if status in [TaskStatus.COMPLETED.value, TaskStatus.IN_PROGRESS.value] else text_color
        ax.text(
            x, y - 0.22,
            status_text,
            color=status_sub_color,
            fontsize=6.5,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=4,
        )

        # Task title caption below node
        title_str = task.title if task else f"Task {node}"
        if len(title_str) > 18:
            title_str = title_str[:16] + ".."
        ax.text(
            x, y - 0.72,
            title_str,
            color="#0F172A",
            fontsize=8,
            fontweight="bold",
            ha="center",
            va="top",
            zorder=4,
        )

    # Margins and axis cleanup
    xs = [pos[0] for pos in positions.values()]
    ys = [pos[1] for pos in positions.values()]
    x_min, x_max = min(xs) - 1.2, max(xs) + 1.2
    y_min, y_max = min(ys) - 1.2, max(ys) + 1.0

    ax.set_xlim(x_min, max(x_max, x_min + 3.0))
    ax.set_ylim(y_min, y_max)
    ax.axis("off")
    plt.tight_layout()
    return fig


def render_dependency_view(
    storage: TaskStorage,
    dep_service: DependencyService,
    scheduler: SchedulerService,
    queue_service: TaskQueueService,
) -> None:
    """Render the full Dependency Map and Graph Traversal module (CO5)."""
    render_section_header(
        eyebrow="COURSE OUTCOME 5 (CO5) • GRAPH DATA STRUCTURES",
        title="Task Dependency Map & Graph Studio",
        subtitle="Model task prerequisites using an Adjacency-List Directed Acyclic Graph (DAG). Enforces cycle deadlock rejection via 3-color DFS and computes deterministic dispatch sequences via Kahn's algorithm.",
    )

    # Always ensure graph is synchronized with SQLite
    dep_service.rebuild()
    graph = dep_service.get_graph()
    tasks = storage.list_tasks()
    tasks_by_id = {t.id: t for t in tasks if t.id is not None}

    # Summary Metric Strip
    is_dag = graph.is_acyclic()
    eligible_tasks = scheduler.get_eligible_pending_tasks()
    blocked_tasks = scheduler.get_blocked_tasks()

    render_metric_strip([
        {"label": "Graph Nodes (|V|)", "value": str(graph.node_count()), "caption": "Task Vertices"},
        {"label": "Dependencies (|E|)", "value": str(graph.edge_count()), "caption": "Directed Constraints"},
        {"label": "Graph Topology", "value": "Acyclic DAG" if is_dag else "Cycle Present", "caption": "3-Color DFS"},
        {"label": "Ready to Start", "value": str(len(eligible_tasks)), "caption": "Prereqs Satisfied"},
        {"label": "Blocked Tasks", "value": str(len(blocked_tasks)), "caption": "Awaiting Prereqs"},
    ])

    # Dependency Management & Visual Graph Tabs
    tab_map, tab_manage, tab_topo, tab_traverse, tab_sandbox = st.tabs([
        "🗺️ Visual Graph",
        "➕ Manage Dependencies",
        "📊 Topological Order (Kahn's)",
        "🔍 BFS & DFS Traversal",
        "🧪 Cycle Simulator (Viva Demo)",
    ])

    # TAB 1: Visual Graph
    with tab_map:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Directed Dependency Visual Graph
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Arrows indicate execution flow: <code>Prerequisite ➔ Dependent</code> ($A \\to B$ means $A$ must complete before $B$ can start).
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        col_l1.markdown(f"{render_pill('Completed', 'lime')}", unsafe_allow_html=True)
        col_l2.markdown(f"{render_pill('In Progress', 'blue')}", unsafe_allow_html=True)
        col_l3.markdown(f"{render_pill('Eligible (Ready)', 'muted')}", unsafe_allow_html=True)
        col_l4.markdown(f"{render_pill('Blocked by Prereq', 'coral')}", unsafe_allow_html=True)

        fig = draw_dependency_graph(graph, tasks_by_id, scheduler)
        st.pyplot(fig)
        plt.close(fig)

        # Adjacency List Inspection
        with st.expander("📋 View Raw Adjacency List & Degrees Table"):
            if not tasks:
                st.info("No tasks recorded.")
            else:
                table_rows = []
                for t in tasks:
                    assert t.id is not None
                    prereqs = graph.get_prerequisites(t.id)
                    deps = graph.get_dependents(t.id)
                    prereq_titles = [f"#{pid} ({tasks_by_id[pid].title})" for pid in prereqs if pid in tasks_by_id]
                    dep_titles = [f"#{did} ({tasks_by_id[did].title})" for did in deps if did in tasks_by_id]
                    status_badge = "Ready" if scheduler.is_task_eligible(t.id) else ("Blocked" if t.status == TaskStatus.PENDING.value else t.status)
                    table_rows.append({
                        "Task ID": t.id,
                        "Title": t.title,
                        "Status": t.status,
                        "Eligibility": status_badge,
                        "In-Degree (Prereqs)": graph.in_degree(t.id),
                        "Out-Degree (Dependents)": graph.out_degree(t.id),
                        "Prerequisites": ", ".join(prereq_titles) if prereq_titles else "None (Root)",
                        "Dependents": ", ".join(dep_titles) if dep_titles else "None (Terminal)",
                    })
                st.dataframe(table_rows, use_container_width=True)

    # TAB 2: Manage Dependencies
    with tab_manage:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Dependency Registration & Constraint Management
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Specify that Task B requires Task A. All additions are pre-tested with 3-color DFS cycle validation.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if len(tasks) < 2:
            st.warning("You need at least 2 tasks in the system to create dependencies.")
        else:
            task_options = {t.id: f"#{t.id}: {t.title} [{t.status}]" for t in tasks if t.id is not None}
            task_ids = list(task_options.keys())

            col_add, col_del = st.columns(2)

            with col_add:
                st.markdown("#### ➕ Add Dependency")
                prereq_id = st.selectbox(
                    "1. Prerequisite Task (Task A — must complete first):",
                    options=task_ids,
                    format_func=lambda tid: task_options[tid],
                    key="select_prereq_task",
                )
                dep_id = st.selectbox(
                    "2. Dependent Task (Task B — depends on Task A):",
                    options=task_ids,
                    format_func=lambda tid: task_options[tid],
                    index=1 if len(task_ids) > 1 else 0,
                    key="select_dep_task",
                )

                if st.button("🔗 Add Dependency (A ➔ B)", type="primary", use_container_width=True):
                    try:
                        dep_service.add_dependency(prereq_id, dep_id)
                        queue_service.refresh()
                        st.success(f"Added dependency: Task #{prereq_id} ➔ Task #{dep_id}")
                        st.rerun()
                    except InvalidDependencyError as ide:
                        st.error(f"Invalid Dependency: {ide}")
                    except CycleDetectedError as cde:
                        st.error(f"Cycle Prevention: {cde}")

            with col_del:
                st.markdown("#### 🗑️ Registered Dependencies")
                dependencies = storage.get_dependencies()
                if not dependencies:
                    st.info("No dependencies currently registered.")
                else:
                    for prereq, dep in dependencies:
                        col_text, col_btn = st.columns([4, 1])
                        t_prereq = tasks_by_id.get(prereq)
                        t_dep = tasks_by_id.get(dep)
                        prereq_title = t_prereq.title if t_prereq else f"#{prereq}"
                        dep_title = t_dep.title if t_dep else f"#{dep}"

                        with col_text:
                            st.markdown(f"<span style='font-family: JetBrains Mono; font-size: 0.88rem; color: #0F172A;'>#{prereq} ({prereq_title}) ➔ #{dep} ({dep_title})</span>", unsafe_allow_html=True)
                        with col_btn:
                            if st.button("Remove", key=f"del_dep_{prereq}_{dep}", use_container_width=True):
                                dep_service.remove_dependency(prereq, dep)
                                queue_service.refresh()
                                st.success(f"Removed dependency #{prereq} ➔ #{dep}")
                                st.rerun()

    # TAB 3: Topological Order
    with tab_topo:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Topological Task Scheduling Order (Kahn's Algorithm)
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Arranges directed graph nodes in a linear sequence such that for every directed edge $A \\to B$, Task $A$ strictly precedes Task $B$.
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            topological_tasks = dep_service.get_topological_order()
            if not topological_tasks:
                st.info("No tasks to schedule.")
            else:
                for step, task in enumerate(topological_tasks, start=1):
                    assert task.id is not None
                    prereqs = graph.get_prerequisites(task.id)
                    prereq_desc = f"Depends on: {', '.join(f'#{p}' for p in prereqs)}" if prereqs else "Root Task (0 prerequisites)"
                    status_pill = render_pill(task.status, variant="lime" if task.status == "Completed" else "muted")

                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 3px solid #2563EB; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            <span style="font-family: JetBrains Mono; font-size: 0.72rem; color: #2563EB; font-weight: 700; text-transform: uppercase;">Step {step}</span> &bull; 
                            <strong style="color: #0F172A; font-size: 0.95rem;">Task #{task.id}: {task.title}</strong> {status_pill}<br/>
                            <small style="color: #64748B; font-family: JetBrains Mono; font-size: 0.75rem;">Priority: {task.priority_label} &bull; Duration: {task.duration}m &bull; {prereq_desc}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.1rem 1.3rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #475569;">
                        <strong style="color: #0F172A;">Kahn's Algorithm Execution State:</strong><br>
                        1. In-degrees: { {t.id: graph.in_degree(t.id) for t in tasks if t.id is not None} }<br>
                        2. Zero-indegree queue initial state: { [t.id for t in tasks if t.id is not None and graph.in_degree(t.id) == 0] }<br>
                        3. Linear FIFO dispatch sequence: { [t.id for t in topological_tasks] }<br>
                        4. All <strong>{graph.node_count()}</strong> nodes visited cleanly with zero cycle deadlocks.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except CycleDetectedError as err:
            st.error(f"Topological sorting failed: {err}")

    # TAB 4: Traversal Runner (BFS & DFS)
    with tab_traverse:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Graph Traversal Engine: BFS vs DFS
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Traverse the dependency hierarchy from any task root to inspect downstream dependents.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not tasks:
            st.info("No tasks available to traverse.")
        else:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                start_node_id = st.selectbox(
                    "Select Traversal Root Task:",
                    options=list(tasks_by_id.keys()),
                    format_func=lambda tid: f"#{tid}: {tasks_by_id[tid].title}",
                    key="traversal_start_node",
                )
            with col_t2:
                algo_choice = st.radio(
                    "Traversal Algorithm:",
                    options=[
                        "🌊 Breadth-First Search (BFS) [Queue-driven, Level-by-Level]",
                        "🧗 Depth-First Search (DFS) [Stack-driven, Deep Branching]",
                    ],
                )

            if st.button("🚀 Run Traversal", type="primary", use_container_width=True):
                if "BFS" in algo_choice:
                    visited_tasks = dep_service.run_bfs(start_node_id)
                    algo_name = "Breadth-First Search (BFS)"
                    ds_name = "Queue (FIFO)"
                else:
                    visited_tasks = dep_service.run_dfs(start_node_id)
                    algo_name = "Depth-First Search (DFS)"
                    ds_name = "Stack (LIFO)"

                st.success(f"Ran **{algo_name}** using custom **{ds_name}**. Visited {len(visited_tasks)} task(s).")

                st.markdown("#### Discovery Sequence:")
                cols = st.columns(min(max(len(visited_tasks), 1), 5))
                for i, v_task in enumerate(visited_tasks):
                    assert v_task.id is not None
                    with cols[i % len(cols)]:
                        st.markdown(
                            f"""
                            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px; text-align: center; margin-bottom: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                                <span style="font-family: JetBrains Mono; font-size: 0.68rem; color: #2563EB; font-weight: 700;">Step {i+1}</span><br/>
                                <strong style="color: #0F172A;">#{v_task.id}</strong><br/>
                                <small style="color: #64748B;">{v_task.title[:15]}</small>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # TAB 5: Interactive Cycle Detection Sandbox (Viva Demo)
    with tab_sandbox:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Interactive Circular Dependency Simulator (Viva Sandbox)
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Demonstrates <strong>3-Color DFS cycle detection</strong> in an isolated in-memory sandbox without mutating primary SQLite records.
            </div>
            """,
            unsafe_allow_html=True,
        )

        sim_col1, sim_col2 = st.columns([2, 1])

        with sim_col1:
            st.markdown(
                """
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #475569; line-height: 1.6;">
                    Hypothetical chain:<br>
                    &bull; <code>Task 101 (Database Schema)</code> ➔ <code>Task 102 (API Server)</code><br>
                    &bull; <code>Task 102 (API Server)</code> ➔ <code>Task 103 (Frontend Dashboard)</code><br>
                    Attempting to add: <code>Task 103 ➔ Task 101</code> creates a deadlocked cycle.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sim_col2:
            test_mode = st.button("🧪 Simulate Cycle Detection", use_container_width=True)

        if test_mode:
            sample_graph = DependencyGraph()
            sample_graph.add_edge(101, 102)
            sample_graph.add_edge(102, 103)

            would_cycle = sample_graph.would_create_cycle(103, 101)
            try:
                if would_cycle:
                    sample_graph._adj[103].add(101)
                    sample_graph._rev_adj[101].add(103)
                    has_cycle, cycle_path = sample_graph.detect_cycle()
                    st.markdown(
                        f"""
                        <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 8px; padding: 1.1rem 1.3rem; margin-top: 1rem; color: #B91C1C;">
                            <strong>🚨 Cycle Detected via 3-Color DFS!</strong><br>
                            Deadlocked Cycle Path: <code>{' ➔ '.join(map(str, cycle_path))}</code><br>
                            <small style="color: #64748B;">Because TaskForge pre-checks dependencies before commit, this edge is rejected and never reaches SQLite storage.</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.error(str(e))
