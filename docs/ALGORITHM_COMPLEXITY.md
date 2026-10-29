# TaskForge — Algorithm & Data Structure Complexity Analysis

This document details the theoretical time and space complexity of custom data structures, operations, and service layers implemented in **TaskForge**.

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

### Distinguishing In-Memory Stack vs. Persistent Storage Operations

It is essential in college viva evaluation to distinguish between **in-memory data structure operations** and **persistent storage operations**:

| Manager Action | In-Memory Stack Operation | SQLite Storage Operation | Total Combined Complexity |
| :--- | :--- | :--- | :--- |
| **`record_action()`** | `_undo_stack.push()`: $O(1)$<br>`_redo_stack.clear()`: $O(1)$ | None (Action is recorded *after* successful storage mutation) | **$O(1)$** |
| **`undo()`** | `_undo_stack.pop()`: $O(1)$<br>`_redo_stack.push()`: $O(1)$ | Inverse SQL mutation:<br>- Create undo: `DELETE WHERE id=?` ($O(1)$ via primary key index)<br>- Edit undo: `UPDATE WHERE id=?` ($O(1)$ via index)<br>- Delete undo: `INSERT (id, ...)` ($O(1)$ via B-Tree index) | **$O(1)$ in-memory + $O(\log N_{tasks})$ SQLite write** |
| **`redo()`** | `_redo_stack.pop()`: $O(1)$<br>`_undo_stack.push()`: $O(1)$ | Forward SQL mutation:<br>- Create redo: `INSERT` ($O(1)$ via index)<br>- Edit redo: `UPDATE` ($O(1)$ via index)<br>- Delete redo: `DELETE` ($O(1)$ via index) | **$O(1)$ in-memory + $O(\log N_{tasks})$ SQLite write** |

---

## 4. Task Queue Service (`taskforge/services/task_queue_service.py`)

| Operation | Complexity | Description |
| :--- | :--- | :--- |
| **Queue Refresh (`refresh`)** | $O(K \log K)$ | SQL query fetches $K$ pending tasks ordered by `created_at ASC, id ASC`, followed by $K$ constant-time `enqueue` operations into the custom linked-list queue. |
| **Process Next Task (`process_next_task`)** | $O(1)$ queue dequeue + $O(1)$ SQLite update | Dequeues the front task from the custom queue ($O(1)$), updates status to `In Progress` in SQLite ($O(\log N_{tasks})$), and pushes an `EDIT` action to the Undo Stack ($O(1)$). |
