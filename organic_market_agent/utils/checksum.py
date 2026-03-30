"""SHA-256 checksum utilities for raw asset deduplication."""
import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    """Return hex SHA-256 digest of in-memory bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_of_bytes(data: bytes) -> str:
    """Alias kept for backward compatibility."""
    return sha256_bytes(data)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
