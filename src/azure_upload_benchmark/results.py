"""CSV / JSON persistence for benchmark results."""

import csv
import json
import os

from .constants import CSV_FIELDNAMES


def init_csv(output_dir: str) -> str:
    """Create the CSV file with headers if it doesn't already exist."""
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
    return csv_path


def append_csv(csv_path: str, row: dict):
    """Append a single result row to the CSV file."""
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writerow(row)


def load_csv(csv_path: str) -> list[dict]:
    """Load existing results from a CSV file."""
    results: list[dict] = []
    if not os.path.exists(csv_path):
        return results
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(
                {
                    "chunk_size_mb": int(float(row["chunk_size_mb"])),
                    "concurrency": int(row["concurrency"]),
                    "avg_elapsed_s": float(row["avg_elapsed_s"]),
                    "avg_throughput_mbps": float(row["avg_throughput_mbps"]),
                    "min_elapsed_s": float(row["min_elapsed_s"]),
                    "max_elapsed_s": float(row["max_elapsed_s"]),
                    "file_size_mb": float(row["file_size_mb"]),
                }
            )
    return results


def save_csv(results: list[dict], output_dir: str) -> str:
    """Save results to a CSV file (full rewrite)."""
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV saved to: {csv_path}")
    return csv_path


def save_json(results: list[dict], output_dir: str) -> str:
    """Save results to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"JSON saved to: {json_path}")
    return json_path
