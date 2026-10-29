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
| **CO1 + CO5** | **Phase 07** | Custom Heap Priority Queue, Smart Auto-Scheduler, Rule-Based Deadline Risk Analyzer | `taskforge/structures/priority_queue.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/services/risk_analyzer.py`<br>`taskforge/ui/scheduling_view.py` | **Implemented (Phase 07)** | `tests/test_priority_queue.py`<br>`tests/test_smart_scheduler.py`<br>`tests/test_risk_analyzer.py`<br>`tests/test_phase7_integration.py` (25 tests passing) |
| **CO5** | **Phase 08** | Critical Path Analyzer (DAG Longest Path) & What-If Schedule Simulator (Non-mutating) | `taskforge/services/critical_path.py`<br>`taskforge/services/what_if_simulator.py`<br>`taskforge/ui/planning_view.py` | **Implemented (Phase 08)** | `tests/test_critical_path.py`<br>`tests/test_what_if_simulator.py`<br>`tests/test_phase8_integration.py` (22 tests passing) |
| **All COs** | **Phase 09** | Full System Integration, Cross-Phase Workflows A–E, Reliability & Viva Documentation | Whole application integration | **Implemented (Phase 09)** | `tests/test_phase9_final_integration.py` (5 tests passing; 201 total project tests) |

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

### Phase 07 Extension (CO1 + CO5): Smart Priority Auto-Scheduler & Deadline Risk Analyzer
*(Implemented in Phase 07)*
- **CO1 (Binary Min-Heap Priority Queue):**
  - Pure Python generic binary Min-Heap `PriorityQueue[T, P]` in `taskforge/structures/priority_queue.py`.
  - Manual array-based heap with `_sift_up` and `_sift_down` algorithms ($O(\log N)$ push and pop, $O(1)$ peek).
  - Absolutely zero dependence on Python's built-in `heapq` module or external priority queue libraries.
  - Generates multi-criteria lexicographical ranking keys: `(-priority, has_deadline, normalized_deadline, duration, task_id, seq)`.
- **CO5 (Dependency Awareness & Cycle Safety):**
  - Integrates `detect_cycle()` from `DependencyGraph` prior to scheduling: rejects scheduling and warns user if deadlocked by circular dependencies.
  - Automatically filters only **eligible** Pending tasks (those with all prerequisite tasks in `Completed` status).
  - Isolates and reports blocked tasks and their blocking prerequisite task titles.
- **Deadline Risk Analyzer (`taskforge/services/risk_analyzer.py`):**
  - Rigorous, deterministic rule-based evaluation (strictly zero probabilistic or ML models).
  - 5 mutually exclusive primary categories evaluated in strict precedence:
    `Completed` $\to$ `Overdue` $\to$ `At Risk` $\to$ `Unscheduled` $\to$ `Safe`.
  - Calculates deterministic slack buffer: $\text{Slack} = \text{Remaining Time} - \text{Task Duration}$.
  - Flags incomplete prerequisites as risk drivers (`is_blocked = True`).
- **Coexistence Architecture:**
  - FIFO Execution Queue (`TaskQueueService`) and Smart Heap Scheduler (`SchedulerService`) coexist seamlessly; both read SQLite independently without mutative side-effects.
- **Verification:**
  - `tests/test_priority_queue.py`: 7 tests covering min-heap invariants, sift operations, push/pop/peek, and FIFO tie-breaking.
  - `tests/test_smart_scheduler.py`: 5 tests covering multi-criteria ranking, prerequisite exclusion, cycle detection abort, and FIFO coexistence.
  - `tests/test_risk_analyzer.py`: 10 tests covering all 5 categories, boundary conditions, and aggregate metrics.
  - `tests/test_phase7_integration.py`: 3 end-to-end integration tests verifying prerequisite unblocking, undo/redo synchronization, and queue coexistence.
  - **Total active tests for Phase 07:** 25 tests (all passing). Total project tests: 174 passing.

