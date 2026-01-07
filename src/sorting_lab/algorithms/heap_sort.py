from __future__ import annotations

from typing import List, MutableSequence, Sequence, TypeVar

T = TypeVar("T")


def _record_state(states: list[list[T]], arr: MutableSequence[T], record_steps: bool, step_limit: int) -> None:
    if record_steps and len(states) < step_limit:
        states.append(list(arr))


def sort(items: Sequence[T], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[T], list[list[T]]]:
    """Sort items using heap sort and optionally capture states."""
    arr: List[T] = list(items)
    steps: list[list[T]] = []
    n = len(arr)

    def heapify(n: int, i: int) -> None:
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            _record_state(steps, arr, record_steps, step_limit)
            heapify(n, largest)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        _record_state(steps, arr, record_steps, step_limit)
        heapify(i, 0)

    return arr, steps


__all__ = ["sort"]
