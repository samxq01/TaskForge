# TaskForge — Intelligent Task Scheduling and Dependency Management System

TaskForge is a Python web application that combines task management with practical demonstrations of **Data Structures and Algorithms (DSA)**. It helps users manage tasks, deadlines, priorities, dependencies, and project schedules while serving as an academic showcase for five official Course Outcomes (CO1–CO5).

---

## 🌟 Key Features

### Phase 01: Foundation & Task Management
- **Typed Task Domain Model:** Enforces domain invariants (non-empty titles, strict priorities 1–4, positive durations, and valid lifecycle states).
- **Persistent SQLite Storage:** Robust relational schema with parameterized queries, indexes for performance, and foreign-key awareness.
- **Interactive Streamlit Dashboard:**
  - Real-time summary metric cards (Total, Pending, In Progress, Completed, Overdue).
  - Add Task form with custom deadline, duration, and priority inputs.
  - Multi-criteria filtering by Status, Priority, and keyword search (Title/Description).
  - In-place editing and deletion with safety confirmations.
  - One-click sample task loader for quick live demonstration.
- **Safe Date & Deadline Handling:** Supports optional deadlines, automatic overdue calculation, and end-of-day normalization for date-only entries.

### Phase 02: Linear Data Structures & Undo/Redo (CO1)
- **Custom Stack (LIFO):** Pure Python generic `Stack[T]` with $O(1)$ `push`, `pop`, and `peek` operations.
- **Custom Queue (FIFO):** Singly-linked list implementation of generic `Queue[T]` guaranteeing $O(1)$ `enqueue` and `dequeue` without relying on `collections.deque` or $O(n)$ `list.pop(0)`.
- **Dual-Stack Undo/Redo Engine:** Real-world reversible operations across task creation, editing, deletion, and queue processing. Restores exact original task IDs in SQLite and safely invalidates redo branches upon new mutations.
- **Deterministic FIFO Task Dispatching:** Pending tasks are queued according to creation timestamp (`created_at ASC, id ASC`) and dispatched via a one-click `Process Next Task` action.

### Phase 03: Searching, Sorting, and DSA Performance Lab (CO3)
- **Manual Searching Algorithms:**
  - **Linear Search:** Sequential search ($O(1)$ best, $O(n)$ average/worst case) with deterministic first-match resolution.
  - **Binary Search:** Iterative divide-and-conquer search ($O(\log n)$) on pre-sorted data with duplicate-safe first-occurrence detection.
- **Manual Sorting Algorithms:**
  - **Insertion Sort:** Stable incremental sorting with $O(n)$ best case on sorted data and $O(n^2)$ worst case.
  - **Merge Sort:** Stable divide-and-conquer sorting with guaranteed $O(n \log n)$ performance across all input distributions.
  - **Task Sorting Rules:** Deterministic ordering by Deadline (earliest first), Priority (Urgent to Low), Priority & Deadline combined, and Task ID ascending.
- **DSA Performance Laboratory:** Interactive benchmark runner measuring execution time using `time.perf_counter()` and recording comparisons/shifts, visualized with Matplotlib.

### Phase 04: Binary Search Tree Task Index (CO4)
- **Custom Binary Search Tree (BST):** Generic `TreeNode[K, V]` and `BinarySearchTree[K, V]` implementing manual `insert`, `search`, and 3-case `delete`.
- **Composite Deadline Indexing:** Indexes tasks using `(has_no_deadline_flag, normalized_deadline, task_id)` ensuring scheduled tasks precede unscheduled tasks and identical deadlines are uniquely preserved.
- **Deadline-Ordered Inorder Retrieval:** Inorder traversal ($O(n)$) extracts all tasks in chronological deadline order directly from the tree structure.
- **Interactive Tree Visualizer & Lab:** Traversal laboratory for Inorder, Preorder, and Postorder sequences, interactive exact key search, hierarchical ASCII tree diagram, and skewness diagnostics.

