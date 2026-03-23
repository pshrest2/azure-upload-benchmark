"""Command-line interface for the Azure upload benchmark."""

import argparse
import os
import signal
import sys

from .benchmark import run_benchmark
from .constants import (
    DEFAULT_CHUNK_SIZES_MB,
    DEFAULT_CONCURRENCIES,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPEAT,
)
from .reporting import finalize
from .results import load_csv
from .utils import generate_test_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="azure-upload-benchmark",
        description="Benchmark Azure Blob Storage uploads with varying chunk sizes and concurrency.",
    )

    sas = p.add_argument_group("SAS URL source (pick one)")
    sas.add_argument(
        "--sas-url",
        help="Pre-signed Azure Blob SAS URL with write permission (skips API generate/delete)",
    )
    sas.add_argument(
        "--api-url",
        help="Upload API endpoint that returns a SAS URL (POST, expects JSON {filename})",
    )
    sas.add_argument(
        "--delete-url",
        help="Delete API endpoint for cleanup after each upload (DELETE, filename as query param)",
    )
    sas.add_argument(
        "--token",
        help="Bearer token for the upload/delete API (without 'Bearer ' prefix)",
    )

    f = p.add_argument_group("File")
    f.add_argument("--file", help="Path to the file to upload")
    f.add_argument(
        "--generate-file",
        type=int,
        metavar="SIZE_MB",
        help="Generate a synthetic test file of the given size in MB",
    )

    g = p.add_argument_group("Benchmark grid")
    g.add_argument(
        "--chunk-sizes",
        nargs="+",
        type=int,
        default=DEFAULT_CHUNK_SIZES_MB,
        metavar="MB",
        help=f"Chunk sizes in MB (default: {DEFAULT_CHUNK_SIZES_MB})",
    )
    g.add_argument(
        "--concurrencies",
        nargs="+",
        type=int,
        default=DEFAULT_CONCURRENCIES,
        metavar="N",
        help=f"Concurrency levels (default: {DEFAULT_CONCURRENCIES})",
    )
    g.add_argument(
        "--repeat",
        type=int,
        default=DEFAULT_REPEAT,
        help=f"Repetitions per config for averaging (default: {DEFAULT_REPEAT})",
    )

    o = p.add_argument_group("Output")
    o.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save results and plots (default: {DEFAULT_OUTPUT_DIR})",
    )
    o.add_argument(
        "--report",
        action="store_true",
        help="Skip benchmarking — regenerate report and plots from existing CSV",
    )

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.report:
        os.makedirs(args.output_dir, exist_ok=True)
        csv_path = os.path.join(args.output_dir, "benchmark_results.csv")
        results = load_csv(csv_path)
        if not results:
            sys.exit(f"Error: No data found in {csv_path}")
        print(f"Loaded {len(results)} results from {csv_path}")
        finalize(results, args.output_dir)
        return

    if not args.sas_url and not args.token:
        sys.exit(
            "Error: Provide --token (with --api-url) for API auth, or --sas-url for direct upload"
        )
    if not args.sas_url and not args.api_url:
        sys.exit(
            "Error: Provide --api-url when using --token, or use --sas-url directly"
        )
    if not args.file and not args.generate_file:
        sys.exit("Error: Provide either --file or --generate-file")

    if args.generate_file:
        file_path = generate_test_file(args.generate_file)
    else:
        file_path = args.file
        if not os.path.isfile(file_path):
            sys.exit(f"Error: File not found: {file_path}")

    os.makedirs(args.output_dir, exist_ok=True)

    results_ref: list = []

    def _on_interrupt(signum, frame):
        print("\n\n  Interrupted! Generating report from collected data...\n")
        finalize(results_ref, args.output_dir)
        sys.exit(1)

    signal.signal(signal.SIGINT, _on_interrupt)
    signal.signal(signal.SIGTERM, _on_interrupt)

    try:
        results = run_benchmark(
            sas_url=args.sas_url,
            api_url=args.api_url,
            delete_url=args.delete_url,
            token=args.token,
            file_path=file_path,
            chunk_sizes_mb=args.chunk_sizes,
            concurrencies=args.concurrencies,
            repeat=args.repeat,
            output_dir=args.output_dir,
        )
        results_ref[:] = results
    except Exception as e:
        print(f"\n  Benchmark stopped: {e}")
        csv_path = os.path.join(args.output_dir, "benchmark_results.csv")
        results = load_csv(csv_path)
        results_ref[:] = results

    finalize(results_ref, args.output_dir)
