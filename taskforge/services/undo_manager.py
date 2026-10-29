"""Undo and Redo service powered by custom LIFO Stacks."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from taskforge.models import Task
from taskforge.storage import TaskStorage
from taskforge.structures.stack import EmptyStackError, Stack


class NoHistoryError(IndexError):
    """Raised when an undo or redo operation is requested with no history."""
    pass


class ActionType(StrEnum):
    """Enumeration of actions that can be recorded for undo/redo."""
    CREATE = "CREATE"
    EDIT = "EDIT"
    DELETE = "DELETE"


@dataclass
class Action:
    """Represents a recorded reversible mutation in TaskForge.
    
    Attributes:
        action_type: CREATE, EDIT, or DELETE.
        task_id: Identifier of the affected task.
        before_state: Snapshot of task prior to the action (None for CREATE).
        after_state: Snapshot of task following the action (None for DELETE).
        summary: Human-readable description of the operation.
    """
    action_type: ActionType
    task_id: int
    before_state: Optional[Task]
    after_state: Optional[Task]
    summary: str


class UndoManager:
    """Manages reversible task operations using dual custom Stack instances.
    
    Uses an Undo Stack (LIFO) and a Redo Stack (LIFO) to record and reverse
    mutations to SQLite records.
    
    Note:
        In accordance with Phase 02 requirements, Undo/Redo history is session-local.
        It manages operations in memory for the active session, while SQLite remains
        the durable source of truth for task state.
    """

    def __init__(self) -> None:
        """Initialize empty undo and redo stacks."""
        self._undo_stack: Stack[Action] = Stack()
        self._redo_stack: Stack[Action] = Stack()

    def record_action(
        self,
        action_type: ActionType,
        task_id: int,
        before_state: Optional[Task] = None,
        after_state: Optional[Task] = None,
        summary: str = "",
    ) -> Action:
        """Record a successful database mutation onto the undo stack.
        
        Recording a new action resets/clears the redo stack to prevent branching
        timeline inconsistencies.
        
        Args:
            action_type: CREATE, EDIT, or DELETE.
            task_id: Primary key of the affected task.
            before_state: State of task prior to mutation.
            after_state: State of task after mutation.
            summary: Brief description for UI display.
            
        Returns:
            The recorded Action instance.
        """
        # Take isolated deep copies so later in-memory edits do not contaminate history
        b_state = copy.deepcopy(before_state) if before_state is not None else None
        a_state = copy.deepcopy(after_state) if after_state is not None else None

        if not summary:
            if action_type == ActionType.CREATE:
                title = a_state.title if a_state else f"#{task_id}"
                summary = f"Created task #{task_id} '{title}'"
            elif action_type == ActionType.EDIT:
                title = a_state.title if a_state else f"#{task_id}"
                summary = f"Updated task #{task_id} '{title}'"
            elif action_type == ActionType.DELETE:
                title = b_state.title if b_state else f"#{task_id}"
                summary = f"Deleted task #{task_id} '{title}'"

        action = Action(
            action_type=action_type,
            task_id=task_id,
            before_state=b_state,
            after_state=a_state,
            summary=summary,
        )

        self._undo_stack.push(action)
        # Any new mutation invalidates the redo branch
        self._redo_stack.clear()
        return action

    def can_undo(self) -> bool:
        """Return True if there is at least one action to undo."""
        return not self._undo_stack.is_empty()

    def can_redo(self) -> bool:
        """Return True if there is at least one action to redo."""
        return not self._redo_stack.is_empty()

    def peek_undo(self) -> Optional[Action]:
        """Return the top action on the undo stack without popping it."""
        if self._undo_stack.is_empty():
            return None
        return self._undo_stack.peek()

    def peek_redo(self) -> Optional[Action]:
        """Return the top action on the redo stack without popping it."""
        if self._redo_stack.is_empty():
            return None
        return self._redo_stack.peek()

    def undo(self, storage: TaskStorage) -> Action:
        """Reverse the most recent operation on SQLite and transfer it to the redo stack.
        
        Args:
            storage: Persistent SQLite storage instance.
            
        Returns:
            The Action that was undone.
            
        Raises:
            NoHistoryError: If there are no actions to undo.
        """
        if self._undo_stack.is_empty():
            raise NoHistoryError("No operations available to undo.")

        action = self._undo_stack.pop()

        try:
            if action.action_type == ActionType.CREATE:
                # Creation undo: delete the newly created task from database
                storage.delete_task(action.task_id)

            elif action.action_type == ActionType.EDIT:
                # Edit undo: restore previous task state
                assert action.before_state is not None
                storage.update_task(copy.deepcopy(action.before_state))

            elif action.action_type == ActionType.DELETE:
                # Deletion undo: restore deleted task with original ID and full data
                assert action.before_state is not None
                storage.restore_task(copy.deepcopy(action.before_state))

            # Database operation succeeded: push to redo stack
            self._redo_stack.push(action)
            return action

        except Exception:
            # If the storage operation fails, preserve stack integrity by re-pushing
            self._undo_stack.push(action)
            raise

    def redo(self, storage: TaskStorage) -> Action:
        """Re-apply the previously undone operation to SQLite and transfer it back to undo stack.
        
        Args:
            storage: Persistent SQLite storage instance.
            
        Returns:
            The Action that was redone.
            
        Raises:
            NoHistoryError: If there are no operations to redo.
        """
        if self._redo_stack.is_empty():
            raise NoHistoryError("No operations available to redo.")

        action = self._redo_stack.pop()

        try:
            if action.action_type == ActionType.CREATE:
                # Creation redo: re-insert the task with its original ID
                assert action.after_state is not None
                storage.restore_task(copy.deepcopy(action.after_state))

            elif action.action_type == ActionType.EDIT:
                # Edit redo: re-apply edited task state
                assert action.after_state is not None
                storage.update_task(copy.deepcopy(action.after_state))

            elif action.action_type == ActionType.DELETE:
                # Deletion redo: re-delete the task
                storage.delete_task(action.task_id)

            # Database operation succeeded: push to undo stack
            self._undo_stack.push(action)
            return action

        except Exception:
            # If storage operation fails, preserve stack integrity by re-pushing
            self._redo_stack.push(action)
            raise

    def get_undo_history(self) -> list[Action]:
        """Return undo stack items ordered from most recent (top) to oldest (bottom)."""
        items = self._undo_stack.to_list()
        items.reverse()
        return items

    def get_redo_history(self) -> list[Action]:
        """Return redo stack items ordered from next up (top) to oldest (bottom)."""
        items = self._redo_stack.to_list()
        items.reverse()
        return items

    def clear(self) -> None:
        """Clear all undo and redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
