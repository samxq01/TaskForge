"""DSA Performance Laboratory UI module for Course Outcome 3 (CO3)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from taskforge.services.benchmark_service import (
    BenchmarkService,
    SearchBenchmarkResult,
    SortBenchmarkResult,
)


def _render_search_chart(result: SearchBenchmarkResult) -> None:
    """Render a clean Matplotlib chart comparing comparisons and execution time."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    fig.patch.set_facecolor("#0e1117")

    algorithms = ["Linear Search", "Binary Search"]
    comparisons = [result.linear_comparisons, result.binary_comparisons]
    times_ms = [result.linear_time_ms, result.binary_time_ms]
    colors = ["#ff4b4b", "#00d26a"]

    # 1. Comparison Count Bar Chart
    bars1 = ax1.bar(algorithms, comparisons, color=colors, width=0.45)
    ax1.set_title(f"Key Comparisons (Size: {result.dataset_size})", color="white", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Comparisons", color="white", fontsize=10)
    ax1.set_facecolor("#161a24")
    ax1.tick_params(colors="white")
    ax1.grid(axis="y", linestyle="--", alpha=0.3, color="gray")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{int(yval):,}", ha="center", va="bottom", color="white", fontsize=9, fontweight="bold")

    # 2. Execution Time (ms) Bar Chart
    bars2 = ax2.bar(algorithms, times_ms, color=colors, width=0.45)
    ax2.set_title(f"Execution Time in ms (Repetitions avg)", color="white", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Time (milliseconds)", color="white", fontsize=10)
    ax2.set_facecolor("#161a24")
    ax2.tick_params(colors="white")
    ax2.grid(axis="y", linestyle="--", alpha=0.3, color="gray")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.4f} ms", ha="center", va="bottom", color="white", fontsize=9, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _render_sort_chart(result: SortBenchmarkResult) -> None:
    """Render a clean Matplotlib chart comparing sorting comparisons and execution time."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    fig.patch.set_facecolor("#0e1117")

    algorithms = ["Insertion Sort", "Merge Sort"]
    comparisons = [result.insertion_comparisons, result.merge_comparisons]
    times_ms = [result.insertion_time_ms, result.merge_time_ms]
    colors = ["#ff9f1a", "#3880ff"]

    # 1. Comparison Count Bar Chart
    bars1 = ax1.bar(algorithms, comparisons, color=colors, width=0.45)
    ax1.set_title(f"Key Comparisons ({result.distribution.capitalize()}, N={result.dataset_size})", color="white", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Comparisons", color="white", fontsize=10)
    ax1.set_facecolor("#161a24")
    ax1.tick_params(colors="white")
    ax1.grid(axis="y", linestyle="--", alpha=0.3, color="gray")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{int(yval):,}", ha="center", va="bottom", color="white", fontsize=9, fontweight="bold")

    # 2. Execution Time (ms) Bar Chart
    bars2 = ax2.bar(algorithms, times_ms, color=colors, width=0.45)
    ax2.set_title(f"Execution Time in ms (N={result.dataset_size})", color="white", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Time (milliseconds)", color="white", fontsize=10)
    ax2.set_facecolor("#161a24")
    ax2.tick_params(colors="white")
    ax2.grid(axis="y", linestyle="--", alpha=0.3, color="gray")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f} ms", ha="center", va="bottom", color="white", fontsize=9, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_dsa_performance_lab() -> None:
    """Render the full DSA Performance Lab interface for Searching and Sorting."""
    st.markdown("## 🔬 DSA Performance Laboratory (CO3)")
    st.markdown(
        """
        > **Course Outcome 3 (CO3):** *Evaluate the performance of searching and sorting algorithms for solving engineering problems.*
        
        This interactive laboratory executes our manual algorithm implementations against reproducible datasets, measuring wall-clock execution time with `time.perf_counter()` and recording exact operation counts.
        """
    )

    tab_searching, tab_sorting, tab_summary = st.tabs(
        ["🔍 Searching Laboratory", "📊 Sorting Laboratory", "📚 Complexity Matrix & Viva Guide"]
    )

    # ---------------- TAB 1: SEARCHING LAB ----------------
    with tab_searching:
        st.markdown("### 🔍 Linear Search vs. Binary Search")
        st.markdown(
            """
            - **Linear Search:** Examines each element sequentially ($O(n)$ average/worst case). Operates on unsorted or sorted data.
            - **Binary Search:** Eliminates half of the search space on each comparison ($O(\\log n)$).
              **Important Precondition:** Binary Search *strictly requires* input pre-sorted by the search key.
            """
        )

        col_s1, col_s2, col_s3 = st.columns([2, 2, 2])
        with col_s1:
            dataset_size = st.selectbox(
                "Dataset Size (N)",
                options=[100, 500, 1000, 2500, 5000],
                index=2,
                key="search_size_select",
            )
        with col_s2:
            scenario = st.selectbox(
                "Search Target Scenario",
                options=[
                    ("middle", "Middle Element (Typical Case)"),
                    ("first", "First Element (Linear Best Case: O(1))"),
                    ("last", "Last Element (Linear Worst Case: O(n))"),
                    ("absent", "Absent Target (Unsuccessful Search: O(n))"),
                ],
                format_func=lambda x: x[1],
                index=0,
                key="search_scen_select",
            )[0]
        with col_s3:
            repetitions = st.number_input(
                "Timing Repetitions (Average)",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                key="search_reps",
            )

        if st.button("🚀 Run Searching Benchmark", type="primary", use_container_width=True):
            with st.spinner("Executing searching algorithms..."):
                result = BenchmarkService.benchmark_search(
                    size=dataset_size,
                    scenario=scenario,
                    repetitions=repetitions,
                )
            st.session_state.last_search_benchmark = result

        if "last_search_benchmark" in st.session_state:
            res: SearchBenchmarkResult = st.session_state.last_search_benchmark

            st.markdown("#### 📈 Benchmark Results")
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Linear Search Time", f"{res.linear_time_ms:.5f} ms")
            with metric_col2:
                st.metric("Binary Search Time", f"{res.binary_time_ms:.5f} ms")
            with metric_col3:
                st.metric("Linear Comparisons", f"{res.linear_comparisons:,}")
            with metric_col4:
                st.metric("Binary Comparisons", f"{res.binary_comparisons:,}")

            # Ratio highlight
            comp_ratio = (
                res.linear_comparisons / max(res.binary_comparisons, 1)
            )
            st.success(
                f"🎯 **Algorithmic Efficiency:** Binary Search required **{res.binary_comparisons}** comparisons "
                f"versus **{res.linear_comparisons}** for Linear Search (a **{comp_ratio:.1f}x** reduction in comparison operations!)."
            )

            # Numerical Table
            table_data = [
                {
                    "Algorithm": "Linear Search",
                    "Target Value": res.target,
                    "Found?": "✅ Yes" if res.linear_found else "❌ No",
                    "Comparisons": res.linear_comparisons,
                    "Execution Time (ms)": f"{res.linear_time_ms:.5f}",
                    "Theoretical Complexity": "O(1) best, O(n) worst",
                },
                {
                    "Algorithm": "Binary Search",
                    "Target Value": res.target,
                    "Found?": "✅ Yes" if res.binary_found else "❌ No",
                    "Comparisons": res.binary_comparisons,
                    "Execution Time (ms)": f"{res.binary_time_ms:.5f}",
                    "Theoretical Complexity": "O(1) best, O(log n) worst",
                },
            ]
            st.table(table_data)

            # Matplotlib Visualizer
            _render_search_chart(res)

    # ---------------- TAB 2: SORTING LAB ----------------
    with tab_sorting:
        st.markdown("### 📊 Insertion Sort vs. Merge Sort")
        st.markdown(
            """
            - **Insertion Sort:** Incremental algorithm ($O(n^2)$ average/worst case, $O(n)$ on pre-sorted data). Stable.
            - **Merge Sort:** Divide-and-conquer algorithm ($O(n \\log n)$ guaranteed in all cases). Stable.
            """
        )

        col_sort1, col_sort2 = st.columns(2)
        with col_sort1:
            sort_size = st.selectbox(
                "Dataset Size (N)",
                options=[100, 500, 1000, 2000, 3000],
                index=1,
                help="Note: Insertion Sort is quadratic O(n^2). Sizes > 3000 are capped to ensure UI responsiveness.",
                key="sort_size_select",
            )
        with col_sort2:
            distribution = st.selectbox(
                "Input Distribution",
                options=[
                    ("random", "Randomized Input (Average Case)"),
                    ("sorted", "Already Sorted (Insertion Sort Best Case: O(n))"),
                    ("reversed", "Reverse Sorted (Insertion Sort Worst Case: O(n^2))"),
                ],
                format_func=lambda x: x[1],
                index=0,
                key="sort_dist_select",
            )[0]

        if st.button("🚀 Run Sorting Benchmark", type="primary", use_container_width=True):
            with st.spinner("Executing sorting algorithms on equivalent datasets..."):
                sort_res = BenchmarkService.benchmark_sorting(
                    size=sort_size,
                    distribution=distribution,
                )
            st.session_state.last_sort_benchmark = sort_res

        if "last_sort_benchmark" in st.session_state:
            s_res: SortBenchmarkResult = st.session_state.last_sort_benchmark

            st.markdown("#### 📈 Benchmark Results")
            sm1, sm2, sm3, sm4 = st.columns(4)
            with sm1:
                st.metric("Insertion Sort Time", f"{s_res.insertion_time_ms:.2f} ms")
            with sm2:
                st.metric("Merge Sort Time", f"{s_res.merge_time_ms:.2f} ms")
            with sm3:
                st.metric("Insertion Comparisons", f"{s_res.insertion_comparisons:,}")
            with sm4:
                st.metric("Merge Comparisons", f"{s_res.merge_comparisons:,}")

            if s_res.is_correct:
                st.success("✅ **Correctness Verified:** Both algorithms produced exact ground-truth sorted output.")
            else:
                st.error("❌ Output verification failed.")

            # Numerical Table
            sort_table_data = [
                {
                    "Algorithm": "Insertion Sort",
                    "Dataset Size": s_res.dataset_size,
                    "Distribution": s_res.distribution.capitalize(),
                    "Comparisons": f"{s_res.insertion_comparisons:,}",
                    "Data Shifts": f"{s_res.insertion_shifts:,}",
                    "Time (ms)": f"{s_res.insertion_time_ms:.2f}",
                    "Complexity Class": "O(n) best, O(n²) avg/worst",
                },
                {
                    "Algorithm": "Merge Sort",
                    "Dataset Size": s_res.dataset_size,
                    "Distribution": s_res.distribution.capitalize(),
                    "Comparisons": f"{s_res.merge_comparisons:,}",
                    "Data Shifts (Merge)": f"{s_res.merge_shifts:,}",
                    "Time (ms)": f"{s_res.merge_time_ms:.2f}",
                    "Complexity Class": "O(n log n) in all cases",
                },
            ]
            st.table(sort_table_data)

            # Matplotlib Visualizer
            _render_sort_chart(s_res)

    # ---------------- TAB 3: SUMMARY & VIVA ----------------
    with tab_summary:
        st.markdown("### 📚 Comprehensive Complexity Matrix")
        matrix_data = [
            {
                "Algorithm": "Linear Search",
                "Best Case": "O(1)",
                "Average Case": "O(n)",
                "Worst Case": "O(n)",
                "Auxiliary Space": "O(1)",
                "Preconditions": "None (Any sequence)",
                "Stability / Notes": "Deterministic first-match",
            },
            {
                "Algorithm": "Binary Search",
                "Best Case": "O(1)",
                "Average Case": "O(log n)",
                "Worst Case": "O(log n)",
                "Auxiliary Space": "O(1) iterative",
                "Preconditions": "Input must be pre-sorted by search key",
                "Stability / Notes": "Deterministic first-match",
            },
            {
                "Algorithm": "Insertion Sort",
                "Best Case": "O(n)",
                "Average Case": "O(n²)",
                "Worst Case": "O(n²)",
                "Auxiliary Space": "O(1) sort (O(n) returned copy)",
                "Preconditions": "Comparable elements",
                "Stability / Notes": "Guaranteed Stable",
            },
            {
                "Algorithm": "Merge Sort",
                "Best Case": "O(n log n)",
                "Average Case": "O(n log n)",
                "Worst Case": "O(n log n)",
                "Auxiliary Space": "O(n) merge buffers",
                "Preconditions": "Comparable elements",
                "Stability / Notes": "Guaranteed Stable",
            },
        ]
        st.table(matrix_data)

        st.markdown("---")
        st.markdown("### 🎓 Academic Viva Walkthrough: Theoretical Big-O vs. Measured Timings")
        st.markdown(
            """
            #### Key Points to Explain to Faculty:
            1. **Why does Binary Search require pre-sorted data?**
               - Binary search relies on the invariant that if the middle element is greater than the target, the target *must* reside in the left partition. If the data is unsorted, this invariant is broken and elements would be missed.
            2. **Why does Insertion Sort outperform Merge Sort on already-sorted input?**
               - On already-sorted input, Insertion Sort performs only $n - 1$ comparisons and $0$ data shifts ($O(n)$ linear time), avoiding the recursive partitioning and buffer merging overhead of Merge Sort.
            3. **Why do theoretical operation counts differ from wall-clock milliseconds?**
               - Big-$O$ notation models growth rate as $n \\to \\infty$, ignoring constant factors ($c \\cdot g(n)$).
               - Real wall-clock time is influenced by hardware factors: CPU cache spatial locality, branch prediction, Python bytecode interpretation, and memory allocation overhead.
            4. **Data Safety in TaskForge:**
               - All custom sorting functions allocate a defensive working copy; caller collections and SQLite records are never mutated by sorting demonstrations.
            """
        )
