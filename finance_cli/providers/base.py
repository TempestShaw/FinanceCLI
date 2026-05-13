"""Provider primitives shared by finance data-source clients."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict, dataclass, field
from io import StringIO
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


def quiet_call(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Call noisy third-party APIs without polluting CLI JSON output."""
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        return func(*args, **kwargs)
