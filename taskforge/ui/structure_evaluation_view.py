"""Data Structure Evaluation Lab UI view comparing List, HashTable, and BST (CO2)."""

from __future__ import annotations

from typing import Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.structure_evaluation import (
    StructureBenchmarkResult,
    StructureEvaluationService,
    generate_evaluation_dataset,
)
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.storage import TaskStorage
from taskforge.structures.hash_table import HashTable
from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_LIME,
    COLOR_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    render_metric_strip,
    render_pill,
    render_section_header,
    style_anthracite_ax,
)


def render_evaluation_charts(results: list[StructureBenchmarkResult]) -> plt.Figure:
    """Generate comparative visualization charts using Anthracite Studio styling."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), dpi=120)
    fig.patch.set_facecolor(COLOR_BG)

    colors = [COLOR_TEXT_MUTED, COLOR_LIME, "#60A5FA"]  # List (Muted), Hash (Lime), BST (Blue)
    names = [r.structure_name.split(" ")[0] for r in results]

    # Chart 1: Average Lookup Time (microseconds)
    ax1 = axes[0]
    lookup_times = [r.lookup_time_avg_us for r in results]
    bars1 = ax1.bar(names, lookup_times, color=colors, width=0.48, edgecolor="#2A2A2A", linewidth=0.8)
    style_anthracite_ax(ax1, title="Avg Lookup Time (µs)", ylabel="Microseconds (µs)")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f}µs", ha="center", va="bottom", color=COLOR_TEXT_PRIMARY, fontsize=8.5, fontweight="bold")

    # Chart 2: Comparisons / Entries Inspected
    ax2 = axes[1]
    comparisons = [r.comparisons_count for r in results]
    bars2 = ax2.bar(names, comparisons, color=colors, width=0.48, edgecolor="#2A2A2A", linewidth=0.8)
    style_anthracite_ax(ax2, title="Comparisons / Inspected Nodes", ylabel="Count")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:,}", ha="center", va="bottom", color=COLOR_TEXT_PRIMARY, fontsize=8.5, fontweight="bold")

    # Chart 3: Construction / Indexing Time (ms)
    ax3 = axes[2]
    const_times = [r.construction_time_ms for r in results]
    bars3 = ax3.bar(names, const_times, color=colors, width=0.48, edgecolor="#2A2A2A", linewidth=0.8)
    style_anthracite_ax(ax3, title="Construction Time (ms)", ylabel="Milliseconds (ms)")
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f}ms", ha="center", va="bottom", color=COLOR_TEXT_PRIMARY, fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    return fig


def render_bucket_distribution_chart(stats: dict[str, Any]) -> plt.Figure:
    """Generate a bucket chain length distribution chart using Anthracite Studio styling."""
    fig, ax = plt.subplots(figsize=(10, 3.4), dpi=120)
    fig.patch.set_facecolor(COLOR_BG)

    bucket_sizes = stats.get("bucket_sizes", [])
    indices = list(range(len(bucket_sizes)))

    ax.bar(indices, bucket_sizes, color=COLOR_LIME, width=0.65, edgecolor="#2A2A2A", alpha=0.9)
    style_anthracite_ax(
        ax,
        title=f"Bucket Chain Length Distribution (Capacity: {stats.get('capacity', 0)}, Items: {stats.get('size', 0)})",
        xlabel="Bucket Index",
        ylabel="Entries per Chain",
    )

    plt.tight_layout()
    return fig


def render_structure_evaluation_view(
    storage: TaskStorage,
    hash_index: TaskHashIndexService,
) -> None:
    """Render the Data Structure Evaluation & Hash Table module (CO2)."""
    render_section_header(
        eyebrow="COURSE OUTCOME 2 (CO2) • STORAGE & RETRIEVAL EVALUATION",
        title="Data Structure Evaluation Laboratory",
        subtitle="Empirically evaluate the storage and retrieval characteristics of custom Unsorted List O(n), Hash Table O(1), and Binary Search Tree O(log n) across identical synthetic workloads.",
    )

    # Initialize demo hash table in session state if not present
    if "demo_hash_table" not in st.session_state:
        st.session_state.demo_hash_table = HashTable[str, str](initial_capacity=8, max_load_factor=0.75)

    demo_ht: HashTable[str, str] = st.session_state.demo_hash_table

    # Tabs
    tab_lab, tab_index, tab_bench, tab_matrix, tab_viva = st.tabs([
        "🗄️ Custom Hash Table Lab",
        "🔍 Live Task-ID Hash Index",
        "🔬 Comparative Benchmark (List vs Hash vs BST)",
        "📋 Complexity & Suitability Matrix",
        "🎓 Academic Viva Guide (CO2)",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Custom Hash Table Lab
    # -------------------------------------------------------------------------
    with tab_lab:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Custom Hash Table Interactive Demonstration
            </div>
            <div style="font-size: 0.85rem; color: #A6A49E; margin-bottom: 1.2rem;">
                Interact with our custom <code>HashTable[K, V]</code> implementation featuring separate chaining collision resolution and dynamic rehashing.
            </div>
            """,
            unsafe_allow_html=True,
        )

        stats = demo_ht.collision_stats()

        render_metric_strip([
            {"label": "Bucket Capacity (m)", "value": str(stats["capacity"]), "caption": "Static Array Size"},
            {"label": "Stored Keys (n)", "value": str(stats["size"]), "caption": "Unique Key Count"},
            {"label": "Load Factor (α)", "value": f"{stats['load_factor']:.3f}", "caption": "Resizes at > 0.75"},
            {"label": "Total Collisions", "value": str(stats["total_collisions"]), "caption": "Chain Collisions"},
            {"label": "Max Chain Length", "value": str(stats["max_chain_length"]), "caption": "Longest Linked Chain"},
        ])

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.6rem;">🛠️ Hash Table Operations</div>', unsafe_allow_html=True)
            op_mode = st.radio(
                "Select Operation:",
                options=["Insert / Upsert", "Retrieve (Get)", "Update Existing", "Delete"],
                horizontal=True,
            )

            if op_mode == "Insert / Upsert":
                with st.form("ht_insert_form"):
                    k = st.text_input("Key:", placeholder="e.g. task_alpha")
                    v = st.text_input("Value:", placeholder="e.g. Implement Cache")
                    submitted = st.form_submit_button("Insert Entry", type="primary")
                    if submitted:
                        if not k:
                            st.error("Key cannot be empty.")
                        else:
                            is_new = demo_ht.insert(k, v)
                            st.success(f"{'Inserted new key' if is_new else 'Updated existing key'} '{k}' ➔ '{v}'")
                            st.rerun()

            elif op_mode == "Retrieve (Get)":
                with st.form("ht_get_form"):
                    k = st.text_input("Lookup Key:", placeholder="e.g. task_alpha")
                    submitted = st.form_submit_button("Retrieve Value")
                    if submitted:
                        val, comps = demo_ht.get_with_comparisons(k)
                        if val is not None:
                            st.success(f"Found: `{k}` ➔ `{val}` (Inspected {comps} chain entry/entries)")
                        else:
                            st.warning(f"Key '{k}' not found in hash table (Inspected {comps} chain entries).")

            elif op_mode == "Update Existing":
                with st.form("ht_update_form"):
                    k = st.text_input("Existing Key:", placeholder="e.g. task_alpha")
                    v = st.text_input("New Value:", placeholder="e.g. Updated Cache Spec")
                    submitted = st.form_submit_button("Update Value")
                    if submitted:
                        updated = demo_ht.update(k, v)
                        if updated:
                            st.success(f"Updated '{k}' to '{v}'")
                            st.rerun()
                        else:
                            st.error(f"Cannot update: Key '{k}' does not exist.")

            elif op_mode == "Delete":
                with st.form("ht_delete_form"):
                    k = st.text_input("Key to Delete:", placeholder="e.g. task_alpha")
                    submitted = st.form_submit_button("Delete Entry", type="primary")
                    if submitted:
                        deleted = demo_ht.delete(k)
                        if deleted:
                            st.success(f"Deleted key '{k}'")
                            st.rerun()
                        else:
                            st.warning(f"Key '{k}' not found.")

            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 1.2rem 0 0.6rem 0;">⚡ Quick Actions</div>', unsafe_allow_html=True)
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("🌱 Load Samples", use_container_width=True):
                    demo_ht.insert("compiler", "Lexer & Parser")
                    demo_ht.insert("database", "B-Tree Index")
                    demo_ht.insert("scheduler", "Topological Kahn")
                    demo_ht.insert("cache", "LRU & HashTable")
                    st.rerun()
            with col_b2:
                if st.button("💥 Collision Demo", use_container_width=True):
                    demo_ht.insert("alpha_1", "Module A")
                    demo_ht.insert("alpha_2", "Module B")
                    demo_ht.insert("alpha_3", "Module C")
                    demo_ht.insert("alpha_4", "Module D")
                    st.rerun()
            with col_b3:
                if st.button("🗑️ Clear Demo", use_container_width=True):
                    demo_ht.clear()
                    st.rerun()

        with col_right:
            st.markdown('<div style="font-family: Syne, sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.6rem;">⛓️ Bucket Chains & Collision Structure</div>', unsafe_allow_html=True)
            fig = render_bucket_distribution_chart(stats)
            st.pyplot(fig)
            plt.close(fig)

            bucket_rows = []
            for idx, bucket in enumerate(demo_ht._buckets):
                if bucket:
                    chain_repr = " ➔ ".join([f"[{e.key}: '{e.value}']" for e in bucket])
                    bucket_rows.append({
                        "Bucket Index": idx,
                        "Chain Length": len(bucket),
                        "Collision Status": "⚠️ Collision" if len(bucket) > 1 else "✅ Single",
                        "Chained Entries": chain_repr,
                    })

            if bucket_rows:
                st.dataframe(bucket_rows, use_container_width=True)
            else:
                st.markdown("<span style='color: #6E6D68; font-size: 0.85rem;'>Demo table is currently empty. Insert keys or click 'Load Samples' above.</span>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: Live Task-ID Hash Index
    # -------------------------------------------------------------------------
    with tab_index:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Production Task-ID Hash Index
            </div>
            <div style="font-size: 0.85rem; color: #A6A49E; margin-bottom: 1.2rem;">
                TaskForge maintains an in-memory <code>HashTable[int, Task]</code> synchronized with SQLite to enable <code>O(1)</code> average primary key retrieval.
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_tasks = storage.list_tasks()
        p_stats = hash_index.get_statistics()

        render_metric_strip([
            {"label": "Indexed Tasks", "value": str(p_stats["size"]), "caption": "Primary Key Index"},
            {"label": "Bucket Capacity", "value": str(p_stats["capacity"]), "caption": "Internal Buckets"},
            {"label": "Load Factor (α)", "value": f"{p_stats['load_factor']:.3f}", "caption": "Target < 0.75"},
            {"label": "Lookup Complexity", "value": "O(1) Average", "caption": "Constant-Time Hash"},
        ])

        col_search, col_rebuild = st.columns([3, 1])
        with col_search:
            if not all_tasks:
                st.info("No tasks recorded in SQLite. Use the sidebar to load sample tasks.")
            else:
                task_ids = [t.id for t in all_tasks if t.id is not None]
                selected_id = st.selectbox(
                    "Select Task ID to Lookup in Hash Index:",
                    options=task_ids,
                    format_func=lambda tid: f"Task #{tid}: {next((t.title for t in all_tasks if t.id == tid), '')}",
                )

                if selected_id is not None:
                    found_task, comparisons = hash_index.get_task_with_comparisons(selected_id)
                    if found_task:
                        st.markdown(
                            f"""
                            <div style="background-color: #1A1F16; border: 1px solid rgba(215, 255, 100, 0.35); border-radius: 3px; padding: 1.2rem 1.4rem; margin-top: 0.8rem;">
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #D7FF64; font-weight: 700; margin-bottom: 0.3rem;">
                                    ● Instant Hash Match Found ({comparisons} Chain Comparison/s)
                                </div>
                                <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.3rem;">
                                    #{found_task.id}: {found_task.title}
                                </div>
                                <p style="color: #A6A49E; margin-bottom: 0.6rem; font-size: 0.88rem;">{found_task.description or 'No description'}</p>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #A6A49E;">
                                    Priority: <strong style="color: #FFFFFF;">{found_task.priority_label}</strong> &bull; Status: <strong style="color: #FFFFFF;">{found_task.status}</strong> &bull; Duration: <strong style="color: #FFFFFF;">{found_task.duration}m</strong> &bull; Deadline: <strong style="color: #FFFFFF;">{found_task.formatted_deadline}</strong>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        with col_rebuild:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🔄 Rebuild Index", use_container_width=True):
                cnt = hash_index.rebuild_index()
                st.success(f"Reindexed {cnt} tasks into HashTable.")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Comparison Laboratory
    # -------------------------------------------------------------------------
    with tab_bench:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Comparative Evaluation: List vs Hash Table vs BST
            </div>
            <div style="font-size: 0.85rem; color: #A6A49E; margin-bottom: 1.2rem;">
                Empirically compare Sequential Scanning <code>O(n)</code>, Hash Table Indexing <code>O(1)</code>, and Binary Search Tree <code>O(log n)</code> across identical workloads.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            size_choice = st.selectbox(
                "Dataset Size (N):",
                options=[100, 1000, 5000],
                index=1,
                help="Number of synthetic task items generated with deterministic seed.",
            )
        with col_c2:
            scenario_choice = st.selectbox(
                "Lookup Target Scenario:",
                options=["middle", "early", "late", "absent"],
                format_func=lambda s: {
                    "middle": "Middle Hit (~50% mark)",
                    "early": "Early Hit (~5% mark)",
                    "late": "Late Hit (~95% mark)",
                    "absent": "Absent Key (Miss Case)",
                }.get(s, s),
            )
        with col_c3:
            reps_choice = st.slider("Repetitions for Timing:", min_value=50, max_value=500, value=250, step=50)

        if st.button("🚀 Run Comparative Benchmark", type="primary", use_container_width=True):
            eval_service = StructureEvaluationService()
            dataset = generate_evaluation_dataset(size=size_choice, seed=42)

            with st.spinner("Executing benchmark across List, Hash Table, and BST..."):
                bench_results = eval_service.run_evaluation(
                    dataset=dataset,
                    scenario=scenario_choice,
                    repetitions=reps_choice,
                )
                st.session_state.last_bench_results = bench_results

        if "last_bench_results" in st.session_state:
            results = st.session_state.last_bench_results

            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            table_data = []
            for r in results:
                table_data.append({
                    "Data Structure": r.structure_name,
                    "Items (N)": r.dataset_size,
                    "Scenario": r.scenario.capitalize(),
                    "Construction Time (ms)": f"{r.construction_time_ms:.3f} ms",
                    "Total Lookup Time (ms)": f"{r.lookup_time_total_ms:.3f} ms",
                    "Avg Lookup Time (µs)": f"{r.lookup_time_avg_us:.3f} µs",
                    "Comparisons / Inspected": f"{r.comparisons_count:,}",
                    "Found?": "Yes" if r.result_found else "No",
                    "Structural Metrics": str(r.extra_stats),
                })
            st.dataframe(table_data, use_container_width=True)

            chart_fig = render_evaluation_charts(results)
            st.pyplot(chart_fig)
            plt.close(chart_fig)

    # -------------------------------------------------------------------------
    # TAB 4: Complexity Matrix
    # -------------------------------------------------------------------------
    with tab_matrix:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; margin-bottom: 0.8rem;">
                Data Structure Complexity & Suitability Comparison
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            | Data Structure | Lookup (Avg) | Lookup (Worst) | Construction Time | Sorted Ordering? | Space Overhead | Ideal Engineering Application |
            | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
            | **List (Linear Search)** | $O(n)$ | $O(n)$ | $O(n)$ | Preserves insertion order | Low (contiguous array) | Small collections ($N < 50$), queue buffers, ordered audit logs |
            | **Custom Hash Table** | **$O(1)$** | $O(n)$ (all collide) | $O(n)$ amortized | ❌ None | Moderate (buckets + chains) | Primary key retrieval, cache lookup, symbol tables |
            | **Custom BST** | **$O(\\log n)$** | $O(n)$ (skewed) | $O(n \\log n)$ | ✅ Inorder sorted | Node pointers (`left`, `right`) | Priority schedules, range queries, deadline-sorted views |
            """
        )

        st.markdown(
            """
            <div style="background-color: #1B1B1B; border: 1px solid #2A2A2A; border-radius: 3px; padding: 1.4rem 1.6rem; margin-top: 1.5rem;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.6rem;">
                    Key Architectural Takeaways:
                </div>
                <div style="color: #A6A49E; font-size: 0.88rem; line-height: 1.6;">
                    <p><strong style="color: #D7FF64;">1. Why is Hash Table Lookup $O(1)$ on Average?</strong><br>
                    The hash function computes a numeric array index from the key in constant time. When $\\alpha \\le 0.75$, linked chains remain tiny ($\\le 1.3$ entries on average), yielding constant search time.</p>

                    <p><strong style="color: #D7FF64;">2. When is a BST Preferable to a Hash Table?</strong><br>
                    A Hash Table has no ordering semantics. A BST maintains strict hierarchical order, enabling sorted Inorder traversals (e.g. chronological deadlines) and range queries without re-sorting.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # TAB 5: Viva Guide (CO2)
    # -------------------------------------------------------------------------
    with tab_viva:
        st.markdown(
            """
            <div style="background-color: #1B1B1B; border: 1px solid #2A2A2A; border-radius: 3px; padding: 1.6rem 1.8rem; margin-top: 0.5rem;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.8rem;">
                    Course Outcome 2 (CO2) Viva Examination Guide
                </div>
                <div style="color: #A6A49E; font-size: 0.9rem; line-height: 1.6;">
                    <p><strong style="color: #D7FF64;">Q1: How is your Hash Table implemented? Did you use Python dictionaries?</strong><br>
                    <strong>No.</strong> <code>HashTable[K, V]</code> is built completely from scratch using a fixed-capacity list of buckets (<code>list[list[_HashEntry]]</code>). Collisions are resolved using <strong>separate chaining</strong>.</p>

                    <p><strong style="color: #D7FF64;">Q2: What is the Load Factor and why does resizing matter?</strong><br>
                    The load factor is $\\alpha = n / m$ (stored items divided by bucket capacity). When $\\alpha > 0.75$, TaskForge automatically triggers dynamic rehashing, doubling capacity to keep average chain length minimal and preserve $O(1)$ lookup.</p>

                    <p><strong style="color: #D7FF64;">Q3: How do the empirical results validate CO2?</strong><br>
                    As dataset size scales from $N=100$ to $N=5,000$, Linear Search time grows linearly ($O(n)$), while Hash Table lookup remains flat at $\approx 1$ comparison ($O(1)$), proving suitability for high-frequency key-based retrieval.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
