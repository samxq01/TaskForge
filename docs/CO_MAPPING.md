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
| **CO4** | **Phase 04** | Custom Binary Search Tree (BST) for deadline indexing and inorder traversal | `taskforge/structures/bst.py`<br>`taskforge/services/task_index.py`<br>`taskforge/ui/tree_view.py` | **Implemented (Active)** | `tests/test_bst.py`<br>`tests/test_bst_integration.py` (20 tests passing) |
| **CO5** | **Phase 05** | Custom Adjacency-List Graph, BFS/DFS Traversal, Cycle Detection, Topological Sorting | `taskforge/graph/dependency_graph.py`<br>`taskforge/ui/dependency_map.py` | *Planned (Phase 05)* | Directed graph edge tests, cycle prevention, prerequisite resolution tests |
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
*(Implemented in Phase 04)*
- **Custom Binary Search Tree (`taskforge/structures/bst.py`):**
  - Pure manual implementation of generic `TreeNode[K, V]` and `BinarySearchTree[K, V]`.
  - Implements `insert`, `search`, `delete` (3-case node deletion: leaf, 1 child, 2 children via in-order successor), and tree height calculation.
  - Implements tree traversals: `inorder_traversal()` (sorted key order), `preorder_traversal()` (prefix/reconstruction), and `postorder_traversal()` (postfix/bottom-up).
- **Task Deadline Indexing Service (`taskforge/services/task_index.py`):**
  - Dynamically builds the BST index from persistent SQLite records using composite keys:
    `key = (has_no_deadline_flag, normalized_deadline, task_id)`
  - Guarantees tasks with deadlines precede unscheduled tasks, and equal deadlines are deterministically tie-broken by task ID without key collisions or node overwrite.
  - Synchronizes seamlessly with task mutations and Undo/Redo cycles without modifying underlying SQLite data.
- **Interactive UI Tree View (`taskforge/ui/tree_view.py`):**
  - Live deadline-ordered table generated strictly from BST Inorder Traversal.
  - Interactive BST search widget testing exact key presence and absence.
  - Traversal laboratory comparing Inorder, Preorder, and Postorder sequences.
  - Hierarchical ASCII tree structure diagram and skewness diagnostic.
- **Automated Verification:**
  - `tests/test_bst.py`: 15 unit tests covering empty trees, insertion, search, duplicates, 3-case deletion, traversals, and left/right skewness.
  - `tests/test_bst_integration.py`: 5 integration tests covering SQLite index rebuilding, composite key sorting, search by deadline/ID, and consistency through mutations/undo/redo.
  - **Total active tests for CO4:** 20 tests (all passing).

---

## Academic Viva Demonstration Procedure (CO4)

1. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
2. **Access the BST Task Index:**
   - In the sidebar navigation, select **🌲 BST Task Index (CO4)**.
   - Click **🌱 Load Sample Tasks** in the sidebar to populate diverse tasks if the database is empty.
3. **Demonstrate Deadline-Ordered Retrieval (Inorder Traversal):**
   - In the **📋 Inorder Traversal (Deadline Order)** tab, observe the list of tasks.
   - Point out to faculty: *The order of these rows was NOT produced by SQL `ORDER BY` or Python `sorted()`. It is generated by an Inorder traversal (Left $\to$ Root $\to$ Right) on our custom Binary Search Tree, extracting nodes in strictly increasing deadline order ($O(n)$ time).*
   - Notice that tasks with deadlines appear first, and unscheduled tasks appear at the bottom.
4. **Demonstrate Tree Search:**
   - Switch to the **🔍 BST Key Search** tab.
   - Select any task from the dropdown and click **Execute BST Search**.
   - Explain to faculty: *The search traverses the tree nodes using key comparison, achieving $O(\log n)$ average search complexity without scanning the entire list.*
   - Click **Search Missing Key** and observe that it safely returns `None`.
5. **Demonstrate Tree Traversals & Structure:**
   - Open the **🔄 Traversal Laboratory** tab. Toggle between **Inorder**, **Preorder**, and **Postorder**. Point out how the visited sequence changes.
   - Open the **🌳 Visual Tree Structure** tab. Show the hierarchical tree diagram displaying the root, `├── (L)` subtrees, and `└── (R)` subtrees.
   - Highlight the **Skewness Analysis** metric showing tree height vs. minimum theoretical height.
