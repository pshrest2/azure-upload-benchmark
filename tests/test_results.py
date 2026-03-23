"""Tests for the results (CSV/JSON) module."""

import json
import os

import pytest

from azure_upload_benchmark.results import (
    append_csv,
    init_csv,
    load_csv,
    save_csv,
    save_json,
)

SAMPLE_ROWS = [
    {
        "chunk_size_mb": 4,
        "concurrency": 2,
        "avg_elapsed_s": 10.5,
        "avg_throughput_mbps": 9.52,
        "min_elapsed_s": 10.0,
        "max_elapsed_s": 11.0,
        "file_size_mb": 100.0,
    },
    {
        "chunk_size_mb": 8,
        "concurrency": 4,
        "avg_elapsed_s": 6.2,
        "avg_throughput_mbps": 16.13,
        "min_elapsed_s": 6.0,
        "max_elapsed_s": 6.4,
        "file_size_mb": 100.0,
    },
]


class TestInitCsv:
    def test_creates_file_with_headers(self, tmp_path):
        csv_path = init_csv(str(tmp_path))
        assert os.path.exists(csv_path)
        with open(csv_path) as f:
            header = f.readline().strip()
        assert "chunk_size_mb" in header
        assert "concurrency" in header

    def test_does_not_overwrite_existing(self, tmp_path):
        csv_path = init_csv(str(tmp_path))
        append_csv(csv_path, SAMPLE_ROWS[0])
        # Call again — should not overwrite
        csv_path2 = init_csv(str(tmp_path))
        assert csv_path == csv_path2
        loaded = load_csv(csv_path)
        assert len(loaded) == 1

    def test_creates_nested_directory(self, tmp_path):
        nested = str(tmp_path / "a" / "b" / "c")
        csv_path = init_csv(nested)
        assert os.path.exists(csv_path)


class TestAppendAndLoadCsv:
    def test_append_and_load_roundtrip(self, tmp_path):
        csv_path = init_csv(str(tmp_path))
        for row in SAMPLE_ROWS:
            append_csv(csv_path, row)
        loaded = load_csv(csv_path)
        assert len(loaded) == 2
        assert loaded[0]["chunk_size_mb"] == 4
        assert loaded[1]["concurrency"] == 4
        assert loaded[1]["avg_throughput_mbps"] == pytest.approx(16.13)

    def test_load_nonexistent_returns_empty(self):
        assert load_csv("/nonexistent/path.csv") == []


class TestSaveCsv:
    def test_full_rewrite(self, tmp_path):
        out = str(tmp_path)
        save_csv(SAMPLE_ROWS, out)
        loaded = load_csv(os.path.join(out, "benchmark_results.csv"))
        assert len(loaded) == 2

    def test_creates_directory(self, tmp_path):
        out = str(tmp_path / "new_dir")
        save_csv(SAMPLE_ROWS, out)
        assert os.path.exists(os.path.join(out, "benchmark_results.csv"))


class TestSaveJson:
    def test_json_roundtrip(self, tmp_path):
        out = str(tmp_path)
        save_json(SAMPLE_ROWS, out)
        json_path = os.path.join(out, "benchmark_results.json")
        with open(json_path) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["chunk_size_mb"] == 4
