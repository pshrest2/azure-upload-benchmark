"""Tests for the API module."""

import requests

from azure_upload_benchmark.api import (
    _api_headers,
    delete_uploaded_file,
    get_sas_url_from_api,
)


class TestApiHeaders:
    def test_with_token(self):
        h = _api_headers("my-token")
        assert h["Authorization"] == "Bearer my-token"
        assert h["Content-Type"] == "application/json"

    def test_without_token(self):
        h = _api_headers("")
        assert "Authorization" not in h


class TestGetSasUrl:
    def test_returns_url(self, monkeypatch):
        class MockResp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"url": "https://blob.example.com/sas?token=abc"}

        def mock_post(url, json, headers, timeout):
            assert json == {"filename": "test.bin"}
            return MockResp()

        monkeypatch.setattr(requests, "post", mock_post)
        url = get_sas_url_from_api("https://api.example.com", "tok", "test.bin")
        assert url == "https://blob.example.com/sas?token=abc"


class TestDeleteUploadedFile:
    def test_success(self, monkeypatch):
        class MockResp:
            status_code = 200

            def raise_for_status(self):
                pass

        monkeypatch.setattr(requests, "delete", lambda **kw: MockResp())
        monkeypatch.setattr(
            requests, "delete", lambda url, params, headers, timeout: MockResp()
        )
        delete_uploaded_file("https://api.example.com", "tok", "test.bin")

    def test_404_is_not_error(self, monkeypatch):
        class MockResp:
            status_code = 404

            def raise_for_status(self):
                raise requests.HTTPError("404")

        monkeypatch.setattr(
            requests, "delete", lambda url, params, headers, timeout: MockResp()
        )
        # Should not raise
        delete_uploaded_file("https://api.example.com", "tok", "test.bin")
