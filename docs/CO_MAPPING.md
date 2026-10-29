# TaskForge — Course Outcome (CO) Mapping

This document provides the official Course Outcome (CO) mapping for **TaskForge: Intelligent Task Scheduling and Dependency Management System**. It aligns the academic course outcomes with corresponding data structures, algorithms, modular implementations, and test suites.

---

## Official Course Outcomes

> **CO1:** Develop efficient solutions using stack and/or queue data structures.
> 
> **CO2:** Evaluate the suitability of data structures for efficient storage and retrieval.
> 
> **CO3:** Evaluate the performance of searching and sorting algorithms for solving engineering problems.
> 
> **CO4:** Develop tree structure for solving engineering problems.
> 
> **CO5:** Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.

---

## Course Outcome Feature & Implementation Matrix

| Course Outcome | Project Phase | Planned Feature & Data Structure | Target Implementation Module | Implementation Status | Test Suite & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Foundation** | **Phase 01** | Task Model, SQLite Storage, Parameterized Queries, Interactive Dashboard | `taskforge/models.py`<br>`taskforge/storage.py`<br>`taskforge/ui/` | **Implemented (Phase 01)** | `tests/test_models.py`<br>`tests/test_storage.py` (18 tests passing) |
| **CO1** | **Phase 02** | Custom Stack (LIFO undo/redo manager) & Custom Queue (FIFO task execution engine) | `taskforge/structures/stack.py`<br>`taskforge/structures/queue.py`<br>`taskforge/services/undo_manager.py`<br>`taskforge/services/task_queue_service.py` | **Implemented (Phase 02)** | `tests/test_stack.py`<br>`tests/test_queue.py`<br>`tests/test_undo_manager.py`<br>`tests/test_task_queue_service.py`<br>`tests/test_phase2_integration.py` (26 tests passing) |
| **CO3** | **Phase 03** | Searching (Linear Search, Binary Search) & Sorting (Insertion Sort, Merge Sort) + DSA Performance Lab | `taskforge/algorithms/searching.py`<br>`taskforge/algorithms/sorting.py`<br>`taskforge/services/benchmark_service.py`<br>`taskforge/ui/dsa_labs.py` | **Implemented (Active)** | `tests/test_searching.py`<br>`tests/test_sorting.py`<br>`tests/test_benchmarks.py`<br>`tests/test_dsa_integration.py` (34 tests passing) |
| **CO4** | **Phase 04** | Custom Binary Search Tree (BST) for deadline indexing and inorder traversal | `taskforge/structures/bst.py` | *Planned (Phase 04)* | BST insertion, search, traversals, composite key handling, tree rebuilding tests |
| **CO5** | **Phase 05** | Custom Adjacency-List Graph, BFS/DFS Traversal, Cycle Detection, Topological Sorting | `taskforge/graph/dependency_graph.py`<br>`taskforge/ui/dependency_map.py` | *Planned (Phase 05)* | Directed graph edge tests, cycle prevention, prerequisite resolution tests |
| **CO2** | **Phase 06** | Custom Hash Table (separate chaining) & Multi-Structure Storage/Retrieval Evaluation Lab | `taskforge/structures/hash_table.py`<br>`taskforge/services/structure_evaluation.py` | *Planned (Phase 06)* | Collision handling, load-factor analysis, comparative retrieval benchmark tests |
| **CO1 + CO5** | **Phase 07** | Custom Heap Priority Queue, Smart Auto-Scheduler, Rule-Based Deadline Risk Analyzer | `taskforge/structures/priority_queue.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/services/risk_analyzer.py` | *Planned (Phase 07)* | Priority heap invariant tests, scheduler eligibility, risk boundary tests |
| **CO5** | **Phase 08** | Critical Path Analyzer (DAG Longest Path) & What-If Schedule Simulator (Non-mutating) | `taskforge/services/critical_path.py`<br>`taskforge/services/what_if_simulator.py` | *Planned (Phase 08)* | Critical path duration tests, downstream delay propagation tests, non-mutation proofs |
| **All COs** | **Phase 09** | Full Integration, System Verification, Performance Audit & Viva Documentation | Whole application integration | *Planned (Phase 09)* | End-to-end integration tests covering all CO criteria |

---

## Detailed Evidence for Implemented Course Outcomes

