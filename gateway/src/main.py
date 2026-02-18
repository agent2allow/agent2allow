import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response
from sqlalchemy import text

from .connectors.github_client import GithubClient
from .db import SessionLocal, engine, run_startup_migrations
from .models import Base
from .policy import PolicyEngine
from .schemas import (
    ApprovalDecisionRequest,
    ApprovalView,
    AuditLogView,
    BulkApprovalRequest,
    ToolCallRequest,
    ToolCallResponse,
)
from .service import Agent2AllowService, IdempotencyConflictError
from .settings import settings


def build_service() -> Agent2AllowService:
    policy_path = Path(settings.policy_path)
    if not policy_path.exists() and Path("gateway").exists():
        policy_path = Path("gateway") / settings.policy_path

    return Agent2AllowService(
        session_factory=SessionLocal,
        policy_engine=PolicyEngine(str(policy_path)),
        github_client=GithubClient(
            settings.github_base_url,
            settings.github_token,
            retry_attempts=settings.github_retry_attempts,
            retry_backoff_ms=settings.github_retry_backoff_ms,
        ),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()
    app.state.service = build_service()
    yield


app = FastAPI(title="Agent2Allow", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(response: Response) -> dict[str, str | bool | dict[str, bool]]:
    checks: dict[str, bool] = {"service": False, "database": False, "policy_file": False}

    service = getattr(app.state, "service", None)
    if service is not None:
        checks["service"] = True
        policy_path = Path(service.policy_engine.policy_path)
        checks["policy_file"] = policy_path.exists()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    ready_state = all(checks.values())
    payload: dict[str, str | bool | dict[str, bool]] = {
        "status": "ok" if ready_state else "not_ready",
        "ready": ready_state,
        "checks": checks,
    }
    if not ready_state:
        response.status_code = 503
    return payload


@app.post("/v1/tool-calls", response_model=ToolCallResponse)
def tool_calls(
    request: ToolCallRequest,
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
) -> ToolCallResponse:
    if x_idempotency_key:
        request = request.model_copy(update={"idempotency_key": x_idempotency_key})
    try:
        status, message, result, approval_id, idempotent_replay = (
            app.state.service.handle_tool_call(request)
        )
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ToolCallResponse(
        status=status,
        message=message,
        result=result,
        approval_id=approval_id,
        idempotent_replay=idempotent_replay,
    )


@app.get("/v1/approvals/pending", response_model=list[ApprovalView])
def approvals_pending() -> list[ApprovalView]:
    approvals = app.state.service.list_pending_approvals()
    return [
        ApprovalView(
            id=a.id,
            status=a.status,
            tool=a.tool,
            action=a.action,
            repo=a.repo,
            risk_level=a.risk_level,
            request_payload=json.loads(a.request_payload),
            reason=a.reason,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in approvals
    ]


@app.post("/v1/approvals/{approval_id}/approve")
def approvals_approve(approval_id: int, request: ApprovalDecisionRequest) -> dict:
    status, result = app.state.service.approve(approval_id, request.approver, request.reason)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="approval not found")
    if status == "invalid_state":
        raise HTTPException(status_code=400, detail="approval not pending")
    return {"status": status, "result": result}


@app.post("/v1/approvals/{approval_id}/deny")
def approvals_deny(approval_id: int, request: ApprovalDecisionRequest) -> dict:
    status = app.state.service.deny(approval_id, request.approver, request.reason)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="approval not found")
    if status == "invalid_state":
        raise HTTPException(status_code=400, detail="approval not pending")
    return {"status": status}


@app.post("/v1/approvals/bulk")
def approvals_bulk(request: BulkApprovalRequest) -> dict:
    if request.decision not in {"approve", "deny"}:
        raise HTTPException(status_code=400, detail="decision must be approve or deny")

    results: list[dict] = []
    for approval_id in request.ids:
        if request.decision == "approve":
            status, result = app.state.service.approve(
                approval_id,
                request.approver,
                request.reason,
            )
            if status == "not_found":
                results.append({"id": approval_id, "status": "not_found"})
            elif status == "invalid_state":
                results.append({"id": approval_id, "status": "invalid_state"})
            else:
                results.append({"id": approval_id, "status": status, "result": result})
        else:
            status = app.state.service.deny(approval_id, request.approver, request.reason)
            results.append({"id": approval_id, "status": status})
    return {"results": results}


@app.get("/v1/audit", response_model=list[AuditLogView])
def audit_logs() -> list[AuditLogView]:
    rows = app.state.service.list_audit_logs()
    return [
        AuditLogView(
            id=row.id,
            timestamp=row.timestamp,
            agent_id=row.agent_id,
            tool=row.tool,
            action=row.action,
            repo=row.repo,
            risk_level=row.risk_level,
            schema_version=row.schema_version,
            status=row.status,
            request_payload=json.loads(row.request_payload),
            response_payload=json.loads(row.response_payload),
            approval_id=row.approval_id,
            message=row.message,
        )
        for row in rows
    ]


@app.get("/v1/audit/export")
def audit_export() -> dict:
    rows = app.state.service.list_audit_logs()
    lines = []
    for row in rows:
        payload = {
            "id": row.id,
            "timestamp": row.timestamp.isoformat(),
            "agent_id": row.agent_id,
            "tool": row.tool,
            "action": row.action,
            "repo": row.repo,
            "risk_level": row.risk_level,
            "schema_version": row.schema_version,
            "status": row.status,
            "request_payload": json.loads(row.request_payload),
            "response_payload": json.loads(row.response_payload),
            "approval_id": row.approval_id,
            "message": row.message,
        }
        lines.append(json.dumps(payload))
    return {"format": "jsonl", "lines": lines}
