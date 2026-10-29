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
| **CO3** | **Phase 03** | Searching (Linear Search, Binary Search) & Sorting (Insertion Sort, Merge Sort) + DSA Performance Lab | `taskforge/algorithms/searching.py`<br>`taskforge/algorithms/sorting.py`<br>`taskforge/services/benchmark_service.py`<br>`taskforge/ui/dsa_labs.py` | **Implemented (Phase 03)** | `tests/test_searching.py`<br>`tests/test_sorting.py`<br>`tests/test_benchmarks.py`<br>`tests/test_dsa_integration.py` (34 tests passing) |
| **CO4** | **Phase 04** | Custom Binary Search Tree (BST) for deadline indexing and inorder traversal | `taskforge/structures/bst.py`<br>`taskforge/services/task_index.py`<br>`taskforge/ui/tree_view.py` | **Implemented (Phase 04)** | `tests/test_bst.py`<br>`tests/test_bst_integration.py` (20 tests passing) |
| **CO5** | **Phase 05** | Custom Adjacency-List Graph, BFS/DFS Traversal, Cycle Detection, Topological Sorting (Kahn's), Dependency Scheduler | `taskforge/graph/dependency_graph.py`<br>`taskforge/services/dependency_service.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/ui/dependency_view.py` | **Implemented (Phase 05)** | `tests/test_dependency_graph.py`<br>`tests/test_dependency_service.py`<br>`tests/test_scheduler.py`<br>`tests/test_dependency_integration.py` (28 tests passing) |
| **CO2** | **Phase 06** | Custom Hash Table (separate chaining), Task-ID Index, & Multi-Structure Evaluation Lab (List vs Hash vs BST) | `taskforge/structures/hash_table.py`<br>`taskforge/services/task_hash_index.py`<br>`taskforge/services/structure_evaluation.py`<br>`taskforge/ui/structure_evaluation_view.py` | **Implemented (Phase 06)** | `tests/test_hash_table.py`<br>`tests/test_task_hash_index.py`<br>`tests/test_structure_evaluation.py`<br>`tests/test_phase6_integration.py` (23 tests passing) |
| **CO1 + CO5** | **Phase 07** | Custom Heap Priority Queue, Smart Auto-Scheduler, Rule-Based Deadline Risk Analyzer | `taskforge/structures/priority_queue.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/services/risk_analyzer.py` | *Planned (Phase 07)* | Priority heap invariant tests, scheduler eligibility, risk boundary tests |
| **CO5** | **Phase 08** | Critical Path Analyzer (DAG Longest Path) & What-If Schedule Simulator (Non-mutating) | `taskforge/services/critical_path.py`<br>`taskforge/services/what_if_simulator.py` | *Planned (Phase 08)* | Critical path duration tests, downstream delay propagation tests, non-mutation proofs |
| **All COs** | **Phase 09** | Full Integration, System Verification, Performance Audit & Viva Documentation | Whole application integration | *Planned (Phase 09)* | End-to-end integration tests covering all CO criteria |

---

## Detailed Evidence for Implemented Course Outcomes

### CO1: Develop efficient solutions using stack and/or queue data structures.
*(Implemented in Phase 02 — see commit `30c3f9c`)*
- Custom generic `Stack` (LIFO) and `Queue` (FIFO singly-linked list without `collections.deque`).
- Dual-stack `UndoManager` reversing task creation, editing, deletion, and queue processing.
- FIFO pending-task dispatching via `TaskQueueService`.
- Verified by 26 automated tests.

### CO2: Evaluate the suitability of data structures for efficient storage and retrieval.
*(Implemented in Phase 06)*
- **Custom Hash Table (`taskforge/structures/hash_table.py`):**
  - Pure manual generic `HashTable[K, V]` using an internal list of buckets (`list[list[_HashEntry]]`).
  - Python dictionaries are strictly **not** used for internal bucket storage.
  - Implements **separate chaining** to handle collisions gracefully without data overwrites.
  - Dynamic resizing: Automatically doubles bucket capacity and rehashes entries when load factor $\alpha > 0.75$.
  - Exposes comprehensive diagnostic metrics: capacity $m$, items $n$, load factor $\alpha$, occupied buckets, colliding buckets, total collisions, and maximum chain length.
- **Task-ID Hash Indexing Service (`taskforge/services/task_hash_index.py`):**
  - Rebuilds in-memory hash table directly from SQLite persistent storage.
  - Enables rapid $O(1)$ average-case primary key lookup for tasks.
  - Synchronizes with SQLite across mutations and undo/redo cycles.
- **Multi-Structure Evaluation Service (`taskforge/services/structure_evaluation.py`):**
  - Controlled empirical comparison across **Sequential List Search** ($O(n)$), **Custom Hash Table** ($O(1)$ avg), and **Custom Binary Search Tree** ($O(\log n)$ avg).
  - Enforces strict fair-comparison rules: identical datasets, identical task ID keys, identical query targets, and separated construction vs. lookup timing.
  - Evaluates across varied workloads: Early hit (5%), Middle hit (50%), Late hit (95%), and Absent key (guaranteed miss).
  - Measures key comparisons / inspected entries outside timed blocks and validates output correctness.
- **Interactive UI Evaluation Lab (`taskforge/ui/structure_evaluation_view.py`):**
  - Interactive Hash Table sandbox with real-time collision trigger and bucket chain visualizer.
  - Live task-ID lookup widget measuring bucket chain inspections.
  - Comparative benchmark runner with dynamic Matplotlib charts (Lookup Time, Comparisons, Construction Time).
  - Academic complexity and trade-offs matrix.
- **Automated Verification:**
  - `tests/test_hash_table.py`: 12 unit tests covering insertions, duplicate upserts, deletions, collisions, separate chaining, comparisons, resizing, and capacity limits.
  - `tests/test_task_hash_index.py`: 3 tests covering SQLite synchronization, task retrieval, comparisons, and undo/redo consistency.
  - `tests/test_structure_evaluation.py`: 7 tests covering synthetic dataset generation, target selection, linear search baseline, hit/miss scenarios, and multi-size benchmarks.
  - `tests/test_phase6_integration.py`: 1 full workflow integration test verifying hash indexing alongside Phase 01–05 components.
  - **Total active tests for CO2:** 23 tests (all passing).

### CO3: Evaluate the performance of searching and sorting algorithms for solving engineering problems.
*(Implemented in Phase 03 — see commit `54548eb`)*
- Manual implementations of `linear_search`, `binary_search`, `insertion_sort`, and `merge_sort`.
- Interactive `DSA Performance Lab` measuring execution time via `time.perf_counter()` and recording comparisons/shifts.
- Verified by 34 automated tests.

### CO4: Develop tree structure for solving engineering problems.
*(Implemented in Phase 04 — see commit `b2a6b7b`)*
- Custom generic `BinarySearchTree` implementing manual 3-case node deletion, height calculation, and tree traversals.
- Composite key indexing `(has_no_deadline_flag, normalized_deadline, task_id)` preventing collisions.
- Verified by 20 automated tests.

### CO5: Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems.
*(Implemented in Phase 05 — see commit `69e2324`)*
- Custom directed `DependencyGraph` with adjacency list representation ($A \to B$ convention).
- 3-color DFS cycle detection and `would_create_cycle` safety check.
- Kahn's algorithm topological sorting with custom FIFO Queue.
- Dependency-aware scheduler filtering the FIFO task processing queue.
- Verified by 28 automated tests.

---

## Academic Viva Demonstration Procedure (CO2)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Access the Data Structure Evaluation Module:**
   - In the sidebar navigation, select **🧮 Data Structure Evaluation (CO2)**.
   - Click **🌱 Load Sample Tasks** in the sidebar to populate tasks if the database is empty.
3. **Demonstrate the Custom Hash Table Lab:**
   - Go to the **🗄️ Custom Hash Table Lab** tab.
   - Inspect the top metric cards showing Capacity ($m$), Stored Keys ($n$), Load Factor ($\alpha = n/m$), Collisions, and Max Chain Length.
   - Insert key-value pairs (e.g. `task_1` ➔ `Schema Design`).
   - Click **💥 Collision Demo** to demonstrate **separate chaining**:
     * Point out to faculty: *“Multiple keys have mapped into the same bucket. Notice that our implementation preserves all entries in a chain rather than overwriting previous values.”*
     * Look at the **Bucket Chains & Collision Structure** chart and table to observe the chained entries.
   - Delete one colliding key: Show that the other entries in the same bucket remain completely unaffected.
4. **Demonstrate the Production Task-ID Hash Index:**
   - Switch to the **🔍 Live Task-ID Hash Index** tab.
   - Select an existing Task ID from the dropdown.
   - Show how the hash table locates the task:
     * *“Notice the lookup message: Task found in 1 chain inspection. The primary key hash index gives constant $O(1)$ average retrieval time.”*
5. **Demonstrate the Multi-Structure Comparative Benchmark:**
   - Switch to the **🔬 Comparative Benchmark (List vs Hash vs BST)** tab.
   - Select Dataset Size: `1000`, Scenario: `Middle Hit (~50% mark)`, Repetitions: `250`.
   - Click **🚀 Run Comparative Benchmark**.
   - Walk faculty through the empirical results table and visual charts:
     * **Lookup Time:** Point out that Sequential List takes $O(n)$ time, BST takes $O(\log n)$ time, and Custom Hash Table takes $O(1)$ time.
     * **Key Comparisons:** Point out the difference in comparisons:
       - List: Scans $\approx 500$ items (halfway through 1,000 tasks).
       - BST: Inspects $\approx 10$ nodes ($\log_2 1000 \approx 10$).
       - Hash Table: Inspects $\approx 1$ chain entry.
     * **Construction Time:** Note that List construction is fastest ($O(n)$ array allocation), Hash Table requires hashing entries ($O(n)$), and BST requires tree node link updates ($O(n \log n)$).
   - Change scenario to `Absent Key (Miss Case)` and run again:
     * Observe that List must inspect all 1,000 items before confirming absence ($O(n)$), while Hash Table immediately accesses an empty bucket or small chain ($O(1)$).
6. **Conclude with Complexity & Trade-Offs (Tab 4):**
   - Summarize to faculty:
     * *“For pure primary-key retrieval, a Hash Table is optimal ($O(1)$).*
     * *For chronological deadline ordering and range queries, a BST is optimal ($O(\log n)$ with sorted Inorder traversal).*
     * *For small sequential queues and logs, a List is simplest.”*
