from __future__ import annotations

import os
from typing import Any

from langfuse import Langfuse


def _get_client() -> Langfuse | None:
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return None
    try:
        return Langfuse()
    except Exception:
        return None


def fetch_traces(limit: int = 50) -> list[dict[str, Any]]:
    client = _get_client()
    if client is None:
        return []
    try:
        response = client.api.trace.list(limit=limit, order_by="timestamp.desc")
        traces: list[dict[str, Any]] = []
        for t in response.data:
            traces.append({
                "id": t.id,
                "name": t.name or "Agent.run",
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "user_id": t.user_id,
                "session_id": t.session_id,
                "latency": getattr(t, "latency", None),
                "total_cost": getattr(t, "total_cost", None),
                "tags": t.tags or [],
                "metadata": t.metadata,
            })
        return traces
    except Exception:
        return []


def fetch_trace_detail(trace_id: str) -> dict[str, Any] | None:
    client = _get_client()
    if client is None:
        return None
    try:
        t = client.api.trace.get(trace_id)
        return {
            "id": t.id,
            "name": t.name or "Agent.run",
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            "user_id": t.user_id,
            "session_id": t.session_id,
            "latency": getattr(t, "latency", None),
            "total_cost": getattr(t, "total_cost", None),
            "tags": t.tags or [],
            "metadata": t.metadata,
            "observations": [
                {
                    "id": o.id,
                    "name": o.name,
                    "type": o.type,
                    "start_time": o.start_time.isoformat() if o.start_time else None,
                    "latency": getattr(o, "latency", None),
                    "cost": getattr(o, "total_cost", None),
                    "input": str(o.input)[:200] if o.input else None,
                    "output": str(o.output)[:200] if o.output else None,
                }
                for o in getattr(t, "observations", [])
            ],
            "scores": [
                {
                    "id": s.id,
                    "name": s.name,
                    "value": getattr(s, "value", None),
                    "data_type": getattr(s, "data_type", None),
                }
                for s in getattr(t, "scores", [])
            ],
        }
    except Exception:
        return None


def fetch_sessions(limit: int = 20) -> list[dict[str, Any]]:
    client = _get_client()
    if client is None:
        return []
    try:
        response = client.api.sessions.list(limit=limit, order_by="createdAt.desc")
        sessions: list[dict[str, Any]] = []
        for s in response.data:
            sessions.append({
                "id": s.id,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            })
        return sessions
    except Exception:
        return []


def health_check() -> dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"connected": False, "reason": "no_credentials"}
    try:
        result = client.auth_check()
        return {"connected": True, "result": str(result)}
    except Exception as e:
        return {"connected": False, "reason": str(e)}
