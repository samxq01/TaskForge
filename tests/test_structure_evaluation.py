"""Tests for StructureEvaluationService comparing List, HashTable, and BST (CO2)."""

import pytest

from taskforge.services.structure_evaluation import (
    StructureEvaluationService,
    generate_evaluation_dataset,
    linear_search_task,
    select_target_id,
)


def test_generate_evaluation_dataset_valid() -> None:
    """Test synthetic dataset generation with deterministic seed."""
    ds1 = generate_evaluation_dataset(size=50, seed=123)
    assert len(ds1) == 50
    # All IDs must be unique
    ids = [t.id for t in ds1]
    assert len(set(ids)) == 50
    # Seed reproducibility
    ds2 = generate_evaluation_dataset(size=50, seed=123)
    assert [t.id for t in ds2] == ids


def test_generate_evaluation_dataset_invalid_size() -> None:
    """Test that generating too small a dataset raises ValueError."""
    with pytest.raises(ValueError, match="at least 10"):
        generate_evaluation_dataset(size=5)


def test_select_target_id_scenarios() -> None:
    """Test target ID selection for all benchmark scenarios."""
    dataset = generate_evaluation_dataset(size=100, seed=42)
    existing_ids = {t.id for t in dataset}

    early_id = select_target_id(dataset, "early")
    middle_id = select_target_id(dataset, "middle")
    late_id = select_target_id(dataset, "late")
    absent_id = select_target_id(dataset, "absent")

    assert early_id in existing_ids
    assert middle_id in existing_ids
    assert late_id in existing_ids
    assert absent_id not in existing_ids


def test_linear_search_task() -> None:
    """Test sequential list search reference implementation."""
    dataset = generate_evaluation_dataset(size=20, seed=1)
    target = dataset[5]
    assert target.id is not None

    found_task, comps = linear_search_task(dataset, target.id)
    assert found_task is not None
    assert found_task.id == target.id
    assert comps == 6  # 0-indexed position 5 requires 6 comparisons

    missing_task, miss_comps = linear_search_task(dataset, 99999)
    assert missing_task is None
    assert miss_comps == 20  # Checked all 20 items


def test_structure_evaluation_hit_scenario() -> None:
    """Test running evaluation on an existing key across List, HashTable, and BST."""
    service = StructureEvaluationService()
    dataset = generate_evaluation_dataset(size=100, seed=42)

    results = service.run_evaluation(dataset, scenario="middle", repetitions=50)
    assert len(results) == 3

    list_res, hash_res, bst_res = results

    # Verify identical lookup success and target match
    assert list_res.result_found is True
    assert hash_res.result_found is True
    assert bst_res.result_found is True
    assert list_res.result_task_id == hash_res.result_task_id == bst_res.result_task_id

    # Verify construction time measured
    assert list_res.construction_time_ms >= 0.0
    assert hash_res.construction_time_ms >= 0.0
    assert bst_res.construction_time_ms >= 0.0

    # Verify comparisons counted
    assert list_res.comparisons_count >= 1
    assert hash_res.comparisons_count >= 1
    assert bst_res.comparisons_count >= 1

    # Verify extra statistics populated
    assert "load_factor" in hash_res.extra_stats
    assert "tree_height" in bst_res.extra_stats


def test_structure_evaluation_absent_scenario() -> None:
    """Test running evaluation on an absent key across List, HashTable, and BST."""
    service = StructureEvaluationService()
    dataset = generate_evaluation_dataset(size=50, seed=99)

    results = service.run_evaluation(dataset, scenario="absent", repetitions=30)
    assert len(results) == 3

    for res in results:
        assert res.result_found is False
        assert res.result_task_id is None
        assert res.lookup_time_total_ms >= 0.0


def test_multi_size_comparison() -> None:
    """Test running evaluation across multiple dataset sizes."""
    service = StructureEvaluationService()
    results = service.run_multi_size_comparison(sizes=[20, 50], scenario="early", repetitions=20)
    # 2 sizes * 3 structures = 6 records
    assert len(results) == 6
    sizes_present = {r.dataset_size for r in results}
    assert sizes_present == {20, 50}
