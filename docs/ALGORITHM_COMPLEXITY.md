# TaskForge — Algorithm & Data Structure Complexity Analysis

This document details the theoretical time and space complexity of custom data structures, operations, searching algorithms, sorting algorithms, trees, and benchmark methodologies implemented in **TaskForge**.

---

## 1. Custom Stack (`taskforge/structures/stack.py`)

The custom `Stack` encapsulates Last-In, First-Out (LIFO) operations using a dynamically sized internal array with strict public method encapsulation.

| Operation | Method Signature | Time Complexity | Space Complexity | Description & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Push** | `push(item: T) -> None` | $O(1)$ amortized | $O(1)$ | Appends element to the top of the stack. |
| **Pop** | `pop() -> T` | $O(1)$ | $O(1)$ | Removes and returns the top element. Raises `EmptyStackError` if empty. |
| **Peek** | `peek() -> T` | $O(1)$ | $O(1)$ | Reads the top element without removing it. Raises `EmptyStackError` if empty. |
| **Is Empty** | `is_empty() -> bool` | $O(1)$ | $O(1)$ | Checks whether element count is zero. |
| **Size** | `size() -> int` | $O(1)$ | $O(1)$ | Returns current element count. |
| **Inspect** | `to_list() -> list[T]` | $O(n)$ | $O(n)$ | Returns a shallow copy from bottom to top for UI display without mutating internal state. |

**Overall Space Complexity:** $O(n)$, where $n$ is the number of elements held in the stack.

---

## 2. Custom Queue (`taskforge/structures/queue.py`)

The custom `Queue` implements First-In, First-Out (FIFO) semantics using a **singly-linked list** with explicit `head` and `tail` pointers. This avoids the $O(n)$ shifting penalty of list-based `pop(0)` and removes any reliance on `collections.deque`.

| Operation | Method Signature | Time Complexity | Space Complexity | Description & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Enqueue** | `enqueue(item: T) -> None` | $O(1)$ | $O(1)$ | Links a new `_Node` at the tail pointer. |
| **Dequeue** | `dequeue() -> T` | $O(1)$ | $O(1)$ | Detaches and returns node from the head pointer. Raises `EmptyQueueError` if empty. |
| **Peek** | `peek() -> T` | $O(1)$ | $O(1)$ | Returns value at head without removing. Raises `EmptyQueueError` if empty. |
| **Is Empty** | `is_empty() -> bool` | $O(1)$ | $O(1)$ | Checks if queue size is zero. |
| **Size** | `size() -> int` | $O(1)$ | $O(1)$ | Returns cached node count. |
| **Inspect** | `to_list() -> list[T]` | $O(n)$ | $O(n)$ | Traverses linked list from head to tail to generate a snapshot list for display. |

**Overall Space Complexity:** $O(n)$ nodes, where $n$ is the number of queued elements.

---

## 3. Undo/Redo Manager (`taskforge/services/undo_manager.py`)

The `UndoManager` utilizes two `Stack[Action]` instances: the **Undo Stack** and the **Redo Stack**.

### In-Memory Stack vs. Persistent Storage Operations

| Manager Action | In-Memory Stack Operation | SQLite Storage Operation | Total Combined Complexity |
| :--- | :--- | :--- | :--- |
| **`record_action()`** | `_undo_stack.push()`: $O(1)$<br>`_redo_stack.clear()`: $O(1)$ | None (Action is recorded *after* successful storage mutation) | **$O(1)$** |
| **`undo()`** | `_undo_stack.pop()`: $O(1)$<br>`_redo_stack.push()`: $O(1)$ | Inverse SQL mutation:<br>- Create undo: `DELETE WHERE id=?` ($O(1)$ via primary key index)<br>- Edit undo: `UPDATE WHERE id=?` ($O(1)$ via index)<br>- Delete undo: `INSERT (id, ...)` ($O(1)$ via B-Tree index) | **$O(1)$ in-memory + $O(\log N_{tasks})$ SQLite write** |
| **`redo()`** | `_redo_stack.pop()`: $O(1)$<br>`_undo_stack.push()`: $O(1)$ | Forward SQL mutation:<br>- Create redo: `INSERT` ($O(1)$ via index)<br>- Edit redo: `UPDATE` ($O(1)$ via index)<br>- Delete redo: `DELETE` ($O(1)$ via index) | **$O(1)$ in-memory + $O(\log N_{tasks})$ SQLite write** |

