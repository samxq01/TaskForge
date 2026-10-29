"""What-If Schedule Simulation service (CO5).

Simulates the propagation of delays across dependent tasks without
modifying persistent database records or application state.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Optional

from taskforge.graph.dependency_graph import CycleDetectedError, DependencyGraph
from taskforge.models import Task, TaskStatus
from taskforge.services.critical_path import format_duration
from taskforge.services.dependency_service import DependencyService
from taskforge.storage import TaskStorage


@dataclass(frozen=True)
class TaskSimulationImpact:
    """Detailed impact analysis for an individual task under simulation."""

    task_id: int
    task_title: str
    status: str
    duration_minutes: int
    baseline_start: int
    baseline_finish: int
    simulated_start: int
    simulated_finish: int
    start_delay_minutes: int
    finish_delay_minutes: int
    is_affected: bool


@dataclass(frozen=True)
class WhatIfSimulationResult:
    """Structured result of a what-if schedule delay simulation."""

    is_valid: bool
    error_message: Optional[str]
    selected_task_id: Optional[int]
    selected_task_title: Optional[str]
    added_delay_minutes: int
    baseline_project_duration: int
    simulated_project_duration: int
    project_delay_increase: int
    affected_tasks_count: int
    affected_task_ids: list[int]
    unaffected_task_ids: list[int]
    impacts: list[TaskSimulationImpact]
    explanation: str


class WhatIfSimulatorService:
    """Simulates schedule impacts of task delays in-memory without database persistence.
    
    Principles:
        1. Persistence Safety: Zero mutation of SQLite, task models, or application indexes.
        2. Status Awareness: Completed tasks are treated as completed prerequisites at t=0.
           Incomplete tasks (Pending, In Progress) require duration-based remaining work.
        3. Dependency Propagation: Delays only propagate downstream where precedence constraints require.
        4. Parallel Branch Absorption: Delays on non-critical branches can be absorbed by parallel slack.
    """

    def __init__(self, storage: TaskStorage, dependency_service: DependencyService) -> None:
        """Initialize simulation service with storage and dependency coordinator."""
        self.storage = storage
        self.dependency_service = dependency_service

    def simulate_delay(
        self,
        task_id: int,
        delay_minutes: int,
        rebuild_graph: bool = True,
        custom_graph: Optional[DependencyGraph] = None,
        custom_tasks: Optional[list[Task]] = None,
    ) -> WhatIfSimulationResult:
        """Simulate the effect of delaying an incomplete task by a specified duration.
        
        Args:
            task_id: ID of the incomplete task to delay.
            delay_minutes: Additional waiting delay in minutes (must be >= 0).
            rebuild_graph: Whether to rebuild the dependency graph from storage.
            custom_graph: Optional in-memory graph override (used in testing).
            custom_tasks: Optional in-memory task list override.
            
        Returns:
            WhatIfSimulationResult with baseline vs. simulated comparison.
        """
        if delay_minutes < 0:
            return WhatIfSimulationResult(
                is_valid=False,
                error_message=f"Invalid delay: {delay_minutes} minutes. Delay cannot be negative.",
                selected_task_id=task_id,
                selected_task_title=None,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation="Simulation failed due to negative delay value.",
            )

        # Step 1: Obtain dependency graph
        if custom_graph is not None:
            graph = custom_graph
        else:
            if rebuild_graph:
                self.dependency_service.rebuild()
            graph = self.dependency_service.get_graph()

        # Step 2: Validate graph acyclicity
        has_cycle, cycle_path = graph.detect_cycle()
        if has_cycle:
            cycle_desc = " ➔ ".join(map(str, cycle_path))
            return WhatIfSimulationResult(
                is_valid=False,
                error_message=f"Circular dependency detected ({cycle_desc}). Simulation aborted.",
                selected_task_id=task_id,
                selected_task_title=None,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation="Simulation aborted due to circular dependency in project graph.",
            )

        # Step 3: Fetch in-memory copies of tasks
        raw_tasks = custom_tasks if custom_tasks is not None else self.storage.list_tasks()
        # Take isolated deep copies to guarantee zero mutation of shared structures
        tasks = copy.deepcopy(raw_tasks)
        task_map: dict[int, Task] = {t.id: t for t in tasks if t.id is not None}

        # Step 4: Validate selected task existence and status
        if task_id not in task_map:
            return WhatIfSimulationResult(
                is_valid=False,
                error_message=f"Task #{task_id} not found in project database.",
                selected_task_id=task_id,
                selected_task_title=None,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation=f"Task #{task_id} does not exist.",
            )

        selected_task = task_map[task_id]
        if selected_task.status == TaskStatus.COMPLETED.value:
            return WhatIfSimulationResult(
                is_valid=False,
                error_message=(
                    f"Task #{task_id} ('{selected_task.title}') is already Completed. "
                    f"Only incomplete tasks can be delayed in simulation."
                ),
                selected_task_id=task_id,
                selected_task_title=selected_task.title,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation=f"Cannot delay completed task #{task_id}.",
            )

        # Step 5: Filter incomplete tasks for remaining-work simulation
        incomplete_tasks = [t for t in tasks if t.status != TaskStatus.COMPLETED.value and t.id is not None]
        incomplete_set = {t.id for t in incomplete_tasks if t.id is not None}

        if not incomplete_tasks:
            return WhatIfSimulationResult(
                is_valid=True,
                error_message=None,
                selected_task_id=task_id,
                selected_task_title=selected_task.title,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation="All project tasks are already completed. No remaining work to simulate.",
            )

        # Step 6: Determine topological order
        try:
            full_topo = graph.topological_sort()
        except CycleDetectedError as err:
            return WhatIfSimulationResult(
                is_valid=False,
                error_message=str(err),
                selected_task_id=task_id,
                selected_task_title=selected_task.title,
                added_delay_minutes=delay_minutes,
                baseline_project_duration=0,
                simulated_project_duration=0,
                project_delay_increase=0,
                affected_tasks_count=0,
                affected_task_ids=[],
                unaffected_task_ids=[],
                impacts=[],
                explanation="Failed to establish topological sort.",
            )

        # Filter topological order to only include incomplete tasks
        topo_incomplete = [tid for tid in full_topo if tid in incomplete_set]
        # Append any isolated incomplete tasks missing from graph
        for tid in sorted(incomplete_set):
            if tid not in topo_incomplete:
                topo_incomplete.append(tid)

        # Step 7: Calculate Baseline Remaining Schedule
        baseline_start: dict[int, int] = {}
        baseline_finish: dict[int, int] = {}

        for node in topo_incomplete:
            task = task_map[node]
            # Prerequisite tasks that are incomplete (completed ones take 0 time)
            all_prereqs = graph.get_prerequisites(node)
            unfinished_prereqs = [p for p in all_prereqs if p in incomplete_set]

            if not unfinished_prereqs:
                baseline_start[node] = 0
            else:
                baseline_start[node] = max(baseline_finish.get(p, 0) for p in unfinished_prereqs)

            baseline_finish[node] = baseline_start[node] + task.duration

        baseline_project_duration = max((baseline_finish.values()), default=0)

        # Step 8: Calculate Simulated Schedule with Delay
        simulated_start: dict[int, int] = {}
        simulated_finish: dict[int, int] = {}

        for node in topo_incomplete:
            task = task_map[node]
            all_prereqs = graph.get_prerequisites(node)
            unfinished_prereqs = [p for p in all_prereqs if p in incomplete_set]

            # Prerequisite finish boundary
            if not unfinished_prereqs:
                prereq_boundary = 0
            else:
                prereq_boundary = max(simulated_finish.get(p, 0) for p in unfinished_prereqs)

            if node == task_id:
                # Add delay to the selected task
                simulated_start[node] = prereq_boundary + delay_minutes
            else:
                simulated_start[node] = prereq_boundary

            simulated_finish[node] = simulated_start[node] + task.duration

        simulated_project_duration = max((simulated_finish.values()), default=0)
        project_delay_increase = max(0, simulated_project_duration - baseline_project_duration)

        # Step 9: Assemble Task Impacts and Diff Comparison
        impacts: list[TaskSimulationImpact] = []
        affected_ids: list[int] = []
        unaffected_ids: list[int] = []

        for node in topo_incomplete:
            task = task_map[node]
            b_start = baseline_start.get(node, 0)
            b_finish = baseline_finish.get(node, 0)
            s_start = simulated_start.get(node, 0)
            s_finish = simulated_finish.get(node, 0)

            start_diff = s_start - b_start
            finish_diff = s_finish - b_finish
            is_affected = start_diff > 0 or finish_diff > 0

            if is_affected:
                affected_ids.append(node)
            else:
                unaffected_ids.append(node)

            impacts.append(
                TaskSimulationImpact(
                    task_id=node,
                    task_title=task.title,
                    status=task.status,
                    duration_minutes=task.duration,
                    baseline_start=b_start,
                    baseline_finish=b_finish,
                    simulated_start=s_start,
                    simulated_finish=s_finish,
                    start_delay_minutes=start_diff,
                    finish_delay_minutes=finish_diff,
                    is_affected=is_affected,
                )
            )

        # Step 10: Human-Readable Justification
        if delay_minutes == 0:
            explanation = (
                f"Zero delay simulated for Task #{task_id} ('{selected_task.title}'). "
                f"Schedule is unchanged (Remaining: {format_duration(baseline_project_duration)})."
            )
        else:
            downstream_count = len([aid for aid in affected_ids if aid != task_id])
            if project_delay_increase > 0:
                explanation = (
                    f"Delaying Task #{task_id} ('{selected_task.title}') by {delay_minutes} min "
                    f"increases project completion time by {project_delay_increase} min "
                    f"(from {format_duration(baseline_project_duration)} to {format_duration(simulated_project_duration)}). "
                    f"{downstream_count} downstream task(s) affected."
                )
            else:
                explanation = (
                    f"Delaying Task #{task_id} ('{selected_task.title}') by {delay_minutes} min "
                    f"is absorbed by existing parallel slack. Total project duration remains unchanged at "
                    f"{format_duration(baseline_project_duration)} ({downstream_count} downstream task(s) affected)."
                )

        return WhatIfSimulationResult(
            is_valid=True,
            error_message=None,
            selected_task_id=task_id,
            selected_task_title=selected_task.title,
            added_delay_minutes=delay_minutes,
            baseline_project_duration=baseline_project_duration,
            simulated_project_duration=simulated_project_duration,
            project_delay_increase=project_delay_increase,
            affected_tasks_count=len(affected_ids),
            affected_task_ids=affected_ids,
            unaffected_task_ids=unaffected_ids,
            impacts=impacts,
            explanation=explanation,
        )
