"""Timing and memory measurement helpers."""

from __future__ import annotations

import threading
import time
import tracemalloc
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
    memory_peak_mb: float | None
    output: Any


def measure(func: Callable[..., Any], *args: Any, **kwargs: Any) -> MeasureResult:
    """Measure runtime, Python allocation peak (extra) and process RSS peak of callable."""
    process = psutil.Process() if psutil else None
    mem_before = process.memory_info().rss if process else None
    peak_rss = mem_before
    stop_event = threading.Event()
    peak_lock = threading.Lock()
    tracing_started = False
    py_current_before = None

    if tracemalloc.is_tracing():
        py_current_before, _ = tracemalloc.get_traced_memory()
        tracemalloc.reset_peak()
    else:
        tracemalloc.start()
        tracing_started = True
        py_current_before, _ = tracemalloc.get_traced_memory()

    def sampler() -> None:
        nonlocal peak_rss
        while not stop_event.is_set():
            try:
                rss = process.memory_info().rss if process else None
            except Exception:
                break
            if rss is not None:
                with peak_lock:
                    if peak_rss is None or rss > peak_rss:
                        peak_rss = rss
            stop_event.wait(0.01)

    thread = None
    if process is not None:
        thread = threading.Thread(target=sampler, daemon=True)
        thread.start()
    start = time.perf_counter()
    output = func(*args, **kwargs)
    duration = time.perf_counter() - start
    mem_after = process.memory_info().rss if process else None
    if process is not None:
        stop_event.set()
        if thread is not None:
            thread.join(timeout=1.0)
    if mem_after is not None:
        with peak_lock:
            if peak_rss is None or mem_after > peak_rss:
                peak_rss = mem_after
    _, py_peak = tracemalloc.get_traced_memory()
    if tracing_started:
        tracemalloc.stop()
    memory_mb = None
    memory_peak_mb = None
    if py_current_before is not None and py_peak is not None:
        memory_mb = max(0.0, (py_peak - py_current_before) / (1024 * 1024))
    if peak_rss is not None:
        memory_peak_mb = peak_rss / (1024 * 1024)
    return MeasureResult(duration=duration, memory_mb=memory_mb, memory_peak_mb=memory_peak_mb, output=output)


@dataclass
class TrialStats:
    durations: List[float]
    avg: float
    std: float
    memory_mb: float | None
    memory_peak_mb: float | None


def run_trials(func: Callable[..., Any], runs: int = 3, *args: Any, **kwargs: Any) -> TrialStats:
    """Execute function multiple times, returning timing stats."""
    durations: List[float] = []
    mem_samples: list[float] = []
    mem_peak_samples: list[float] = []
    for _ in range(runs):
        result = measure(func, *args, **kwargs)
        durations.append(result.duration)
        if result.memory_mb is not None:
            mem_samples.append(result.memory_mb)
        if result.memory_peak_mb is not None:
            mem_peak_samples.append(result.memory_peak_mb)
    avg = mean(durations) if durations else 0.0
    std_val = stdev(durations) if len(durations) > 1 else 0.0
    memory = mean(mem_samples) if mem_samples else None
    memory_peak = mean(mem_peak_samples) if mem_peak_samples else None
    return TrialStats(durations=durations, avg=avg, std=std_val, memory_mb=memory, memory_peak_mb=memory_peak)


__all__ = ["MeasureResult", "TrialStats", "measure", "run_trials"]
