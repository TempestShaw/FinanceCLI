"""Provider primitives shared by finance data-source clients."""
from __future__ import annotations

import sys
import threading

from dataclasses import asdict, dataclass, field
from typing import Any


class ProviderError(RuntimeError):
    """Raised when an external provider cannot satisfy a finance request."""


@dataclass(frozen=True)
class ProviderMetadata:
    name: str
    label: str
    capabilities: tuple[str, ...]
    required_env: tuple[str, ...] = ()
    optional_env: tuple[str, ...] = ()
    package: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderHealth:
    name: str
    configured: bool
    ok: bool | None = None
    status: str = "unknown"
    latency_ms: float | None = None
    error: str | None = None
    required_env: list[dict[str, Any]] = field(default_factory=list)
    optional_env: list[dict[str, Any]] = field(default_factory=list)
    capabilities: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def require_dependency(module_name: str, install_hint: str) -> Any:
    """Import a runtime dependency with a finance-specific error message."""
    try:
        return __import__(module_name)
    except ImportError as exc:
        raise ProviderError(f"Missing dependency '{module_name}'. {install_hint}") from exc


class _QuietAwareStream:
    """Drops writes from threads inside quiet_call and forwards all others."""

    def __init__(self, target: Any) -> None:
        self._target = target

    def write(self, text: str) -> int:
        if getattr(_quiet_thread, "depth", 0):
            return len(text)
        return self._target.write(text)

    def flush(self) -> None:
        if not getattr(_quiet_thread, "depth", 0):
            self._target.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._target, name)


_quiet_thread = threading.local()
_quiet_lock = threading.Lock()
_quiet_active = 0
_saved_streams: tuple[Any, Any] | None = None


def quiet_call(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Call noisy third-party APIs without polluting CLI JSON output.

    contextlib.redirect_stdout swaps the process-wide sys.stdout, so concurrent
    calls restored each other's buffers and left stdout silenced for good. Only
    the calling thread is silenced here: the first caller installs a filtering
    stream and the last one to leave restores the original streams.
    """
    global _quiet_active, _saved_streams
    with _quiet_lock:
        if _quiet_active == 0:
            _saved_streams = (sys.stdout, sys.stderr)
            sys.stdout, sys.stderr = _QuietAwareStream(sys.stdout), _QuietAwareStream(sys.stderr)
        _quiet_active += 1
    _quiet_thread.depth = getattr(_quiet_thread, "depth", 0) + 1
    try:
        return func(*args, **kwargs)
    finally:
        _quiet_thread.depth -= 1
        with _quiet_lock:
            _quiet_active -= 1
            if _quiet_active == 0 and _saved_streams is not None:
                sys.stdout, sys.stderr = _saved_streams
                _saved_streams = None
