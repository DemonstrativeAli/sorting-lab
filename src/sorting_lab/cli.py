"""Command-line interface for running batch experiments."""

import argparse
from typing import List

from sorting_lab.analysis.runner import run_experiments


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sorting Lab batch runner")
    parser.add_argument("--algos", default="quick,heap,merge", help="Comma-separated algorithm list")
    parser.add_argument("--sizes", default="1000,10000", help="Comma-separated dataset sizes")
    parser.add_argument("--dataset", default="random", choices=["random", "partial", "reverse"], help="Dataset type")
    parser.add_argument("--runs", type=int, default=3, help="Repeat count per scenario")
    parser.add_argument("--save", default="data/results/experiments.csv", help="CSV output path (empty to skip)")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    algo_list = [a.strip() for a in args.algos.split(",") if a.strip()]
    size_list = [int(x) for x in args.sizes.split(",") if x.strip()]
    save_path = args.save if args.save else None
    df = run_experiments(algo_list, size_list, args.dataset, runs=args.runs, save_path=save_path)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