---

## 4. Searching Algorithms (`taskforge/algorithms/searching.py`)

### A. Linear Search (`linear_search`)
- **Working Principle:** Sequentially traverses the sequence from index $0$ to $n-1$, evaluating the key of each element against the search target.
- **Preconditions:** None. Operates on arbitrary, unsorted, or sorted sequences.
- **Duplicate Behavior:** Deterministically halts and returns the **first matching index**.
- **Time Complexity:**
  - **Best Case:** $O(1)$ — Target is situated at index 0.
  - **Average Case:** $O(n)$ — Target is found near the middle or evenly distributed across trials ($n/2$ comparisons).
  - **Worst Case:** $O(n)$ — Target is located at index $n-1$ or is entirely absent from the sequence.
- **Auxiliary Space:** $O(1)$ — Operates directly via an index pointer without allocating auxiliary arrays.

### B. Binary Search (`binary_search`)
- **Working Principle:** Divide-and-conquer strategy on pre-sorted arrays. Computes `mid = low + (high - low) // 2`. If `target == mid_val`, continues left to find the first occurrence deterministically.
- **Preconditions:** **CRITICAL:** Input sequence MUST be strictly ordered in ascending order by the comparison key.
- **Time Complexity:**
  - **Best Case:** $O(1)$ — Initial middle element match.
  - **Average Case:** $O(\log n)$ — Search space halved at each step.
  - **Worst Case:** $O(\log n)$ — Up to $\lfloor \log_2 n \rfloor + 1$ iterations.
- **Auxiliary Space:** $O(1)$ — Iterative implementation uses only pointer variables (`low`, `high`, `mid`).

---

## 5. Sorting Algorithms (`taskforge/algorithms/sorting.py`)

### A. Insertion Sort (`insertion_sort`)
- **Working Principle:** Incrementally builds the sorted array by consuming one element per iteration and shifting previously sorted elements that are greater to the right.
- **Stability:** **Guaranteed Stable**. Equal elements are not shifted past one another.
- **Time Complexity:**
  - **Best Case:** $O(n)$ — Already sorted input ($n-1$ comparisons, 0 shifts).
  - **Average Case:** $O(n^2)$ — Random input ($\approx n^2/4$ comparisons).
  - **Worst Case:** $O(n^2)$ — Reverse-sorted input ($\approx n(n-1)/2$ comparisons and shifts).
- **Auxiliary Space:** $O(1)$ sorting auxiliary space beyond the $O(n)$ return copy.

### B. Merge Sort (`merge_sort`)
- **Working Principle:** Classic divide-and-conquer algorithm. Recursively bisects the sequence into halves, sorts each half, and merges sorted sub-arrays.
- **Stability:** **Guaranteed Stable**. Left elements are picked first when keys match.
- **Time Complexity:**
  - **Best Case:** $O(n \log n)$
  - **Average Case:** $O(n \log n)$
  - **Worst Case:** $O(n \log n)$
- **Auxiliary Space:** $O(n)$ for sub-array allocations during the merge phase.

---

## 6. Custom Binary Search Tree (`taskforge/structures/bst.py` & `taskforge/services/task_index.py`)

The custom `BinarySearchTree` implements a hierarchical, ordered data structure where each node satisfies $Left.key < Node.key < Right.key$.

