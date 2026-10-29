"""Benchmark service for evaluating searching and sorting performance (CO3)."""

from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Any, Sequence

from taskforge.algorithms.searching import binary_search, linear_search
from taskforge.algorithms.sorting import insertion_sort, merge_sort


@dataclass(frozen=True)
class SearchBenchmarkResult:
    """Benchmark outcome comparing Linear Search and Binary Search on equivalent data."""
    dataset_size: int
    scenario: str
    target: int
    linear_time_ms: float
    linear_comparisons: int
    linear_found: bool
    binary_time_ms: float
    binary_comparisons: int
    binary_found: bool
    both_matched: bool


@dataclass(frozen=True)
class SortBenchmarkResult:
    """Benchmark outcome comparing Insertion Sort and Merge Sort on equivalent data."""
    dataset_size: int
    distribution: str
    insertion_time_ms: float
    insertion_comparisons: int
    insertion_shifts: int
    merge_time_ms: float
    merge_comparisons: int
    merge_shifts: int
    is_correct: bool


class BenchmarkService:
    """Service providing reproducible benchmarking for searching and sorting algorithms."""

    DEFAULT_SEARCH_SIZES = [100, 1000, 5000]
    DEFAULT_SORT_SIZES = [100, 500, 1000, 2000]

    @staticmethod
    def generate_dataset(size: int, distribution: str = "random", seed: int = 42) -> list[int]:
        """Generate a deterministic dataset of integers.
        
        Args:
            size: Number of elements (must be positive).
            distribution: 'random', 'sorted', or 'reversed'.
            seed: Seed for reproducible pseudo-random generation.
            
        Returns:
            List of integers matching the requested distribution.
        """
        if size <= 0:
            return []

        rng = random.Random(seed)
        # Generate random unique-ish integers
        base = [rng.randint(1, size * 10) for _ in range(size)]

        if distribution == "sorted":
            base.sort()
        elif distribution == "reversed":
            base.sort(reverse=True)
        # 'random' retains the generated order

        return base

    @classmethod
    def benchmark_search(
        cls,
        size: int = 1000,
        scenario: str = "middle",
        repetitions: int = 5,
        seed: int = 42,
    ) -> SearchBenchmarkResult:
        """Benchmark Linear Search vs. Binary Search on equivalent data.
        
        Binary Search input is pre-sorted outside of timed execution.
        
        Args:
            size: Dataset size.
            scenario: 'first', 'middle', 'last', or 'absent'.
            repetitions: Number of iterations to average timings.
            seed: RNG seed.
            
        Returns:
            SearchBenchmarkResult with real timing and comparison counts.
        """
        if size <= 0:
            raise ValueError("Dataset size must be positive.")

        # Generate base dataset and pre-sort it for Binary Search
        data = cls.generate_dataset(size, distribution="random", seed=seed)
        sorted_data = sorted(data)

        # Determine target
        if scenario == "first":
            target = sorted_data[0]
        elif scenario == "middle":
            target = sorted_data[len(sorted_data) // 2]
        elif scenario == "last":
            target = sorted_data[-1]
        elif scenario == "absent":
            # Distinct number guaranteed absent
            target = max(sorted_data) + 999
        else:
            raise ValueError(f"Unknown scenario '{scenario}'. Choose from: first, middle, last, absent.")

        # 1. Benchmark Linear Search (on sorted_data or data)
        # We search the sorted array so targets are identical and comparable
        linear_times: list[float] = []
        lin_res = linear_search(sorted_data, target)
        for _ in range(repetitions):
            t0 = time.perf_counter()
            lin_res = linear_search(sorted_data, target)
            t1 = time.perf_counter()
            linear_times.append((t1 - t0) * 1000.0)

        # 2. Benchmark Binary Search (on pre-sorted array)
        binary_times: list[float] = []
        bin_res = binary_search(sorted_data, target)
        for _ in range(repetitions):
            t0 = time.perf_counter()
            bin_res = binary_search(sorted_data, target)
            t1 = time.perf_counter()
            binary_times.append((t1 - t0) * 1000.0)

        avg_lin_time = sum(linear_times) / len(linear_times)
        avg_bin_time = sum(binary_times) / len(binary_times)
        both_matched = (lin_res.found == bin_res.found)

        return SearchBenchmarkResult(
            dataset_size=size,
            scenario=scenario,
            target=target,
            linear_time_ms=round(avg_lin_time, 5),
            linear_comparisons=lin_res.comparisons,
            linear_found=lin_res.found,
            binary_time_ms=round(avg_bin_time, 5),
            binary_comparisons=bin_res.comparisons,
            binary_found=bin_res.found,
            both_matched=both_matched,
        )

    @classmethod
    def benchmark_sorting(
        cls,
        size: int = 500,
        distribution: str = "random",
        repetitions: int = 1,
        seed: int = 42,
    ) -> SortBenchmarkResult:
        """Benchmark Insertion Sort vs. Merge Sort on independent copies of equivalent data.
        
        Args:
            size: Dataset size (recommended <= 3000 for responsive UI due to Insertion Sort's O(n^2)).
            distribution: 'random', 'sorted', or 'reversed'.
            repetitions: Iteration count for timing.
            seed: RNG seed.
            
        Returns:
            SortBenchmarkResult with real timing, comparisons, and shift counts.
        """
        if size <= 0:
            raise ValueError("Dataset size must be positive.")

        base_data = cls.generate_dataset(size, distribution=distribution, seed=seed)
        expected_sorted = sorted(base_data)

        # 1. Insertion Sort Benchmark
        ins_times: list[float] = []
        ins_res = insertion_sort(list(base_data))
        for _ in range(repetitions):
            input_copy = list(base_data)
            t0 = time.perf_counter()
            ins_res = insertion_sort(input_copy)
            t1 = time.perf_counter()
            ins_times.append((t1 - t0) * 1000.0)

        # 2. Merge Sort Benchmark
        merge_times: list[float] = []
        merge_res = merge_sort(list(base_data))
        for _ in range(repetitions):
            input_copy = list(base_data)
            t0 = time.perf_counter()
            merge_res = merge_sort(input_copy)
            t1 = time.perf_counter()
            merge_times.append((t1 - t0) * 1000.0)

        avg_ins_time = sum(ins_times) / len(ins_times)
        avg_merge_time = sum(merge_times) / len(merge_times)
        is_correct = (ins_res.items == expected_sorted) and (merge_res.items == expected_sorted)

        return SortBenchmarkResult(
            dataset_size=size,
            distribution=distribution,
            insertion_time_ms=round(avg_ins_time, 4),
            insertion_comparisons=ins_res.comparisons,
            insertion_shifts=ins_res.shifts,
            merge_time_ms=round(avg_merge_time, 4),
            merge_comparisons=merge_res.comparisons,
            merge_shifts=merge_res.shifts,
            is_correct=is_correct,
        )

    @classmethod
    def run_search_suite(
        cls,
        sizes: Sequence[int] = (100, 1000, 5000),
        scenario: str = "middle",
        seed: int = 42,
    ) -> list[SearchBenchmarkResult]:
        """Run a full searching benchmark suite across multiple dataset sizes."""
        return [cls.benchmark_search(size=s, scenario=scenario, seed=seed) for s in sizes]

    @classmethod
    def run_sort_suite(
        cls,
        sizes: Sequence[int] = (100, 500, 1000, 2000),
        distribution: str = "random",
        seed: int = 42,
    ) -> list[SortBenchmarkResult]:
        """Run a full sorting benchmark suite across multiple dataset sizes."""
        return [cls.benchmark_sorting(size=s, distribution=distribution, seed=seed) for s in sizes]
