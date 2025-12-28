"""Radix Sort implementation with optional step capture (non-negative integers)."""

from __future__ import annotations

from typing import List, Sequence


def sort(items: Sequence[int], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[int], list[list[int]]]:
    """Sort items using LSD radix sort (base 10)."""
    arr: List[int] = list(items)
    steps: list[list[int]] = []
    if not arr:
        return arr, steps
    if any(x < 0 for x in arr):
        raise ValueError("Radix sort only supports non-negative integers.")

    exp = 1
    max_val = max(arr)

    def record():
        if record_steps and len(steps) < step_limit:
            steps.append(list(arr))

    while max_val // exp > 0:
        buckets = [list() for _ in range(10)]
        for num in arr:
            index = (num // exp) % 10
            buckets[index].append(num)
        pos = 0
        for bucket in buckets:
            for num in bucket:
                arr[pos] = num
                pos += 1
                record()
        exp *= 10
    return arr, steps


__all__ = ["sort"]