| BST Operation | Average Case Time | Worst Case Time | Auxiliary Space | Description & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Search (`search`)** | $O(\log n)$ | $O(n)$ | $O(1)$ iterative | Traverses left/right branches based on key comparison. Skews to $O(n)$ if degenerate. |
| **Insert (`insert`)** | $O(\log n)$ | $O(n)$ | $O(1)$ iterative | Locates insertion point and attaches new `TreeNode`. In-place updates on exact key match. |
| **Delete (`delete`)** | $O(\log n)$ | $O(n)$ | $O(h)$ recursion | Standard 3-case deletion (leaf, 1 child, 2 children using in-order successor). |
| **Inorder (`inorder_traversal`)** | $O(n)$ | $O(n)$ | $O(h)$ recursion | Left $\to$ Root $\to$ Right. **Guaranteed sorted deadline order.** |
| **Preorder (`preorder_traversal`)** | $O(n)$ | $O(n)$ | $O(h)$ recursion | Root $\to$ Left $\to$ Right. Prefix order for tree reconstruction/cloning. |
| **Postorder (`postorder_traversal`)** | $O(n)$ | $O(n)$ | $O(h)$ recursion | Left $\to$ Right $\to$ Root. Postfix order for bottom-up cleanup. |
| **Tree Rebuild from SQLite** | $O(n \log n)$ | $O(n^2)$ | $O(n)$ | $n$ sequential `insert` operations reading tasks from SQLite. |

### Structural Invariants and Degeneracy (Skewness)
- **What $n$ represents:** The total number of unique indexed tasks in the tree.
- **Why a BST can become skewed:** If keys are inserted in monotonic sorted order (e.g. $[1, 2, 3, 4, 5]$), every new node is attached exclusively to the right child pointer. The tree height degenerates from $\lfloor \log_2 n \rfloor$ to $n-1$, behaving identically to a singly-linked list with $O(n)$ search and insertion.
- **Un-balanced Design:** The TaskForge BST is deliberately implemented as a **standard un-balanced BST** to demonstrate structural properties and viva trade-offs transparently, without falsely claiming to be an AVL or Red-Black tree.
- **Composite Key Invariant:** TaskForge employs composite keys:
  `key = (has_no_deadline_flag, normalized_deadline, task_id)`
  This guarantees that every task occupies a unique node even when deadlines are identical, preventing node overwrite while strictly enforcing that scheduled tasks precede unscheduled tasks in Inorder traversal.


---

## 7. Directed Dependency Graph & Graph Algorithms (`taskforge/graph/dependency_graph.py` & `taskforge/services/scheduler.py`)

The custom `DependencyGraph` represents directed task prerequisites using manual adjacency lists without external graph libraries (such as NetworkX).

### A. Graph Representation and Storage Complexity
- **Directed Edge Convention:** An edge $A \to B$ signifies that **Task B depends on Task A** (Task A is a prerequisite for Task B; A must finish before B can start).
- **Adjacency Lists:**
  - `_adj`: Forward adjacency list mapping $u \to \{v \mid u \to v\}$ (dependents).
  - `_rev_adj`: Reverse adjacency list mapping $v \to \{u \mid u \to v\}$ (prerequisites).
  - `_nodes`: Set of all registered task IDs $V$.
- **Graph Space Complexity:** $O(|V| + |E|)$, where $|V|$ is the number of task nodes and $|E|$ is the number of directed dependency edges.

### B. Graph Operation Complexities

