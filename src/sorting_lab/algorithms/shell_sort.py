"""Shell Sort implementation with optional step capture."""

from __future__ import annotations

from typing import List, MutableSequence, Sequence, TypeVar

T = TypeVar("T")


def _record_state(states: list[list[T]], arr: MutableSequence[T], record_steps: bool, step_limit: int) -> None:
    if record_steps and len(states) < step_limit:
        states.append(list(arr))


def sort(items: Sequence[T], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[T], list[list[T]]]:
    """Sort items using shell sort and optionally capture states."""
    arr: List[T] = list(items)
    steps: list[list[T]] = []
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
                _record_state(steps, arr, record_steps, step_limit)
            arr[j] = temp
            _record_state(steps, arr, record_steps, step_limit)
        gap //= 2
    return arr, steps


__all__ = ["sort"]
