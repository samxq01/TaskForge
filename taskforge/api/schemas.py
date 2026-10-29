"""Pydantic schemas for the TaskForge FastAPI local integration layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


# =====================================================================
# Task Models
# =====================================================================

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    priority: int = Field(default=2, ge=1, le=4)
    duration: int = Field(default=30, gt=0, le=14400)
    status: str = Field(default="Pending")
    description: str = Field(default="", max_length=1000)
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    priority: Optional[int] = Field(None, ge=1, le=4)
    duration: Optional[int] = Field(None, gt=0, le=14400)
    status: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    title: str
    priority: int
    priority_label: str
    duration: int
    duration_formatted: str
    status: str
    description: str
    due_date: Optional[datetime] = None
    due_date_formatted: str
    created_at: datetime
    updated_at: datetime
    is_ready: bool = True
    prerequisites_count: int = 0
    dependents_count: int = 0


# =====================================================================
# Overview / KPI
# =====================================================================

class OverviewOut(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    safe_tasks: int
    at_risk_tasks: int
    unscheduled_tasks: int
    bst_nodes: int
    bst_height: int
    hash_size: int
    queue_size: int
    can_undo: bool
    can_redo: bool
    recommended_task_id: Optional[int] = None
    recommended_task_title: Optional[str] = None
    critical_path_duration_formatted: Optional[str] = None


# =====================================================================
# Queue & Undo / Redo
# =====================================================================

class QueueProcessOut(BaseModel):
    success: bool
    message: str
    processed_task: Optional[TaskOut] = None
    remaining_queue_size: int
    next_task: Optional[TaskOut] = None


class UndoRedoOut(BaseModel):
    success: bool
    action_type: str
    task_id: int
    summary: str
    can_undo: bool
    can_redo: bool


class QueueStatusOut(BaseModel):
    queue_size: int
    head_task: Optional[TaskOut] = None
    queue_tasks: List[TaskOut]
    can_undo: bool
    can_redo: bool
    undo_history_count: int
    redo_history_count: int


# =====================================================================
# Dependencies & Graph
# =====================================================================

class DependencyCreateIn(BaseModel):
    prerequisite_id: int
    dependent_id: int


class DependencyDeleteIn(BaseModel):
    prerequisite_id: int
    dependent_id: int


class EdgeOut(BaseModel):
    source: int
    target: int


class DependencyGraphOut(BaseModel):
    nodes: List[TaskOut]
    edges: List[EdgeOut]
    is_cyclic: bool
    cycle_nodes: List[int]
    topological_order: List[int]
    blocked_tasks_count: int


class TraversalIn(BaseModel):
    start_task_id: int


class TraversalOut(BaseModel):
    algorithm: str
    start_task_id: int
    visited_sequence: List[int]


# =====================================================================
# Algorithms & Benchmarks (CO3 / CO4)
# =====================================================================

class SearchBenchmarkIn(BaseModel):
    dataset_size: int = Field(default=1000, ge=10, le=100000)
    scenario: str = Field(default="random")  # 'first', 'middle', 'last', 'absent', 'random'
    target: Optional[int] = None


class SearchBenchmarkOut(BaseModel):
    dataset_size: int
    scenario: str
    target: int
    linear_time_ms: float
    linear_comparisons: int
    linear_found: bool
    binary_time_ms: float
    binary_comparisons: int
    binary_found: bool
    speedup_factor: float


class SortBenchmarkIn(BaseModel):
    dataset_size: int = Field(default=500, ge=10, le=10000)
    distribution: str = Field(default="random")  # 'random', 'sorted', 'reversed'


class SortBenchmarkOut(BaseModel):
    dataset_size: int
    distribution: str
    insertion_time_ms: float
    insertion_comparisons: int
    insertion_shifts: int
    merge_time_ms: float
    merge_comparisons: int
    merge_shifts: int
    speedup_factor: float


# =====================================================================
# Tree & Hash Table (CO2 / CO3)
# =====================================================================

class TreeOverviewOut(BaseModel):
    total_nodes: int
    height: int
    is_balanced: bool
    inorder_tasks: List[TaskOut]
    preorder_tasks: List[TaskOut]
    postorder_tasks: List[TaskOut]


class TreeSearchIn(BaseModel):
    task_id: int
    due_date: Optional[datetime] = None


class HashIndexStatsOut(BaseModel):
    capacity: int
    size: int
    load_factor: float
    occupied_buckets: int
    empty_buckets: int
    collision_count: int
    max_chain_length: int
    bucket_distribution: List[int]


class HashLookupOut(BaseModel):
    task_id: int
    found: bool
    comparisons: int
    task: Optional[TaskOut] = None


class StructureEvaluationIn(BaseModel):
    dataset_size: int = Field(default=100, ge=10, le=5000)
    scenario: str = Field(default="hit")  # 'hit' or 'absent'


class StructureResultOut(BaseModel):
    structure_name: str
    dataset_size: int
    scenario: str
    target_id: int
    construction_time_ms: float
    lookup_time_total_ms: float
    lookup_time_avg_us: float
    operations_count: int
    comparisons_count: int
    result_found: bool


class StructureEvaluationSuiteOut(BaseModel):
    dataset_size: int
    scenario: str
    target_id: int
    results: List[StructureResultOut]


# =====================================================================
# Scheduling & Risk Analyzer (CO1 / CO5)
# =====================================================================

class RankedRecommendationOut(BaseModel):
    rank: int
    task: TaskOut
    explanation: str
    ranking_key_priority: int
    ranking_key_deadline: str
    ranking_key_duration: int


class BlockedTaskDetailOut(BaseModel):
    task: TaskOut
    blocking_prerequisites: List[TaskOut]


class SmartScheduleOut(BaseModel):
    is_valid: bool
    error_message: Optional[str]
    total_tasks_count: int
    eligible_count: int
    blocked_count: int
    in_progress_count: int
    completed_count: int
    recommendation: Optional[RankedRecommendationOut] = None
    ranked_tasks: List[RankedRecommendationOut]
    blocked_tasks: List[BlockedTaskDetailOut]


class TaskRiskAssessmentOut(BaseModel):
    task_id: int
    task_title: str
    priority: int
    status: str
    risk_category: str
    deadline_formatted: str
    duration_formatted: str
    time_remaining_minutes: Optional[float] = None
    slack_minutes: Optional[float] = None
    is_blocked: bool
    explanation: str


class RiskSummaryOut(BaseModel):
    total_tasks: int
    completed_count: int
    safe_count: int
    at_risk_count: int
    overdue_count: int
    unscheduled_count: int
    blocked_count: int
    assessments: List[TaskRiskAssessmentOut]


# =====================================================================
# Critical Path & What-If Simulation (CO5)
# =====================================================================

class CriticalPathDetailOut(BaseModel):
    task_id: int
    task_title: str
    duration_minutes: int
    earliest_start: int
    earliest_finish: int
    is_on_critical_path: bool
    predecessor_id: Optional[int]


class CriticalPathOut(BaseModel):
    is_valid: bool
    error_message: Optional[str]
    total_duration_minutes: int
    total_duration_formatted: str
    critical_path_ids: List[int]
    topological_order: List[int]
    explanation: str
    schedule_details: List[CriticalPathDetailOut]


class WhatIfIn(BaseModel):
    task_id: int
    delay_minutes: int = Field(..., ge=0, le=14400)


class TaskSimulationImpactOut(BaseModel):
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


class WhatIfOut(BaseModel):
    is_valid: bool
    error_message: Optional[str]
    selected_task_id: Optional[int]
    selected_task_title: Optional[str]
    added_delay_minutes: int
    baseline_project_duration: int
    simulated_project_duration: int
    project_delay_increase: int
    affected_tasks_count: int
    affected_task_ids: List[int]
    unaffected_task_ids: List[int]
    impacts: List[TaskSimulationImpactOut]
    explanation: str
    is_persistent: bool = False  # Mandatory safety contract
