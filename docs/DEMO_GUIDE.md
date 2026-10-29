# TaskForge — Academic Viva & Demonstration Guide (CO1–CO5)

This guide provides a structured **5- to 8-minute demonstration script** for presenting **TaskForge** to faculty examiners during an academic project review or viva.

---

## 🎯 Project Overview at a Glance

**TaskForge** is an intelligent task scheduling and dependency management system that combines an operational task manager with practical implementations of core Data Structures and Algorithms (DSA).

### The Five Official Course Outcomes (COs)

| Course Outcome | Academic Definition | TaskForge Implementation Module |
| :--- | :--- | :--- |
| **CO1** | Develop efficient solutions using stack and/or queue data structures. | Custom `Stack` (LIFO undo/redo), `Queue` (FIFO dispatching), and binary `PriorityQueue` (Min-Heap recommendations). |
| **CO2** | Evaluate the suitability of data structures for efficient storage and retrieval. | Custom `HashTable` with separate chaining and empirical benchmark comparing List ($O(n)$) vs Hash Table ($O(1)$) vs BST ($O(\log n)$). |
| **CO3** | Evaluate the performance of searching and sorting algorithms for solving engineering problems. | Manual `linear_search`, `binary_search`, `insertion_sort`, `merge_sort`, and interactive DSA Performance Lab. |
| **CO4** | Develop tree structure for solving engineering problems. | Custom `BinarySearchTree` with composite deadline key indexing and ordered Inorder retrieval. |
| **CO5** | Evaluate the applicability of graph data structures and traversal techniques for solving engineering problems. | Custom directed `DependencyGraph`, BFS/DFS, 3-color cycle detection, Kahn's topological sort, Critical Path Analyzer, and What-If Simulator. |

---

## ⏱️ Step-by-Step 7-Minute Viva Demonstration Script

### Minute 1: Startup & Sample Dataset Initialization
1. **Launch the Web Application:**
   ```bash
   streamlit run app.py
   ```
2. **Initialize Demonstration Records:**
   - In the left sidebar, click **🌱 Load Sample Tasks**.
   - Explain to the examiner:
     > *"TaskForge uses persistent SQLite storage with parameterized queries. Clicking 'Load Sample Tasks' idempotently seeds 6 realistic engineering tasks with defined durations, deadlines, priorities, and dependency relationships."*

---

### Minute 2: Stack, Queue & Undo/Redo Engine (CO1)
1. **Navigate to:** `📋 Task Dashboard & Registry`
   - Highlight dashboard metric cards: Total Tasks, Pending, In Progress, Completed, and Overdue.
2. **Perform a State Mutation:**
   - Change a task's priority or status (e.g. advance Task #2 to "In Progress").
3. **Navigate to:** `🔄 Task Processing & History (CO1)`
   - Show the **FIFO Task Processing Queue**: Only tasks whose prerequisites are completely satisfied enter the active queue in chronological arrival order ($O(1)$ enqueue/dequeue via singly-linked queue).
   - Show the **Undo & Redo Stacks (LIFO)**: Click **↩️ Undo Action**. Point out that the task record in SQLite instantly reverts to its previous state while preserving its exact primary key ID.
   - Click **↪️ Redo Action**: Demonstrate that the redo stack restores the forward state cleanly.

---

### Minute 3: Searching, Sorting & DSA Performance Lab (CO3)
1. **Navigate to:** `🔬 DSA Performance Lab (CO3)`
2. **Demonstrate Algorithm Benchmarking:**
   - Select Algorithm Benchmark: **Merge Sort vs. Insertion Sort**.
   - Choose Dataset Size: **500 items**, Distribution: **Random**.
   - Click **🚀 Run Sorting Benchmark**.
   - Explain to the examiner:
     > *"Our algorithms are written in pure Python without calling Python's built-in `sorted()` or `.sort()`. Notice that Merge Sort maintains stable $O(n \log n)$ execution across all input distributions, whereas Insertion Sort performs $O(n^2)$ work on random data but drops to $O(n)$ on nearly-sorted data."*
3. **Show Search Benchmarking:**
   - Compare Linear Search ($O(n)$) against Binary Search ($O(\log n)$ on pre-sorted arrays) and point out the key comparison counters.

---

### Minute 4: BST Task Deadline Index (CO4)
1. **Navigate to:** `🌲 BST Task Index (CO4)`
2. **Demonstrate Binary Search Tree Deadline Ordering:**
   - Explain the composite key: `(has_no_deadline_flag, normalized_deadline, task_id)`.
   - Show the **Inorder Traversal Table**:
     > *"By performing an Inorder Traversal ($Left \to Root \to Right$), the BST extracts all tasks in exact chronological deadline order in $O(n)$ time without requiring a global sorting pass."*
   - Show the **Interactive Key Search**: Enter a target task deadline to demonstrate $O(\log n)$ average search.
   - Show the **ASCII Tree Structure & Skewness Diagnostics**.

---

### Minute 5: Custom Hash Table & Multi-Structure Evaluation (CO2)
1. **Navigate to:** `🧮 Data Structure Evaluation (CO2)`
2. **Demonstrate Separate Chaining Collision Handling (Tab 1):**
   - Click **💥 Collision Demo**.
   - Show the examiners the bucket distribution:
     > *"Notice that our Hash Table does not use Python dictionaries for internal storage. It manages an array of buckets using separate chaining. When collisions occur, entries form a linked sequence in that bucket rather than overwriting existing records."*