### Phase 08 Extension (CO5): Critical Path Analyzer and What-If Schedule Simulator
*(Implemented in Phase 08)*
- **Critical Path Analyzer (`taskforge/services/critical_path.py`):**
  - Implements dynamic programming over Kahn's topological sort on custom `DependencyGraph` without third-party graph packages (no NetworkX).
  - Calculates Earliest Start ($\text{ES}$) and Earliest Finish ($\text{EF}$) times in $\mathcal{O}(V + E)$ time.
  - Reconstructs the longest predecessor chain determining total project duration ($\max_{v \in V} \text{EF}[v]$).
  - Deterministic tie-breaking for equal-duration paths using task-ID ordering.
  - Cycle-safe: aborts gracefully and reports circular dependency cycle paths.
- **What-If Schedule Simulator (`taskforge/services/what_if_simulator.py`):**
  - Evaluates hypothetical delay propagation in-memory without persistent database mutation.
  - Status-aware: treats `Completed` tasks as completed prerequisites at $t=0$, modeling remaining work accurately.
  - Propagates delays strictly along dependent downstream paths; delays on parallel branches with sufficient float are absorbed without shifting the project completion date.
  - Guaranteed persistence safety: zero mutation of SQLite, models, undo history, or indexes.
- **Verification:**
  - `tests/test_critical_path.py`: 10 unit tests covering empty, single, linear, diamond branching, disconnected components, tie-breaking, cycle aborts, and recalculations.
  - `tests/test_what_if_simulator.py`: 9 unit tests covering validations, zero delay, linear propagation, intermediate task delay, parallel slack absorption, completed prereqs, and persistence safety.
  - `tests/test_phase8_integration.py`: 3 end-to-end integration tests verifying planning lifecycle, remaining-work differences, and cycle safety across services.
  - **Total active tests for Phase 08:** 22 tests (all passing). Total project tests: 196 passing.

### Phase 09 Final Integration (CO1–CO5 Comprehensive Validation)
*(Implemented in Phase 09)*
- **End-to-End Cross-Phase Verification:**
  - **Workflow A (Task & History):** Task creation, in-place editing, dual-stack undo/redo, deletion, and exact primary key ID restoration.
  - **Workflow B (Dependencies & Queue):** Dependency validation, blocked status exclusion, and FIFO task dispatching.
  - **Workflow C (Algorithms & Indexes):** Linear/Binary search, Insertion/Merge sort, BST deadline indexing, and Hash Table indexing.
  - **Workflow D (Smart Scheduling & Risk):** Heap-based task recommendation, dynamic justification, and deterministic deadline risk categorization.
  - **Workflow E (Planning & Persistence Safety):** DAG critical path dynamic programming, What-If delay simulation, and verified non-mutation of SQLite.
- **Verification Suite:**
  - `tests/test_phase9_final_integration.py`: 5 cross-phase integration tests verifying Workflows A through E.
  - **Grand Total Automated Tests:** 201 automated tests passing with 100% pass rate.
  - Full academic demonstration script available in [`docs/DEMO_GUIDE.md`](DEMO_GUIDE.md).

---

## Academic Viva Demonstration Procedure (CO5: Phase 08)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Access the Planning Module:**
   - In the sidebar navigation, select **🗺️ Critical Path & What-If Planning (CO5)**.
   - Click **🌱 Load Sample Tasks** in the sidebar if the project database is empty.
3. **Demonstrate the Critical Path Analyzer (Tab 1):**
   - Click **🔄 Recalculate Critical Path**.
   - Walk faculty through the top metrics: Total Project Duration, Critical Path Length, and Critical Task Ratio.
   - Point out the **🎯 Critical Dependency Chain** callout:
     * *“Notice the highlighted chain of tasks: this is the longest-duration dependency path from project start to finish. Our algorithm uses dynamic programming over Kahn's topological sort in $\mathcal{O}(V + E)$ time without relying on NetworkX.”*
     * *“Because independent branches execute concurrently, non-critical tasks have slack float and do not prolong the project.”*
   - Inspect the **Project Earliest Schedule (Gantt Chart)**:
     * Red bars denote Critical Path tasks with zero float.
     * Blue bars denote parallel tasks with float buffer.
