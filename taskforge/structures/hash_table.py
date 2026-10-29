"""Custom generic Hash Table data structure implementing separate chaining (CO2)."""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class _HashEntry(Generic[K, V]):
    """Internal key-value entry stored inside a bucket chain."""

    __slots__ = ("key", "value")

    def __init__(self, key: K, value: V) -> None:
        self.key: K = key
        self.value: V = value

    def __repr__(self) -> str:
        return f"_HashEntry({self.key!r}: {self.value!r})"


class HashTable(Generic[K, V]):
    """A generic Hash Table data structure implementing separate chaining for collision resolution.
    
    Academic Objectives (CO2):
        - Demonstrates bucket array mapping via hash functions.
        - Handles hash collisions gracefully using separate chaining (list of entries per bucket).
        - Maintains an O(1) average-case time complexity for insertion, retrieval, and deletion.
        - Implements automatic dynamic resizing and rehashing when load factor threshold is exceeded.
        - Exposes detailed collision and bucket statistics for educational evaluation.
        
    Internal Architecture:
        - Internal storage is a Python list of buckets (`list[list[_HashEntry]]`).
        - Python dictionaries are strictly NOT used for internal bucket storage.
        
    Complexity:
        - Insertion: O(1) average, O(n) worst-case (all keys collide into a single bucket)
        - Retrieval: O(1) average, O(n) worst-case
        - Deletion: O(1) average, O(n) worst-case
        - Space: O(m + n), where m is bucket capacity and n is stored items
    """

    def __init__(
        self,
        initial_capacity: int = 16,
        max_load_factor: float = 0.75,
        hash_fn: Optional[Callable[[K], int]] = None,
    ) -> None:
        """Initialize the hash table.
        
        Args:
            initial_capacity: Initial number of buckets (must be >= 1). Default: 16.
            max_load_factor: Load factor threshold triggering dynamic resize. Default: 0.75.
            hash_fn: Optional custom hash function for educational demonstrations/testing.
                     Defaults to Python's built-in `hash`.
        """
        if initial_capacity < 1:
            raise ValueError("Initial capacity must be at least 1.")
        if max_load_factor <= 0.0:
            raise ValueError("Max load factor must be strictly positive.")

        self._initial_capacity: int = initial_capacity
        self._capacity: int = initial_capacity
        self._max_load_factor: float = max_load_factor
        self._hash_fn: Optional[Callable[[K], int]] = hash_fn
        self._size: int = 0

        # Internal container: List of buckets, each bucket is a list of _HashEntry objects
        self._buckets: list[list[_HashEntry[K, V]]] = [[] for _ in range(self._capacity)]

    def _get_bucket_index(self, key: K, capacity: Optional[int] = None) -> int:
        """Compute the bucket index for a given key.
        
        Args:
            key: The lookup key.
            capacity: Optional target capacity (used during rehashing).
            
        Returns:
            An integer index in range [0, capacity - 1].
        """
        cap = capacity if capacity is not None else self._capacity
        raw_hash = self._hash_fn(key) if self._hash_fn is not None else hash(key)
        return abs(raw_hash) % cap

    def insert(self, key: K, value: V) -> bool:
        """Insert a key-value entry or update the value if the key already exists (upsert).
        
        Args:
            key: The entry key.
            value: The associated value.
            
        Returns:
            True if a new key was inserted, False if an existing key was updated.
        """
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]

        # Check for existing key in the bucket chain
        for entry in bucket:
            if entry.key == key:
                entry.value = value
                return False

        # Key is new: append entry to chain
        bucket.append(_HashEntry(key, value))
        self._size += 1

        # Check load factor threshold for resizing
        if self.load_factor() > self._max_load_factor:
            self._resize(self._capacity * 2)

        return True

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Retrieve the value associated with key, or default if missing.
        
        Args:
            key: The lookup key.
            default: Value to return if key is absent. Default: None.
            
        Returns:
            The associated value, or default.
        """
        val, _ = self.get_with_comparisons(key, default)
        return val

    def get_with_comparisons(
        self, key: K, default: Optional[V] = None
    ) -> tuple[Optional[V], int]:
        """Retrieve value along with the exact count of key comparisons performed.
        
        Educational helper used by the Data Structure Evaluation Lab to quantify
        chain inspection work.
        
        Args:
            key: The lookup key.
            default: Value to return if key is absent.
            
        Returns:
            A tuple of (value_or_default, comparisons_count).
        """
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]
        comparisons = 0

        for entry in bucket:
            comparisons += 1
            if entry.key == key:
                return entry.value, comparisons

        return default, comparisons

    def contains(self, key: K) -> bool:
        """Check whether a key exists in the hash table.
        
        Args:
            key: The key to check.
            
        Returns:
            True if key is present, False otherwise.
        """
        return self.get(key) is not None

    def update(self, key: K, value: V) -> bool:
        """Update an existing key's value without inserting if missing.
        
        Args:
            key: Existing key to update.
            value: New value to assign.
            
        Returns:
            True if key existed and was updated, False if key was missing.
        """
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]

        for entry in bucket:
            if entry.key == key:
                entry.value = value
                return True

        return False

    def delete(self, key: K) -> bool:
        """Remove a key and its associated value from the hash table.
        
        Preserves all other entries in the same bucket chain.
        
        Args:
            key: The key to delete.
            
        Returns:
            True if the key was found and deleted, False if key was missing.
        """
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]

        for i, entry in enumerate(bucket):
            if entry.key == key:
                bucket.pop(i)
                self._size -= 1
                return True

        return False

    def size(self) -> int:
        """Return the number of stored unique keys."""
        return self._size

    def capacity(self) -> int:
        """Return the current bucket capacity."""
        return self._capacity

    def is_empty(self) -> bool:
        """Return True if the hash table contains no keys."""
        return self._size == 0

    def load_factor(self) -> float:
        """Calculate and return the current load factor alpha = n / m."""
        if self._capacity == 0:
            return 0.0
        return self._size / self._capacity

    def items(self) -> list[tuple[K, V]]:
        """Return a snapshot list of all stored (key, value) pairs."""
        all_items: list[tuple[K, V]] = []
        for bucket in self._buckets:
            for entry in bucket:
                all_items.append((entry.key, entry.value))
        return all_items

    def keys(self) -> list[K]:
        """Return a snapshot list of all stored keys."""
        return [item[0] for item in self.items()]

    def values(self) -> list[V]:
        """Return a snapshot list of all stored values."""
        return [item[1] for item in self.items()]

    def clear(self) -> None:
        """Reset the hash table to its initial empty state."""
        self._capacity = self._initial_capacity
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]

    def _resize(self, new_capacity: int) -> None:
        """Resize the bucket array and rehash all existing entries.
        
        Args:
            new_capacity: New number of buckets.
        """
        if new_capacity < 1:
            return

        new_buckets: list[list[_HashEntry[K, V]]] = [[] for _ in range(new_capacity)]

        # Rehash all entries into new buckets without creating a dictionary
        for old_bucket in self._buckets:
            for entry in old_bucket:
                new_idx = self._get_bucket_index(entry.key, capacity=new_capacity)
                new_buckets[new_idx].append(entry)

        self._capacity = new_capacity
        self._buckets = new_buckets

    def collision_stats(self) -> dict[str, Any]:
        """Compute detailed collision and bucket distribution metrics.
        
        Returns:
            Dictionary with keys:
                - capacity: Current bucket count (m)
                - size: Total stored unique keys (n)
                - load_factor: n / m
                - occupied_buckets: Number of buckets with len > 0
                - empty_buckets: Number of buckets with len == 0
                - colliding_buckets: Number of buckets with len > 1
                - total_collisions: Excess entries beyond the first item in each bucket
                - max_chain_length: Maximum number of entries in any single bucket
                - bucket_sizes: List of lengths for all buckets
        """
        bucket_lengths = [len(b) for b in self._buckets]
        occupied = sum(1 for length in bucket_lengths if length > 0)
        colliding = sum(1 for length in bucket_lengths if length > 1)
        total_collisions = sum(max(0, length - 1) for length in bucket_lengths)
        max_chain = max(bucket_lengths) if bucket_lengths else 0

        return {
            "capacity": self._capacity,
            "size": self._size,
            "load_factor": round(self.load_factor(), 4),
            "max_load_factor": self._max_load_factor,
            "occupied_buckets": occupied,
            "empty_buckets": self._capacity - occupied,
            "colliding_buckets": colliding,
            "total_collisions": total_collisions,
            "max_chain_length": max_chain,
            "bucket_sizes": bucket_lengths,
        }
