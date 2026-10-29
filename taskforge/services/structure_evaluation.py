"""Data structure evaluation service comparing List, Hash Table, and BST (CO2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import time
from typing import Any, Optional

from taskforge.models import Priority, Task, TaskStatus
from taskforge.structures.bst import BinarySearchTree
from taskforge.structures.hash_table import HashTable


@dataclass
class StructureBenchmarkResult:
    """Stores the empirical measurements of a single data structure evaluation run."""

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
    result_task_id: Optional[int]
    extra_stats: dict[str, Any] = field(default_factory=dict)


def generate_evaluation_dataset(size: int, seed: int = 42) -> list[Task]:
    """Generate a reproducible, synthetic task dataset for empirical benchmarking.
    
    Args:
        size: Number of Task instances to produce (must be >= 10).
        seed: Random seed for deterministic generation.
        
    Returns:
        List of Task instances with unique IDs.
        
    Raises:
        ValueError: If size < 10.
    """
    if size < 10:
        raise ValueError(f"Dataset size must be at least 10, got {size}.")

    rng = random.Random(seed)
    now = datetime.now()
    statuses = [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, TaskStatus.COMPLETED.value]
    priorities = [Priority.LOW.value, Priority.MEDIUM.value, Priority.HIGH.value, Priority.URGENT.value]

    tasks: list[Task] = []
    # Generate sequential unique IDs
    raw_ids = list(range(1, size + 1))
    # Randomly shuffle IDs so tree insertions form a balanced natural BST
    rng.shuffle(raw_ids)

    for task_id in raw_ids:
        due = now + timedelta(days=rng.randint(1, 30), hours=rng.randint(0, 23)) if rng.random() > 0.15 else None
        tasks.append(
            Task(
                id=task_id,
                title=f"Synthetic Task #{task_id}",
                description=f"Generated workload item with key ID {task_id}",
                priority=rng.choice(priorities),
                duration=rng.randint(15, 240),
                status=rng.choice(statuses),
                due_date=due,
            )
        )

    return tasks


def select_target_id(dataset: list[Task], scenario: str, seed: int = 42) -> int:
    """Select a search target task ID corresponding to the requested scenario.
    
    Args:
        dataset: The evaluation task dataset.
        scenario: One of 'early', 'middle', 'late', 'absent'.
        seed: Random seed for randomized selections.
        
    Returns:
        An integer task ID.
    """
    if not dataset:
        return -999

    n = len(dataset)
    # The list is scanned in order, so positions in dataset determine hit scenario
    if scenario == "early":
        idx = max(0, int(n * 0.05))
        target_id = dataset[idx].id
    elif scenario == "middle":
        idx = int(n * 0.50)
        target_id = dataset[idx].id
    elif scenario == "late":
        idx = min(n - 1, int(n * 0.95))
        target_id = dataset[idx].id
    elif scenario == "absent":
        # Guaranteed absent key
        max_id = max((t.id for t in dataset if t.id is not None), default=0)
        return max_id + 99999
    else:  # fallback to random existing ID
        rng = random.Random(seed)
        target_id = rng.choice(dataset).id

    assert target_id is not None
    return target_id


def linear_search_task(dataset: list[Task], target_id: int) -> tuple[Optional[Task], int]:
    """Perform sequential list search on tasks and count key comparisons.
    
    Args:
        dataset: Task list.
        target_id: ID to search for.
        
    Returns:
        Tuple of (Task_or_None, comparison_count).
    """
    comparisons = 0
    for task in dataset:
        comparisons += 1
        if task.id == target_id:
            return task, comparisons
    return None, comparisons


class StructureEvaluationService:
    """Evaluates and compares the storage and retrieval characteristics of List, HashTable, and BST (CO2)."""

    def __init__(self) -> None:
        pass

    def run_evaluation(
        self,
        dataset: list[Task],
        scenario: str = "middle",
        repetitions: int = 250,
        seed: int = 42,
    ) -> list[StructureBenchmarkResult]:
        """Execute a controlled comparison across List, Custom HashTable, and Custom BST.
        
        Args:
            dataset: The input task dataset.
            scenario: Lookup scenario ('early', 'middle', 'late', 'absent').
            repetitions: Number of lookup iterations for statistical timing stability.
            seed: Seed for target determination.
            
        Returns:
            List of StructureBenchmarkResult for List, HashTable, and BST.
        """
        if not dataset:
            raise ValueError("Dataset cannot be empty.")
        if repetitions < 1:
            raise ValueError("Repetitions must be at least 1.")

        n = len(dataset)
        target_id = select_target_id(dataset, scenario, seed=seed)

        # -------------------------------------------------------------
        # 1. Structure Construction (Timed Separately)
        # -------------------------------------------------------------
        # 1A. List Construction
        t0 = time.perf_counter()
        task_list: list[Task] = list(dataset)
        list_const_ms = (time.perf_counter() - t0) * 1000.0

        # 1B. Custom Hash Table Construction
        t0 = time.perf_counter()
        hash_table: HashTable[int, Task] = HashTable(initial_capacity=max(16, n // 2))
        for task in dataset:
            assert task.id is not None
            hash_table.insert(task.id, task)
        hash_const_ms = (time.perf_counter() - t0) * 1000.0

        # 1C. Custom BST Construction (Keyed strictly by task ID)
        t0 = time.perf_counter()
        bst: BinarySearchTree[int, Task] = BinarySearchTree()
        for task in dataset:
            assert task.id is not None
            bst.insert(task.id, task)
        bst_const_ms = (time.perf_counter() - t0) * 1000.0

        # -------------------------------------------------------------
        # 2. Retrieval / Lookup Benchmarks (Repeated across repetitions)
        # -------------------------------------------------------------
        # 2A. List Lookup
        t0 = time.perf_counter()
        for _ in range(repetitions):
            list_res, list_comps = linear_search_task(task_list, target_id)
        list_lookup_total_ms = (time.perf_counter() - t0) * 1000.0
        list_avg_us = (list_lookup_total_ms / repetitions) * 1000.0

        # 2B. Hash Table Lookup
        t0 = time.perf_counter()
        for _ in range(repetitions):
            hash_res, hash_comps = hash_table.get_with_comparisons(target_id)
        hash_lookup_total_ms = (time.perf_counter() - t0) * 1000.0
        hash_avg_us = (hash_lookup_total_ms / repetitions) * 1000.0

        # 2C. BST Lookup
        t0 = time.perf_counter()
        for _ in range(repetitions):
            bst_res, bst_comps = bst.search_with_comparisons(target_id)
        bst_lookup_total_ms = (time.perf_counter() - t0) * 1000.0
        bst_avg_us = (bst_lookup_total_ms / repetitions) * 1000.0

        # -------------------------------------------------------------
        # 3. Correctness Verification (Outside Timed Window)
        # -------------------------------------------------------------
        # Verify that all three methods returned equivalent results
        list_found = list_res is not None
        hash_found = hash_res is not None
        bst_found = bst_res is not None

        assert list_found == hash_found == bst_found, (
            f"Retrieval mismatch: list={list_found}, hash={hash_found}, bst={bst_found}"
        )
        if list_found:
            assert list_res.id == hash_res.id == bst_res.id  # type: ignore

        # Gather extra statistics
        hash_stats = hash_table.collision_stats()
        bst_stats = {"tree_height": bst.height(), "tree_size": bst.size()}

        results = [
            StructureBenchmarkResult(
                structure_name="List (Sequential Search)",
                dataset_size=n,
                scenario=scenario,
                target_id=target_id,
                construction_time_ms=round(list_const_ms, 4),
                lookup_time_total_ms=round(list_lookup_total_ms, 4),
                lookup_time_avg_us=round(list_avg_us, 3),
                operations_count=repetitions,
                comparisons_count=list_comps,
                result_found=list_found,
                result_task_id=list_res.id if list_res else None,
                extra_stats={"capacity": n, "ordering": "Preserves Insertion Order"},
            ),
            StructureBenchmarkResult(
                structure_name="Custom Hash Table",
                dataset_size=n,
                scenario=scenario,
                target_id=target_id,
                construction_time_ms=round(hash_const_ms, 4),
                lookup_time_total_ms=round(hash_lookup_total_ms, 4),
                lookup_time_avg_us=round(hash_avg_us, 3),
                operations_count=repetitions,
                comparisons_count=hash_comps,
                result_found=hash_found,
                result_task_id=hash_res.id if hash_res else None,
                extra_stats=hash_stats,
            ),
            StructureBenchmarkResult(
                structure_name="Custom Binary Search Tree",
                dataset_size=n,
                scenario=scenario,
                target_id=target_id,
                construction_time_ms=round(bst_const_ms, 4),
                lookup_time_total_ms=round(bst_lookup_total_ms, 4),
                lookup_time_avg_us=round(bst_avg_us, 3),
                operations_count=repetitions,
                comparisons_count=bst_comps,
                result_found=bst_found,
                result_task_id=bst_res.id if bst_res else None,
                extra_stats=bst_stats,
            ),
        ]

        return results

    def run_multi_size_comparison(
        self,
        sizes: list[int] = [100, 1000, 5000],
        scenario: str = "middle",
        repetitions: int = 150,
    ) -> list[StructureBenchmarkResult]:
        """Execute evaluations across multiple dataset sizes for comparative charting.
        
        Args:
            sizes: List of dataset sizes.
            scenario: Lookup scenario.
            repetitions: Repetitions per trial.
            
        Returns:
            Combined list of StructureBenchmarkResult records across all sizes.
        """
        all_results: list[StructureBenchmarkResult] = []
        for s in sizes:
            dataset = generate_evaluation_dataset(size=s, seed=42 + s)
            res = self.run_evaluation(dataset, scenario=scenario, repetitions=repetitions)
            all_results.extend(res)
        return all_results
