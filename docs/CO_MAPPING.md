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
| **Foundation** | **Phase 01** | Task Model, SQLite Storage, Parameterized Queries, Interactive Dashboard | `taskforge/models.py`<br>`taskforge/storage.py`<br>`taskforge/ui/` | **Implemented (Active)** | `tests/test_models.py`<br>`tests/test_storage.py` (18 tests passing) |
| **CO1** | **Phase 02** | Custom Stack (LIFO undo/redo manager) & Custom Queue (FIFO task execution engine) | `taskforge/structures/stack.py`<br>`taskforge/structures/queue.py`<br>`taskforge/services/undo_manager.py` | *Planned (Phase 02)* | Normal & edge operations, empty stack/queue checks, undo/redo persistence tests |
| **CO3** | **Phase 03** | Searching (Linear Search, Binary Search) & Sorting (Insertion Sort, Merge Sort) + DSA Performance Lab | `taskforge/algorithms/searching.py`<br>`taskforge/algorithms/sorting.py`<br>`taskforge/services/benchmark_service.py` | *Planned (Phase 03)* | Correctness tests, deterministic tie-breaking, benchmark reproducibility tests |
| **CO4** | **Phase 04** | Custom Binary Search Tree (BST) for deadline indexing and inorder traversal | `taskforge/structures/bst.py` | *Planned (Phase 04)* | BST insertion, search, traversals, composite key handling, tree rebuilding tests |
| **CO5** | **Phase 05** | Custom Adjacency-List Graph, BFS/DFS Traversal, Cycle Detection, Topological Sorting | `taskforge/graph/dependency_graph.py`<br>`taskforge/ui/dependency_map.py` | *Planned (Phase 05)* | Directed graph edge tests, cycle prevention, prerequisite resolution tests |
| **CO2** | **Phase 06** | Custom Hash Table (separate chaining) & Multi-Structure Storage/Retrieval Evaluation Lab | `taskforge/structures/hash_table.py`<br>`taskforge/services/structure_evaluation.py` | *Planned (Phase 06)* | Collision handling, load-factor analysis, comparative retrieval benchmark tests |
| **CO1 + CO5** | **Phase 07** | Custom Heap Priority Queue, Smart Auto-Scheduler, Rule-Based Deadline Risk Analyzer | `taskforge/structures/priority_queue.py`<br>`taskforge/services/scheduler.py`<br>`taskforge/services/risk_analyzer.py` | *Planned (Phase 07)* | Priority heap invariant tests, scheduler eligibility, risk boundary tests |
| **CO5** | **Phase 08** | Critical Path Analyzer (DAG Longest Path) & What-If Schedule Simulator (Non-mutating) | `taskforge/services/critical_path.py`<br>`taskforge/services/what_if_simulator.py` | *Planned (Phase 08)* | Critical path duration tests, downstream delay propagation tests, non-mutation proofs |
| **All COs** | **Phase 09** | Full Integration, System Verification, Performance Audit & Viva Documentation | Whole application integration | *Planned (Phase 09)* | End-to-end integration tests covering all CO criteria |

---

## Phase 01 Implementation Evidence

- **Task Domain Model (`taskforge/models.py`):**
  - Typed dataclass with validation for unique IDs, non-empty titles, strict priority bounds (1 to 4), positive duration (> 0 min), and verified lifecycle states (`Pending`, `In Progress`, `Completed`).
  - Safe deadline handling: Optional deadline, with date-only inputs normalized to 23:59:59 end-of-day.
  - Overdue status calculation relative to injectable reference timestamps.
- **Persistent Storage (`taskforge/storage.py`):**
  - Parameterized SQLite operations prevent SQL injection.
  - Automated schema and index initialization (`tasks`, `idx_tasks_status`, `idx_tasks_priority`, `idx_tasks_due_date`).
  - Full CRUD operations: `create_task`, `get_task`, `list_tasks` (with status, priority, and text search), `update_task`, `delete_task`, and `count_tasks`.
- **Streamlit Web Interface (`app.py`, `taskforge/ui/`):**
  - Real-time dashboard with metrics (Total, Pending, In Progress, Completed, Overdue).
  - Add Task and Edit Task forms with client-side and server-side validation.
  - Search and filter controls by status and priority.
  - Delete safeguard with confirmation before record removal.
- **Automated Verification:**
  - 18 automated unit and integration tests passing in `tests/test_models.py` and `tests/test_storage.py` utilizing isolated temporary databases.
