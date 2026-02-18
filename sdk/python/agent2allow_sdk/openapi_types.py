# Generated from OpenAPI. Do not edit manually.
from __future__ import annotations

from typing import NotRequired, TypedDict

class ApprovalDecisionRequest(TypedDict, total=False):
    approver: NotRequired[str]
    reason: NotRequired[str]

class ApprovalView(TypedDict, total=False):
    action: str
    created_at: str
    id: int
    reason: str
    repo: str
    request_payload: dict[str, object]
    risk_level: str
    status: str
    tool: str
    updated_at: str

class AuditLogView(TypedDict, total=False):
    action: str
    agent_id: str
    approval_id: int | None
    id: int
    message: str
    repo: str
    request_payload: dict[str, object]
    response_payload: dict[str, object]
    risk_level: str
    schema_version: int
    status: str
    timestamp: str
    tool: str

class BulkApprovalRequest(TypedDict, total=False):
    approver: NotRequired[str]
    decision: str
    ids: list[int]
    reason: NotRequired[str]

class HTTPValidationError(TypedDict, total=False):
    detail: NotRequired[list[ValidationError]]

class ToolCallRequest(TypedDict, total=False):
    action: str
    agent_id: str
    idempotency_key: NotRequired[str | None]
    params: NotRequired[dict[str, object]]
    repo: str
    tool: str

class ToolCallResponse(TypedDict, total=False):
    approval_id: NotRequired[int | None]
    idempotent_replay: NotRequired[bool]
    message: str
    result: NotRequired[dict[str, object] | None]
    status: str

class ValidationError(TypedDict, total=False):
    ctx: NotRequired[dict[str, object]]
    input: NotRequired[object]
    loc: list[str | int]
    msg: str
    type: str
