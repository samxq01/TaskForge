"""FastAPI local integration layer for TaskForge intelligent task scheduling and DSA services."""

from __future__ import annotations

from datetime import datetime
import os
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from taskforge.algorithms.searching import binary_search, linear_search
from taskforge.algorithms.sorting import insertion_sort, merge_sort
from taskforge.api.converters import task_to_schema
from taskforge.api.dependencies import ServiceContainer, get_service_container
from taskforge.api.schemas import (
    BlockedTaskDetailOut,
    CriticalPathDetailOut,
    CriticalPathOut,
    DependencyCreateIn,
    DependencyDeleteIn,
    DependencyGraphOut,
    EdgeOut,
    HashIndexStatsOut,
    HashLookupOut,
    OverviewOut,
    QueueProcessOut,
    QueueStatusOut,
    RankedRecommendationOut,
    RiskSummaryOut,
    SearchBenchmarkIn,
    SearchBenchmarkOut,
    SortBenchmarkIn,
    SortBenchmarkOut,
    StructureEvaluationIn,
    StructureEvaluationSuiteOut,
    StructureResultOut,
    TaskCreate,
    TaskOut,
    TaskRiskAssessmentOut,
    TaskSimulationImpactOut,
    TaskUpdate,
    TraversalIn,
    TraversalOut,
    TreeOverviewOut,
    UndoRedoOut,
    WhatIfIn,
    WhatIfOut,
)
from taskforge.graph.dependency_graph import CycleDetectedError, InvalidDependencyError
from taskforge.models import Priority, Task, TaskStatus
from taskforge.services.critical_path import format_duration
from taskforge.services.risk_analyzer import RiskCategory
from taskforge.services.undo_manager import ActionType, NoHistoryError


