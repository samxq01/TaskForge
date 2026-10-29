# TaskForge — Intelligent Task Scheduling and Dependency Management System

TaskForge is a modern web application that combines practical task management with rigorous demonstrations of **Data Structures and Algorithms (DSA)**. It helps users manage tasks, deadlines, priorities, dependencies, and project schedules while serving as an academic showcase for five official Course Outcomes (CO1–CO5).

TaskForge features a **dual-frontend architecture**:
1. **Next.js 14 Product Frontend (Potadot-Inspired):** A bright, polished digital product experience built with TypeScript, App Router, Tailwind CSS, and Lucide icons, connected to Python services via a local FastAPI integration layer.
2. **Streamlit Application (Preserved Fallback):** The original, fully functional Python dashboard with custom Matplotlib visualizations.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+** installed (`python --version`)
- **Node.js 18+** and **npm** installed (`node --version`, `npm --version`)

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Option A: Launch Next.js Product Frontend (Recommended)

#### Step 1: Start the FastAPI Backend
```bash
# In project root:
uvicorn taskforge.api.main:app --host 127.0.0.1 --port 8000 --reload
```
*The FastAPI documentation and OpenAPI schema are accessible at `http://127.0.0.1:8000/docs`.*

#### Step 2: Install and Start the Next.js Frontend
```bash
# In a new terminal:
cd frontend
npm install
npm run dev
```
*Open your browser at `http://localhost:3000` to access the Potadot-inspired TaskForge interface.*

---

### 4. Option B: Launch Streamlit Fallback Application
```bash
# In project root:
streamlit run app.py
```
*The Streamlit application will launch automatically at `http://localhost:8501`.*

---

## 🧪 Automated Testing

### Run Python Test Suite (213 Tests)
```bash
pytest -v
```
*Covers all unit tests, integration workflows, Course Outcome validations, and FastAPI endpoints.*

### Run Next.js Production Build Test
```bash
cd frontend
npm run build
```
*Verifies complete TypeScript compilation, type checking, and production page prerendering (10/10 static routes).*

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Client Layer
        NJ["Next.js 14 App Router (localhost:3000)"]
        ST["Streamlit UI (localhost:8501)"]
    end

    subgraph Integration Adapter
        API["FastAPI Local Integration Layer (taskforge/api)"]
    end

    subgraph Service Orchestration
        NJ -->|REST API| API
        API --> SRV["TaskForge Services"]
        ST -->|Direct Python Calls| SRV
    end

    subgraph Custom DSA Engine (First-Principles)
        SRV --> S["Custom Stack (LIFO)"]
        SRV --> Q["Custom Queue (FIFO)"]
        SRV --> BST["Binary Search Tree Index"]
        SRV --> HT["Separate-Chaining Hash Table"]
        SRV --> HP["Min-Heap Priority Queue"]
        SRV --> G["Directed Graph DAG"]
        SRV --> ALGO["Search & Sort Algorithms"]
    end

    subgraph Persistence Layer
        SRV --> DB[("SQLite Database (taskforge.db)")]
    end
```

---

## 🌟 Key Application Areas

| View & Module | Capabilities & Course Outcome |
| :--- | :--- |
| **Product Landing Page** (`/`) | Editorial Potadot-inspired introduction, live operational preview, 5-stage interactive workflow, and verified academic proof. |
| **Dashboard** (`/dashboard`) | 6-metric KPI strip, Min-Heap #1 dispatch recommendation, upcoming deadlines, and dual-mode task registry (Cards or Table). |
| **Task Workspace** (`/tasks`) | Complete CRUD lifecycle, status transitions, dual-stack Undo/Redo (LIFO), and priority filters. |
| **DSA Performance Lab** (`/laboratory`) | FIFO queue visualizer, stack undo/redo history, empirical search (Linear vs Binary) & sort (Insertion vs Merge) runners, BST traversals, and custom Hash Table bucket exploration. |
| **Dependency Map** (`/dependencies`) | Directed acyclic graph layout, cycle detection with topological sorting (Kahn's), and BFS/DFS traversal runners. |
| **Smart Scheduler** (`/scheduling`) | Deterministic binary min-heap rankings with multi-criteria key explanations, FIFO vs Heap comparison, and Deadline Risk Analyzer. |
| **Critical Path & What-If** (`/planning`) | Longest dependency chain Gantt chart, project duration, and non-persistent What-If delay simulator with zero database mutations. |

---

## 🎓 Course Outcome (CO) Mapping

- **CO1 (Stacks & Queues):** Custom generic `Stack` (LIFO) and pointer-linked `Queue` (FIFO) powering session-local Undo/Redo and chronological task dispatching.
- **CO2 (Storage & Retrieval):** Custom `HashTable` using separate chaining with dynamic rehashing ($\alpha > 0.75$) and controlled comparative evaluation against List and BST.
- **CO3 (Binary Search Trees):** Generic `BinarySearchTree` indexing composite deadline keys `(has_deadline, deadline, id)` with Inorder, Preorder, and Postorder traversals.
- **CO4 (Searching & Sorting):** First-principles `linear_search`, `binary_search`, `insertion_sort`, and `merge_sort` benchmarked with microsecond timers and comparison counters.
- **CO5 (Graphs & Project Scheduling):** Custom `DependencyGraph` with cycle detection, Kahn's topological sort, Min-Heap scheduler, Critical Path dynamic programming, and non-persistent What-If simulation.

---

## 📁 Repository Directory Structure

```text
TaskForge/
├── app.py                      # Streamlit application entrypoint
├── taskforge/
│   ├── models.py               # Task data model & priority/status enums
│   ├── storage.py              # SQLite storage layer with parameterized SQL
│   ├── structures/             # Custom DSA implementations (Stack, Queue, BST, HashTable, MinHeap)
│   ├── algorithms/             # Searching & sorting implementations
│   ├── graph/                  # Directed graph & cycle detection
│   ├── services/               # Orchestration layer (Scheduler, Risk, Critical Path, What-If)
│   ├── ui/                     # Streamlit presentation views & Potadot theme
│   └── api/                    # FastAPI local integration layer
│       ├── main.py             # FastAPI application & REST endpoints
│       ├── schemas.py          # Pydantic request & response schemas
│       ├── dependencies.py     # Service container & singleton lifecycle
│       └── converters.py       # Domain-to-schema mapping helpers
├── frontend/                   # Next.js 14 TypeScript Product Frontend
│   ├── app/                    # App Router pages (/, dashboard, tasks, laboratory, etc.)
│   ├── components/             # Reusable UI components (Navbar, etc.)
│   ├── lib/                    # API client with full type safety
│   ├── package.json            # Frontend dependencies
│   ├── tailwind.config.ts      # Tailwind CSS configuration with Potadot tokens
│   └── tsconfig.json           # TypeScript configuration
├── tests/                      # Automated test suite (213 passing tests)
│   ├── test_api.py             # FastAPI endpoint integration tests
│   ├── test_ui_theme.py        # Streamlit AppTest verification
│   └── test_*.py               # Exhaustive unit tests for all DSA modules
├── docs/                       # Academic documentation (CO mapping, demo guide, complexity)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🔒 Mandatory Safety & Integrity Guarantees

1. **Non-Persistent Simulation:** What-If schedule simulations are strictly isolated in memory and never mutate SQLite records, task statuses, deadlines, durations, dependencies, or undo histories.
2. **First-Principles Algorithms:** Zero reliance on Python's built-in `heapq`, `collections.deque`, or external graph packages like `networkx`. All data structures are built from first principles.
3. **Authoritative Backend:** The Python services remain the authoritative source of truth for all business logic, validation, and data integrity.
