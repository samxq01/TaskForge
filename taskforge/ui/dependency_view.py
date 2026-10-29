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

    # Calculate topological rank / layer for each node (longest path from root)
    layers: dict[int, int] = {}
    
    # Try topological ordering to assign layers
    try:
        topo_order = graph.topological_sort()
        for node in topo_order:
            prereqs = graph.get_prerequisites(node)
            if not prereqs:
                layers[node] = 0
            else:
                layers[node] = max(layers.get(p, 0) for p in prereqs) + 1
    except CycleDetectedError:
        # Fallback to in-degree based or grid layout if cyclic
        for i, node in enumerate(nodes):
            layers[node] = i % 4

    # Group nodes by layer
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
    """Render a directed graph visualization using Matplotlib.
    
    Color codes nodes by execution status:
        - Green: Completed
        - Yellow: In Progress
        - Blue: Eligible to Start
        - Red: Blocked by Prerequisite
    """
    positions = compute_node_positions(graph, tasks_by_id)
    fig, ax = plt.subplots(figsize=(10, max(4.5, len(positions) * 0.7)), dpi=120)
    ax.set_facecolor("#0e1117")
    fig.patch.set_facecolor("#0e1117")

    if not positions:
        ax.text(
            0.5, 0.5, "No tasks or dependencies in graph.\nAdd tasks and dependencies to visualize.",
            color="#888888", fontsize=12, ha="center", va="center", transform=ax.transAxes
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
                    color="#4a90e2",
                    lw=2.0,
                    mutation_scale=16,
                    shrinkA=22,
                    shrinkB=22,
                    alpha=0.85,
                ),
            )

    # Status color map
    for node, (x, y) in positions.items():
        task = tasks_by_id.get(node)
        status = task.status if task else "Pending"
        is_eligible = scheduler.is_task_eligible(node)

        if status == TaskStatus.COMPLETED.value:
            node_color = "#2ecc71"  # Emerald Green
            border_color = "#27ae60"
            status_text = "Completed"
        elif status == TaskStatus.IN_PROGRESS.value:
            node_color = "#f39c12"  # Amber Orange
            border_color = "#d35400"
            status_text = "In Progress"
        elif is_eligible:
            node_color = "#3498db"  # Blue
            border_color = "#2980b9"
            status_text = "Eligible"
        else:
            node_color = "#e74c3c"  # Coral Red (Blocked)
            border_color = "#c0392b"
            status_text = "Blocked"

        # Draw node circle
        circle = patches.Circle(
            (x, y),
            radius=0.55,
            facecolor=node_color,
            edgecolor=border_color,
            linewidth=2.5,
            zorder=3,
        )
        ax.add_patch(circle)

        # Node label (ID)
        ax.text(
            x, y + 0.08,
            f"#{node}",
            color="#ffffff",
            fontweight="bold",
            fontsize=11,
            ha="center",
            va="center",
            zorder=4,
        )

        # Task title (truncated)
        title_text = task.title if task else f"Task {node}"
        if len(title_text) > 18:
            title_text = title_text[:16] + ".."
        ax.text(
            x, y - 0.75,
            f"{title_text}\n({status_text})",
            color="#ecf0f1",
            fontsize=8.5,
            ha="center",
            va="top",
            zorder=4,
        )

    # Set plot bounds with padding
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    margin_x = 1.2
    margin_y = 1.2
    ax.set_xlim(min(xs) - margin_x, max(xs) + margin_x)
    ax.set_ylim(min(ys) - margin_y, max(ys) + margin_y)
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
    st.header("🔗 Dependency Map & Graph Algorithms (CO5)")
    st.caption("Course Outcome 5: Evaluate applicability of graph data structures and traversal techniques.")

    # Educational CO5 Accordion
    with st.expander("📘 **About CO5 & Directed Dependency Graphs**", expanded=False):
        st.markdown(
            """
            ### What is a Dependency Graph?
            In real-world project management and compiler build systems, tasks have strict execution prerequisites.
            - **Graph Model:** Directed Graph $G = (V, E)$ where nodes $V$ represent tasks and directed edges $A \\to B$ mean **Task B depends on Task A** (Task A is a prerequisite for Task B).
            - **Adjacency List:** Each task stores outgoing edges (dependents) and incoming edges (prerequisites) in $O(V + E)$ space.
            - **Cycle Detection:** Deadlocks occur when circular dependencies exist ($A \\to B \\to C \\to A$). We use **3-color DFS** to detect back-edges and reject cycle-inducing dependencies *before* they are written to SQLite!
            - **Topological Sorting:** **Kahn's Algorithm** uses in-degrees and our Phase 02 custom **FIFO Queue** to derive a deterministic, valid execution sequence.
            - **Traversal:**
                - **BFS (Breadth-First Search):** Uses Phase 02 custom **Queue** to explore tasks level by level.
                - **DFS (Depth-First Search):** Uses Phase 02 custom **Stack** to explore deep prerequisite chains.
            """
        )

    # Always ensure graph is synchronized with SQLite
    dep_service.rebuild()
    graph = dep_service.get_graph()
    tasks = storage.list_tasks()
    tasks_by_id = {t.id: t for t in tasks if t.id is not None}

    # Summary Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    is_dag = graph.is_acyclic()
    eligible_tasks = scheduler.get_eligible_pending_tasks()
    blocked_tasks = scheduler.get_blocked_tasks()

    with col1:
        st.metric("📦 Graph Nodes", graph.node_count())
    with col2:
        st.metric("➡️ Dependencies", graph.edge_count())
    with col3:
        st.metric("🛡️ Graph Structure", "Acyclic (DAG)" if is_dag else "⚠️ Cycle Present")
    with col4:
        st.metric("🚀 Ready to Start", len(eligible_tasks))
    with col5:
        st.metric("⛔ Blocked Tasks", len(blocked_tasks))

    st.markdown("---")

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
        st.subheader("Directed Task Dependency Graph")
        st.markdown(
            "Directed arrows point from **Prerequisite ➔ Dependent** ($A \\to B$ means $A$ must complete before $B$ can start)."
        )

        col_legend1, col_legend2, col_legend3, col_legend4 = st.columns(4)
        col_legend1.markdown("🟢 **Completed**")
        col_legend2.markdown("🟡 **In Progress**")
        col_legend3.markdown("🔵 **Eligible (Ready)**")
        col_legend4.markdown("🔴 **Blocked by Prereq**")

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
                    status_badge = "✅ Ready" if scheduler.is_task_eligible(t.id) else ("🔒 Blocked" if t.status == TaskStatus.PENDING.value else t.status)
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
        st.subheader("Register or Remove Dependencies")
        if len(tasks) < 2:
            st.warning("You need at least 2 tasks in the system to create dependencies.")
        else:
            task_options = {t.id: f"#{t.id}: {t.title} [{t.status}]" for t in tasks if t.id is not None}
            task_ids = list(task_options.keys())

            col_add, col_del = st.columns(2)

            with col_add:
                st.markdown("#### ➕ Add Dependency")
                st.caption("Specify that Task B depends on Task A (Task A must finish first).")

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
                        st.error(f"❌ Invalid Dependency: {ide}")
                    except CycleDetectedError as cde:
                        st.error(f"🚨 Cycle Prevention: {cde}")

            with col_del:
                st.markdown("#### 🗑️ Existing Dependencies")
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
                            st.markdown(f"**#{prereq}** ({prereq_title}) ➔ **#{dep}** ({dep_title})")
                        with col_btn:
                            if st.button("Remove", key=f"del_dep_{prereq}_{dep}", use_container_width=True):
                                dep_service.remove_dependency(prereq, dep)
                                queue_service.refresh()
                                st.success(f"Removed dependency #{prereq} ➔ #{dep}")
                                st.rerun()

    # TAB 3: Topological Order
    with tab_topo:
        st.subheader("Topological Task Scheduling Order (Kahn's Algorithm)")
        st.markdown(
            """
            Topological sorting arranges directed graph nodes in a linear sequence such that for every directed edge
            $A \\to B$, Task $A$ appears before Task $B$.
            TaskForge executes Kahn's Algorithm using our custom **Queue** data structure.
            """
        )

        try:
            topological_tasks = dep_service.get_topological_order()
            if not topological_tasks:
                st.info("No tasks to schedule.")
            else:
                st.markdown("### 📋 Valid Linear Execution Sequence")
                for step, task in enumerate(topological_tasks, start=1):
                    assert task.id is not None
                    prereqs = graph.get_prerequisites(task.id)
                    prereq_desc = f"Depends on: {', '.join(f'#{p}' for p in prereqs)}" if prereqs else "Root Task (0 prerequisites)"
                    status_icon = "✅" if task.status == TaskStatus.COMPLETED.value else ("⚙️" if task.status == TaskStatus.IN_PROGRESS.value else "⏳")

                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background-color: #1e2430; border-left: 4px solid #3498db;">
                            <strong>Step {step}:</strong> {status_icon} <strong>Task #{task.id}: {task.title}</strong> — <em>{task.status}</em><br/>
                            <small style="color: #a0aec0;">Priority: {task.priority_label} | Duration: {task.duration}m | {prereq_desc}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
                st.markdown("#### 🔬 Kahn's Algorithm Trace")
                st.markdown(
                    f"""
                    1. **Initial in-degrees computed:** { {t.id: graph.in_degree(t.id) for t in tasks if t.id is not None} }
                    2. **Zero in-degree nodes enqueued to Queue:** { [t.id for t in tasks if t.id is not None and graph.in_degree(t.id) == 0] }
                    3. **FIFO Queue processing order:** { [t.id for t in topological_tasks] }
                    4. **All {graph.node_count()} nodes visited without cycle deadlock.**
                    """
                )
        except CycleDetectedError as err:
            st.error(f"🚨 Topological sorting failed: {err}")

    # TAB 4: Traversal Runner (BFS & DFS)
    with tab_traverse:
        st.subheader("Graph Traversal Engine: BFS vs DFS")
        st.markdown(
            "Traverse the dependency hierarchy starting from any task node to explore its downstream dependents."
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
                            <div style="background-color: #242c3d; padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 6px;">
                                <span style="font-size: 11px; color: #64b5f6;">Step {i+1}</span><br/>
                                <strong>#{v_task.id}</strong><br/>
                                <small>{v_task.title[:15]}</small>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # TAB 5: Interactive Cycle Detection Sandbox (Viva Demo)
    with tab_sandbox:
        st.subheader("Interactive Circular Dependency Simulator (Viva Sandbox)")
        st.markdown(
            """
            This interactive simulator demonstrates **cycle detection** in action without modifying your primary database.
            A circular dependency occurs when a cycle is introduced, e.g.:
            $$\\text{Task A} \\to \\text{Task B} \\to \\text{Task C} \\to \\text{Task A}$$
            In this situation, no task can ever start because each task waits for the next to complete!
            """
        )

        st.markdown("#### Test Graph Simulation:")
        sim_col1, sim_col2 = st.columns([2, 1])

        with sim_col1:
            st.markdown(
                """
                Imagine a 3-task project:
                - `Task 101 (Database Setup)` ➔ `Task 102 (API Service)`
                - `Task 102 (API Service)` ➔ `Task 103 (Frontend App)`
                
                Now imagine trying to add:
                - `Task 103 (Frontend App)` ➔ `Task 101 (Database Setup)`
                """
            )

        with sim_col2:
            test_mode = st.button("🧪 Simulate Cycle Detection", use_container_width=True)

        if test_mode:
            # Build sample graph
            sample_graph = DependencyGraph()
            sample_graph.add_edge(101, 102)
            sample_graph.add_edge(102, 103)

            st.write("Current sample graph: `101 -> 102 -> 103`. Is acyclic:", sample_graph.is_acyclic())
            would_cycle = sample_graph.would_create_cycle(103, 101)
            st.write(f"Pre-check `would_create_cycle(103, 101)`: **{would_cycle}**")

            # Try adding cycle
            try:
                if would_cycle:
                    # Intentionally simulate force adding to demonstrate 3-color DFS detection
                    sample_graph._adj[103].add(101)
                    sample_graph._rev_adj[101].add(103)
                    has_cycle, cycle_path = sample_graph.detect_cycle()
                    st.error(
                        f"🚨 **Cycle Detected via 3-Color DFS!** Loop: `{' -> '.join(map(str, cycle_path))}`"
                    )
                    st.info("Because TaskForge pre-validates all edges with `would_create_cycle()`, this circular dependency is rejected and never reaches SQLite!")
            except Exception as e:
                st.error(str(e))
