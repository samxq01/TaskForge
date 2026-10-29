"""Unit tests for TaskForge data models."""

from datetime import date, datetime, timedelta, time
import pytest

from taskforge.models import Priority, Task, TaskStatus


def test_task_creation_valid() -> None:
    """Test valid task creation with explicit and default attributes."""
    task = Task(
        title="Complete DSA project",
        description="Implement all requirements for Phase 01",
        priority=Priority.URGENT.value,
        duration=120,
        status=TaskStatus.IN_PROGRESS.value,
        due_date=datetime(2026, 11, 1, 18, 0, 0),
    )
    assert task.title == "Complete DSA project"
    assert task.description == "Implement all requirements for Phase 01"
    assert task.priority == 4
    assert task.duration == 120
    assert task.status == "In Progress"
    assert task.due_date == datetime(2026, 11, 1, 18, 0, 0)
    assert task.id is None
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_defaults() -> None:
    """Test default values on minimal task creation."""
    task = Task(title="Quick review")
    assert task.title == "Quick review"
    assert task.description == ""
    assert task.priority == Priority.MEDIUM.value
    assert task.duration == 30
    assert task.status == TaskStatus.PENDING.value
    assert task.due_date is None
    assert task.formatted_deadline == "No deadline"


def test_empty_or_whitespace_title_rejected() -> None:
    """Empty or whitespace-only titles must raise ValueError."""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        Task(title="")

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        Task(title="   \t\n  ")


def test_invalid_priorities_rejected() -> None:
    """Priority must be an integer between 1 and 4."""
    for invalid_p in [0, 5, -1, 10]:
        with pytest.raises(ValueError, match="Priority must be between 1"):
            Task(title="Valid title", priority=invalid_p)

    with pytest.raises(ValueError, match="Priority must be an integer"):
        Task(title="Valid title", priority="urgent")  # type: ignore


def test_invalid_durations_rejected() -> None:
    """Duration must be a positive integer > 0."""
    for invalid_dur in [0, -10, -1]:
        with pytest.raises(ValueError, match="Estimated duration must be a positive integer"):
            Task(title="Valid title", duration=invalid_dur)

    with pytest.raises(ValueError, match="Duration must be an integer"):
        Task(title="Valid title", duration="abc")  # type: ignore


def test_invalid_status_rejected() -> None:
    """Status must belong to predefined lifecycle states."""
    for invalid_status in ["Blocked", "Waiting", "Done", ""]:
        with pytest.raises(ValueError, match="Invalid status"):
            Task(title="Valid title", status=invalid_status)


def test_date_only_deadline_normalized_to_end_of_day() -> None:
    """Date-only deadline must be converted to 23:59:59 of that date."""
    target_date = date(2026, 12, 31)
    task = Task(title="Year-end review", due_date=target_date)  # type: ignore
    assert isinstance(task.due_date, datetime)
    assert task.due_date.year == 2026
    assert task.due_date.month == 12
    assert task.due_date.day == 31
    assert task.due_date.hour == 23
    assert task.due_date.minute == 59
    assert task.due_date.second == 59


def test_overdue_calculation() -> None:
    """Verify is_overdue works properly across statuses and deadlines."""
    now = datetime(2026, 10, 29, 12, 0, 0)
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Past deadline, Pending -> Overdue
    task_pending_overdue = Task(title="Task 1", due_date=past, status=TaskStatus.PENDING.value)
    assert task_pending_overdue.is_overdue(as_of=now) is True

    # Past deadline, In Progress -> Overdue
    task_in_prog_overdue = Task(title="Task 2", due_date=past, status=TaskStatus.IN_PROGRESS.value)
    assert task_in_prog_overdue.is_overdue(as_of=now) is True

    # Past deadline, Completed -> NOT overdue
    task_completed = Task(title="Task 3", due_date=past, status=TaskStatus.COMPLETED.value)
    assert task_completed.is_overdue(as_of=now) is False

    # Future deadline, Pending -> NOT overdue
    task_future = Task(title="Task 4", due_date=future, status=TaskStatus.PENDING.value)
    assert task_future.is_overdue(as_of=now) is False

    # No deadline -> NOT overdue
    task_no_deadline = Task(title="Task 5", due_date=None, status=TaskStatus.PENDING.value)
    assert task_no_deadline.is_overdue(as_of=now) is False


def test_to_dict_and_from_dict_roundtrip() -> None:
    """Verify serialization to and from dictionary preserves data."""
    original = Task(
        id=42,
        title="Serialize me",
        description="Check dict conversion",
        priority=Priority.HIGH.value,
        duration=45,
        status=TaskStatus.IN_PROGRESS.value,
        due_date=datetime(2026, 11, 15, 14, 30),
    )
    d = original.to_dict()
    assert d["id"] == 42
    assert d["title"] == "Serialize me"
    assert d["priority"] == 3
    assert d["duration"] == 45
    assert d["due_date"] == "2026-11-15T14:30:00"

    reconstructed = Task.from_dict(d)
    assert reconstructed.id == original.id
    assert reconstructed.title == original.title
    assert reconstructed.priority == original.priority
    assert reconstructed.duration == original.duration
    assert reconstructed.status == original.status
    assert reconstructed.due_date == original.due_date
