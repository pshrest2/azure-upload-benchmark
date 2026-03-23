"""Summary printing and finalization helpers."""

import os

from .plotting import generate_plots
from .results import save_csv, save_json


def print_summary(results: list[dict]) -> None:
    """Print a formatted summary table of results to stdout."""
    print(f"\n{'=' * 70}")
    print("  BENCHMARK RESULTS SUMMARY")
    print(f"{'=' * 70}")
    print(
        f"  {'Chunk (MB)':>10}  {'Concurrency':>11}  {'Time (s)':>9}  {'Throughput (MB/s)':>17}"
    )
    print(f"  {'-' * 10}  {'-' * 11}  {'-' * 9}  {'-' * 17}")

    sorted_results = sorted(
        results, key=lambda r: r["avg_throughput_mbps"], reverse=True
    )
    for r in sorted_results:
        print(
            f"  {r['chunk_size_mb']:>10}  {r['concurrency']:>11}  "
            f"{r['avg_elapsed_s']:>9.2f}  {r['avg_throughput_mbps']:>17.2f}"
        )

    best = sorted_results[0]
    worst = sorted_results[-1]

    print(
        f"\n  BEST:    chunk={best['chunk_size_mb']}MB, concurrency={best['concurrency']}"
        f"  ->  {best['avg_throughput_mbps']} MB/s ({best['avg_elapsed_s']}s)"
    )
    print(
        f"  WORST:   chunk={worst['chunk_size_mb']}MB, concurrency={worst['concurrency']}"
        f"  ->  {worst['avg_throughput_mbps']} MB/s ({worst['avg_elapsed_s']}s)"
    )
    print(f"{'=' * 70}\n")


def finalize(results: list[dict], output_dir: str) -> None:
    """Generate report and plots from whatever results we have."""
    if not results:
        print("\nNo results collected — nothing to report.")
        return

    save_csv(results, output_dir)
    save_json(results, output_dir)
    print_summary(results)
    generate_plots(results, output_dir)
    print(f"\nAll results saved to: {os.path.abspath(output_dir)}/")
