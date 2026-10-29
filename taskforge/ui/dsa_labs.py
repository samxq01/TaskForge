"""DSA Performance Laboratory UI module for Course Outcome 3 (CO3)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from taskforge.services.benchmark_service import (
    BenchmarkService,
    SearchBenchmarkResult,
    SortBenchmarkResult,
)
from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_BRAND,
    COLOR_SURFACE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    render_metric_strip,
    render_section_header,
    style_potadot_ax,
)


def _render_search_chart(result: SearchBenchmarkResult) -> None:
    """Render a clean Potadot-styled Matplotlib chart comparing comparisons and execution time."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    fig.patch.set_facecolor("#FFFFFF")

    algorithms = ["Linear Search", "Binary Search"]
    comparisons = [result.linear_comparisons, result.binary_comparisons]
    times_ms = [result.linear_time_ms, result.binary_time_ms]
    colors = ["#94A3B8", "#2563EB"]

    # 1. Comparison Count Bar Chart
    bars1 = ax1.bar(algorithms, comparisons, color=colors, width=0.42, edgecolor="#CBD5E1", linewidth=0.8)
    style_potadot_ax(ax1, title=f"Key Comparisons (Size: N={result.dataset_size})", ylabel="Comparisons")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{int(yval):,}", ha="center", va="bottom", color="#0F172A", fontsize=9, fontweight="bold")

    # 2. Execution Time (ms) Bar Chart
    bars2 = ax2.bar(algorithms, times_ms, color=colors, width=0.42, edgecolor="#CBD5E1", linewidth=0.8)
    style_potadot_ax(ax2, title="Execution Time (Avg ms)", ylabel="Milliseconds")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.4f} ms", ha="center", va="bottom", color="#0F172A", fontsize=9, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _render_sort_chart(result: SortBenchmarkResult) -> None:
    """Render a clean Potadot-styled Matplotlib chart comparing sorting comparisons and execution time."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    fig.patch.set_facecolor("#FFFFFF")

    algorithms = ["Insertion Sort", "Merge Sort"]
    comparisons = [result.insertion_comparisons, result.merge_comparisons]
    times_ms = [result.insertion_time_ms, result.merge_time_ms]
    colors = ["#F59E0B", "#2563EB"]

    # 1. Comparison Count Bar Chart
    bars1 = ax1.bar(algorithms, comparisons, color=colors, width=0.42, edgecolor="#CBD5E1", linewidth=0.8)
    style_potadot_ax(ax1, title=f"Key Comparisons ({result.distribution.capitalize()}, N={result.dataset_size})", ylabel="Comparisons")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{int(yval):,}", ha="center", va="bottom", color="#0F172A", fontsize=9, fontweight="bold")

    # 2. Execution Time (ms) Bar Chart
    bars2 = ax2.bar(algorithms, times_ms, color=colors, width=0.42, edgecolor="#CBD5E1", linewidth=0.8)
    style_potadot_ax(ax2, title=f"Execution Time (N={result.dataset_size})", ylabel="Milliseconds")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval, f"{yval:.2f} ms", ha="center", va="bottom", color="#0F172A", fontsize=9, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_dsa_performance_lab() -> None:
    """Render the full DSA Performance Lab interface for Searching and Sorting."""
    render_section_header(
        eyebrow="COURSE OUTCOME 3 (CO3) • EMPIRICAL ALGORITHM BENCHMARKING",
        title="Algorithm Performance Laboratory",
        subtitle="Benchmark custom linear vs. logarithmic searches and quadratic vs. divide-and-conquer sorts against synthetic reproducible datasets using high-resolution performance counters.",
    )

    tab_searching, tab_sorting, tab_summary = st.tabs(
        ["🔍 Searching Laboratory", "📊 Sorting Laboratory", "📚 Complexity Matrix & Viva Guide"]
    )

    # ---------------- TAB 1: SEARCHING LAB ----------------
    with tab_searching:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Linear Search vs. Binary Search
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Compare sequential scanning <code>O(n)</code> against divide-and-conquer <code>O(log n)</code> elimination on identical sorted data.
            </div>
            """,
            unsafe_allow_html=True,
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

            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            render_metric_strip([
                {"label": "Linear Search Time", "value": f"{res.linear_time_ms:.4f} ms", "caption": "Sequential Scan"},
                {"label": "Binary Search Time", "value": f"{res.binary_time_ms:.4f} ms", "caption": "Logarithmic"},
                {"label": "Linear Comparisons", "value": f"{res.linear_comparisons:,}", "caption": "O(n) steps"},
                {"label": "Binary Comparisons", "value": f"{res.binary_comparisons:,}", "caption": "O(log n) steps"},
            ])

            # Ratio highlight
            comp_ratio = res.linear_comparisons / max(res.binary_comparisons, 1)
            st.markdown(
                f"""
                <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; border-radius: 8px; padding: 1rem 1.3rem; margin-bottom: 1.2rem; font-size: 0.88rem; color: #0F172A; box-shadow: 0 1px 3px rgba(37,99,235,0.06);">
                    <strong style="color: #2563EB;">● Algorithmic Efficiency:</strong> Binary Search required <strong>{res.binary_comparisons}</strong> comparisons 
                    versus <strong>{res.linear_comparisons}</strong> for Linear Search (<strong style="color: #2563EB;">{comp_ratio:.1f}x reduction</strong> in comparison operations).
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Numerical Table
            table_data = [
                {
                    "Algorithm": "Linear Search",
                    "Target Value": res.target,
                    "Found?": "Yes" if res.linear_found else "No",
                    "Comparisons": res.linear_comparisons,
                    "Execution Time (ms)": f"{res.linear_time_ms:.5f}",
                    "Theoretical Complexity": "O(1) best, O(n) worst",
                },
                {
                    "Algorithm": "Binary Search",
                    "Target Value": res.target,
                    "Found?": "Yes" if res.binary_found else "No",
                    "Comparisons": res.binary_comparisons,
                    "Execution Time (ms)": f"{res.binary_time_ms:.5f}",
                    "Theoretical Complexity": "O(1) best, O(log n) worst",
                },
            ]
            st.dataframe(table_data, use_container_width=True)

            # Matplotlib Visualizer
            _render_search_chart(res)

    # ---------------- TAB 2: SORTING LAB ----------------
    with tab_sorting:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.2rem;">
                Insertion Sort vs. Merge Sort
            </div>
            <div style="font-size: 0.86rem; color: #475569; margin-bottom: 1.2rem;">
                Examine asymptotic scaling: quadratic <code>O(n²)</code> insertion sorting vs guaranteed <code>O(n log n)</code> recursive merge sorting.
            </div>
            """,
            unsafe_allow_html=True,
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

            st.markdown("<hr style='margin: 1.4rem 0 1rem 0;'>", unsafe_allow_html=True)
            render_metric_strip([
                {"label": "Insertion Sort Time", "value": f"{s_res.insertion_time_ms:.2f} ms", "caption": "O(n²) Quadratic"},
                {"label": "Merge Sort Time", "value": f"{s_res.merge_time_ms:.2f} ms", "caption": "O(n log n) Guaranteed"},
                {"label": "Insertion Comparisons", "value": f"{s_res.insertion_comparisons:,}", "caption": "Pairwise comparisons"},
                {"label": "Merge Comparisons", "value": f"{s_res.merge_comparisons:,}", "caption": "Divide-and-Conquer"},
            ])

            if s_res.is_correct:
                st.markdown(
                    """
                    <div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 4px solid #10B981; border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 1rem; font-size: 0.88rem; color: #047857;">
                        ● Correctness Verified: Both algorithms produced identical ground-truth sorted permutations.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("Output verification failed.")

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
            st.dataframe(sort_table_data, use_container_width=True)

            # Matplotlib Visualizer
            _render_sort_chart(s_res)

    # ---------------- TAB 3: SUMMARY & VIVA ----------------
    with tab_summary:
        st.markdown(
            """
            <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem; margin-bottom: 0.8rem;">
                Theoretical Complexity Matrix & Viva Examination Reference
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        st.dataframe(matrix_data, use_container_width=True)

        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.6rem 1.8rem; margin-top: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;">
                    Key Examiner Viva Questions & Answers
                </div>
                <div style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                    <p><strong style="color: #2563EB;">Q1: Why does Binary Search require pre-sorted data?</strong><br>
                    Binary Search requires an invariant: if the midpoint value exceeds the target, the target strictly cannot reside in the right partition. On unsorted inputs, this invariant fails and elements are erroneously bypassed.</p>

                    <p><strong style="color: #2563EB;">Q2: Why does Insertion Sort outperform Merge Sort on sorted arrays?</strong><br>
                    On already-sorted input, each item compares only once against its immediate left predecessor and incurs 0 shifts ($O(n)$ time), eliminating Merge Sort's recursive partition and merge buffer allocation overhead.</p>

                    <p><strong style="color: #2563EB;">Q3: How do we preserve persistence safety during benchmarks?</strong><br>
                    BenchmarkService creates synthetic, isolated Python lists in memory using high-resolution <code>time.perf_counter()</code>; persistent SQLite records are completely untouched.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