### Phase 05: Dependency Graph, Traversal, and Visual Map (CO5)
- **Custom Directed Graph (`DependencyGraph`):** Manual adjacency-list directed graph implementation representing $A \to B$ prerequisites without external graph packages (no NetworkX).
- **Cycle Detection & Prevention:** Pre-validation reachability check (`would_create_cycle`) and 3-color DFS state tracking (WHITE, GRAY, BLACK) preventing circular dependencies from being persisted to SQLite.
- **Topological Sorting (Kahn's Algorithm):** Derives deterministic linear task execution order using in-degrees and Phase 02 custom **FIFO Queue**.
- **Graph Traversals:** Interactive Breadth-First Search (BFS) using custom **Queue** and Depth-First Search (DFS) using custom **Stack**.
- **Dependency-Aware Scheduling:** Identifies blocked tasks with incomplete prerequisites and filters the active FIFO processing queue so only unblocked tasks are dispatched.
- **Interactive UI Dependency Map:** Visual Matplotlib directed graph with execution status color-coding, adjacency and in/out-degree tables, and a dedicated viva cycle simulator.

### Phase 06: Custom Hash Table and Data Structure Evaluation (CO2)
- **Custom Hash Table (`HashTable`):** Pure manual implementation using separate chaining without Python dictionaries for internal bucket storage.
- **Dynamic Resizing & Rehashing:** Doubles capacity when load factor $\alpha = n / m > 0.75$, maintaining $O(1)$ average-case operations.
- **Task-ID Hash Index:** In-memory hash indexing of SQLite task records for rapid constant-time primary key retrieval.
- **Multi-Structure Evaluation Lab:** Controlled benchmark comparing Sequential List ($O(n)$), Custom Hash Table ($O(1)$ avg), and Custom BST ($O(\log n)$ avg) using equivalent datasets, targets, and operations.
- **Interactive UI Lab & Charts:** Collision trigger demo, bucket distribution graphs, real-time comparison tables, and Matplotlib timing/comparison charts.

---

## 🛠️ Technology Stack

- **Language:** Python 3.11+ (Tested on Python 3.12)
- **Web Interface:** [Streamlit](https://streamlit.io/)
- **Database:** SQLite (`sqlite3` with parameterized queries)
- **Testing:** `pytest`
- **Visualization:** `matplotlib`

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/samxq01/TaskForge.git
cd TaskForge
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Running the Application

Launch the Streamlit web dashboard:

```bash
streamlit run app.py
```

Once launched, open your web browser at `http://localhost:8501`.

---

## 🧪 Running the Test Suite

Run all automated unit and integration tests:

```bash
pytest -v
```

All database tests use isolated temporary databases to ensure tests never contaminate user records.

---

## 📁 Project Structure

```text
TaskForge/
├── app.py                          # Main Streamlit web application entrypoint
├── requirements.txt                # Project dependencies
├── README.md                       # Project overview and setup instructions
├── .gitignore                      # Git exclusions (databases, virtualenvs, caches)
├── taskforge/                      # Core package
│   ├── __init__.py                 # Package initialization
│   ├── models.py                   # Typed Task dataclass and validation
│   ├── storage.py                  # SQLite storage layer with parameterized queries & dependency table
│   ├── structures/                 # Custom manual DSA implementations (CO1, CO2, CO4)
│   │   ├── __init__.py
│   │   ├── stack.py                # Generic LIFO Stack implementation (CO1)
│   │   ├── queue.py                # Generic FIFO Queue (singly-linked list) (CO1)
│   │   ├── bst.py                  # Generic Binary Search Tree (CO4)
│   │   └── hash_table.py           # Generic Hash Table with separate chaining (CO2)
│   ├── graph/                      # Custom graph implementations (CO5)
│   │   ├── __init__.py
│   │   └── dependency_graph.py     # Custom adjacency-list Directed Graph, BFS, DFS, Kahn's sort (CO5)
│   ├── algorithms/                 # Custom manual algorithms (CO3)
│   │   ├── __init__.py
│   │   ├── searching.py            # Manual Linear Search & Binary Search
│   │   └── sorting.py              # Manual Insertion Sort & Merge Sort
│   ├── services/                   # Application service layer
│   │   ├── __init__.py
│   │   ├── undo_manager.py         # Dual-stack Undo/Redo manager
│   │   ├── task_queue_service.py   # FIFO pending task dispatcher with dependency awareness
│   │   ├── benchmark_service.py    # Searching & Sorting benchmark runner
│   │   ├── task_index.py           # BST deadline indexing service (CO4)
│   │   ├── task_hash_index.py      # HashTable task-ID indexing service (CO2)
│   │   ├── structure_evaluation.py # List vs HashTable vs BST evaluation engine (CO2)
│   │   ├── dependency_service.py   # Graph SQLite sync and cycle validation (CO5)
│   │   └── scheduler.py            # Dependency-aware task eligibility evaluator (CO5)
│   └── ui/                         # Modular Streamlit UI components
│       ├── __init__.py
│       ├── dashboard.py            # Dashboard metrics, filters, task table, custom sorting
│       ├── task_manager.py         # Task creation and editing forms
│       ├── history_view.py         # CO1 Queue & Stack visualizer and viva guide
│       ├── dsa_labs.py             # CO3 DSA Performance Lab & Matplotlib charts
│       ├── tree_view.py            # CO4 BST Task Index, Traversals & Tree Visualizer
│       ├── dependency_view.py      # CO5 Dependency Map, Topological Order & Traversals
│       └── structure_evaluation_view.py # CO2 Hash Table Lab & Structure Comparison
├── tests/                          # Automated test suite (149 tests)
│   ├── __init__.py
│   ├── test_models.py              # Domain model and validation tests
│   ├── test_storage.py             # SQLite CRUD and persistence tests
│   ├── test_stack.py               # Custom Stack unit tests
│   ├── test_queue.py               # Custom Queue unit tests
│   ├── test_undo_manager.py        # Undo/Redo manager tests
│   ├── test_task_queue_service.py  # FIFO queue service tests
│   ├── test_phase2_integration.py  # Phase 02 workflow integration test
│   ├── test_searching.py           # Linear Search & Binary Search unit tests
│   ├── test_sorting.py             # Insertion Sort & Merge Sort unit tests
│   ├── test_benchmarks.py          # BenchmarkService unit tests
│   ├── test_dsa_integration.py     # Live task sorting & searching integration tests
│   ├── test_bst.py                 # Custom BST unit tests (CO4)
│   ├── test_bst_integration.py     # Task index service & SQLite integration tests (CO4)
│   ├── test_dependency_graph.py    # Custom DependencyGraph unit tests (CO5)
│   ├── test_dependency_service.py  # Dependency service & SQLite persistence tests (CO5)
│   ├── test_scheduler.py           # Scheduler eligibility & blocker tests (CO5)
│   ├── test_dependency_integration.py # End-to-end dependency & queue lifecycle tests (CO5)
│   ├── test_hash_table.py          # Custom HashTable unit tests (CO2)
│   ├── test_task_hash_index.py     # Task hash index service tests (CO2)
│   ├── test_structure_evaluation.py # List vs Hash vs BST benchmark tests (CO2)
│   └── test_phase6_integration.py  # Phase 06 multi-structure integration tests (CO2)
└── docs/                           # Project documentation
    ├── CO_MAPPING.md               # Official Course Outcome alignment matrix & viva guide
    └── ALGORITHM_COMPLEXITY.md     # Data structure & algorithm complexity analysis
```

---

## 🎓 Course Outcomes (CO) Alignment

- **CO1:** Develop efficient solutions using stack and/or queue data structures. *(Implemented in Phase 02)*
- **CO2:** Evaluate the suitability of data structures for efficient storage and retrieval. *(Implemented in Phase 06)*
- **CO3:** Evaluate the performance of searching and sorting algorithms for solving engineering problems. *(Implemented in Phase 03)*
- **CO4:** Develop tree structure for solving engineering problems. *(Implemented in Phase 04)*
- **CO5:** Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems. *(Implemented in Phase 05)*

See [`docs/CO_MAPPING.md`](docs/CO_MAPPING.md) and [`docs/ALGORITHM_COMPLEXITY.md`](docs/ALGORITHM_COMPLEXITY.md) for detailed verification and complexity tables.