| Graph Operation | Method Signature | Time Complexity | Auxiliary Space | Description & Engineering Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Add Node** | `add_node(node: int) -> None` | $O(1)$ | $O(1)$ | Initializes empty adjacency sets in `_adj` and `_rev_adj`. |
| **Remove Node** | `remove_node(node: int) -> bool` | $O(|V| + |E|)$ | $O(1)$ | Discards node and all incident incoming and outgoing edges. |
| **Add Edge** | `add_edge(prereq, dep) -> None` | $O(1)$ | $O(1)$ | Adds `dep` to `_adj[prereq]` and `prereq` to `_rev_adj[dep]`. Raises `InvalidDependencyError` on self-loops. |
| **Remove Edge** | `remove_edge(prereq, dep) -> bool` | $O(1)$ | $O(1)$ | Discards directed edge from forward and reverse adjacency sets. |
| **Has Edge** | `has_edge(prereq, dep) -> bool` | $O(1)$ | $O(1)$ | Hash-set lookup in `_adj[prereq]`. |
| **In-Degree / Prerequisites** | `get_prerequisites(task_id)` | $O(\text{deg}^-(u) \log \text{deg}^-(u))$ | $O(\text{deg}^-(u))$ | Returns sorted list of prerequisite task IDs. |
| **Out-Degree / Dependents** | `get_dependents(task_id)` | $O(\text{deg}^+(u) \log \text{deg}^+(u))$ | $O(\text{deg}^+(u))$ | Returns sorted list of dependent task IDs. |
| **Path Reachability** | `has_path(start, target) -> bool` | $O(|V| + |E|)$ | $O(|V|)$ | Explores reachability using BFS with custom `Queue`. |
| **Cycle Pre-Validation** | `would_create_cycle(prereq, dep)` | $O(|V| + |E|)$ | $O(|V|)$ | Evaluates if `has_path(dep, prereq)`. If true, adding `prereq -> dep` would induce a cycle. |
| **Breadth-First Search (BFS)** | `bfs(start_node) -> list[int]` | $O(|V| + |E|)$ | $O(|V|)$ | Traverses downstream dependents level by level using Phase 02 custom `Queue`. |
| **Depth-First Search (DFS)** | `dfs(start_node) -> list[int]` | $O(|V| + |E|)$ | $O(|V|)$ | Traverses deep dependency chains using Phase 02 custom `Stack`. |
| **Cycle Detection (3-Color DFS)** | `detect_cycle() -> (bool, list[int])` | $O(|V| + |E|)$ | $O(|V|)$ | Colors nodes WHITE (0), GRAY (1), BLACK (2). Encountering a GRAY node identifies a back-edge and extracts the circular loop. |
| **Topological Sort (Kahn's)** | `topological_sort() -> list[int]` | $O(|V| + |E|)$ | $O(|V|)$ | Computes in-degrees, enqueues 0-in-degree nodes to custom `Queue`, decrements neighbors. Raises `CycleDetectedError` on cyclic graph. |

### C. Dependency-Aware Scheduling Complexity (`SchedulerService`)
- **Eligibility Check:** `is_task_eligible(task_id)`:
  - Fetches task: $O(1)$
  - Checks status: $O(1)$
  - Validates all prerequisites $\in \text{Completed}$: $O(k)$ where $k = \text{in\_degree}(task\_id)$.
- **Global Ready Tasks Extraction:** `get_eligible_pending_tasks()`:
  - $O(N_{pending} \times \bar{k})$ where $\bar{k}$ is the average prerequisite count per task.
- **Queue Filtering (`TaskQueueService.refresh()`):**
  - Runs parameterized SQLite query to exclude tasks with incomplete prerequisites.
  - Guarantees $O(N_{tasks})$ database pass with single-index lookups.


---

## 8. Custom Hash Table & Multi-Structure Evaluation (`taskforge/structures/hash_table.py` & `taskforge/services/structure_evaluation.py`)

The custom `HashTable[K, V]` implements an in-memory key-value dictionary using **separate chaining** for collision resolution without relying on Python's built-in dictionary container for bucket storage.

### A. Hash Table Asymptotic Complexity

| Operation | Method Signature | Average / Expected Case | Worst Case | Auxiliary Space | Description & Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Insertion (Upsert)** | `insert(key, value) -> bool` | $O(1)$ amortized | $O(n)$ | $O(1)$ | Hashes key to bucket; searches chain. Appends new entry if absent, updates in place if present. Triggers dynamic resizing when load factor $\alpha > 0.75$. |
| **Lookup (Get)** | `get(key, default) -> V` | $O(1)$ | $O(n)$ | $O(1)$ | Hashes key to bucket and inspects chain entries. In worst case (all keys collide into same bucket), degenerates to $O(n)$. |
| **Contains** | `contains(key) -> bool` | $O(1)$ | $O(n)$ | $O(1)$ | Validates presence of key via bucket chain inspection. |
| **Update** | `update(key, value) -> bool` | $O(1)$ | $O(n)$ | $O(1)$ | Updates value of an existing entry; returns `False` if key is absent without inserting. |
| **Deletion** | `delete(key) -> bool` | $O(1)$ | $O(n)$ | $O(1)$ | Removes entry from bucket chain without affecting other colliding entries in the same bucket. |
| **Iteration** | `items() / keys() / values()` | $O(m + n)$ | $O(m + n)$ | $O(n)$ | Scans all $m$ buckets and extracts $n$ entries across all chains. |
| **Dynamic Resize** | `_resize(new_capacity)` | $O(n)$ | $O(n)$ | $O(m_{new})$ | Allocates $2m$ buckets and rehashes all existing entries. Amortized over all insertions, insertion remains $O(1)$. |

*Here, $n$ denotes the total number of unique keys stored in the table, and $m$ denotes the total bucket capacity.*

### B. Comparative Complexity: List vs. Hash Table vs. Binary Search Tree

| Criterion | Sequential List Search | Custom Hash Table (Chaining) | Custom Binary Search Tree |
| :--- | :--- | :--- | :--- |
| **Lookup Time (Average)** | $O(n)$ | **$O(1)$** | **$O(\log n)$** |
| **Lookup Time (Worst Case)** | $O(n)$ (end of list or absent) | $O(n)$ (all keys collide) | $O(n)$ (completely skewed tree) |
| **Index Construction Time** | $O(n)$ (array allocation / copy) | $O(n)$ amortized | $O(n \log n)$ average, $O(n^2)$ worst |
| **Key Inherent Ordering** | Preserves insertion sequence | **None** (hash position modulo $m$) | **Strict Inorder Sorting** ($L < N < R$) |
| **Memory / Space Overhead** | Low (contiguous array of references) | Moderate ($m$ bucket pointers + chain nodes) | Moderate (2 pointers `left` & `right` per node) |
| **Optimal Use Case** | Small datasets ($N < 50$), queue logs | Exact primary-key retrieval ($O(1)$) | Ordered range queries, priority schedules |

### C. Separate Chaining, Load Factor, and Rehashing Dynamics
1. **Separate Chaining:** Each bucket in the internal array stores a dynamic sequence (chain) of `_HashEntry` objects. When two distinct keys hash to the same bucket index (a collision), both entries are appended to the bucket's chain. Retrievals inspect only the entries in the target bucket chain.
2. **Load Factor ($\alpha = n / m$):** Quantifies table saturation. A low load factor ensures short chains ($\le 1$ average entries per bucket).
3. **Resizing Policy:** When $\alpha > 0.75$, capacity doubles ($m \leftarrow 2m$). All existing entries are rehashed into the new bucket array. Because capacity is doubled geometrically, the $O(n)$ cost of rehashing is amortized over $\Omega(n)$ preceding insertions, yielding $O(1)$ amortized cost per insertion.
4. **Empirical vs. Theoretical Observations:**
   - On small workloads ($N \le 100$), CPU cache locality and small constant factors can make linear array scanning perform within a few microseconds of hash lookup.
   - As $N$ scales ($N = 1,000$ and $N = 5,000$), linear search time grows strictly linearly with $N$ ($O(n)$), while Hash Table lookup remains flat at $\approx 1$ comparison ($O(1)$) and BST search grows logarithmically ($O(\log n)$).

---

## 9. Priority Queue (Binary Min-Heap) and Smart Auto-Scheduler (CO1 + CO5)

### A. Binary Min-Heap Architecture & Operations (`PriorityQueue[T, P]`)

TaskForge implements a pure Python generic **Binary Min-Heap Priority Queue** (`taskforge/structures/priority_queue.py`) with zero reliance on the Python standard library `heapq` module or third-party queue libraries.

The binary heap is represented as a 0-indexed contiguous dynamic array (`list`), where for any element at index $i$:
- **Parent index:** $\lfloor (i - 1) / 2 \rfloor$
- **Left child index:** $2i + 1$
- **Right child index:** $2i + 2$

| Heap Operation | Time Complexity (Best) | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`push(item, priority)`** | $O(1)$ | $O(\log N)$ | $O(\log N)$ | $O(1)$ auxiliary | Appends item to array end and bubbles up via `_sift_up`. |
| **`pop()`** | $O(1)$ | $O(\log N)$ | $O(\log N)$ | $O(1)$ auxiliary | Replaces root with last leaf and bubbles down via `_sift_down`. |
| **`peek()`** | $O(1)$ | $O(1)$ | $O(1)$ | $O(1)$ | Direct inspection of root element at index 0. |
| **`is_empty()` / `size()`** | $O(1)$ | $O(1)$ | $O(1)$ | $O(1)$ | Query size of internal array. |
| **`clear()`** | $O(1)$ | $O(1)$ | $O(1)$ | $O(1)$ | Discards internal array. |

### B. Multi-Criteria Task Ranking Tuple

To establish an optimal, deterministic schedule, TaskForge transforms task attributes into a composite lexicographical comparison tuple:

$$\text{Key} = \left(-\text{priority\_value},\; \text{has\_deadline\_flag},\; \text{normalized\_timestamp},\; \text{duration},\; \text{task\_id},\; \text{seq}\right)$$

1. **Primary Key: Priority Level ($-\text{priority}$):**
   - Higher priority tasks must execute first (Urgent: 4, High: 3, Medium: 2, Low: 1).
   - In a Min-Heap, negating the priority $(-4 < -3 < -2 < -1)$ ensures Urgent tasks bubble to the root.
2. **Secondary Key: Deadline Urgency ($\text{has\_deadline}, \text{normalized\_timestamp}$):**
   - Tasks with deadlines precede tasks without deadlines (`0 < 1`).
   - For tasks with deadlines, earlier deadlines (smaller Unix timestamps) bubble up before later deadlines.
3. **Tertiary Key: Shortest Duration ($\text{duration}$):**
   - Tie-breaker for identical priority and deadline: shorter duration tasks execute first (Shortest Job First heuristic) to maximize completion velocity.
4. **Quaternary Key: Task ID & Insertion Sequence ($\text{task\_id}, \text{seq}$):**
   - Deterministic tie-breakers that strictly prevent non-deterministic comparison failures when all other attributes match.

### C. Smart Auto-Scheduler Overall Complexity (`SchedulerService`)

Given a project graph with $V$ tasks, $E$ dependency edges, and $K$ eligible pending tasks ($K \le V$):

1. **Graph Synchronization & Cycle Detection:** $O(V + E)$ using DFS 3-color cycle detection.
2. **Prerequisite Filtering:** $O(V)$ to filter unblocked tasks where all prerequisites have status `Completed`.
3. **Heap Construction & Extraction:** Pushing $K$ eligible tasks into `PriorityQueue` takes $O(K \log K)$, and extracting them in order takes $O(K \log K)$.
4. **Total Time Complexity:** $\mathcal{O}(V + E + K \log K)$.
5. **Total Space Complexity:** $\mathcal{O}(V + E + K)$ auxiliary memory for the in-memory graph, adjacency sets, and heap elements.

### D. Architectural Comparison: FIFO Dispatch Queue vs. Heap Priority Queue

| Dimension | FIFO Execution Queue (`TaskQueueService`) | Heap Priority Queue (`PriorityQueue`) |
| :--- | :--- | :--- |
| **Course Outcome** | **CO1** (Basic linear queue) + **CO5** | **CO1** (Advanced tree-based priority queue) + **CO5** |
| **Underlying Structure** | Doubly-Linked / Circular Linear Queue | Complete Binary Tree mapped to Array |
| **Ordering Metric** | Arrival Timestamp (`created_at ASC, id ASC`) | Multi-criteria priority tuple ($-\text{priority}$, deadline, duration) |
| **Enqueue / Push** | **$O(1)$** | **$O(\log N)$** |
| **Dequeue / Pop** | **$O(1)$** | **$O(\log N)$** |
| **Peek Next Task** | **$O(1)$** | **$O(1)$** |
| **System Role** | Operational execution dispatch (fair background worker) | Strategic planning & schedule optimization (recommendation engine) |
| **Interference** | **Independent** (both read SQLite; neither mutates the other) | **Independent** (both read SQLite; neither mutates the other) |

---

## 10. Critical Path Analysis and What-If Schedule Simulator (CO5)

### A. Algorithmic Complexity Table

Let $V$ be the number of project tasks (nodes) and $E$ be the number of directed dependency constraints (edges).

| Operation | Time Complexity | Auxiliary Space | Algorithm Description |
| :--- | :--- | :--- | :--- |
| **Graph Validation & Topological Sorting** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ | Kahn's Algorithm with in-degree queue & 3-color DFS cycle verification. |
| **Critical Path Dynamic Programming** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Single-pass recurrence evaluation across topologically ordered vertices. |
| **Earliest Start & Finish Calculations** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | $\text{ES}[v] = \max_{u \in \text{pred}(v)} \text{EF}[u]$; $\text{EF}[v] = \text{ES}[v] + D[v]$. |
| **Baseline Schedule Computation** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | In-memory evaluation over incomplete tasks with completed tasks at $t=0$. |
| **Simulated Schedule Recomputation** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Propagates added waiting delay strictly downstream along dependent paths. |
| **Comparison & Impact Differencing** | $\mathcal{O}(V)$ | $\mathcal{O}(V)$ | Linear comparison of baseline vs. simulated intervals to classify shifted tasks. |

### B. Theoretical Foundations & Proof of Correctness

#### 1. Why Dynamic Programming Works on DAGs
A Directed Acyclic Graph (DAG) defines a strict strict partial ordering over tasks. Because there are no directed cycles, dependencies form an asymmetric, irreflexive, and transitive relation. This guarantees **optimal substructure**: the earliest completion time of any task $v$ depends solely on the already-finalized earliest completion times of its immediate predecessors:
$$\text{ES}[v] = \max_{u \in \text{prerequisites}(v)} \text{EF}[u], \quad \text{EF}[v] = \text{ES}[v] + \text{Duration}[v]$$

#### 2. Why Topological Order is Essential
In an arbitrary graph or unsorted vertex array, computing $\text{ES}[v]$ would risk evaluating unfinalized predecessors. In Kahn's topological order $\pi = [v_1, v_2, \dots, v_n]$, every directed edge $(u, v)$ satisfies $\pi^{-1}(u) < \pi^{-1}(v)$. Processing vertices in topological sequence ensures that by the time task $v$ is examined, all of its prerequisites $u \in \text{prerequisites}(v)$ have already had their $\text{EF}[u]$ computed and permanently finalized.

#### 3. Why Cycles Invalidate the Analysis
If a directed cycle $A \to B \to C \to A$ exists, task $A$ cannot finish until $C$ finishes, $C$ cannot finish until $B$ finishes, and $B$ cannot finish until $A$ finishes. This constitutes a deadlocked recurrence equation $\text{ES}[A] \ge \text{ES}[A] + D[A] + D[B] + D[C]$, which has no finite solution for positive durations. Topological sorting fails, and Kahn's algorithm halts before visiting all nodes. TaskForge strictly halts and returns a structured diagnostic error displaying the cycle path.

#### 4. How the Critical Path Determines Project Duration
Independent branches execute concurrently. The total duration of the project is not the sum of all task durations, but the maximum earliest finish across all terminal or leaf tasks:
$$\text{Project Duration} = \max_{v \in V} \text{EF}[v]$$
The **Critical Path** is the longest directed predecessor chain connecting the project start to the task $v^*$ achieving this maximum earliest finish. Any delay to any task on the critical path directly delays the overall project completion date.

#### 5. Parallel Execution and Slack Absorption
Tasks on non-critical parallel branches possess **Total Float (Slack)**:
$$\text{Slack}[u] = \text{Latest Finish}[u] - \text{Earliest Finish}[u]$$
When an incomplete task on a non-critical branch experiences an added delay $\Delta \le \text{Slack}[u]$, the delay propagates only within the parallel branch and is absorbed by the convergence point. Downstream tasks beyond the convergence point and the total project finish time remain entirely unaffected ($\Delta_{\text{project}} = 0$).

#### 6. Full-Plan vs. Remaining-Work Schedules
- **Critical Path Analyzer (`CriticalPathService`):** Evaluates the entire project specification assuming all tasks require their defined duration from project inception ($t=0$).
- **What-If Schedule Simulator (`WhatIfSimulatorService`):** Models real-time remaining work. Tasks already marked `Completed` represent satisfied constraints requiring $0$ additional time ($t=0$). Only unfinished tasks (`Pending`, `In Progress`) contribute to remaining project completion time.

#### 7. Persistence Safety Architecture
What-If simulations operate entirely on isolated in-memory deep copies. Persistent SQLite storage, undo/redo stacks, priority queue recommendations, and index trees are never modified during simulation runs, preventing data corruption or speculative state contamination.


