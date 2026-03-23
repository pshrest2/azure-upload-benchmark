"""Tests for the CLI argument parser."""

from azure_upload_benchmark.cli import parse_args
from azure_upload_benchmark.constants import (
    DEFAULT_CHUNK_SIZES_MB,
    DEFAULT_CONCURRENCIES,
)


class TestParseArgs:
    def test_sas_url_and_file(self):
        args = parse_args(["--sas-url", "https://example.com", "--file", "test.bin"])
        assert args.sas_url == "https://example.com"
        assert args.file == "test.bin"

    def test_api_url_and_token(self):
        args = parse_args(
            [
                "--api-url",
                "https://api.example.com/upload",
                "--token",
                "secret",
                "--file",
                "test.bin",
            ]
        )
        assert args.api_url == "https://api.example.com/upload"
        assert args.token == "secret"

    def test_defaults(self):
        args = parse_args(["--sas-url", "https://x", "--file", "f.bin"])
        assert args.chunk_sizes == DEFAULT_CHUNK_SIZES_MB
        assert args.concurrencies == DEFAULT_CONCURRENCIES
        assert args.repeat == 1
        assert args.output_dir == "benchmark_results"
        assert args.report is False

    def test_custom_grid(self):
        args = parse_args(
            [
                "--sas-url",
                "https://x",
                "--file",
                "f.bin",
                "--chunk-sizes",
                "2",
                "4",
                "--concurrencies",
                "1",
                "8",
                "--repeat",
                "3",
            ]
        )
        assert args.chunk_sizes == [2, 4]
        assert args.concurrencies == [1, 8]
        assert args.repeat == 3

    def test_report_mode(self):
        args = parse_args(["--report", "--output-dir", "my_results"])
        assert args.report is True
        assert args.output_dir == "my_results"

    def test_generate_file(self):
        args = parse_args(["--sas-url", "https://x", "--generate-file", "500"])
        assert args.generate_file == 500
