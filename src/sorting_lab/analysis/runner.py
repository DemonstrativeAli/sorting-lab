"""Experiment runner for batch benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from sorting_lab import algorithms
from sorting_lab.utils import data_gen, metrics


def run_experiments(
    algorithms_keys: Iterable[str],
    sizes: Iterable[int],
    dataset: str,
    runs: int = 3,
    save_path: str | None = "data/results/experiments.csv",
) -> pd.DataFrame:
    """Run benchmarks across algorithms and sizes, optionally persisting results."""
    records: list[dict[str, object]] = []
    for algo_key in algorithms_keys:
        for size in sizes:
            base_data = data_gen.generate(dataset, size)
            trial_stats = metrics.run_trials(lambda: algorithms.run_algorithm(algo_key, base_data)[0], runs=runs)
            records.append(
                {
                    "algorithm": algo_key,
                    "dataset": dataset,
                    "size": size,
                    "runs": runs,
                    "avg_time_s": trial_stats.avg,
                    "std_time_s": trial_stats.std,
                    "memory_mb": trial_stats.memory_mb,
                }
            )

    df = pd.DataFrame.from_records(records)
    if save_path:
        out_path = Path(save_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
    return df