### CO1: Develop efficient solutions using stack and/or queue data structures.
*(Implemented in Phase 02 — see previous commit `30c3f9c`)*
- Custom generic `Stack` (LIFO) and `Queue` (FIFO singly-linked list without `collections.deque`).
- Dual-stack `UndoManager` reversing task creation, editing, deletion, and queue processing.
- FIFO pending-task dispatching via `TaskQueueService`.
- Verified by 26 automated tests.

### CO3: Evaluate the performance of searching and sorting algorithms for solving engineering problems.
*(Implemented in Phase 03)*
- **Manual Searching Algorithms (`taskforge/algorithms/searching.py`):**
  - `linear_search`: Sequential search with $O(1)$ best, $O(n)$ average/worst case, returning deterministic first-matches.
  - `binary_search`: Iterative divide-and-conquer search with $O(\log n)$ efficiency on pre-sorted data.
- **Manual Sorting Algorithms (`taskforge/algorithms/sorting.py`):**
  - `insertion_sort`: Stable incremental sort ($O(n)$ best case on sorted data, $O(n^2)$ worst case).
  - `merge_sort`: Stable divide-and-conquer sort with guaranteed $O(n \log n)$ time across all distributions.
  - Custom key functions: `task_deadline_key` (deadline ascending, unscheduled last), `task_priority_key` (Urgent to Low), `task_priority_deadline_key` (combined tie-break), and `task_id_key`.
- **DSA Performance Laboratory (`taskforge/services/benchmark_service.py`, `taskforge/ui/dsa_labs.py`):**
  - Empirical evaluation comparing Linear vs. Binary search across first, middle, last, and absent targets.
  - Comparison of Insertion vs. Merge sort on randomized, sorted, and reverse-sorted distributions across configurable sizes ($N=100$ to $N=5000$).
  - Measured with `time.perf_counter()`, recording exact comparison and data-shift operations.
  - Visualized using Matplotlib bar charts.
- **Automated Verification:**
  - `tests/test_searching.py`: 13 tests covering edge cases, positions, duplicates, and task lookups.
  - `tests/test_sorting.py`: 14 tests covering stability, reverse flags, distributions, and task sorting rules.
  - `tests/test_benchmarks.py`: 6 tests verifying reproducible benchmark runs, metric shapes, and distributions.
  - `tests/test_dsa_integration.py`: 1 integration test verifying non-mutating search and sort over live SQLite records.
  - **Total active tests for CO3:** 34 tests (all passing).

---

## Academic Viva Demonstration Procedure (CO3)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Demonstrate Custom Task Sorting on the Dashboard:**
   - In **📋 Task Dashboard & Registry**, locate the **⚡ Sort Tasks By** selector.
   - Select **Deadline Ascending** and choose **Merge Sort (O(n log n))**.
   - Show that tasks immediately reorder with earliest deadlines first, while unscheduled tasks are pushed to the end. Point out the operational counter badge (`Sorted via Merge Sort in X comparisons, Y shifts`).
   - Switch to **Priority Descending** with **Insertion Sort (O(n²))**. Show that Urgent (P4) tasks appear first, followed by High, Medium, and Low.
3. **Demonstrate Algorithm Search by Task ID:**
   - Open the **🔎 Algorithm Search Demonstration** expander on the dashboard.
   - Enter a target Task ID and select **Binary Search**.
   - Explain to faculty: *Binary Search requires pre-sorting by Task ID first, then operates in $O(\log n)$ comparisons.* Show that it locates the task in very few comparisons.
4. **Demonstrate the DSA Performance Lab:**
   - Navigate to **🔬 DSA Performance Lab (CO3)** from the sidebar.
   - Under **🔍 Searching Laboratory**, set $N=5000$ and target to **Middle Element**. Click **Run Searching Benchmark**.
   - Show the resulting chart: Linear Search requires $\approx 2500$ comparisons, whereas Binary Search needs only $\approx 12$ comparisons!
   - Under **📊 Sorting Laboratory**, set $N=2000$ and distribution to **Randomized**. Click **Run Sorting Benchmark**.
   - Point out that Merge Sort runs significantly faster and executes far fewer operations than Insertion Sort's quadratic shifts.
   - Now change distribution to **Already Sorted**. Click **Run Sorting Benchmark**.
   - Point out that Insertion Sort now executes only $n-1 = 1999$ comparisons ($O(n)$ best case), illustrating why understanding theoretical complexity matters in engineering!
