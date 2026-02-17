import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .db import SessionLocal, engine
from .models import Base
from .policy import PolicyEngine
from .schemas import (
    ApprovalDecisionRequest,
    ApprovalView,
    AuditLogView,
    ToolCallRequest,
    ToolCallResponse,
)
from .service import Agent2AllowService
from .settings import settings
from .connectors.github_client import GithubClient


app = FastAPI(title="Agent2Allow", version="0.1.0")


def build_service() -> Agent2AllowService:
    policy_path = Path(settings.policy_path)
    if not policy_path.exists() and Path("gateway") .exists():
        policy_path = Path("gateway") / settings.policy_path

    return Agent2AllowService(
        session_factory=SessionLocal,
        policy_engine=PolicyEngine(str(policy_path)),
        github_client=GithubClient(settings.github_base_url, settings.github_token),
    )


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    app.state.service = build_service()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/tool-calls", response_model=ToolCallResponse)
def tool_calls(request: ToolCallRequest) -> ToolCallResponse:
    status, message, result, approval_id = app.state.service.handle_tool_call(request)
    return ToolCallResponse(status=status, message=message, result=result, approval_id=approval_id)


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
            "status": row.status,
            "request_payload": json.loads(row.request_payload),
            "response_payload": json.loads(row.response_payload),
            "approval_id": row.approval_id,
            "message": row.message,
        }
        lines.append(json.dumps(payload))
    return {"format": "jsonl", "lines": lines}
