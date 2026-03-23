"""Azure Blob upload logic."""

import os
import time

from azure.storage.blob import BlobClient

from .constants import MB


def upload_blob(
    sas_url: str, file_path: str, chunk_size: int, concurrency: int
) -> dict:
    """Upload a file to Azure Blob Storage using the Python SDK.

    Parameters
    ----------
    sas_url:
        Azure Blob SAS URL with write permission.
    file_path:
        Path to the local file to upload.
    chunk_size:
        Block size in bytes for the upload.
    concurrency:
        Number of parallel connections for uploading.

    Returns
    -------
    dict with keys: file_size_mb, chunk_size_mb, concurrency, elapsed_s,
        throughput_mbps.
    """
    file_size = os.path.getsize(file_path)
    client = BlobClient.from_blob_url(
        sas_url,
        max_block_size=chunk_size,
        max_single_put_size=chunk_size,
    )

    start = time.perf_counter()
    with open(file_path, "rb") as data:
        client.upload_blob(
            data,
            overwrite=True,
            max_concurrency=concurrency,
            blob_type="BlockBlob",
        )
    elapsed = time.perf_counter() - start

    throughput_mbps = (file_size / MB) / elapsed if elapsed > 0 else 0

    return {
        "file_size_mb": round(file_size / MB, 2),
        "chunk_size_mb": round(chunk_size / MB, 2),
        "concurrency": concurrency,
        "elapsed_s": round(elapsed, 3),
        "throughput_mbps": round(throughput_mbps, 2),
    }
