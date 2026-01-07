import pytest

from sorting_lab import algorithms


@pytest.mark.parametrize("algo_key", algorithms.keys())
@pytest.mark.parametrize(
    "data",
    [
        [],
        [1],
        [3, 1, 2, 5, 4, 4, 0],
        [10, 9, 8, 7, 6, 5, 4],
    ],
)
def test_algorithms_sort_correctly(algo_key, data):
    expected = sorted(data)
    result, steps = algorithms.run_algorithm(algo_key, data, record_steps=True, step_limit=10)
    assert result == expected
    assert len(steps) <= 10


def test_radix_sort_rejects_negative_values():
    with pytest.raises(ValueError):
        algorithms.run_algorithm("radix", [3, -1, 2])
