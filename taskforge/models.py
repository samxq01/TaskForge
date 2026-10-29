"""Data models for TaskForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import IntEnum, StrEnum
from typing import Any, Mapping


class Priority(IntEnum):
    """Task priority levels conforming to TaskForge specifications.
    
    1: Low
    2: Medium
    3: High
    4: Urgent
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

    @classmethod
    def label(cls, value: int) -> str:
        """Return a human-readable label for a priority value."""
        labels = {
            cls.LOW: "Low (P1)",
            cls.MEDIUM: "Medium (P2)",
            cls.HIGH: "High (P3)",
            cls.URGENT: "Urgent (P4)",
        }
        return labels.get(cls(value), f"P{value}")


class TaskStatus(StrEnum):
    """Task lifecycle statuses."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


VALID_STATUSES = {s.value for s in TaskStatus}
VALID_PRIORITIES = {p.value for p in Priority}


@dataclass
class Task:
    """Represents a scheduled work item in TaskForge.
    
    Attributes:
        id: Unique task identifier (None if unsaved).
        title: Short descriptive name of the task.
        description: Extended information or notes.
        priority: Urgency/importance weight (1=Low, 2=Medium, 3=High, 4=Urgent).
        due_date: Optional deadline timestamp.
        duration: Estimated duration in minutes (positive integer).
        status: Current state ('Pending', 'In Progress', 'Completed').
        created_at: Creation timestamp.
        updated_at: Last modification timestamp.
    """
    title: str
    priority: int = Priority.MEDIUM.value
    duration: int = 30
    status: str = TaskStatus.PENDING.value
    description: str = ""
    due_date: datetime | None = None
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate all fields upon initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate task invariants.
        
        Raises:
            ValueError: If any attribute fails business rules.
        """
        # Title validation
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        self.title = self.title.strip()

        # Priority validation
        try:
            priority_val = int(self.priority)
        except (ValueError, TypeError):
            raise ValueError(f"Priority must be an integer between 1 and 4, got {self.priority!r}.")
        if priority_val not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be between 1 (Low) and 4 (Urgent), got {priority_val}.")
        self.priority = priority_val

        # Duration validation
        try:
            duration_val = int(self.duration)
        except (ValueError, TypeError):
            raise ValueError(f"Duration must be an integer, got {self.duration!r}.")
        if duration_val <= 0:
            raise ValueError(f"Estimated duration must be a positive integer in minutes (> 0), got {duration_val}.")
        self.duration = duration_val

        # Status validation
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{self.status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}."
            )

        # Description normalization
        if self.description is None:
            self.description = ""

        # Normalize due_date if given as a pure date object
        if isinstance(self.due_date, date) and not isinstance(self.due_date, datetime):
            # Treat date-only deadlines as the end of that local day (23:59:59)
            self.due_date = datetime.combine(self.due_date, time(23, 59, 59))

    def is_overdue(self, as_of: datetime | None = None) -> bool:
        """Check if the task has passed its deadline and is not completed.
        
        Args:
            as_of: Timestamp to compare against (defaults to current time).
            
        Returns:
            True if deadline exists, task is not completed, and deadline < as_of.
        """
        if self.status == TaskStatus.COMPLETED.value or self.due_date is None:
            return False
        reference_time = as_of if as_of is not None else datetime.now()
        return self.due_date < reference_time

    @property
    def formatted_deadline(self) -> str:
        """Human-readable deadline format or 'No deadline'."""
        if self.due_date is None:
            return "No deadline"
        return self.due_date.strftime("%Y-%m-%d %H:%M")

    @property
    def priority_label(self) -> str:
        """Return human-friendly priority label."""
        return Priority.label(self.priority)

    def to_dict(self) -> dict[str, Any]:
        """Convert task instance to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "duration": self.duration,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Task:
        """Instantiate a Task from a dictionary."""
        due_date = None
        if data.get("due_date"):
            if isinstance(data["due_date"], str):
                due_date = datetime.fromisoformat(data["due_date"])
            elif isinstance(data["due_date"], (datetime, date)):
                due_date = data["due_date"]

        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.now())
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data.get("updated_at"), str)
            else data.get("updated_at", datetime.now())
        )

        return cls(
            id=data.get("id"),
            title=data["title"],
            description=data.get("description", ""),
            priority=int(data.get("priority", Priority.MEDIUM.value)),
            due_date=due_date,
            duration=int(data.get("duration", 30)),
            status=str(data.get("status", TaskStatus.PENDING.value)),
            created_at=created_at,
            updated_at=updated_at,
        )
