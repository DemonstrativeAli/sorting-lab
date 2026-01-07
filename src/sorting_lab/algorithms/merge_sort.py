from __future__ import annotations

from typing import List, MutableSequence, Sequence, TypeVar

T = TypeVar("T")


def _record_state(states: list[list[T]], arr: MutableSequence[T], record_steps: bool, step_limit: int) -> None:
    if record_steps and len(states) < step_limit:
        states.append(list(arr))


def sort(items: Sequence[T], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[T], list[list[T]]]:
    """Sort items using merge sort and optionally capture states."""
    arr: List[T] = list(items)
    steps: list[list[T]] = []

    def merge_sort(sub: List[T], left: int, right: int) -> None:
        if left >= right:
            return
        mid = (left + right) // 2
        merge_sort(sub, left, mid)
        merge_sort(sub, mid + 1, right)
        merge(sub, left, mid, right)

    def merge(sub: List[T], left: int, mid: int, right: int) -> None:
        left_part = sub[left : mid + 1]
        right_part = sub[mid + 1 : right + 1]
        i = j = 0
        k = left
        while i < len(left_part) and j < len(right_part):
            if left_part[i] <= right_part[j]:
                sub[k] = left_part[i]
                i += 1
            else:
                sub[k] = right_part[j]
                j += 1
            k += 1
            _record_state(steps, arr, record_steps, step_limit)
        while i < len(left_part):
            sub[k] = left_part[i]
            i += 1
            k += 1
            _record_state(steps, arr, record_steps, step_limit)
        while j < len(right_part):
            sub[k] = right_part[j]
            j += 1
            k += 1
            _record_state(steps, arr, record_steps, step_limit)

    merge_sort(arr, 0, len(arr) - 1)
    return arr, steps


__all__ = ["sort"]
