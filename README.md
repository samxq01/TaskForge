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
- **DSA Performance Laboratory:**
  - Interactive benchmark runner measuring execution time using `time.perf_counter()` and recording exact operation counts.
  - Empirical comparison of Linear vs. Binary search (sizes 100 to 5,000; scenarios: first, middle, last, absent).
  - Empirical comparison of Insertion vs. Merge sort (sizes 100 to 3,000; distributions: random, sorted, reversed).
  - Visualization via Matplotlib charts and academic viva walkthrough.

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
│   ├── storage.py                  # SQLite storage layer with parameterized queries
│   ├── structures/                 # Custom manual DSA implementations (CO1)
│   │   ├── __init__.py
│   │   ├── stack.py                # Generic LIFO Stack implementation
│   │   └── queue.py                # Generic FIFO Queue (singly-linked list)
│   ├── algorithms/                 # Custom manual algorithms (CO3)
│   │   ├── __init__.py
│   │   ├── searching.py            # Manual Linear Search & Binary Search
│   │   └── sorting.py              # Manual Insertion Sort & Merge Sort
│   ├── services/                   # Application service layer
│   │   ├── __init__.py
│   │   ├── undo_manager.py         # Dual-stack Undo/Redo manager
│   │   ├── task_queue_service.py   # FIFO pending task dispatcher
│   │   └── benchmark_service.py    # Searching & Sorting benchmark runner
│   └── ui/                         # Modular Streamlit UI components
│       ├── __init__.py
│       ├── dashboard.py            # Dashboard metrics, filters, task table, custom sorting
│       ├── task_manager.py         # Task creation and editing forms
│       ├── history_view.py         # CO1 Queue & Stack visualizer and viva guide
│       └── dsa_labs.py             # CO3 DSA Performance Lab & Matplotlib charts
├── tests/                          # Automated test suite (78 tests)
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
│   └── test_dsa_integration.py     # Live task sorting & searching integration tests
└── docs/                           # Project documentation
    ├── CO_MAPPING.md               # Official Course Outcome alignment matrix & viva guide
    └── ALGORITHM_COMPLEXITY.md     # Data structure & algorithm complexity analysis
```

---

## 🎓 Course Outcomes (CO) Alignment

- **CO1:** Develop efficient solutions using stack and/or queue data structures. *(Implemented in Phase 02)*
- **CO2:** Evaluate the suitability of data structures for efficient storage and retrieval. *(Planned for Phase 06)*
- **CO3:** Evaluate the performance of searching and sorting algorithms for solving engineering problems. *(Implemented in Phase 03)*
- **CO4:** Develop tree structure for solving engineering problems. *(Planned for Phase 04)*
- **CO5:** Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems. *(Planned for Phase 05)*

See [`docs/CO_MAPPING.md`](docs/CO_MAPPING.md) and [`docs/ALGORITHM_COMPLEXITY.md`](docs/ALGORITHM_COMPLEXITY.md) for detailed verification and complexity tables.
