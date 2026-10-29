"""Unit tests for custom HashTable data structure and separate chaining (CO2)."""

import pytest

from taskforge.structures.hash_table import HashTable


def test_empty_hash_table() -> None:
    """Test initial state of an empty hash table."""
    ht: HashTable[str, int] = HashTable(initial_capacity=8)
    assert ht.size() == 0
    assert ht.capacity() == 8
    assert ht.is_empty() is True
    assert ht.load_factor() == 0.0
    assert ht.get("missing") is None
    assert ht.get("missing", default=-1) == -1
    assert ht.contains("missing") is False
    assert ht.delete("missing") is False
    assert ht.update("missing", 100) is False
    assert ht.items() == []
    assert ht.keys() == []
    assert ht.values() == []


def test_single_insert_and_get() -> None:
    """Test inserting a single key-value pair and retrieving it."""
    ht: HashTable[str, str] = HashTable()
    assert ht.insert("apple", "fruit") is True  # New key
    assert ht.size() == 1
    assert ht.is_empty() is False
    assert ht.get("apple") == "fruit"
    assert ht.contains("apple") is True
    assert ht.get("banana") is None


def test_duplicate_key_updates_value_without_increasing_size() -> None:
    """Test that inserting a duplicate key updates its value and keeps size constant."""
    ht: HashTable[str, int] = HashTable()
    assert ht.insert("score", 10) is True
    assert ht.size() == 1
    assert ht.get("score") == 10

    # Overwrite value
    assert ht.insert("score", 99) is False  # Updated existing
    assert ht.size() == 1
    assert ht.get("score") == 99


def test_update_existing_and_missing() -> None:
    """Test the update method on existing and absent keys."""
    ht: HashTable[int, str] = HashTable()
    ht.insert(1, "one")

    assert ht.update(1, "ONE") is True
    assert ht.get(1) == "ONE"
    assert ht.size() == 1

    assert ht.update(2, "TWO") is False  # Key 2 does not exist
    assert ht.get(2) is None
    assert ht.size() == 1


def test_delete_operations() -> None:
    """Test deleting keys from the table."""
    ht: HashTable[str, int] = HashTable()
    ht.insert("a", 1)
    ht.insert("b", 2)
    ht.insert("c", 3)
    assert ht.size() == 3

    # Delete existing
    assert ht.delete("b") is True
    assert ht.size() == 2
    assert ht.get("b") is None
    assert ht.contains("b") is False

    # Delete already removed or absent key
    assert ht.delete("b") is False
    assert ht.delete("nonexistent") is False
    assert ht.size() == 2

    # Verify remaining keys
    assert ht.get("a") == 1
    assert ht.get("c") == 3


def test_collision_handling_separate_chaining() -> None:
    """Test deterministic collisions using an injected hash function."""
    # Force all keys to hash to bucket 2
    forced_ht: HashTable[str, int] = HashTable(initial_capacity=10, hash_fn=lambda k: 2)

    assert forced_ht.insert("alpha", 100) is True
    assert forced_ht.insert("beta", 200) is True
    assert forced_ht.insert("gamma", 300) is True

    # All 3 keys stored in the same bucket chain
    assert forced_ht.size() == 3
    stats = forced_ht.collision_stats()
    assert stats["occupied_buckets"] == 1
    assert stats["colliding_buckets"] == 1
    assert stats["total_collisions"] == 2
    assert stats["max_chain_length"] == 3

    # All keys are independently retrievable
    assert forced_ht.get("alpha") == 100
    assert forced_ht.get("beta") == 200
    assert forced_ht.get("gamma") == 300

    # Delete from the middle of the chain (beta)
    assert forced_ht.delete("beta") is True
    assert forced_ht.size() == 2
    assert forced_ht.get("beta") is None
    # alpha and gamma remain intact!
    assert forced_ht.get("alpha") == 100
    assert forced_ht.get("gamma") == 300

    new_stats = forced_ht.collision_stats()
    assert new_stats["total_collisions"] == 1
    assert new_stats["max_chain_length"] == 2


def test_get_with_comparisons() -> None:
    """Test that get_with_comparisons records exact chain traversals."""
    ht: HashTable[str, int] = HashTable(initial_capacity=10, hash_fn=lambda k: 0)
    ht.insert("k1", 1)
    ht.insert("k2", 2)
    ht.insert("k3", 3)

    # First in chain
    val, comps = ht.get_with_comparisons("k1")
    assert val == 1
    assert comps == 1

    # Third in chain
    val, comps = ht.get_with_comparisons("k3")
    assert val == 3
    assert comps == 3

    # Absent key requires inspecting all 3 entries in chain
    val, comps = ht.get_with_comparisons("missing")
    assert val is None
    assert comps == 3


def test_automatic_resizing_and_rehashing() -> None:
    """Test dynamic table resizing when load factor exceeds threshold."""
    # Initial capacity 4, threshold 0.75 -> capacity doubles when size > 3
    ht: HashTable[int, str] = HashTable(initial_capacity=4, max_load_factor=0.75)
    assert ht.capacity() == 4

    ht.insert(1, "one")
    ht.insert(2, "two")
    ht.insert(3, "three")
    assert ht.capacity() == 4
    assert ht.load_factor() == 0.75

    # 4th insert causes load factor to become 4/4 = 1.0 > 0.75 -> triggers resize to 8
    ht.insert(4, "four")
    assert ht.capacity() == 8
    assert ht.size() == 4
    assert ht.load_factor() == 0.5

    # All entries are correctly preserved and retrievable after rehashing
    for i in range(1, 5):
        assert ht.get(i) in ["one", "two", "three", "four"]


def test_items_keys_values_snapshots() -> None:
    """Test item, key, and value snapshot access."""
    ht: HashTable[str, int] = HashTable()
    entries = {"x": 10, "y": 20, "z": 30}
    for k, v in entries.items():
        ht.insert(k, v)

    items = ht.items()
    assert len(items) == 3
    assert set(items) == {("x", 10), ("y", 20), ("z", 30)}
    assert set(ht.keys()) == {"x", "y", "z"}
    assert set(ht.values()) == {10, 20, 30}


def test_clear_table() -> None:
    """Test clearing the hash table."""
    ht: HashTable[str, int] = HashTable(initial_capacity=8)
    ht.insert("a", 1)
    ht.insert("b", 2)
    assert ht.size() == 2

    ht.clear()
    assert ht.size() == 0
    assert ht.is_empty() is True
    assert ht.capacity() == 8
    assert ht.get("a") is None


def test_invalid_initialization_parameters() -> None:
    """Test that invalid capacity and load factors raise ValueError."""
    with pytest.raises(ValueError, match="Initial capacity"):
        HashTable(initial_capacity=0)

    with pytest.raises(ValueError, match="Max load factor"):
        HashTable(max_load_factor=-0.1)


def test_large_sequence_of_inserts_and_lookups() -> None:
    """Test inserting and looking up a large sequence of integer keys."""
    ht: HashTable[int, int] = HashTable(initial_capacity=16)
    count = 1000

    for i in range(count):
        ht.insert(i, i * 10)

    assert ht.size() == count
    assert ht.load_factor() <= 0.75  # Guaranteed by automatic resizing

    # Verify all lookups
    for i in range(count):
        assert ht.get(i) == i * 10

    # Verify missing lookups
    assert ht.get(-1) is None
    assert ht.get(count + 1) is None
