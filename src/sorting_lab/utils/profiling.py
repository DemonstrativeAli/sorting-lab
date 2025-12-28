"""Profiling utilities (cProfile / memory-profiler placeholders)."""

from __future__ import annotations

import cProfile
import pstats
from io import StringIO
from typing import Callable, Any


def profile_func(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """Run cProfile on a function call and return stats as string."""
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args, **kwargs)
    profiler.disable()
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats()
    return stream.getvalue()
