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
| **CO2** | **Phase 06** | Custom Hash Table (separate chaining) & Multi-Structure Storage/Retrieval Evaluation Lab | `taskforge/structures/hash_table.py`<br>`taskforge/services/structure_evaluation.py` | *Planned (Phase 06)* | Collision handling, load-factor analysis, comparative retrieval benchmark tests |
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
*(Implemented in Phase 05)*
- **Custom Adjacency-List Directed Graph (`taskforge/graph/dependency_graph.py`):**
  - Pure manual implementation of directed dependency graph without external algorithmic graph libraries (no NetworkX).
  - Enforces strict edge convention: $A \to B$ means Task B depends on Task A (Task A is a prerequisite for Task B).
  - Forward adjacency mapping $u \to \{v\}$ and reverse adjacency mapping $v \to \{u\}$ for $O(1)$ edge lookups and immediate in/out-degree inspection.
  - Cycle detection using 3-color Depth-First Search (WHITE=0, GRAY=1, BLACK=2) identifying back-edges and extracting circular loop sequences.
  - Pre-validation reachability check: `would_create_cycle(prereq, dep)` evaluates `has_path(dep, prereq)` to reject circular dependencies *before* persisting to SQLite.
  - Topological sorting via **Kahn's Algorithm** utilizing Phase 02 custom **FIFO Queue** with deterministic tie-breaking.
  - Traversals:
    - **BFS:** Uses custom generic `Queue` to explore task dependents level-by-level.
    - **DFS:** Uses custom generic `Stack` to explore deep prerequisite chains.
- **SQLite Dependency Persistence (`taskforge/storage.py`):**
  - Normalized `task_dependencies` table with composite primary key `(prerequisite_id, dependent_id)` and foreign key cascading deletes.
- **Dependency & Eligibility Services (`taskforge/services/dependency_service.py` & `scheduler.py`):**
  - Synchronizes in-memory graph with persistent SQLite storage.
  - Computes task eligibility: a task is eligible if its status is Pending and **all** prerequisites are Completed.
  - Identifies blocked tasks and surfaces their unresolved blockers.
- **FIFO Queue Integration (`taskforge/services/task_queue_service.py`):**
  - Only eligible pending tasks are enqueued into the FIFO processing queue; blocked tasks are safely deferred until prerequisites complete.
- **Interactive UI Dependency Map (`taskforge/ui/dependency_view.py`):**
  - Visual Matplotlib directed graph layout with status color-coding (Green=Completed, Yellow=In Progress, Blue=Eligible, Red=Blocked).
  - Dependency management forms with real-time cycle rejection warnings.
  - Step-by-step Topological Order execution sequence runner.
  - Interactive BFS and DFS traversal comparisons.
  - Sandbox circular dependency simulator for viva demonstration.
- **Automated Verification:**
  - `tests/test_dependency_graph.py`: 15 unit tests covering nodes, edges, reachability, BFS, DFS, cycle detection, Kahn's sort, and tie-breaking.
  - `tests/test_dependency_service.py`: 7 tests covering SQLite persistence, self-dependency rejection, cycle rejection, cascading deletes, and topological models.
  - `tests/test_scheduler.py`: 4 tests covering independent task readiness, blocker tracking, prerequisite completion unblocking, and multi-prerequisite satisfaction.
  - `tests/test_dependency_integration.py`: 2 full workflow tests verifying queue filtering, multi-stage completion, and undo/redo interaction.
  - **Total active tests for CO5:** 28 tests (all passing).

---

## Academic Viva Demonstration Procedure (CO5)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Access the Dependency Map:**
   - In the sidebar navigation, select **🔗 Dependency Map (CO5)**.
   - Click **🌱 Load Sample Tasks** in the sidebar to populate realistic sample tasks and dependency links.
3. **Demonstrate the Visual Graph & Adjacency Structure:**
   - In the **🗺️ Visual Graph** tab, inspect the directed dependency diagram.
   - Point out to faculty:
     * *“Each arrow $A \to B$ denotes that Task A must complete before Task B can start.”*
     * *“Notice the color coding: Completed tasks are green, In-Progress tasks are amber, Eligible tasks ready to start are blue, and Blocked tasks waiting for prerequisites are red.”*
   - Expand the **Raw Adjacency List & Degrees Table** to demonstrate in-degrees, out-degrees, and incoming/outgoing edges.
4. **Demonstrate Circular Dependency Rejection (Safety Invariant):**
   - Switch to the **➕ Manage Dependencies** tab.
   - Show how attempting to make an earlier task depend on a later task raises a cycle error:
     * Try adding a dependency from a downstream task to an upstream prerequisite.
     * Show the red warning: *“🚨 Cycle Prevention: Circular dependency rejected... Adding this dependency would cause a deadlock cycle.”*
     * Explain to faculty: *“Our `DependencyService` runs `would_create_cycle()` in memory using 3-color DFS before writing to SQLite, ensuring the schedule never deadlocks.”*
5. **Demonstrate Topological Sorting (Kahn’s Algorithm):**
   - Switch to the **📊 Topological Order (Kahn's)** tab.
   - Walk faculty through the computed linear sequence:
     * *“Kahn’s algorithm begins with tasks that have in-degree 0 (root prerequisites). It enqueues them into our custom FIFO Queue from Phase 02, dequeues each task, decrements the in-degrees of its dependent neighbors, and enqueues newly freed tasks.”*
     * *“This proves mathematically that all engineering dependencies are strictly honored.”*
6. **Demonstrate Graph Traversals (BFS vs. DFS):**
   - Switch to the **🔍 BFS & DFS Traversal** tab.
   - Select a root task (e.g. `#1 Setup Database Schema`).
   - Run **BFS**: Observe level-by-level exploration powered by our custom **Queue**.
   - Run **DFS**: Observe branch-by-branch deep exploration powered by our custom **Stack**.
7. **Demonstrate Cycle Simulation Sandbox:**
   - Switch to the **🧪 Cycle Simulator (Viva Demo)** tab.
   - Click **🧪 Simulate Cycle Detection** to demonstrate how a cycle `101 -> 102 -> 103 -> 101` is trapped and unpacked into an explicit cycle loop string.
