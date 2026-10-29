"""Critical Path Analysis service using dynamic programming over DAG topological order (CO5).

Calculates the longest dependency chain, earliest start and finish times,
and estimated project duration without third-party graph libraries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from taskforge.graph.dependency_graph import CycleDetectedError, DependencyGraph
from taskforge.models import Task
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


@dataclass(frozen=True)
class CriticalPathTaskDetail:
    """Detailed earliest timing and critical-path membership for a single task."""

    task: Task
    duration_minutes: int
    earliest_start: int
    earliest_finish: int
    is_on_critical_path: bool
    predecessor_id: Optional[int]


@dataclass(frozen=True)
class CriticalPathResult:
    """Structured result of the project critical path analysis."""

    is_valid: bool
    error_message: Optional[str]
    total_duration_minutes: int
    total_duration_formatted: str
    critical_path_ids: list[int]
    critical_path_tasks: list[Task]
    schedule_details: dict[int, CriticalPathTaskDetail]
    topological_order: list[int]
    explanation: str


def format_duration(minutes: int) -> str:
    """Format duration in minutes to a readable 'X min (Yh Zm)' string."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{minutes} min ({hours}h {mins:02d}m)"


class CriticalPathService:
    """Computes the critical path (longest-duration dependency path) for a project DAG.
    
    Uses dynamic programming over Kahn's topological sort order:
        - Earliest Start (ES): max(Earliest Finish of all prerequisites), or 0 if none.
        - Earliest Finish (EF): ES + task duration.
        - Critical Path: Backtracked predecessor chain from the task achieving max(EF).
    """

    def __init__(self, storage: TaskStorage, dependency_service: DependencyService) -> None:
        """Initialize the critical path service.
        
        Args:
            storage: SQLite persistent storage interface.
            dependency_service: Dependency graph coordination service.
        """
        self.storage = storage
        self.dependency_service = dependency_service

    def calculate_critical_path(
        self,
        rebuild: bool = True,
        custom_graph: Optional[DependencyGraph] = None,
        custom_tasks: Optional[list[Task]] = None,
    ) -> CriticalPathResult:
        """Calculate the project critical path and earliest task schedules.
        
        Args:
            rebuild: Whether to synchronize graph with SQLite first. Defaults to True.
            custom_graph: Optional in-memory graph override (used for simulation and testing).
            custom_tasks: Optional list of Task objects override.
            
        Returns:
            CriticalPathResult containing path, timings, and explanations.
        """
        if custom_graph is not None:
            graph = custom_graph
        else:
            if rebuild:
                self.dependency_service.rebuild()
            graph = self.dependency_service.get_graph()

        # Step 1: Verify graph acyclicity
        has_cycle, cycle_path = graph.detect_cycle()
        if has_cycle:
            cycle_desc = " ➔ ".join(map(str, cycle_path))
            return CriticalPathResult(
                is_valid=False,
                error_message=f"Circular dependency detected ({cycle_desc}). Critical path analysis aborted.",
                total_duration_minutes=0,
                total_duration_formatted=format_duration(0),
                critical_path_ids=[],
                critical_path_tasks=[],
                schedule_details={},
                topological_order=[],
                explanation="Analysis aborted due to circular dependency in project graph.",
            )

        # Step 2: Fetch and map all tasks
        tasks = custom_tasks if custom_tasks is not None else self.storage.list_tasks()
        task_map: dict[int, Task] = {t.id: t for t in tasks if t.id is not None}

        if not task_map:
            return CriticalPathResult(
                is_valid=True,
                error_message=None,
                total_duration_minutes=0,
                total_duration_formatted=format_duration(0),
                critical_path_ids=[],
                critical_path_tasks=[],
                schedule_details={},
                topological_order=[],
                explanation="Project contains no tasks.",
            )

        # Step 3: Compute topological sort
        try:
            topo_order = graph.topological_sort()
        except CycleDetectedError as err:
            return CriticalPathResult(
                is_valid=False,
                error_message=str(err),
                total_duration_minutes=0,
                total_duration_formatted=format_duration(0),
                critical_path_ids=[],
                critical_path_tasks=[],
                schedule_details={},
                topological_order=[],
                explanation="Failed to determine topological order.",
            )

        # Ensure any isolated tasks not in topo_order are included
        for tid in sorted(task_map.keys()):
            if tid not in topo_order:
                topo_order.append(tid)

        # Step 4: Dynamic Programming over Topological Order
        earliest_start: dict[int, int] = {}
        earliest_finish: dict[int, int] = {}
        predecessor_map: dict[int, Optional[int]] = {}

        for node in topo_order:
            task = task_map.get(node)
            duration = task.duration if task else 0
            prereqs = sorted(graph.get_prerequisites(node))

            if not prereqs:
                earliest_start[node] = 0
                earliest_finish[node] = duration
                predecessor_map[node] = None
            else:
                max_prereq_finish = -1
                chosen_pred: Optional[int] = None

                for p in prereqs:
                    p_finish = earliest_finish.get(p, 0)
                    if p_finish > max_prereq_finish:
                        max_prereq_finish = p_finish
                        chosen_pred = p
                    elif p_finish == max_prereq_finish:
                        # Deterministic tie-breaking: prefer smaller task ID
                        if chosen_pred is not None and p < chosen_pred:
                            chosen_pred = p

                earliest_start[node] = max(0, max_prereq_finish)
                earliest_finish[node] = earliest_start[node] + duration
                predecessor_map[node] = chosen_pred

        # Step 5: Identify the task that establishes maximum project finish
        # Deterministic tie-breaking: max finish time, then min task ID
        best_end_node = min(
            topo_order,
            key=lambda n: (-earliest_finish.get(n, 0), n),
        )
        total_duration = earliest_finish.get(best_end_node, 0)

        # Step 6: Backtrack along predecessor chain to reconstruct critical path
        critical_path_ids: list[int] = []
        curr: Optional[int] = best_end_node
        while curr is not None:
            critical_path_ids.append(curr)
            curr = predecessor_map.get(curr)

        critical_path_ids.reverse()
        critical_set = set(critical_path_ids)
        critical_tasks = [task_map[tid] for tid in critical_path_ids if tid in task_map]

        # Step 7: Assemble schedule details
        schedule_details: dict[int, CriticalPathTaskDetail] = {}
        for node in topo_order:
            if node in task_map:
                t = task_map[node]
                schedule_details[node] = CriticalPathTaskDetail(
                    task=t,
                    duration_minutes=t.duration,
                    earliest_start=earliest_start.get(node, 0),
                    earliest_finish=earliest_finish.get(node, 0),
                    is_on_critical_path=(node in critical_set),
                    predecessor_id=predecessor_map.get(node),
                )

        # Step 8: Build human-readable explanation
        if not critical_path_ids:
            explanation = "No critical path identified."
        else:
            path_str = " ➔ ".join(f"#{tid} ('{task_map[tid].title}')" for tid in critical_path_ids if tid in task_map)
            explanation = (
                f"Critical Path: {path_str}. "
                f"This longest dependency chain requires {format_duration(total_duration)} "
                f"and dictates the minimum project completion time."
            )

        return CriticalPathResult(
            is_valid=True,
            error_message=None,
            total_duration_minutes=total_duration,
            total_duration_formatted=format_duration(total_duration),
            critical_path_ids=critical_path_ids,
            critical_path_tasks=critical_tasks,
            schedule_details=schedule_details,
            topological_order=topo_order,
            explanation=explanation,
        )
