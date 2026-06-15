from __future__ import annotations

import os
from typing import Any

_langfuse_client = None

try:
    from langfuse import Langfuse, get_client, observe

    _langfuse_client = Langfuse()
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator

    def get_client() -> None:
        return None


def _get_lf_client() -> Any:
    if _langfuse_client is not None:
        return _langfuse_client
    try:
        from langfuse import get_client as _gc
        return _gc()
    except Exception:
        return None


def update_trace_attrs(user_id: str, session_id: str, tags: list[str]) -> None:
    client = _get_lf_client()
    if client is None:
        return
    try:
        client.update_current_trace(
            user_id=user_id,
            session_id=session_id,
            tags=tags,
        )
    except Exception:
        pass


def update_span_attrs(metadata: dict[str, Any], usage_details: dict[str, int]) -> None:
    client = _get_lf_client()
    if client is None:
        return
    try:
        client.update_current_span(
            metadata=metadata,
            usage_details=usage_details,
        )
    except Exception:
        pass


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def flush() -> None:
    if _langfuse_client is not None:
        try:
            _langfuse_client.flush()
        except Exception:
            pass
