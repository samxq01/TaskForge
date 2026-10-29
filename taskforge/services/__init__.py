"""Service layer modules for TaskForge."""

from taskforge.services.critical_path import (
    CriticalPathResult,
    CriticalPathService,
    CriticalPathTaskDetail,
    format_duration,
)
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import (
    DeadlineRiskAnalyzer,
    RiskAnalysisSummary,
    RiskCategory,
    TaskRiskAssessment,
)
from taskforge.services.scheduler import (
    RankedTaskRecommendation,
    SchedulerService,
    SmartScheduleResult,
)
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import Action, ActionType, UndoManager
from taskforge.services.what_if_simulator import (
    TaskSimulationImpact,
    WhatIfSimulationResult,
    WhatIfSimulatorService,
)

__all__ = [
    "Action",
    "ActionType",
    "CriticalPathResult",
    "CriticalPathService",
    "CriticalPathTaskDetail",
    "DeadlineRiskAnalyzer",
    "DependencyService",
    "RankedTaskRecommendation",
    "RiskAnalysisSummary",
    "RiskCategory",
    "SchedulerService",
    "SmartScheduleResult",
    "TaskHashIndexService",
    "TaskIndexService",
    "TaskQueueService",
    "TaskRiskAssessment",
    "TaskSimulationImpact",
    "UndoManager",
    "WhatIfSimulationResult",
    "WhatIfSimulatorService",
    "format_duration",
]

