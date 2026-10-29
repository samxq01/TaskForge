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
| **CO1** | **Phase 02** | Custom Stack (LIFO undo/redo manager) & Custom Queue (FIFO task execution engine) | `taskforge/structures/stack.py`<br>`taskforge/structures/queue.py`<br>`taskforge/services/undo_manager.py`<br>`taskforge/services/task_queue_service.py` | **Implemented (Active)** | `tests/test_stack.py`<br>`tests/test_queue.py`<br>`tests/test_undo_manager.py`<br>`tests/test_task_queue_service.py`<br>`tests/test_phase2_integration.py` (26 tests passing) |
| **CO3** | **Phase 03** | Searching (Linear Search, Binary Search) & Sorting (Insertion Sort, Merge Sort) + DSA Performance Lab | `taskforge/algorithms/searching.py`<br>`taskforge/algorithms/sorting.py`<br>`taskforge/services/benchmark_service.py` | *Planned (Phase 03)* | Correctness tests, deterministic tie-breaking, benchmark reproducibility tests |
| **CO4** | **Phase 04** | Custom Binary Search Tree (BST) for deadline indexing and inorder traversal | `taskforge/structures/bst.py` | *Planned (Phase 04)* | BST insertion, search, traversals, composite key handling, tree rebuilding tests |
| **CO5** | **Phase 05** | Custom Adjacency-List Graph, BFS/DFS Traversal, Cycle Detection, Topological Sorting | `taskforge/graph/dependency_graph.py`<br>`taskforge/ui/dependency_map.py` | *Planned (Phase 05)* | Directed graph edge tests, cycle prevention, prerequisite resolution tests |
| **CO2** | **Phase 06** | Custom Hash Table (separate chaining) & Multi-Structure Storage/Retrieval Evaluation Lab | `taskforge/structures/hash_table.py`<br>`taskforge/services/structure_evaluation.py` | *Planned (Phase 06)* | Collision handling, load-factor analysis, comparative retrieval benchmark tests |
| **CO1 + CO5** | **Phase 07** | Custom Heap Priority Queue, Smart Auto-Scheduler, Rule-Based Deadline Risk Analyzer | `taskforge/structures/priority_queue.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/services/risk_analyzer.py` | *Planned (Phase 07)* | Priority heap invariant tests, scheduler eligibility, risk boundary tests |
| **CO5** | **Phase 08** | Critical Path Analyzer (DAG Longest Path) & What-If Schedule Simulator (Non-mutating) | `taskforge/services/critical_path.py`<br>`taskforge/services/what_if_simulator.py` | *Planned (Phase 08)* | Critical path duration tests, downstream delay propagation tests, non-mutation proofs |
| **All COs** | **Phase 09** | Full Integration, System Verification, Performance Audit & Viva Documentation | Whole application integration | *Planned (Phase 09)* | End-to-end integration tests covering all CO criteria |

---

## Detailed Evidence for Implemented Course Outcomes

### CO1: Develop efficient solutions using stack and/or queue data structures.

- **Custom Stack Implementation (`taskforge/structures/stack.py`):**
  - Custom generic `Stack[T]` strictly upholding LIFO principles with `push`, `pop`, `peek`, `is_empty`, and `size` methods.
  - Guarantees $O(1)$ operations with custom `EmptyStackError` handling.
- **Custom Queue Implementation (`taskforge/structures/queue.py`):**
  - Custom generic `Queue[T]` implementing FIFO mechanics using an internal singly-linked list (`_Node`).
  - Does NOT use `collections.deque` or $O(n)$ `list.pop(0)`. Guarantees strict $O(1)$ enqueue and $O(1)$ dequeue.
- **Dual-Stack Undo/Redo Engine (`taskforge/services/undo_manager.py`):**
  - Manages session-level action history across task creation, editing, and deletion using dual LIFO stacks (`_undo_stack` and `_redo_stack`).
  - Restores exact original task IDs, timestamps, and fields in SQLite.
  - Automatically resets redo stack upon new mutations to prevent branched history corruption.
- **FIFO Task Dispatcher (`taskforge/services/task_queue_service.py`):**
  - Enqueues all `Pending` tasks ordered deterministically by `created_at ASC, id ASC`.
  - Dispatches tasks via `process_next_task()`, updating status to `In Progress` in SQLite and pushing an undoable action to the Undo Stack.
- **Supporting Test Evidence:**
  - `tests/test_stack.py`: 7 tests verifying LIFO order, empty exceptions, and safe inspection.
  - `tests/test_queue.py`: 8 tests verifying FIFO order, constant time head/tail dispatching, and exceptions.
  - `tests/test_undo_manager.py`: 6 tests verifying reversible creation, editing, deletion, and redo invalidation.
  - `tests/test_task_queue_service.py`: 4 tests verifying pending queue ordering and status transitions.
  - `tests/test_phase2_integration.py`: 1 end-to-end integration test verifying full create-undo-redo-process-undo-redo lifecycle.
  - **Total active tests for CO1:** 26 tests (all passing).

---

## Academic Viva Demonstration Procedure (CO1)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Demonstrate FIFO Queue (Task Processing):**
   - Click **🌱 Load Sample Tasks** in the sidebar.
   - Navigate to **🔄 Task Processing & History (CO1)** in the sidebar navigation.
   - Show the **📋 FIFO Pending Queue** tab.
   - Point out that tasks appear in order of creation time (#1 at the front).
   - Click **⚡ Process Next Task (FIFO Dequeue)**. Observe the front task status change from `Pending` to `In Progress` and leave the queue.
3. **Demonstrate LIFO Undo/Redo:**
   - Switch to the **⏪ LIFO Undo / Redo Stacks** tab.
   - Show that the processing action sits at the top of the **📚 Undo Stack**.
   - Click **↩️ Undo**. Observe the task revert back to `Pending` in the database and re-enter the queue.
   - Point out that the action transferred to the **📚 Redo Stack**.
   - Click **↪️ Redo**. Observe the action re-applied to `In Progress` and transferred back to the Undo Stack.
4. **Demonstrate Task Deletion Undo:**
   - Go to **📋 Task Dashboard & Registry**, delete any task.
   - Notice the deletion action appear on the Undo Stack.
   - Click **↩️ Undo** and show that the task is restored with its exact original primary key ID and data!
