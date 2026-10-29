"""Unit tests for the BenchmarkService (CO3)."""

import pytest

from taskforge.services.benchmark_service import (
    BenchmarkService,
    SearchBenchmarkResult,
    SortBenchmarkResult,
)


def test_dataset_generation() -> None:
    """Dataset generation produces expected size, distribution, and reproducibility."""
    # Reproducibility with seed
    d1 = BenchmarkService.generate_dataset(100, "random", seed=123)
    d2 = BenchmarkService.generate_dataset(100, "random", seed=123)
    assert d1 == d2
    assert len(d1) == 100

    # Sorted distribution
    d_sorted = BenchmarkService.generate_dataset(50, "sorted", seed=1)
    assert d_sorted == sorted(d_sorted)

    # Reversed distribution
    d_rev = BenchmarkService.generate_dataset(50, "reversed", seed=1)
    assert d_rev == sorted(d_rev, reverse=True)

    # Empty on zero or negative
    assert BenchmarkService.generate_dataset(0) == []
    assert BenchmarkService.generate_dataset(-5) == []


def test_benchmark_search_scenarios() -> None:
    """Benchmark search generates valid results for first, middle, last, and absent targets."""
    for scen in ["first", "middle", "last", "absent"]:
        res = BenchmarkService.benchmark_search(size=200, scenario=scen, seed=42)
        assert isinstance(res, SearchBenchmarkResult)
        assert res.dataset_size == 200
        assert res.scenario == scen
        assert res.both_matched is True
        assert res.linear_time_ms >= 0.0
        assert res.binary_time_ms >= 0.0

        if scen == "first":
            # Linear search finds in 1 comparison
            assert res.linear_comparisons == 1
            assert res.linear_found is True
        elif scen == "middle":
            # Binary search finds in ~ 1 to 2 comparisons near center
            assert res.binary_found is True
            assert res.linear_found is True
        elif scen == "last":
            # Linear search needs n comparisons
            assert res.linear_comparisons == 200
        elif scen == "absent":
            assert res.linear_found is False
            assert res.binary_found is False


def test_benchmark_search_suite() -> None:
    """run_search_suite returns results for all specified sizes."""
    suite = BenchmarkService.run_search_suite(sizes=[50, 100], scenario="middle")
    assert len(suite) == 2
    assert suite[0].dataset_size == 50
    assert suite[1].dataset_size == 100


def test_benchmark_sorting_distributions() -> None:
    """Benchmark sorting produces verified correct results across distributions."""
    # 1. Random distribution
    res_rand = BenchmarkService.benchmark_sorting(size=100, distribution="random", seed=99)
    assert res_rand.is_correct is True
    assert res_rand.insertion_time_ms >= 0.0
    assert res_rand.merge_time_ms >= 0.0
    assert res_rand.insertion_comparisons > 0
    assert res_rand.merge_comparisons > 0

    # 2. Already sorted distribution (Insertion Sort best case: n - 1 comparisons)
    res_sorted = BenchmarkService.benchmark_sorting(size=100, distribution="sorted", seed=99)
    assert res_sorted.is_correct is True
    assert res_sorted.insertion_comparisons == 99  # (n - 1) comparisons!

    # 3. Reverse sorted distribution (Insertion Sort worst case)
    res_rev = BenchmarkService.benchmark_sorting(size=100, distribution="reversed", seed=99)
    assert res_rev.is_correct is True
    assert res_rev.insertion_comparisons > res_sorted.insertion_comparisons


def test_benchmark_sort_suite() -> None:
    """run_sort_suite returns results for all given sizes."""
    suite = BenchmarkService.run_sort_suite(sizes=[50, 100], distribution="random")
    assert len(suite) == 2
    assert all(r.is_correct for r in suite)


def test_benchmark_invalid_inputs() -> None:
    """Invalid sizes and scenarios raise appropriate ValueErrors."""
    with pytest.raises(ValueError, match="Dataset size must be positive"):
        BenchmarkService.benchmark_search(size=0)

    with pytest.raises(ValueError, match="Unknown scenario"):
        BenchmarkService.benchmark_search(size=100, scenario="invalid")

    with pytest.raises(ValueError, match="Dataset size must be positive"):
        BenchmarkService.benchmark_sorting(size=-10)
