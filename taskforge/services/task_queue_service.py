"""Task queue service implementing deterministic FIFO pending-task processing with dependency awareness (CO1, CO5)."""

from __future__ import annotations

import copy
from typing import Any, Optional

from taskforge.models import Task, TaskStatus
from taskforge.services.undo_manager import ActionType, UndoManager
from taskforge.storage import TaskStorage
from taskforge.structures.queue import EmptyQueueError, Queue


class TaskQueueService:
    """Manages the FIFO processing queue for pending tasks using a custom Queue.
    
    Pending tasks are queued according to creation timestamp (oldest first),
    with task ID used as a deterministic tie-breaker.
    
    Dependency Integration (CO5):
        Only tasks that are eligible to start (i.e. all their prerequisites are Completed)
        are placed in the active processing queue. Blocked pending tasks remain out of the queue
        until their prerequisites finish.
    """

    def __init__(
        self,
        storage: TaskStorage,
        undo_manager: Optional[UndoManager] = None,
        dependency_service: Optional[Any] = None,
    ) -> None:
        """Initialize the queue service with persistent storage, optional undo manager, and dependency service.
        
        Args:
            storage: SQLite task storage interface.
            undo_manager: Optional UndoManager for recording state changes.
            dependency_service: Optional DependencyService for relationship tracking.
        """
        self.storage = storage
        self.undo_manager = undo_manager
        self.dependency_service = dependency_service
        self._queue: Queue[Task] = Queue()
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the queue from current SQLite records to prevent stale state.
        
        Fetches all tasks with status 'Pending' ordered deterministically by
        created_at ASC, id ASC, and enqueues only ELIGIBLE tasks (those whose
        prerequisites are all Completed) into the custom Queue.
        """
        self._queue.clear()
        with self.storage._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status = 'Pending'
                ORDER BY created_at ASC, id ASC;
                """
            )
            for row in cursor.fetchall():
                task = self.storage._row_to_task(row)
                assert task.id is not None
                # Check prerequisites: task is blocked if any prerequisite is not Completed
                prereq_ids = self.storage.get_prerequisites(task.id)
                if prereq_ids:
                    placeholders = ",".join("?" for _ in prereq_ids)
                    check_cursor = conn.execute(
                        f"""
                        SELECT COUNT(*) FROM tasks
                        WHERE id IN ({placeholders}) AND status != 'Completed';
                        """,
                        prereq_ids,
                    )
                    incomplete_count = check_cursor.fetchone()[0]
                    if incomplete_count > 0:
                        # Task is blocked by incomplete prerequisites; skip enqueuing
                        continue
                self._queue.enqueue(task)

    def size(self) -> int:
        """Return the number of pending tasks currently in the queue."""
        return self._queue.size()

    def is_empty(self) -> bool:
        """Return True if the pending queue is empty."""
        return self._queue.is_empty()

    def peek_next_task(self) -> Optional[Task]:
        """Inspect the next task to be processed without dequeuing it.
        
        Returns:
            The front Task, or None if the queue is empty.
        """
        if self._queue.is_empty():
            return None
        return self._queue.peek()

    def get_queue_tasks(self) -> list[Task]:
        """Return a snapshot of all queued pending tasks in FIFO order."""
        return self._queue.to_list()

    def process_next_task(self) -> Optional[Task]:
        """Dequeue the next pending task and advance its status to 'In Progress'.
        
        Updates the database record and records the state transition in the
        UndoManager so that processing can be seamlessly undone.
        
        Returns:
            The processed Task, or None if no pending tasks were available.
        """
        if self._queue.is_empty():
            return None

        # Dequeue from the custom FIFO queue
        task = self._queue.dequeue()
        assert task.id is not None

        # Snapshot before state for undo/redo
        before_task = copy.deepcopy(task)

        # Update task status to In Progress
        task.status = TaskStatus.IN_PROGRESS.value
        self.storage.update_task(task)

        # Record in UndoManager if configured
        if self.undo_manager is not None:
            self.undo_manager.record_action(
                action_type=ActionType.EDIT,
                task_id=task.id,
                before_state=before_task,
                after_state=task,
                summary=f"Processed task #{task.id} '{task.title}' to In Progress",
            )

        return task
