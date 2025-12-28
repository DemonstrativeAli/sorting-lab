"""Visualization helpers (matplotlib/plotly placeholders)."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt


def plot_runtime(sizes: list[int], runtimes: list[float], title: str = "Runtime vs Size") -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(sizes, runtimes, marker="o")
    plt.xlabel("N")
    plt.ylabel("Time (s)")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