def create_app() -> FastAPI:
    """Instantiate and configure the TaskForge FastAPI application."""
    app = FastAPI(
        title="TaskForge API",
        description="Local integration layer for TaskForge algorithms, data structures, and intelligent scheduling services.",
        version="1.0.0",
    )

    # Allow local Next.js frontend and local test callers
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------
    # Health & Overview
    # -----------------------------------------------------------------

    @app.get("/api/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "app": "TaskForge", "timestamp": datetime.now().isoformat()}

    @app.get("/api/overview", response_model=OverviewOut, tags=["Overview"])
    def get_overview(c: ServiceContainer = Depends(get_service_container)) -> OverviewOut:
        counts = c.storage.count_tasks()
        risk_summary = c.risk_analyzer.analyze_all()
        smart_sched = c.scheduler_service.get_smart_schedule()
        cp_result = c.cp_service.calculate_critical_path()

        rec_id = smart_sched.recommended_task.id if (smart_sched.is_valid and smart_sched.recommended_task) else None
        rec_title = smart_sched.recommended_task.title if (smart_sched.is_valid and smart_sched.recommended_task) else None
        cp_fmt = cp_result.total_duration_formatted if cp_result.is_valid else None

        return OverviewOut(
            total_tasks=counts.get("total", 0),
            pending_tasks=counts.get("pending", 0),
            in_progress_tasks=counts.get("in_progress", 0),
            completed_tasks=counts.get("completed", 0),
            overdue_tasks=risk_summary.overdue_count,
            blocked_tasks=len(c.scheduler_service.get_blocked_tasks()),
            safe_tasks=risk_summary.safe_count,
            at_risk_tasks=risk_summary.at_risk_count,
            unscheduled_tasks=risk_summary.unscheduled_count,
            bst_nodes=c.index_service.get_tree_size(),
            bst_height=c.index_service.get_tree_height(),
            hash_size=c.hash_index.size(),
            queue_size=c.queue_service.size(),
            can_undo=c.undo_manager.can_undo(),
            can_redo=c.undo_manager.can_redo(),
            recommended_task_id=rec_id,
            recommended_task_title=rec_title,
            critical_path_duration_formatted=cp_fmt,
        )

    # -----------------------------------------------------------------
    # Task Operations (CRUD, Search, Sort)
    # -----------------------------------------------------------------

    @app.get("/api/tasks", response_model=List[TaskOut], tags=["Tasks"])
    def list_tasks(
        status: Optional[str] = Query(None),
        priority: Optional[int] = Query(None, ge=1, le=4),
        search: Optional[str] = Query(None),
        sort_by: Optional[str] = Query(None),  # 'deadline', 'priority', 'duration', 'id', 'title'
        c: ServiceContainer = Depends(get_service_container),
    ) -> List[TaskOut]:
        tasks = c.storage.list_tasks(status=status, priority=priority, search=search)

        if sort_by == "deadline":
            tasks = merge_sort(
                tasks,
                key=lambda t: (
                    t.due_date if t.due_date is not None else datetime.max,
                    -t.priority,
                    t.id or 0,
                ),
            )
        elif sort_by == "priority":
            tasks = merge_sort(
                tasks,
                key=lambda t: (
                    -t.priority,
                    t.due_date if t.due_date is not None else datetime.max,
                    t.id or 0,
                ),
            )
        elif sort_by == "duration":
            tasks = merge_sort(tasks, key=lambda t: (t.duration, t.id or 0))
        elif sort_by == "id":
            tasks = merge_sort(tasks, key=lambda t: t.id or 0)
        elif sort_by == "title":
            tasks = merge_sort(tasks, key=lambda t: t.title.lower())

        return [task_to_schema(t, c.dep_service) for t in tasks]

    @app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
    def create_task(payload: TaskCreate, c: ServiceContainer = Depends(get_service_container)) -> TaskOut:
        try:
            task = Task(
                title=payload.title,
                priority=payload.priority,
                duration=payload.duration,
                status=payload.status,
                description=payload.description,
                due_date=payload.due_date,
            )
            created = c.storage.create_task(task)
            assert created.id is not None
            c.undo_manager.record_action(
                action_type=ActionType.CREATE,
                task_id=created.id,
                before_state=None,
                after_state=created,
                summary=f"Created task #{created.id}: '{created.title}'",
            )
            c.sync_all()
            return task_to_schema(created, c.dep_service)
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

    @app.get("/api/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"])
    def get_task(task_id: int, c: ServiceContainer = Depends(get_service_container)) -> TaskOut:
        task = c.storage.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task #{task_id} not found.")
        return task_to_schema(task, c.dep_service)

    @app.patch("/api/tasks/{task_id}", response_model=TaskOut, tags=["Tasks"])
    def update_task(task_id: int, payload: TaskUpdate, c: ServiceContainer = Depends(get_service_container)) -> TaskOut:
        existing = c.storage.get_task(task_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Task #{task_id} not found.")

        before_state = existing
        updated_title = payload.title if payload.title is not None else existing.title
        updated_priority = payload.priority if payload.priority is not None else existing.priority
        updated_duration = payload.duration if payload.duration is not None else existing.duration
        updated_status = payload.status if payload.status is not None else existing.status
        updated_description = payload.description if payload.description is not None else existing.description
        updated_due_date = payload.due_date if payload.due_date is not None else existing.due_date

        try:
            mod_task = Task(
                id=task_id,
                title=updated_title,
                priority=updated_priority,
                duration=updated_duration,
                status=updated_status,
                description=updated_description,
                due_date=updated_due_date,
                created_at=existing.created_at,
            )
            updated = c.storage.update_task(mod_task)
            c.undo_manager.record_action(
                action_type=ActionType.EDIT,
                task_id=task_id,
                before_state=before_state,
                after_state=updated,
                summary=f"Edited task #{task_id}: '{updated.title}'",
            )
            c.sync_all()
            return task_to_schema(updated, c.dep_service)
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

    @app.delete("/api/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["Tasks"])
    def delete_task(task_id: int, c: ServiceContainer = Depends(get_service_container)) -> dict[str, Any]:
        existing = c.storage.get_task(task_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Task #{task_id} not found.")

        c.undo_manager.record_action(
            action_type=ActionType.DELETE,
            task_id=task_id,
            before_state=existing,
            after_state=None,
            summary=f"Deleted task #{task_id}: '{existing.title}'",
        )
        c.storage.delete_task(task_id)
        c.sync_all()
        return {"success": True, "message": f"Task #{task_id} deleted."}

    # -----------------------------------------------------------------
    # Queue Processing & History (CO1)
    # -----------------------------------------------------------------

    @app.get("/api/queue", response_model=QueueStatusOut, tags=["Queue & History"])
    def get_queue_status(c: ServiceContainer = Depends(get_service_container)) -> QueueStatusOut:
        c.queue_service.refresh()
        queue_items = c.queue_service.get_queue_tasks()
        head = c.queue_service.peek_next_task()

        return QueueStatusOut(
            queue_size=len(queue_items),
            head_task=task_to_schema(head, c.dep_service) if head else None,
            queue_tasks=[task_to_schema(t, c.dep_service) for t in queue_items],
            can_undo=c.undo_manager.can_undo(),
            can_redo=c.undo_manager.can_redo(),
            undo_history_count=len(c.undo_manager.get_undo_history()),
            redo_history_count=len(c.undo_manager.get_redo_history()),
        )

    @app.post("/api/queue/process-next", response_model=QueueProcessOut, tags=["Queue & History"])
    def process_next_task(c: ServiceContainer = Depends(get_service_container)) -> QueueProcessOut:
        c.queue_service.refresh()
        if c.queue_service.is_empty():
            return QueueProcessOut(
                success=False,
                message="Queue is empty. No eligible Pending tasks available for processing.",
                remaining_queue_size=0,
                next_task=None,
            )

        try:
            updated = c.queue_service.process_next_task()
            c.sync_all()
            next_t = c.queue_service.peek_next_task()
            return QueueProcessOut(
                success=True,
                message=f"Task #{updated.id} ('{updated.title}') processed and transitioned to Completed." if updated else "Processed successfully.",
                processed_task=task_to_schema(updated, c.dep_service) if updated else None,
                remaining_queue_size=c.queue_service.size(),
                next_task=task_to_schema(next_t, c.dep_service) if next_t else None,
            )
        except Exception as err:
            raise HTTPException(status_code=400, detail=str(err))

    @app.post("/api/history/undo", response_model=UndoRedoOut, tags=["Queue & History"])
    def undo_action(c: ServiceContainer = Depends(get_service_container)) -> UndoRedoOut:
        if not c.undo_manager.can_undo():
            raise HTTPException(status_code=400, detail="No actions available to undo.")

        action = c.undo_manager.undo(c.storage)
        c.sync_all()
        return UndoRedoOut(
            success=True,
            action_type=str(action.action_type),
            task_id=action.task_id,
            summary=action.summary,
            can_undo=c.undo_manager.can_undo(),
            can_redo=c.undo_manager.can_redo(),
        )

    @app.post("/api/history/redo", response_model=UndoRedoOut, tags=["Queue & History"])
    def redo_action(c: ServiceContainer = Depends(get_service_container)) -> UndoRedoOut:
        if not c.undo_manager.can_redo():
            raise HTTPException(status_code=400, detail="No actions available to redo.")

        action = c.undo_manager.redo(c.storage)
        c.sync_all()
        return UndoRedoOut(
            success=True,
            action_type=str(action.action_type),
            task_id=action.task_id,
            summary=action.summary,
            can_undo=c.undo_manager.can_undo(),
            can_redo=c.undo_manager.can_redo(),
        )

    # -----------------------------------------------------------------
    # Algorithms & Empirical Benchmarks (CO3 / CO4)
    # -----------------------------------------------------------------

    @app.post("/api/benchmarks/searching", response_model=SearchBenchmarkOut, tags=["Algorithms & Benchmarks"])
    def benchmark_search(payload: SearchBenchmarkIn, c: ServiceContainer = Depends(get_service_container)) -> SearchBenchmarkOut:
        scenario = payload.scenario if payload.scenario in ["first", "middle", "last", "absent"] else "middle"
        res = c.benchmark_service.benchmark_search(
            size=payload.dataset_size,
            scenario=scenario,
        )
        speedup = res.linear_time_ms / res.binary_time_ms if res.binary_time_ms > 0 else 1.0
        return SearchBenchmarkOut(
            dataset_size=res.dataset_size,
            scenario=res.scenario,
            target=res.target,
            linear_time_ms=round(res.linear_time_ms, 4),
            linear_comparisons=res.linear_comparisons,
            linear_found=res.linear_found,
            binary_time_ms=round(res.binary_time_ms, 4),
            binary_comparisons=res.binary_comparisons,
            binary_found=res.binary_found,
            speedup_factor=round(speedup, 2),
        )

    @app.post("/api/benchmarks/sorting", response_model=SortBenchmarkOut, tags=["Algorithms & Benchmarks"])
    def benchmark_sort(payload: SortBenchmarkIn, c: ServiceContainer = Depends(get_service_container)) -> SortBenchmarkOut:
        distribution = payload.distribution if payload.distribution in ["random", "sorted", "reversed"] else "random"
        res = c.benchmark_service.benchmark_sorting(
            size=payload.dataset_size,
            distribution=distribution,
        )
        speedup = res.insertion_time_ms / res.merge_time_ms if res.merge_time_ms > 0 else 1.0
        return SortBenchmarkOut(
            dataset_size=res.dataset_size,
            distribution=res.distribution,
            insertion_time_ms=round(res.insertion_time_ms, 4),
            insertion_comparisons=res.insertion_comparisons,
            insertion_shifts=res.insertion_shifts,
            merge_time_ms=round(res.merge_time_ms, 4),
            merge_comparisons=res.merge_comparisons,
            merge_shifts=res.merge_shifts,
            speedup_factor=round(speedup, 2),
        )

    # -----------------------------------------------------------------
    # Tree (BST) & Custom Hash Table (CO2 / CO3)
    # -----------------------------------------------------------------

    @app.get("/api/tree/overview", response_model=TreeOverviewOut, tags=["Tree & Hash Table"])
    def get_tree_overview(c: ServiceContainer = Depends(get_service_container)) -> TreeOverviewOut:
        c.index_service.rebuild()
        inorder = [t for _, t in c.index_service.get_inorder_entries()]
        preorder = [t for _, t in c.index_service.get_preorder_entries()]
        postorder = [t for _, t in c.index_service.get_postorder_entries()]
        height = c.index_service.get_tree_height()
        size = c.index_service.get_tree_size()

        return TreeOverviewOut(
            total_nodes=size,
            height=height,
            is_balanced=height <= (2 * (size.bit_length() or 1)),
            inorder_tasks=[task_to_schema(t, c.dep_service) for t in inorder],
            preorder_tasks=[task_to_schema(t, c.dep_service) for t in preorder],
            postorder_tasks=[task_to_schema(t, c.dep_service) for t in postorder],
        )

    @app.get("/api/hash-table/stats", response_model=HashIndexStatsOut, tags=["Tree & Hash Table"])
    def get_hash_table_stats(c: ServiceContainer = Depends(get_service_container)) -> HashIndexStatsOut:
        c.hash_index.rebuild_index()
        stats = c.hash_index.get_statistics()
        raw_table = c.hash_index.get_raw_hash_table()
        bucket_counts = [len(chain) for chain in raw_table._buckets]

        return HashIndexStatsOut(
            capacity=stats["capacity"],
            size=stats["size"],
            load_factor=round(stats["load_factor"], 4),
            occupied_buckets=stats["occupied_buckets"],
            empty_buckets=stats["empty_buckets"],
            collision_count=stats["total_collisions"],
            max_chain_length=stats["max_chain_length"],
            bucket_distribution=stats["bucket_sizes"],
        )

    @app.get("/api/hash-table/lookup/{task_id}", response_model=HashLookupOut, tags=["Tree & Hash Table"])
    def lookup_hash_task(task_id: int, c: ServiceContainer = Depends(get_service_container)) -> HashLookupOut:
        task, comparisons = c.hash_index.get_task_with_comparisons(task_id)
        return HashLookupOut(
            task_id=task_id,
            found=task is not None,
            comparisons=comparisons,
            task=task_to_schema(task, c.dep_service) if task else None,
        )

    @app.post("/api/data-structure-evaluation", response_model=StructureEvaluationSuiteOut, tags=["Tree & Hash Table"])
    def evaluate_data_structures(payload: StructureEvaluationIn, c: ServiceContainer = Depends(get_service_container)) -> StructureEvaluationSuiteOut:
        from taskforge.services.structure_evaluation import generate_evaluation_dataset, select_target_id
        dataset = generate_evaluation_dataset(payload.dataset_size)
        scenario = payload.scenario if payload.scenario in ["early", "middle", "late", "absent"] else "middle"
        target_id = select_target_id(dataset, scenario)
        results = c.structure_evaluation_service.run_evaluation(dataset, scenario=scenario)

        def _map(r: Any) -> StructureResultOut:
            return StructureResultOut(
                structure_name=r.structure_name,
                dataset_size=r.dataset_size,
                scenario=r.scenario,
                target_id=r.target_id,
                construction_time_ms=round(r.construction_time_ms, 4),
                lookup_time_total_ms=round(r.lookup_time_total_ms, 6),
                lookup_time_avg_us=round(r.lookup_time_avg_us, 4),
                operations_count=r.operations_count,
                comparisons_count=r.comparisons_count,
                result_found=r.result_found,
            )

        return StructureEvaluationSuiteOut(
            dataset_size=payload.dataset_size,
            scenario=scenario,
            target_id=target_id,
            results=[_map(r) for r in results],
        )

    # -----------------------------------------------------------------
    # Dependency Graph & Management (CO5)
    # -----------------------------------------------------------------

    @app.get("/api/dependencies", response_model=DependencyGraphOut, tags=["Dependencies"])
    def get_dependencies_graph(c: ServiceContainer = Depends(get_service_container)) -> DependencyGraphOut:
        c.dep_service.rebuild()
        graph = c.dep_service.get_graph()
        all_tasks = c.storage.list_tasks()

        edges = [EdgeOut(source=src, target=tgt) for src, tgt in c.storage.get_dependencies()]
        is_cyclic, cycle_nodes = c.dep_service.detect_cycle()
        topological = []
        if not is_cyclic:
            try:
                topological_tasks = c.dep_service.get_topological_order()
                topological = [t.id for t in topological_tasks if t.id is not None]
            except CycleDetectedError:
                pass

        return DependencyGraphOut(
            nodes=[task_to_schema(t, c.dep_service) for t in all_tasks],
            edges=edges,
            is_cyclic=is_cyclic,
            cycle_nodes=cycle_nodes,
            topological_order=topological,
            blocked_tasks_count=len(c.scheduler_service.get_blocked_tasks()),
        )

    @app.post("/api/dependencies", status_code=status.HTTP_201_CREATED, tags=["Dependencies"])
    def add_dependency(payload: DependencyCreateIn, c: ServiceContainer = Depends(get_service_container)) -> dict[str, Any]:
        try:
            c.dep_service.add_dependency(payload.prerequisite_id, payload.dependent_id)
            c.sync_all()
            return {
                "success": True,
                "message": f"Dependency added: #{payload.prerequisite_id} -> #{payload.dependent_id}",
            }
        except (InvalidDependencyError, CycleDetectedError) as err:
            raise HTTPException(status_code=400, detail=str(err))

    @app.delete("/api/dependencies", status_code=status.HTTP_200_OK, tags=["Dependencies"])
    def remove_dependency(payload: DependencyDeleteIn, c: ServiceContainer = Depends(get_service_container)) -> dict[str, Any]:
        removed = c.dep_service.remove_dependency(payload.prerequisite_id, payload.dependent_id)
        c.sync_all()
        return {
            "success": removed,
            "message": f"Dependency #{payload.prerequisite_id} -> #{payload.dependent_id} {'removed' if removed else 'not found'}.",
        }

    @app.post("/api/dependencies/bfs", response_model=TraversalOut, tags=["Dependencies"])
    def run_bfs(payload: TraversalIn, c: ServiceContainer = Depends(get_service_container)) -> TraversalOut:
        seq = c.dep_service.run_bfs(payload.start_task_id)
        return TraversalOut(
            algorithm="Breadth-First Search (BFS)",
            start_task_id=payload.start_task_id,
            visited_sequence=[t.id for t in seq if t.id is not None],
        )

    @app.post("/api/dependencies/dfs", response_model=TraversalOut, tags=["Dependencies"])
    def run_dfs(payload: TraversalIn, c: ServiceContainer = Depends(get_service_container)) -> TraversalOut:
        seq = c.dep_service.run_dfs(payload.start_task_id)
        return TraversalOut(
            algorithm="Depth-First Search (DFS)",
            start_task_id=payload.start_task_id,
            visited_sequence=[t.id for t in seq if t.id is not None],
        )

    @app.get("/api/dependencies/topological-order", response_model=List[TaskOut], tags=["Dependencies"])
    def get_topological_order(c: ServiceContainer = Depends(get_service_container)) -> List[TaskOut]:
        try:
            tasks = c.dep_service.get_topological_order()
            return [task_to_schema(t, c.dep_service) for t in tasks]
        except CycleDetectedError as err:
            raise HTTPException(status_code=400, detail=str(err))

    # -----------------------------------------------------------------
    # Intelligent Scheduling & Deadline Risk (CO1 / CO5)
    # -----------------------------------------------------------------

    @app.get("/api/scheduling/recommendations", response_model=Any, tags=["Intelligent Scheduling"])
    def get_scheduling_recommendations(c: ServiceContainer = Depends(get_service_container)) -> Any:
        sched = c.scheduler_service.get_smart_schedule()

        ranked_list = []
        for r in sched.ranked_tasks:
            ranked_list.append(
                RankedRecommendationOut(
                    rank=r.rank,
                    task=task_to_schema(r.task, c.dep_service),
                    explanation=r.explanation,
                    ranking_key_priority=abs(r.ranking_key[0]),
                    ranking_key_deadline=str(r.ranking_key[2]),
                    ranking_key_duration=int(r.ranking_key[3]),
                )
            )

        blocked_list = []
        for blocked_t, prereqs in sched.blocked_tasks_info:
            blocked_list.append(
                BlockedTaskDetailOut(
                    task=task_to_schema(blocked_t, c.dep_service),
                    blocking_prerequisites=[task_to_schema(p, c.dep_service) for p in prereqs],
                )
            )

        top_rec = ranked_list[0] if ranked_list else None

        return {
            "is_valid": sched.is_valid,
            "error_message": sched.error_message,
            "total_tasks_count": sched.total_tasks_count,
            "eligible_count": sched.eligible_count,
            "blocked_count": sched.blocked_count,
            "in_progress_count": sched.in_progress_count,
            "completed_count": sched.completed_count,
            "recommendation": top_rec,
            "ranked_tasks": ranked_list,
            "blocked_tasks": blocked_list,
        }

    @app.get("/api/scheduling/risks", response_model=RiskSummaryOut, tags=["Intelligent Scheduling"])
    def get_deadline_risks(c: ServiceContainer = Depends(get_service_container)) -> RiskSummaryOut:
        summary = c.risk_analyzer.analyze_all()

        assessments_out = []
        for a in summary.assessments:
            assessments_out.append(
                TaskRiskAssessmentOut(
                    task_id=a.task.id or 0,
                    task_title=a.task.title,
                    priority=a.task.priority,
                    status=a.task.status,
                    risk_category=a.category.value,
                    deadline_formatted=a.task.formatted_deadline if a.task.due_date else "No deadline",
                    duration_formatted=format_duration(a.duration_minutes),
                    time_remaining_minutes=a.time_remaining_minutes,
                    slack_minutes=a.slack_minutes,
                    is_blocked=a.is_blocked,
                    explanation=a.explanation,
                )
            )

        return RiskSummaryOut(
            total_tasks=summary.total_tasks,
            completed_count=summary.completed_count,
            safe_count=summary.safe_count,
            at_risk_count=summary.at_risk_count,
            overdue_count=summary.overdue_count,
            unscheduled_count=summary.unscheduled_count,
            blocked_count=summary.blocked_count,
            assessments=assessments_out,
        )

    # -----------------------------------------------------------------
    # Planning & Critical Path (CO5)
    # -----------------------------------------------------------------

    @app.get("/api/planning/critical-path", response_model=CriticalPathOut, tags=["Planning"])
    def get_critical_path(c: ServiceContainer = Depends(get_service_container)) -> CriticalPathOut:
        res = c.cp_service.calculate_critical_path()
        details_out = []
        for task_id, d in res.schedule_details.items():
            details_out.append(
                CriticalPathDetailOut(
                    task_id=task_id,
                    task_title=d.task.title,
                    duration_minutes=d.duration_minutes,
                    earliest_start=d.earliest_start,
                    earliest_finish=d.earliest_finish,
                    is_on_critical_path=d.is_on_critical_path,
                    predecessor_id=d.predecessor_id,
                )
            )

        return CriticalPathOut(
            is_valid=res.is_valid,
            error_message=res.error_message,
            total_duration_minutes=res.total_duration_minutes,
            total_duration_formatted=res.total_duration_formatted,
            critical_path_ids=res.critical_path_ids,
            topological_order=res.topological_order,
            explanation=res.explanation,
            schedule_details=details_out,
        )

    @app.post("/api/planning/what-if", response_model=WhatIfOut, tags=["Planning"])
    def simulate_what_if(payload: WhatIfIn, c: ServiceContainer = Depends(get_service_container)) -> WhatIfOut:
        """Run What-If simulation without persisting anything to SQLite."""
        res = c.what_if_service.simulate_delay(
            task_id=payload.task_id,
            delay_minutes=payload.delay_minutes,
        )

        impacts_out = [
            TaskSimulationImpactOut(
                task_id=imp.task_id,
                task_title=imp.task_title,
                status=imp.status,
                duration_minutes=imp.duration_minutes,
                baseline_start=imp.baseline_start,
                baseline_finish=imp.baseline_finish,
                simulated_start=imp.simulated_start,
                simulated_finish=imp.simulated_finish,
                start_delay_minutes=imp.start_delay_minutes,
                finish_delay_minutes=imp.finish_delay_minutes,
                is_affected=imp.is_affected,
            )
            for imp in res.impacts
        ]

        return WhatIfOut(
            is_valid=res.is_valid,
            error_message=res.error_message,
            selected_task_id=res.selected_task_id,
            selected_task_title=res.selected_task_title,
            added_delay_minutes=res.added_delay_minutes,
            baseline_project_duration=res.baseline_project_duration,
            simulated_project_duration=res.simulated_project_duration,
            project_delay_increase=res.project_delay_increase,
            affected_tasks_count=res.affected_tasks_count,
            affected_task_ids=res.affected_task_ids,
            unaffected_task_ids=res.unaffected_task_ids,
            impacts=impacts_out,
            explanation=res.explanation,
            is_persistent=False,
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("taskforge.api.main:app", host="127.0.0.1", port=8000, reload=True)
