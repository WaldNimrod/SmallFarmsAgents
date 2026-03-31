"""Cooperative cancellation for background pipeline threads (admin stop)."""
from __future__ import annotations

import threading
from typing import Dict

_lock = threading.Lock()
_events: Dict[int, threading.Event] = {}


class PipelineRunCancelled(Exception):
    """Raised when request_cancel was set for this ingestion_run_id."""


def register_pipeline_run(ingestion_run_id: int) -> None:
    with _lock:
        _events[ingestion_run_id] = threading.Event()


def unregister_pipeline_run(ingestion_run_id: int) -> None:
    with _lock:
        _events.pop(ingestion_run_id, None)


def request_cancel(ingestion_run_id: int) -> None:
    with _lock:
        ev = _events.get(ingestion_run_id)
        if ev is not None:
            ev.set()


def cancel_all_registered() -> None:
    with _lock:
        for ev in _events.values():
            ev.set()


def is_cancelled(ingestion_run_id: int) -> bool:
    with _lock:
        ev = _events.get(ingestion_run_id)
        return ev.is_set() if ev is not None else False
