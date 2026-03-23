# azure-upload-benchmark

Benchmark Azure Blob Storage upload performance with varying chunk sizes and concurrency levels.

Runs a configurable grid of `(chunk_size, concurrency)` combinations, records timing data, and produces CSV/JSON results plus optional heatmap and line plots to help you find optimal upload settings.

## Installation

```bash
uv add azure-upload-benchmark
```

To enable plot generation (heatmaps, line plots, 3-D surface):

```bash
uv add "azure-upload-benchmark[plots]"
```

### From source

```bash
git clone https://github.com/pshrest2/azure-upload-benchmark.git
cd azure-upload-benchmark
uv sync --extra dev
```

## Quick Start

### Using a pre-signed SAS URL

```bash
azure-upload-benchmark --sas-url "https://myaccount.blob.core.windows.net/..." --file path/to/data.bin
```

### Using an upload API

If you have an API that generates SAS URLs on demand:

```bash
azure-upload-benchmark \
    --api-url "https://example.com/api/uploads/url" \
    --token "your-bearer-token" \
    --file path/to/data.bin
```

The `--api-url` endpoint must accept a POST with `{"filename": "..."}` and return `{"url": "<sas_url>"}`.

### Generate a synthetic test file

```bash
azure-upload-benchmark --sas-url "https://..." --generate-file 500
```

### Custom benchmark grid

```bash
azure-upload-benchmark \
    --sas-url "https://..." \
    --file test.bin \
    --chunk-sizes 4 8 16 32 \
    --concurrencies 1 2 4 8 16 \
    --repeat 3
```

### Cleanup after uploads

If your API supports deleting uploaded files, pass `--delete-url` to remove each blob after benchmarking:

```bash
azure-upload-benchmark \
    --api-url "https://example.com/api/uploads/url" \
    --delete-url "https://example.com/api/uploads" \
    --token "your-bearer-token" \
    --file test.bin
```

### Regenerate report from existing data

```bash
azure-upload-benchmark --report --output-dir benchmark_results
```

## CLI Options

| Option                      | Description                                                                      |
| --------------------------- | -------------------------------------------------------------------------------- |
| `--sas-url`                 | Pre-signed Azure Blob SAS URL with write permission                              |
| `--api-url`                 | POST endpoint returning `{"url": "<sas_url>"}`                                   |
| `--delete-url`              | DELETE endpoint for cleanup after each upload                                    |
| `--token`                   | JWT Bearer token for the API endpoints (only Bearer auth is currently supported) |
| `--file`                    | Path to the file to upload                                                       |
| `--generate-file SIZE_MB`   | Generate a synthetic test file of the given size                                 |
| `--chunk-sizes MB [MB ...]` | Chunk sizes in MB (default: 4 8 10 16 32 64)                                     |
| `--concurrencies N [N ...]` | Concurrency levels (default: 2 4 8 12)                                           |
| `--repeat N`                | Repetitions per config for averaging (default: 1)                                |
| `--output-dir DIR`          | Directory for results and plots (default: benchmark_results)                     |
| `--report`                  | Regenerate report/plots from existing CSV                                        |

## Output

Results are saved to the output directory:

- `benchmark_results.csv` — tabular results
- `benchmark_results.json` — JSON results
- `throughput_heatmap.png` — throughput heatmap (requires `plots` extra)
- `upload_time_heatmap.png` — upload time heatmap
- `throughput_line_plots.png` — line plots by chunk size and concurrency
- `throughput_surface_3d.png` — 3-D surface plot

## Programmatic Usage

```python
from azure_upload_benchmark.upload import upload_blob
from azure_upload_benchmark.results import load_csv, save_csv
from azure_upload_benchmark.plotting import generate_plots

# Single upload
result = upload_blob(
    sas_url="https://...",
    file_path="data.bin",
    chunk_size=8 * 1024 * 1024,
    concurrency=4,
)
print(result)
# {'file_size_mb': 100.0, 'chunk_size_mb': 8.0, 'concurrency': 4, 'elapsed_s': 12.5, 'throughput_mbps': 8.0}

# Load existing results and regenerate plots
results = load_csv("benchmark_results/benchmark_results.csv")
generate_plots(results, "benchmark_results")
```

## Package Structure

```
src/azure_upload_benchmark/
├── __init__.py       # Package version
├── api.py            # HTTP helpers for SAS URL generation and cleanup
├── benchmark.py      # Benchmark orchestration (grid runner)
├── cli.py            # Command-line interface
├── constants.py      # Shared constants (defaults, field names)
├── plotting.py       # Heatmap, line plot, and 3-D surface generation
├── reporting.py      # Summary printing and finalization
├── results.py        # CSV / JSON persistence
└── utils.py          # Test-file generation utilities
```

## Running Tests

```bash
uv sync --extra dev
uv run pytest tests/ -v
```

## License

MIT
