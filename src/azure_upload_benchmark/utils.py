"""Utility helpers (test-file generation, etc.)."""

import os
import tempfile

from .constants import MB


def generate_test_file(size_mb: int) -> str:
    """Create a temporary file filled with random bytes.

    The file is placed in the system temp directory and reused if it
    already exists with the expected size.
    """
    path = os.path.join(tempfile.gettempdir(), f"upload_bench_{size_mb}mb.bin")
    if os.path.exists(path) and os.path.getsize(path) == size_mb * MB:
        print(f"Reusing existing test file: {path}")
        return path
    print(f"Generating {size_mb} MB test file at {path} ...")
    with open(path, "wb") as f:
        remaining = size_mb * MB
        block = 8 * MB
        while remaining > 0:
            chunk = min(block, remaining)
            f.write(os.urandom(chunk))
            remaining -= chunk
    print(f"  Done ({os.path.getsize(path) / MB:.1f} MB)")
    return path
