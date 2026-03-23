"""Shared constants for the benchmark tool."""

MB = 1024 * 1024

DEFAULT_CHUNK_SIZES_MB = [4, 8, 10, 16, 32, 64]
DEFAULT_CONCURRENCIES = [2, 4, 8, 12]
DEFAULT_REPEAT = 1
DEFAULT_OUTPUT_DIR = "benchmark_results"

CSV_FIELDNAMES = [
    "chunk_size_mb",
    "concurrency",
    "avg_elapsed_s",
    "avg_throughput_mbps",
    "min_elapsed_s",
    "max_elapsed_s",
    "file_size_mb",
]
