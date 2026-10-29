# TaskForge — Algorithm & Data Structure Complexity Analysis

This document details the theoretical time and space complexity of custom data structures, operations, searching algorithms, sorting algorithms, and benchmark methodologies implemented in **TaskForge**.

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
- **Working Principle:** Divide-and-conquer strategy on pre-sorted arrays. Computes the middle index `mid = low + (high - low) // 2`. If `target == mid_val`, it records the match and continues left to guarantee finding the first occurrence deterministically. If `target < mid_val`, eliminates the right half; otherwise eliminates the left half.
- **Preconditions:** **CRITICAL:** Input sequence MUST be strictly ordered in ascending order by the comparison key. This precondition is not checked at runtime to avoid $O(n)$ verification overhead.
- **Time Complexity:**
  - **Best Case:** $O(1)$ — Element found on the initial middle comparison (though duplicate-safe continuation will perform $\approx \log n$ steps).
  - **Average Case:** $O(\log n)$ — Each iteration halves the search space.
  - **Worst Case:** $O(\log n)$ — Search space reduced from $n \to n/2 \to n/4 \dots \to 1$, requiring $\lfloor \log_2 n \rfloor + 1$ iterations.
- **Auxiliary Space:** $O(1)$ — Iterative implementation uses only pointer variables (`low`, `high`, `mid`).

---

## 5. Sorting Algorithms (`taskforge/algorithms/sorting.py`)

### A. Insertion Sort (`insertion_sort`)
- **Working Principle:** Incrementally builds the sorted array by consuming one element per iteration and shifting previously sorted elements that are greater to the right.
- **Stability:** **Guaranteed Stable**. Equal elements are not shifted past one another.
- **Input Preservation:** Operates on an allocated copy of the input, leaving caller collections unmutated.
- **Time Complexity:**
  - **Best Case:** $O(n)$ — Occurs when the input is **already sorted**. The inner loop performs exactly 1 comparison per element and 0 shifts ($n-1$ total comparisons).
  - **Average Case:** $O(n^2)$ — On randomized input, each element is compared with half of the preceding elements ($\approx n^2/4$ comparisons).
  - **Worst Case:** $O(n^2)$ — Occurs when the input is **reverse-sorted**. Every element must be compared against and shifted past all preceding elements ($\approx n(n-1)/2$ comparisons and shifts).
- **Auxiliary Space:** $O(1)$ in-place sorting memory beyond the $O(n)$ return copy.

### B. Merge Sort (`merge_sort`)
- **Working Principle:** Classic divide-and-conquer algorithm. Recursively bisects the sequence until single-element sub-arrays are reached, then merges pairs of sorted sub-arrays into a unified sorted array.
- **Stability:** **Guaranteed Stable**. During the merge phase, when keys are identical, elements from the left partition are selected before elements from the right partition.
- **Time Complexity:**
  - **Best Case:** $O(n \log n)$
  - **Average Case:** $O(n \log n)$
  - **Worst Case:** $O(n \log n)$
  - The tree of recursive bisections has height $\lceil \log_2 n \rceil$, and at each level, $O(n)$ merge operations occur regardless of initial distribution.
- **Auxiliary Space:** $O(n)$ — Requires memory buffers for allocating left and right sub-arrays and merging them into the final output.

---

## 6. Theoretical Big-O vs. Measured Benchmark Performance

When demonstrating in a college viva, explain the divergence between theoretical operation bounds and empirical wall-clock measurements:

1. **Constant Factors ($c \cdot g(n)$):**
   - Merge Sort incurs overhead from Python function call recursion, list slicing, and memory allocation of sub-arrays.
   - For small arrays ($n \lesssim 30$), Insertion Sort's inner loop runs tightly in Python and can exhibit lower wall-clock time despite its higher asymptotic growth rate.
2. **Distribution Sensitivity:**
   - On **already-sorted** data, Insertion Sort drops to $O(n)$ ($n-1$ comparisons, 0 shifts) and dramatically beats Merge Sort.
   - On **reverse-sorted** data, Insertion Sort degrades to maximum quadratic shifts, whereas Merge Sort remains strictly $O(n \log n)$.
3. **Binary Search Preprocessing Trade-off:**
   - Binary Search execution is virtually instantaneous ($O(\log n)$), but requires pre-sorted data ($O(n \log n)$ preprocessing). If performing only a single search on an unsorted list, Linear Search ($O(n)$) is more efficient than sorting followed by binary searching. Binary search is justified when multiple queries are amortized over the same dataset.