3. **Demonstrate the Comparative Benchmark (Tab 3):**
   - Select Dataset Size: `1000`, Scenario: `Middle Hit (~50%)`.
   - Click **🚀 Run Comparative Benchmark**.
   - Show the comparison table and Matplotlib charts:
     - **List Lookup:** Scans $\approx 500$ entries ($O(n)$).
     - **BST Lookup:** Traverses $\approx 10$ nodes ($\log_2 1000 \approx 10$).
     - **Hash Table:** Locates the entry in $\approx 1$ chain inspection ($O(1)$).

---

### Minute 6: Dependency Map & Kahn's Topological Sorting (CO5)
1. **Navigate to:** `🔗 Dependency Map (CO5)`
2. **Demonstrate Directed Dependency Graph:**
   - Point to the visual graph: arrows point from Prerequisite $\to$ Dependent ($A \to B$).
   - Switch to **Topological Order (Tab 3)**:
     > *"TaskForge uses Kahn's Algorithm driven by our Phase 02 custom Queue to establish a deterministic, cycle-free linear build schedule."*
3. **Demonstrate Cycle Rejection (Tab 5):**
   - In the **Cycle Simulator**, show that attempting to add an edge that closes a loop (e.g. $B \to A$ when $A \to B$ exists) is rejected immediately by 3-color DFS cycle detection.

---

### Minute 7: Smart Heap Scheduler & Deadline Risk Analyzer (CO1 + CO5)
1. **Navigate to:** `🧠 Smart Scheduling & Deadline Risks (CO1 + CO5)`
2. **Demonstrate the Binary Min-Heap Priority Queue:**
   - Show the **Top Recommended Task** card and full priority-ranked sequence.
   - Explain:
     > *"Unlike the FIFO dispatch queue which processes tasks in arrival order, the Smart Auto-Scheduler uses our custom binary Min-Heap (`PriorityQueue[T, P]`) built without `heapq`. It ranks eligible tasks using a multi-criteria tuple: $(-priority, has\_deadline, deadline, duration, id)$."*
3. **Demonstrate the Deterministic Deadline Risk Analyzer:**
   - Explain the 5 strict precedence categories: `Completed > Overdue > At Risk > Unscheduled > Safe`.
   - Point out that tasks with insufficient time ($\text{Slack} < 0$) or incomplete prerequisites are immediately flagged as `At Risk`.

---

### Minute 8: Critical Path & What-If Schedule Simulator (CO5)
1. **Navigate to:** `🗺️ Critical Path & What-If Planning (CO5)`
2. **Demonstrate Critical Path Dynamic Programming (Tab 1):**
   - Click **🔄 Recalculate Critical Path**.
   - Point out the **Critical Dependency Chain** and the Gantt timeline:
     > *"Using dynamic programming over Kahn's topological sort in $\mathcal{O}(V + E)$ time, we compute Earliest Start and Finish times. The longest path determines the minimum project duration."*
3. **Demonstrate What-If Delay Simulation & Persistence Safety (Tab 2):**
   - **Scenario 1 (Slack Absorption):** Select a non-critical task with float and delay it by 30 min.
     - Show: `Project Delay Impact: +0 min (Absorbed)`. Downstream tasks remain unaffected.
   - **Scenario 2 (Critical Delay Propagation):** Select a task on the Critical Path and delay it by 45 min.
     - Show: `Project Delay Impact: +45 min`. Downstream tasks shift forward.
   - Emphasize to faculty:
     > *"Crucially, What-If simulation operates 100% in memory on deep copies. The underlying SQLite database, task records, and undo history remain strictly unchanged."*

---

## 💡 Quick Viva Q&A Reference for Students

| Examiner Question | Ideal Technical Answer |
| :--- | :--- |
| **Why not just use Python's built-in `list.sort()` or `heapq`?** | Built-in methods are implemented in C and abstract away the data structure mechanics. In this micro-project, we implemented every data structure (Stack, Queue, BST, Hash Table, Binary Min-Heap, Adjacency Graph) from scratch in pure Python to demonstrate algorithm mechanics, pointers, sift operations, and complexity analysis. |
| **How does your custom Hash Table handle collisions?** | We implement **separate chaining**. Each bucket in the primary array contains a chain of entry objects. When multiple keys hash to the same bucket index ($h(k) \pmod m$), they are appended to that bucket's chain without overwriting existing data. Dynamic resizing occurs when load factor $\alpha > 0.75$. |
| **How does the Critical Path algorithm handle parallel tasks?** | Dynamic programming over DAG topological sort evaluates $\text{ES}[v] = \max_{u \in \text{prereqs}(v)} \text{EF}[u]$. Because independent branches run concurrently, only the longest branch dictates the earliest start of downstream tasks; shorter branches have positive float (slack). |
| **Why does What-If simulation not save to SQLite?** | What-If simulation is a planning sandbox for risk exploration. Applying hypothetical delays to persistent storage would corrupt production deadlines, mutate user statuses, and invalidate undo/redo histories. We enforce strict persistence safety by running simulations on in-memory deep copies. |
| **How do FIFO queue dispatching and Heap scheduling coexist?** | They serve distinct roles: the FIFO Queue (`TaskQueueService`) models fair, predictable first-come-first-served background job dispatching, while the Heap Priority Queue (`SchedulerService`) models strategic project recommendations. Both read SQLite independently without mutative side-effects. |

