"""Tests for utility functions."""

import os

from azure_upload_benchmark.constants import MB
from azure_upload_benchmark.utils import generate_test_file


class TestGenerateTestFile:
    def test_creates_file_of_correct_size(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
        path = generate_test_file(1)
        assert os.path.exists(path)
        assert os.path.getsize(path) == 1 * MB

    def test_reuses_existing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
        path1 = generate_test_file(1)
        mtime1 = os.path.getmtime(path1)
        path2 = generate_test_file(1)
        mtime2 = os.path.getmtime(path2)
        assert path1 == path2
        assert mtime1 == mtime2
