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

    def median_of_three(lo: int, mid: int, hi: int) -> int:
        a, b, c = arr[lo], arr[mid], arr[hi]
        if a <= b:
            if b <= c:
                return mid
            return hi if a <= c else lo
        if a <= c:
            return lo
        return hi if b <= c else mid

    def partition(lo: int, hi: int) -> int:
        mid = (lo + hi) // 2
        pivot_index = median_of_three(lo, mid, hi)
        if pivot_index != hi:
            arr[pivot_index], arr[hi] = arr[hi], arr[pivot_index]
            _record_state(steps, arr, record_steps, step_limit)
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

    # Iterative quicksort to avoid deep recursion (QThread stack overflow).
    stack: list[tuple[int, int]] = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            p = partition(lo, hi)
            # Recurse on smaller partition, loop on larger to keep stack shallow.
            if p - lo < hi - p:
                stack.append((p + 1, hi))
                hi = p - 1
            else:
                stack.append((lo, p - 1))
                lo = p + 1
    return arr, steps


__all__ = ["sort"]
