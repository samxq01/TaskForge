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


def render_evaluation_charts(results: list[StructureBenchmarkResult]) -> plt.Figure:
    """Generate comparative visualization charts using Matplotlib."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=120)
    fig.patch.set_facecolor("#0e1117")

    colors = ["#e74c3c", "#2ecc71", "#3498db"]  # List (Red), Hash (Green), BST (Blue)
    names = [r.structure_name.split(" ")[0] for r in results]

    # Chart 1: Average Lookup Time (microseconds)
    ax1 = axes[0]
    ax1.set_facecolor("#1a1f2c")
    lookup_times = [r.lookup_time_avg_us for r in results]
    bars1 = ax1.bar(names, lookup_times, color=colors, width=0.55, edgecolor="#ffffff", linewidth=0.8)
    ax1.set_title("Avg Lookup Time (µs)", color="#ffffff", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Microseconds (µs)", color="#cccccc", fontsize=9)
    ax1.tick_params(colors="#cccccc", labelsize=9)
    ax1.grid(axis="y", linestyle="--", alpha=0.25, color="#ffffff")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f}µs", ha="center", va="bottom", color="#ffffff", fontsize=8.5)

    # Chart 2: Comparisons / Entries Inspected
    ax2 = axes[1]
    ax2.set_facecolor("#1a1f2c")
    comparisons = [r.comparisons_count for r in results]
    bars2 = ax2.bar(names, comparisons, color=colors, width=0.55, edgecolor="#ffffff", linewidth=0.8)
    ax2.set_title("Comparisons / Inspected Nodes", color="#ffffff", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Count", color="#cccccc", fontsize=9)
    ax2.tick_params(colors="#cccccc", labelsize=9)
    ax2.grid(axis="y", linestyle="--", alpha=0.25, color="#ffffff")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:,}", ha="center", va="bottom", color="#ffffff", fontsize=8.5)

    # Chart 3: Construction / Indexing Time (ms)
    ax3 = axes[2]
    ax3.set_facecolor("#1a1f2c")
    const_times = [r.construction_time_ms for r in results]
    bars3 = ax3.bar(names, const_times, color=colors, width=0.55, edgecolor="#ffffff", linewidth=0.8)
    ax3.set_title("Construction Time (ms)", color="#ffffff", fontsize=11, fontweight="bold")
    ax3.set_ylabel("Milliseconds (ms)", color="#cccccc", fontsize=9)
    ax3.tick_params(colors="#cccccc", labelsize=9)
    ax3.grid(axis="y", linestyle="--", alpha=0.25, color="#ffffff")
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f}ms", ha="center", va="bottom", color="#ffffff", fontsize=8.5)

    plt.tight_layout()
    return fig


def render_bucket_distribution_chart(stats: dict[str, Any]) -> plt.Figure:
    """Generate a bucket chain length distribution chart."""
    fig, ax = plt.subplots(figsize=(10, 3.5), dpi=120)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#1a1f2c")

    bucket_sizes = stats.get("bucket_sizes", [])
    indices = list(range(len(bucket_sizes)))

    ax.bar(indices, bucket_sizes, color="#2ecc71", width=0.7, edgecolor="#27ae60", alpha=0.85)
    ax.set_title(f"Bucket Chain Length Distribution (Capacity: {stats.get('capacity', 0)}, Items: {stats.get('size', 0)})", color="#ffffff", fontsize=11)
    ax.set_xlabel("Bucket Index", color="#cccccc", fontsize=9)
    ax.set_ylabel("Entries per Chain", color="#cccccc", fontsize=9)
    ax.tick_params(colors="#cccccc", labelsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.2, color="#ffffff")

    plt.tight_layout()
    return fig


def render_structure_evaluation_view(
    storage: TaskStorage,
    hash_index: TaskHashIndexService,
) -> None:
    """Render the Data Structure Evaluation & Hash Table module (CO2)."""
    st.header("🧮 Data Structure Evaluation Lab (CO2)")
    st.caption("Course Outcome 2: Evaluate the suitability of data structures for efficient storage and retrieval.")

    # Educational Accordion
    with st.expander("📘 **About Course Outcome 2 & Multi-Structure Evaluation**", expanded=False):
        st.markdown(
            """
            ### What is CO2?
            Different engineering tasks demand distinct data structures:
            - **Sequential List ($O(n)$)**: Simplest structure; preserves exact insertion order, but lookup requires linear scanning through every element.
            - **Custom Hash Table ($O(1)$ Average)**: Maps keys to bucket positions using a hash function. Handles collisions via **separate chaining** (linked chains per bucket). Extremely fast for exact-key lookups, but does not preserve sorted order.
            - **Binary Search Tree ($O(\\log n)$ Average)**: Hierarchical ordered structure. Enables sorted traversals (e.g. earliest deadline first) while providing logarithmic search on balanced inputs, but can degrade to $O(n)$ if degenerate.
            
            ### Hash Table Invariants:
            - **Load Factor ($\\alpha = n / m$)**: Ratio of unique keys ($n$) to bucket capacity ($m$). When $\\alpha > 0.75$, the table dynamically doubles capacity and rehashes entries.
            - **Separate Chaining**: If keys collide into the same bucket, entries are chained together without overwriting each other.
            """
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
        st.subheader("Custom Hash Table Interactive Demonstration")
        st.markdown("Interact directly with our custom `HashTable[K, V]` using separate chaining.")

        stats = demo_ht.collision_stats()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📦 Capacity (m)", stats["capacity"])
        col2.metric("🔑 Stored Keys (n)", stats["size"])
        col3.metric("📈 Load Factor (α)", f"{stats['load_factor']:.3f}")
        col4.metric("💥 Collisions", stats["total_collisions"])
        col5.metric("📏 Max Chain", stats["max_chain_length"])

        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("#### 🛠️ Hash Table Operations")
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

            st.markdown("#### ⚡ Quick Actions")
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
                    # Force collisions by inserting multiple keys into small capacity
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
            st.markdown("#### ⛓️ Bucket Chains & Collision Structure")
            fig = render_bucket_distribution_chart(stats)
            st.pyplot(fig)
            plt.close(fig)

            # Raw bucket display table
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
                st.info("Demo table is currently empty. Insert keys or click 'Load Samples' above.")

    # -------------------------------------------------------------------------
    # TAB 2: Live Task-ID Hash Index
    # -------------------------------------------------------------------------
    with tab_index:
        st.subheader("Production Task-ID Hash Index")
        st.markdown(
            "TaskForge maintains an in-memory `HashTable[int, Task]` synchronizing with SQLite to enable rapid $O(1)$ average primary key retrieval."
        )

        all_tasks = storage.list_tasks()
        p_stats = hash_index.get_statistics()

        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Indexed Tasks", p_stats["size"])
        col_p2.metric("Bucket Capacity", p_stats["capacity"])
        col_p3.metric("Load Factor", f"{p_stats['load_factor']:.3f}")

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
                        st.success(
                            f"**Hash Table Match:** Task #{found_task.id} found in **{comparisons} bucket chain inspection(s)**."
                        )
                        st.markdown(
                            f"""
                            <div style="background-color: #1e2430; padding: 12px; border-radius: 6px; border-left: 4px solid #2ecc71;">
                                <h4>#{found_task.id}: {found_task.title}</h4>
                                <p style="color: #cccccc; margin-bottom: 4px;">{found_task.description or 'No description'}</p>
                                <small><strong>Priority:</strong> {found_task.priority_label} | <strong>Status:</strong> {found_task.status} | <strong>Duration:</strong> {found_task.duration}m | <strong>Due:</strong> {found_task.due_date or 'None'}</small>
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
        st.subheader("Data Structure Evaluation Lab (List vs Hash Table vs BST)")
        st.markdown(
            "Empirically compare **Sequential List Search**, **Custom Hash Table**, and **Custom BST** using identical workloads."
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

            st.markdown("### 📊 Benchmark Results Table")
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
                    "Found?": "✅ Yes" if r.result_found else "❌ No",
                    "Structural Metrics": str(r.extra_stats),
                })
            st.dataframe(table_data, use_container_width=True)

            # Matplotlib Charts
            st.markdown("### 📈 Visual Benchmark Charts")
            chart_fig = render_evaluation_charts(results)
            st.pyplot(chart_fig)
            plt.close(chart_fig)

    # -------------------------------------------------------------------------
    # TAB 4: Complexity Matrix
    # -------------------------------------------------------------------------
    with tab_matrix:
        st.subheader("Data Structure Complexity & Suitability Comparison")
        st.markdown(
            """
            | Data Structure | Lookup (Avg) | Lookup (Worst) | Construction Time | Sorted Ordering? | Space Overhead | Ideal Engineering Application |
            | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
            | **List (Linear Search)** | $O(n)$ | $O(n)$ | $O(n)$ | Preserves insertion order | Low (contiguous array) | Small collections ($N < 50$), queue buffers, ordered audit logs |
            | **Custom Hash Table** | **$O(1)$** | $O(n)$ (all collide) | $O(n)$ amortized | ❌ None | Moderate (buckets + chains) | Primary key retrieval, cache lookup, symbol tables |
            | **Custom BST** | **$O(\\log n)$** | $O(n)$ (skewed) | $O(n \\log n)$ | ✅ Inorder sorted | Node pointers (`left`, `right`) | Priority schedules, range queries, deadline-sorted views |
            """
        )

        st.markdown("---")
        st.markdown("### 🔍 Key Engineering Takeaways:")
        st.markdown(
            """
            1. **Why is Hash Table Lookup $O(1)$ on Average?**  
               The hash function maps any arbitrary key directly to a bucket array index in $O(1)$ time. With a low load factor ($\\alpha \\le 0.75$), most buckets contain only 0 or 1 entry, requiring $\\approx 1$ key comparison.
            2. **Why does a List scale poorly for lookups?**  
               Sequential search must inspect elements one by one until the target is found. Searching for a late item or missing key requires inspecting all $N$ elements.
            3. **When is a BST preferable to a Hash Table?**  
               A Hash Table has no concept of order (`min`, `max`, `successor`, range search). A BST maintains hierarchical order, allowing **Inorder Traversal** to yield sorted records without re-sorting.
            """
        )

    # -------------------------------------------------------------------------
    # TAB 5: Viva Guide (CO2)
    # -------------------------------------------------------------------------
    with tab_viva:
        st.subheader("🎓 Course Outcome 2 (CO2) Viva Examination Guide")
        st.markdown(
            """
            #### 1. What is Course Outcome 2 (CO2)?
            > *CO2: Evaluate the suitability of data structures for efficient storage and retrieval.*  
            In TaskForge, we satisfy CO2 by manually building a **custom Hash Table** and conducting rigorous, empirical performance evaluations comparing **Sequential List**, **Hash Table**, and **Binary Search Tree** across equivalent task datasets.

            #### 2. How is your Hash Table implemented? Did you use Python dictionaries?
            > **No.** Our `HashTable[K, V]` is manually constructed from scratch using a list of buckets (`list[list[_HashEntry]]`). Python dictionaries are **not** used inside the hash table. Collisions are handled using **separate chaining**, where each bucket contains a chain of entries that hashed to that index.

            #### 3. What is the Load Factor and why does resizing matter?
            > The load factor is defined as $\\alpha = \\frac{n}{m}$, where $n$ is the number of stored unique keys and $m$ is the bucket capacity.  
            As $\\alpha$ increases, bucket chains grow longer and search time degenerates toward $O(n)$. When $\\alpha > 0.75$, TaskForge automatically triggers **rehashing**, doubling the bucket capacity and re-distributing all entries so lookup remains $O(1)$ average time.

            #### 4. Why does our benchmark show that small datasets may not show large differences?
            > On small datasets ($N = 100$), the CPU cache and small constants mean linear search takes mere microseconds, sometimes comparable to hash calculation overhead. However, as $N$ scales to $1,000$ and $5,000$, linear search time grows linearly ($O(n)$), while Hash Table lookup remains flat at $\\approx 1$ comparison ($O(1)$).
            """
        )
