"""Dependency injection and service container for TaskForge FastAPI application."""

from __future__ import annotations

import os
from typing import Optional

from taskforge.services.benchmark_service import BenchmarkService
from taskforge.services.critical_path import CriticalPathService
from taskforge.services.dependency_service import DependencyService
from taskforge.services.risk_analyzer import DeadlineRiskAnalyzer
from taskforge.services.scheduler import SchedulerService
from taskforge.services.structure_evaluation import StructureEvaluationService
from taskforge.services.task_hash_index import TaskHashIndexService
from taskforge.services.task_index import TaskIndexService
from taskforge.services.task_queue_service import TaskQueueService
from taskforge.services.undo_manager import UndoManager
from taskforge.services.what_if_simulator import WhatIfSimulatorService
from taskforge.storage import TaskStorage


class ServiceContainer:
    """Manages shared singleton services for FastAPI operations."""

    def __init__(self, db_path: str = "taskforge.db") -> None:
        self.db_path = db_path
        self.storage = TaskStorage(db_path)
        self.undo_manager = UndoManager()
        self.dep_service = DependencyService(self.storage)
        self.scheduler_service = SchedulerService(self.storage, self.dep_service)
        self.queue_service = TaskQueueService(
            storage=self.storage,
            undo_manager=self.undo_manager,
            dependency_service=self.dep_service,
        )
        self.index_service = TaskIndexService(self.storage)
        self.hash_index = TaskHashIndexService(self.storage)
        self.risk_analyzer = DeadlineRiskAnalyzer(self.storage, self.dep_service)
        self.cp_service = CriticalPathService(self.storage, self.dep_service)
        self.what_if_service = WhatIfSimulatorService(
            storage=self.storage,
            dependency_service=self.dep_service,
        )
        self.benchmark_service = BenchmarkService()
        self.structure_evaluation_service = StructureEvaluationService()

    def sync_all(self) -> None:
        """Synchronize in-memory indexes and queues with persistent SQLite state."""
        self.dep_service.rebuild()
        self.queue_service.refresh()
        self.index_service.rebuild()
        self.hash_index.rebuild_index()


_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    """Retrieve or initialize the active service container singleton."""
    global _container
    if _container is None:
        db_path = os.environ.get("TASKFORGE_DB_PATH", "taskforge.db")
        _container = ServiceContainer(db_path)
    return _container


def set_service_container(container: ServiceContainer) -> None:
    """Set custom container (useful for isolated test runs)."""
    global _container
    _container = container


def reset_service_container() -> None:
    """Reset global container instance."""
    global _container
    _container = None
