from sorting_lab.utils import data_gen, metrics


def test_random_array_bounds_and_size():
    n = 100
    arr = data_gen.random_array(n, seed=123)
    assert len(arr) == n
    assert all(0 <= x <= n * 10 for x in arr)


def test_reverse_sorted_array_order():
    assert data_gen.reverse_sorted_array(5) == [5, 4, 3, 2, 1]


def test_partially_sorted_array_is_not_fully_sorted():
    arr = data_gen.partially_sorted_array(50, sorted_ratio=0.7, seed=42)
    assert arr
    assert arr != sorted(arr)


def test_generate_rejects_unknown_dataset():
    try:
        data_gen.generate("unknown", 10)
    except ValueError as exc:
        assert "Unknown dataset type" in str(exc)
    else:  # pragma: no cover - guard against silent failures
        raise AssertionError("Expected ValueError for unknown dataset type")


def test_metrics_measure_and_trials():
    result = metrics.measure(lambda: sum(range(1000)))
    assert result.duration >= 0
    assert result.output == sum(range(1000))
    if result.memory_mb is not None:
        assert result.memory_mb >= 0
    if result.memory_peak_mb is not None:
        assert result.memory_peak_mb >= 0

    stats = metrics.run_trials(lambda: sum(range(1000)), runs=2)
    assert len(stats.durations) == 2
    assert stats.avg >= 0
