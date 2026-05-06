"""
Simple in-memory session state for the desktop app.
Avoids any dependency on Flet's Session API which changed in v0.80.
"""
from __future__ import annotations

_store: dict = {}


def get(key: str, default=None):
    return _store.get(key, default)


def set(key: str, value) -> None:
    _store[key] = value


def clear() -> None:
    _store.clear()
