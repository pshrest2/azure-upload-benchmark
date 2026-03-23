"""Benchmark orchestration — run the full grid of configurations."""

import os
from itertools import product

from .api import delete_uploaded_file, get_sas_url_from_api
from .constants import MB
from .results import append_csv, init_csv, load_csv
from .upload import upload_blob


def run_benchmark(
    *,
    sas_url: str | None,
    api_url: str | None,
    delete_url: str | None,
    token: str | None,
    file_path: str,
    chunk_sizes_mb: list[int],
    concurrencies: list[int],
    repeat: int,
    output_dir: str,
) -> list[dict]:
    """Run the full benchmark grid and return a list of result dicts.

    Results are saved incrementally to CSV after each config so partial
    data survives crashes or token expiration.  Configs that already
    exist in the CSV (from a previous interrupted run) are skipped.
    """
    csv_path = init_csv(output_dir)
    existing = load_csv(csv_path)
    completed = {(r["chunk_size_mb"], r["concurrency"]) for r in existing}
    results = list(existing)

    grid = list(product(chunk_sizes_mb, concurrencies))
    remaining = [(c, n) for c, n in grid if (c, n) not in completed]
    total = len(grid)
    skipped = total - len(remaining)

    filename = os.path.basename(file_path)
    file_size_mb = os.path.getsize(file_path) / MB

    print(f"\n{'=' * 70}")
    print("  Upload Benchmark")
    print(f"  File: {filename} ({file_size_mb:.1f} MB)")
    print(f"  Chunk sizes (MB): {chunk_sizes_mb}")
    print(f"  Concurrency levels: {concurrencies}")
    print(f"  Repeats per config: {repeat}")
    print(f"  Total configs: {total}  (skipping {skipped} already completed)")
    print(f"{'=' * 70}\n")

    run = skipped
    for chunk_mb, conc in remaining:
        chunk_bytes = chunk_mb * MB
        timings: list[dict] = []

        for r in range(repeat):
            run += 1
            using_api = not sas_url
            url = sas_url
            try:
                if using_api:
                    url = get_sas_url_from_api(api_url, token, filename)
            except Exception as e:
                print(
                    f"  [{run:3d}/{total}] chunk={chunk_mb:3d}MB  concurrency={conc:2d}  "
                    f"repeat={r + 1}/{repeat} ... FAILED to get SAS URL: {e}",
                    flush=True,
                )
                print("\n  ⚠  Stopping benchmark (API auth likely expired).")
                return results

            print(
                f"  [{run:3d}/{total}] chunk={chunk_mb:3d}MB  concurrency={conc:2d}  "
                f"repeat={r + 1}/{repeat} ... ",
                end="",
                flush=True,
            )

            try:
                result = upload_blob(url, file_path, chunk_bytes, conc)
            except Exception as e:
                print(f"UPLOAD FAILED: {e}", flush=True)
                print(
                    "\n  ⚠  Stopping benchmark (upload error — token may have expired)."
                )
                return results

            timings.append(result)
            print(
                f"{result['elapsed_s']:.2f}s  ({result['throughput_mbps']:.1f} MB/s)",
                end="",
            )

            if using_api and delete_url:
                try:
                    delete_uploaded_file(delete_url, token, filename)
                    print("  [deleted]", flush=True)
                except Exception as e:
                    print(f"  [delete failed: {e}]", flush=True)
            else:
                print(flush=True)

        avg_elapsed = sum(t["elapsed_s"] for t in timings) / len(timings)
        avg_throughput = sum(t["throughput_mbps"] for t in timings) / len(timings)
        row = {
            "chunk_size_mb": chunk_mb,
            "concurrency": conc,
            "avg_elapsed_s": round(avg_elapsed, 3),
            "avg_throughput_mbps": round(avg_throughput, 2),
            "min_elapsed_s": round(min(t["elapsed_s"] for t in timings), 3),
            "max_elapsed_s": round(max(t["elapsed_s"] for t in timings), 3),
            "file_size_mb": round(file_size_mb, 2),
        }
        results.append(row)
        append_csv(csv_path, row)

    return results
