"""Quick Sort implementation with optional step capture."""

from __future__ import annotations

from typing import List, MutableSequence, Sequence, TypeVar

T = TypeVar("T")


def _record_state(states: list[list[T]], arr: MutableSequence[T], record_steps: bool, step_limit: int) -> None:
    """Optionally append a copy of the current array state."""
    if record_steps and len(states) < step_limit:
        states.append(list(arr))


def sort(items: Sequence[T], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[T], list[list[T]]]:
    """Sort items using quick sort.

    Returns a tuple of (sorted_list, steps). Steps contains snapshots of array states if requested.
    """
    arr: List[T] = list(items)
    steps: list[list[T]] = []

    def partition(lo: int, hi: int) -> int:
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                _record_state(steps, arr, record_steps, step_limit)
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        _record_state(steps, arr, record_steps, step_limit)
        return i

    def quicksort(lo: int, hi: int) -> None:
        if lo < hi:
            p = partition(lo, hi)
            quicksort(lo, p - 1)
            quicksort(p + 1, hi)

    quicksort(0, len(arr) - 1)
    return arr, steps


__all__ = ["sort"]
