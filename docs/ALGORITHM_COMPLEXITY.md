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
