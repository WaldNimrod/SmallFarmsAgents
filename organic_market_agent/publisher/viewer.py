"""Static file server for local publish output (http.server)."""
from __future__ import annotations

import http.server
import os
import socketserver
from pathlib import Path


def serve_directory(host: str, port: int, directory: Path) -> None:
    """Block and serve `directory` over HTTP (GET only)."""
    directory = Path(directory).resolve()
    handler = http.server.SimpleHTTPRequestHandler
    original_cwd = Path.cwd()
    try:
        os.chdir(directory)
        with socketserver.TCPServer((host, port), handler) as httpd:
            httpd.serve_forever()
    finally:
        os.chdir(original_cwd)
