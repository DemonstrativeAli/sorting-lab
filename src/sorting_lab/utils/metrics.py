"""Timing and memory measurement helpers."""

from __future__ import annotations

import time
from dataclasses import dataclass
from statistics import mean, stdev
from typing import Any, Callable, Iterable, List

try:
    import psutil
except ImportError:  # pragma: no cover - dependency expected
    psutil = None


@dataclass
class MeasureResult:
    duration: float
    memory_mb: float | None
    output: Any


def measure(func: Callable[..., Any], *args: Any, **kwargs: Any) -> MeasureResult:
    """Measure runtime and approximate memory usage of callable."""
    process = psutil.Process() if psutil else None
    mem_before = process.memory_info().rss if process else None
    start = time.perf_counter()
    output = func(*args, **kwargs)
    duration = time.perf_counter() - start
    mem_after = process.memory_info().rss if process else None
    memory_mb = None
    if mem_before is not None and mem_after is not None:
        memory_mb = (mem_after - mem_before) / (1024 * 1024)
    return MeasureResult(duration=duration, memory_mb=memory_mb, output=output)


@dataclass
class TrialStats:
    durations: List[float]
    avg: float
    std: float
    memory_mb: float | None


def run_trials(func: Callable[..., Any], runs: int = 3, *args: Any, **kwargs: Any) -> TrialStats:
    """Execute function multiple times, returning timing stats."""
    durations: List[float] = []
    mem_samples: list[float] = []
    for _ in range(runs):
        result = measure(func, *args, **kwargs)
        durations.append(result.duration)
        if result.memory_mb is not None:
            mem_samples.append(result.memory_mb)
    avg = mean(durations) if durations else 0.0
    std_val = stdev(durations) if len(durations) > 1 else 0.0
    memory = mean(mem_samples) if mem_samples else None
    return TrialStats(durations=durations, avg=avg, std=std_val, memory_mb=memory)


__all__ = ["MeasureResult", "TrialStats", "measure", "run_trials"]
