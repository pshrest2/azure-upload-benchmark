"""Tests for constants."""

from azure_upload_benchmark.constants import CSV_FIELDNAMES, MB


def test_mb_constant():
    assert MB == 1024 * 1024


def test_csv_fieldnames_are_strings():
    assert all(isinstance(f, str) for f in CSV_FIELDNAMES)
    assert "chunk_size_mb" in CSV_FIELDNAMES
    assert "throughput" not in CSV_FIELDNAMES  # it's avg_throughput_mbps
    assert "avg_throughput_mbps" in CSV_FIELDNAMES
