"""Dataset generation utilities."""

from __future__ import annotations

import random
from typing import List


def random_array(n: int, seed: int | None = None) -> List[int]:
    """Generate a random array of size n."""
    if seed is not None:
        random.seed(seed)
    return [random.randint(0, n * 10) for _ in range(n)]


def partially_sorted_array(n: int, sorted_ratio: float = 0.5, seed: int | None = None) -> List[int]:
    """Generate a partially sorted array; sorted_ratio in [0,1]."""
    if seed is not None:
        random.seed(seed)
    k = max(1, int(n * sorted_ratio))
    sorted_part = list(range(k))
    rest = [random.randint(0, n * 10) for _ in range(n - k)]
    data = sorted_part + rest
    random.shuffle(data)
    return data


def reverse_sorted_array(n: int) -> List[int]:
    """Generate a reverse-sorted array."""
    return list(range(n, 0, -1))


def generate(dataset: str, size: int, seed: int | None = None) -> List[int]:
    """Create an array by dataset type."""
    dataset = dataset.lower()
    if dataset == "random":
        return random_array(size, seed=seed)
    if dataset in {"partial", "partially_sorted"}:
        return partially_sorted_array(size, sorted_ratio=0.5, seed=seed)
    if dataset == "reverse":
        return reverse_sorted_array(size)
    raise ValueError(f"Unknown dataset type: {dataset}")


__all__ = [
    "random_array",
    "partially_sorted_array",
    "reverse_sorted_array",
    "generate",
]
