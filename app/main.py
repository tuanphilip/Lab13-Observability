from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv(Path(__file__).parent.parent / ".env")
from fastapi.responses import HTMLResponse, JSONResponse
from structlog.contextvars import bind_contextvars
from .dashboard_html import DASHBOARD_HTML
import json
import subprocess
from pathlib import Path

from .agent import LabAgent
from .incidents import disable, enable, status
from .langfuse_client import fetch_trace_detail, fetch_traces, health_check
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Enrich logs with request context (user_id_hash, session_id, feature, model, env)
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/dashboard-data")
async def api_dashboard_data():
    log_path = Path("data/logs.jsonl")
    records = []
    if log_path.exists():
        try:
            content = log_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
        except Exception:
            pass
            
    api_records = [r for r in records if r.get("service") == "api"]
    
    series = []
    cumulative_cost = 0.0
    cumulative_tokens_in = 0
    cumulative_tokens_out = 0
    error_count = 0
    success_count = 0
    
    for r in api_records:
        ts = r.get("ts", "")
        event = r.get("event", "")
        latency = r.get("latency_ms")
        cost = r.get("cost_usd", 0.0) or 0.0
        tokens_in = r.get("tokens_in", 0) or 0
        tokens_out = r.get("tokens_out", 0) or 0
        quality = r.get("quality_score")
        error_type = r.get("error_type")
        
        is_error = event == "request_failed" or error_type is not None
        if is_error:
            error_count += 1
        else:
            success_count += 1
            
        cumulative_cost += cost
        cumulative_tokens_in += tokens_in
        cumulative_tokens_out += tokens_out
        
        total_requests = success_count + error_count
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0.0
        
        series.append({
            "ts": ts,
            "latency": latency,
            "cost": cost,
            "cumulative_cost": round(cumulative_cost, 6),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cumulative_tokens_in": cumulative_tokens_in,
            "cumulative_tokens_out": cumulative_tokens_out,
            "quality": quality,
            "is_error": is_error,
            "error_rate": round(error_rate, 2)
        })
        
    errors_breakdown = {}
    for r in api_records:
        err = r.get("error_type")
        if err:
            errors_breakdown[err] = errors_breakdown.get(err, 0) + 1

    langfuse_traces = fetch_traces(limit=100)
    langfuse_health = health_check()
    langfuse_error_rate = 0.0
    langfuse_total_cost = 0.0
    langfuse_avg_latency = 0.0
    if langfuse_traces:
        for t in langfuse_traces:
            langfuse_total_cost += t.get("total_cost") or 0.0
            lat = t.get("latency")
            if lat:
                langfuse_avg_latency += lat
        langfuse_avg_latency = round(langfuse_avg_latency / len(langfuse_traces), 3) if langfuse_traces else 0.0
            
    return {
        "series": series,
        "errors_breakdown": errors_breakdown,
        "metrics": snapshot(),
        "langfuse": {
            "connected": langfuse_health.get("connected", False),
            "trace_count": len(langfuse_traces),
            "total_cost": round(langfuse_total_cost, 6),
            "avg_latency_sec": langfuse_avg_latency,
            "traces": langfuse_traces[:50],
        }
    }


@app.get("/api/langfuse/traces")
async def api_langfuse_traces(limit: int = 50):
    traces = fetch_traces(limit=limit)
    return {"traces": traces, "count": len(traces)}


@app.get("/api/langfuse/traces/{trace_id}")
async def api_langfuse_trace_detail(trace_id: str):
    detail = fetch_trace_detail(trace_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Trace not found or Langfuse unavailable")
    return detail


@app.get("/api/langfuse/health")
async def api_langfuse_health():
    return health_check()


@app.post("/run-load-test-api")
async def run_load_test_api():
    try:
        subprocess.Popen([".venv/Scripts/python", "scripts/load_test.py"])
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