4. **Demonstrate the What-If Schedule Simulator (Tab 2):**
   - Switch to the **🔮 What-If Schedule Simulator** tab.
   - Emphasize the **Persistence Safety Guarantee**:
     * *“This simulator operates entirely in memory on deep copies. It will never mutate SQLite database records, change task statuses, or alter application indexes.”*
   - **Scenario 1: Delaying a Parallel Non-Critical Task (Slack Absorption):**
     * Select a task on a parallel branch with float. Enter a moderate delay (e.g., 30 minutes).
     * Click **🚀 Run What-If Simulation**.
     * Show faculty:
       * *“Notice the outcome: Project Delay Impact is +0 min (Absorbed). Because this task has parallel float, its delay is absorbed without pushing the project completion date.”*
   - **Scenario 2: Delaying a Critical Path Task (Delay Propagation):**
     * Select a task on the Critical Path (e.g. Task #1 or Task #2).
     * Enter a delay of 45 minutes.
     * Click **🚀 Run What-If Simulation**.
     * Show faculty:
       * *“Notice the outcome: Project Delay Impact is +45 min. Downstream dependent tasks are shifted forward, pushing the entire project deadline.”*
     * Inspect the **Schedule Comparison Timeline** chart to visually verify which tasks moved (orange/red) versus which remained untouched (green/blue).

---

## Academic Viva Demonstration Procedure (CO1 + CO5: Phase 07)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Access the Smart Scheduling & Deadline Risks Module:**
   - In the sidebar navigation, select **🧠 Smart Scheduling & Deadline Risks (CO1 + CO5)**.
3. **Demonstrate the Binary Min-Heap Priority Queue (CO1):**
   - Click the expander **💡 Architectural Insight: FIFO Dispatch Queue vs. Smart Heap Auto-Scheduler**.
   - Explain to faculty:
     * *“Notice our dual queue design. In Phase 02, we built a FIFO Queue ($O(1)$ enqueue/dequeue) for fair execution dispatching. Here in Phase 07, we built a custom Binary Min-Heap Priority Queue ($O(\log N)$ push/pop) from scratch without using Python’s `heapq` module.”*
     * *“The Min-Heap uses a multi-criteria ranking key: $(-priority, has\_deadline, deadline, duration, id)$. This guarantees that urgent tasks and impending deadlines bubble to the root automatically.”*
4. **Demonstrate Dependency-Aware Scheduling (CO5):**
   - Show the **🎯 Top Recommended Task** card and the **Recommended Execution Sequence** table.
   - Point out that blocked tasks (tasks whose prerequisites are not yet completed) are automatically excluded from recommendations.
   - Inspect the **🔒 Blocked Tasks Waiting on Incomplete Prerequisites** expander to show exactly which prerequisite tasks are currently holding back dependent tasks.
5. **Demonstrate the Deterministic Deadline Risk Analyzer:**
   - Switch to the **🛡️ Deadline Risk Analyzer** tab.
   - Walk through the summary metrics cards: Safe, At Risk, Overdue, Unscheduled, and Blocked.
   - Explain the deterministic precedence rules:
     * *“Our risk engine does not guess or hallucinate. It applies deterministic precedence: Completed > Overdue > At Risk > Unscheduled > Safe.”*
     * *“If a task has available time less than its required duration, its slack buffer is negative, immediately categorizing it as At Risk. Similarly, any task blocked by incomplete prerequisites is flagged as At Risk.”*
   - Use the **Filter by Risk Category** selectbox to inspect only At Risk or Overdue tasks.
   - In the **Task Risk Diagnostics Inspector**, select a task to reveal its mathematical slack equation and prerequisite status.

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
