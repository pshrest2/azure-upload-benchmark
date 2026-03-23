"""Tests for the reporting module."""

from azure_upload_benchmark.reporting import print_summary

SAMPLE_RESULTS = [
    {
        "chunk_size_mb": 4,
        "concurrency": 8,
        "avg_elapsed_s": 11.01,
        "avg_throughput_mbps": 15.38,
        "min_elapsed_s": 11.01,
        "max_elapsed_s": 11.01,
        "file_size_mb": 169.33,
    },
    {
        "chunk_size_mb": 10,
        "concurrency": 2,
        "avg_elapsed_s": 61.265,
        "avg_throughput_mbps": 2.76,
        "min_elapsed_s": 61.265,
        "max_elapsed_s": 61.265,
        "file_size_mb": 169.33,
    },
]


class TestPrintSummary:
    def test_prints_without_error(self, capsys):
        print_summary(SAMPLE_RESULTS)
        captured = capsys.readouterr()
        assert "BEST" in captured.out
        assert "WORST" in captured.out
        assert "15.38" in captured.out

    def test_single_result(self, capsys):
        print_summary([SAMPLE_RESULTS[0]])
        captured = capsys.readouterr()
        assert "BEST" in captured.out
