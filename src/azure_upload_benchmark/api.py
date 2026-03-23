"""HTTP helpers for interacting with a media upload API.

This module provides generic functions for obtaining SAS URLs and cleaning
up uploaded blobs via arbitrary REST endpoints.  No service-specific URLs
are hardcoded — callers must supply their own endpoints and auth tokens.

Note: Only JWT Bearer token authentication is currently supported.
"""

import requests


def _api_headers(token: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_sas_url_from_api(api_url: str, token: str, filename: str) -> str:
    """Call an upload API endpoint to generate a fresh SAS URL.

    Parameters
    ----------
    api_url:
        The POST endpoint that returns ``{"url": "<sas_url>"}``.
    token:
        Bearer token (without the ``Bearer `` prefix – it will be added).
    filename:
        Name of the file to be uploaded.
    """
    resp = requests.post(
        api_url,
        json={"filename": filename},
        headers=_api_headers(token),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["url"]


def delete_uploaded_file(delete_url: str, token: str, filename: str):
    """Delete the uploaded file via a DELETE endpoint.

    Parameters
    ----------
    delete_url:
        The DELETE endpoint (filename is passed as a query parameter).
    token:
        Bearer token for authentication.
    filename:
        Name of the file to delete.
    """
    resp = requests.delete(
        delete_url,
        params={"filename": filename},
        headers=_api_headers(token),
        timeout=30,
    )
    if resp.status_code == 404:
        return
    resp.raise_for_status()
