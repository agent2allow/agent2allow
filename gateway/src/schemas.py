from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    tool: str
    action: str
    repo: str
    params: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class ToolCallResponse(BaseModel):
    status: str
    message: str
    result: dict[str, Any] | None = None
    approval_id: int | None = None
    idempotent_replay: bool = False


class ApprovalDecisionRequest(BaseModel):
    approver: str = "human"
    reason: str = ""


class ApprovalView(BaseModel):
    id: int
    status: str
    tool: str
    action: str
    repo: str
    risk_level: str
    request_payload: dict[str, Any]
    reason: str
    created_at: datetime
    updated_at: datetime


class AuditLogView(BaseModel):
    id: int
    timestamp: datetime
    agent_id: str
    tool: str
    action: str
    repo: str
    risk_level: str
    status: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]
    approval_id: int | None
    message: str
