"""Algorithm registry and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .heap_sort import sort as heap_sort
from .merge_sort import sort as merge_sort
from .quick_sort import sort as quick_sort
from .radix_sort import sort as radix_sort
from .shell_sort import sort as shell_sort


AlgorithmFunc = Callable[[Sequence[Any]], tuple[list[Any], list[list[Any]]]]


@dataclass(frozen=True)
class Algorithm:
    key: str
    name: str
    func: Callable[..., tuple[list[Any], list[list[Any]]]]


ALGORITHMS: dict[str, Algorithm] = {
    "quick": Algorithm("quick", "Quick Sort", quick_sort),
    "heap": Algorithm("heap", "Heap Sort", heap_sort),
    "shell": Algorithm("shell", "Shell Sort", shell_sort),
    "merge": Algorithm("merge", "Merge Sort", merge_sort),
    "radix": Algorithm("radix", "Radix Sort", radix_sort),
}


def run_algorithm(key: str, data: Sequence[Any], *, record_steps: bool = False, step_limit: int = 400) -> tuple[list[Any], list[list[Any]]]:
    """Run an algorithm by key, returning sorted output and optional steps."""
    algo = ALGORITHMS.get(key)
    if not algo:
        raise ValueError(f"Unknown algorithm key: {key}")
    return algo.func(data, record_steps=record_steps, step_limit=step_limit)


def available_algorithms() -> list[Algorithm]:
    return list(ALGORITHMS.values())


def keys() -> list[str]:
    return list(ALGORITHMS.keys())


__all__ = ["Algorithm", "available_algorithms", "run_algorithm", "keys"]
