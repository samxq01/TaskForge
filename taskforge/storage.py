"""SQLite storage layer for TaskForge."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Sequence

from taskforge.models import Priority, Task, TaskStatus


class TaskStorage:
    """Manages persistent SQLite storage and CRUD operations for tasks."""

    def __init__(self, db_path: str | Path = "taskforge.db") -> None:
        """Initialize storage with database path.
        
        Args:
            db_path: Path to the SQLite database file, or ':memory:'.
        """
        self.db_path = str(db_path)
        self.init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a configured SQLite connection.
        
        Enables WAL mode and foreign key constraints, then commits or rolls back.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Foreign keys enabled for future dependency table integration
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize required database tables and indexes safely."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 4),
                    due_date TEXT,
                    duration INTEGER NOT NULL CHECK (duration > 0),
                    status TEXT NOT NULL CHECK (status IN ('Pending', 'In Progress', 'Completed')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    prerequisite_id INTEGER NOT NULL,
                    dependent_id INTEGER NOT NULL,
                    PRIMARY KEY (prerequisite_id, dependent_id),
                    FOREIGN KEY (prerequisite_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (dependent_id) REFERENCES tasks(id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_dep_prereq ON task_dependencies(prerequisite_id);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_dep_dependent ON task_dependencies(dependent_id);"
            )

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert a SQLite row to a Task model instance."""
        due_date = None
        if row["due_date"]:
            due_date = datetime.fromisoformat(row["due_date"])

        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            priority=row["priority"],
            due_date=due_date,
            duration=row["duration"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_task(self, task: Task) -> Task:
        """Persist a new task to SQLite.
        
        Args:
            task: Task instance to insert.
            
        Returns:
            The Task instance with its generated database ID.
            
        Raises:
            ValueError: If task validation fails.
        """
        task.validate()
        now = datetime.now()
        task.created_at = now
        task.updated_at = now

        due_date_str = task.due_date.isoformat() if task.due_date else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (
                    title, description, priority, due_date, duration, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    due_date_str,
                    task.duration,
                    task.status,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            task.id = cursor.lastrowid
        return task

    def restore_task(self, task: Task) -> Task:
        """Restore a previously deleted or undone task with its original ID and timestamps.
        
        Args:
            task: Task instance with an explicit original ID.
            
        Returns:
            The restored Task instance.
            
        Raises:
            ValueError: If task.id is None or task validation fails.
        """
        if task.id is None:
            raise ValueError("Cannot restore a task without an explicit ID.")
        task.validate()
        due_date_str = task.due_date.isoformat() if task.due_date else None

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, description, priority, due_date, duration, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.priority,
                    due_date_str,
                    task.duration,
                    task.status,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
        return task

    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by its unique ID.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            Task instance if found, None otherwise.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE id = ?;", (task_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_task(row)

    def list_tasks(
        self,
        status: str | None = None,
        priority: int | None = None,
        search: str | None = None,
    ) -> list[Task]:
        """List tasks with optional filtering and search.
        
        Args:
            status: Optional status to filter by.
            priority: Optional priority level to filter by.
            search: Optional substring to search in title or description.
            
        Returns:
            List of Task instances matching all given criteria.
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[str | int] = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)

        if search and search.strip():
            query += " AND (title LIKE ? OR description LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term])

        # Order primarily by status (Pending, In Progress, Completed), then priority DESC, id ASC
        query += " ORDER BY CASE status WHEN 'Pending' THEN 1 WHEN 'In Progress' THEN 2 WHEN 'Completed' THEN 3 ELSE 4 END, priority DESC, id ASC;"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_task(row) for row in cursor.fetchall()]

    def update_task(self, task: Task) -> Task:
        """Update an existing task in SQLite.
        
        Args:
            task: Task instance with updated fields and existing ID.
            
        Returns:
            The updated Task instance.
            
        Raises:
            ValueError: If task ID is missing or task does not exist.
        """
        if task.id is None:
            raise ValueError("Cannot update a task without an ID.")

        task.validate()
        task.updated_at = datetime.now()
        due_date_str = task.due_date.isoformat() if task.due_date else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, due_date = ?,
                    duration = ?, status = ?, updated_at = ?
                WHERE id = ?;
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    due_date_str,
                    task.duration,
                    task.status,
                    task.updated_at.isoformat(),
                    task.id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Task with ID {task.id} does not exist.")

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID.
        
        Args:
            task_id: Identifier of the task to delete.
            
        Returns:
            True if a record was deleted, False if no task was found.
        """
        with self._get_connection() as conn:
            # Explicit cleanup of dependencies
            conn.execute(
                "DELETE FROM task_dependencies WHERE prerequisite_id = ? OR dependent_id = ?;",
                (task_id, task_id),
            )
            cursor = conn.execute(
                "DELETE FROM tasks WHERE id = ?;", (task_id,)
            )
            return cursor.rowcount > 0

    def add_dependency(self, prerequisite_id: int, dependent_id: int) -> bool:
        """Persist a directed dependency (prerequisite_id -> dependent_id).
        
        Args:
            prerequisite_id: ID of the prerequisite task.
            dependent_id: ID of the dependent task.
            
        Returns:
            True if inserted, False if already present.
            
        Raises:
            ValueError: If either task does not exist or if prerequisite_id == dependent_id.
        """
        if prerequisite_id == dependent_id:
            raise ValueError(f"Self-dependency not allowed: task {prerequisite_id} cannot depend on itself.")

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE id IN (?, ?);",
                (prerequisite_id, dependent_id),
            )
            existing_ids = {row["id"] for row in cursor.fetchall()}
            if prerequisite_id not in existing_ids:
                raise ValueError(f"Prerequisite task with ID {prerequisite_id} does not exist.")
            if dependent_id not in existing_ids:
                raise ValueError(f"Dependent task with ID {dependent_id} does not exist.")

            try:
                conn.execute(
                    """
                    INSERT INTO task_dependencies (prerequisite_id, dependent_id)
                    VALUES (?, ?);
                    """,
                    (prerequisite_id, dependent_id),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def remove_dependency(self, prerequisite_id: int, dependent_id: int) -> bool:
        """Remove a directed dependency between two tasks.
        
        Args:
            prerequisite_id: ID of prerequisite task.
            dependent_id: ID of dependent task.
            
        Returns:
            True if removed, False if no such dependency existed.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM task_dependencies
                WHERE prerequisite_id = ? AND dependent_id = ?;
                """,
                (prerequisite_id, dependent_id),
            )
            return cursor.rowcount > 0

    def has_dependency(self, prerequisite_id: int, dependent_id: int) -> bool:
        """Check whether a dependency exists in SQLite."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT 1 FROM task_dependencies
                WHERE prerequisite_id = ? AND dependent_id = ?;
                """,
                (prerequisite_id, dependent_id),
            )
            return cursor.fetchone() is not None

    def get_dependencies(self) -> list[tuple[int, int]]:
        """Retrieve all registered dependencies as (prerequisite_id, dependent_id) tuples."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT prerequisite_id, dependent_id FROM task_dependencies ORDER BY prerequisite_id, dependent_id;"
            )
            return [(row["prerequisite_id"], row["dependent_id"]) for row in cursor.fetchall()]

    def get_prerequisites(self, task_id: int) -> list[int]:
        """Retrieve all prerequisite IDs for a given task ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT prerequisite_id FROM task_dependencies WHERE dependent_id = ? ORDER BY prerequisite_id;",
                (task_id,),
            )
            return [row["prerequisite_id"] for row in cursor.fetchall()]

    def get_dependents(self, task_id: int) -> list[int]:
        """Retrieve all dependent task IDs for a given task ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT dependent_id FROM task_dependencies WHERE prerequisite_id = ? ORDER BY dependent_id;",
                (task_id,),
            )
            return [row["dependent_id"] for row in cursor.fetchall()]

    def count_tasks(self, as_of: datetime | None = None) -> dict[str, int]:
        """Calculate summary counts for dashboard metrics.
        
        Args:
            as_of: Reference time for overdue calculation.
            
        Returns:
            Dictionary with keys: total, pending, in_progress, completed, overdue.
        """
        ref_time = (as_of or datetime.now()).isoformat()

        with self._get_connection() as conn:
            # Aggregate status counts
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status != 'Completed' AND due_date IS NOT NULL AND due_date < ? THEN 1 ELSE 0 END) as overdue
                FROM tasks;
                """,
                (ref_time,),
            )
            row = cursor.fetchone()
            return {
                "total": row["total"] or 0,
                "pending": row["pending"] or 0,
                "in_progress": row["in_progress"] or 0,
                "completed": row["completed"] or 0,
                "overdue": row["overdue"] or 0,
            }
