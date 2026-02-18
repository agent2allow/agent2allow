import json
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .audit_sink import AuditSinkContract, NoopAuditSink, safe_emit
from .connectors.contracts import GithubConnectorContract
from .models import Approval, AuditLog, IdempotencyRecord
from .policy import PolicyDecision, PolicyEngine
from .schemas import ToolCallRequest


class IdempotencyConflictError(ValueError):
    pass


class Agent2AllowService:
    audit_schema_version = 1

    def __init__(
        self,
        session_factory: Callable[[], Session],
        policy_engine: PolicyEngine,
        github_client: GithubConnectorContract,
        audit_sink: AuditSinkContract | None = None,
    ):
        if not isinstance(github_client, GithubConnectorContract):
            raise TypeError("github_client does not satisfy GithubConnectorContract")
        self.session_factory = session_factory
        self.policy_engine = policy_engine
        self.github_client = github_client
        self.audit_sink = audit_sink or NoopAuditSink()

    def _audit(
        self,
        db: Session,
        *,
        agent_id: str,
        tool: str,
        action: str,
        repo: str,
        risk_level: str,
        status: str,
        request_payload: dict,
        response_payload: dict | None = None,
        approval_id: int | None = None,
        message: str = "",
    ) -> None:
        entry = AuditLog(
            timestamp=datetime.now(UTC),
            agent_id=agent_id,
            tool=tool,
            action=action,
            repo=repo,
            risk_level=risk_level,
            schema_version=self.audit_schema_version,
            status=status,
            request_payload=json.dumps(request_payload),
            response_payload=json.dumps(response_payload or {}),
            approval_id=approval_id,
            message=message,
        )
        db.add(entry)
        db.commit()
        safe_emit(
            self.audit_sink,
            {
                "timestamp": entry.timestamp.isoformat(),
                "agent_id": entry.agent_id,
                "tool": entry.tool,
                "action": entry.action,
                "repo": entry.repo,
                "risk_level": entry.risk_level,
                "schema_version": entry.schema_version,
                "status": entry.status,
                "request_payload": request_payload,
                "response_payload": response_payload or {},
                "approval_id": approval_id,
                "message": message,
            },
        )

    def _execute(self, request: ToolCallRequest) -> dict:
        if request.tool != "github":
            raise ValueError("unsupported tool")

        if request.action == "issues.list":
            state = str(request.params.get("state", "open"))
            return self.github_client.list_issues(request.repo, state=state)

        if request.action == "issues.set_labels":
            issue_number = int(request.params["issue_number"])
            labels = list(request.params["labels"])
            return self.github_client.set_labels(request.repo, issue_number, labels)

        if request.action == "issues.create_comment":
            issue_number = int(request.params["issue_number"])
            body = str(request.params["body"])
            return self.github_client.create_comment(request.repo, issue_number, body)

        raise ValueError("unsupported action")

    def _request_hash(self, request: ToolCallRequest) -> str:
        payload = request.model_dump()
        payload.pop("idempotency_key", None)
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return sha256(serialized.encode("utf-8")).hexdigest()

    def _record_idempotency(
        self,
        db: Session,
        *,
        key: str,
        request_hash: str,
        response_payload: dict,
    ) -> None:
        row = IdempotencyRecord(
            key=key,
            request_hash=request_hash,
            response_payload=json.dumps(response_payload),
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.key == key))
            if existing and existing.request_hash != request_hash:
                raise IdempotencyConflictError(
                    "idempotency key already used with a different request payload"
                ) from None
            if not existing:
                raise

    def handle_tool_call(
        self, request: ToolCallRequest
    ) -> tuple[str, str, dict | None, int | None, bool]:
        request_hash = self._request_hash(request)
        decision: PolicyDecision = self.policy_engine.decide(
            request.tool, request.action, request.repo
        )

        with self.session_factory() as db:
            request_payload = request.model_dump()
            idempotency_key = request.idempotency_key

            if idempotency_key:
                record = db.scalar(
                    select(IdempotencyRecord).where(IdempotencyRecord.key == idempotency_key)
                )
                if record:
                    if record.request_hash != request_hash:
                        raise IdempotencyConflictError(
                            "idempotency key already used with a different request payload"
                        )
                    cached = json.loads(record.response_payload)
                    self._audit(
                        db,
                        agent_id=request.agent_id,
                        tool=request.tool,
                        action=request.action,
                        repo=request.repo,
                        risk_level=decision.risk_level,
                        status="idempotent_replay",
                        request_payload=request_payload,
                        response_payload={"cached_status": cached["status"]},
                        message=f"replayed response for key {idempotency_key}",
                    )
                    return (
                        cached["status"],
                        cached["message"],
                        cached.get("result"),
                        cached.get("approval_id"),
                        True,
                    )

            if not decision.allowed:
                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=request.tool,
                    action=request.action,
                    repo=request.repo,
                    risk_level=decision.risk_level,
                    status="denied",
                    request_payload=request_payload,
                    message=decision.message,
                )
                if idempotency_key:
                    self._record_idempotency(
                        db,
                        key=idempotency_key,
                        request_hash=request_hash,
                        response_payload={
                            "status": "denied",
                            "message": decision.message,
                            "result": None,
                            "approval_id": None,
                        },
                    )
                return "denied", decision.message, None, None, False

            if decision.approval_required:
                approval = Approval(
                    status="pending",
                    tool=request.tool,
                    action=request.action,
                    repo=request.repo,
                    risk_level=decision.risk_level,
                    request_payload=json.dumps(request_payload),
                    result_payload="{}",
                    reason="",
                )
                db.add(approval)
                db.commit()
                db.refresh(approval)

                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=request.tool,
                    action=request.action,
                    repo=request.repo,
                    risk_level=decision.risk_level,
                    status="pending_approval",
                    request_payload=request_payload,
                    approval_id=approval.id,
                    message="approval required",
                )
                if idempotency_key:
                    self._record_idempotency(
                        db,
                        key=idempotency_key,
                        request_hash=request_hash,
                        response_payload={
                            "status": "pending_approval",
                            "message": "approval required",
                            "result": None,
                            "approval_id": approval.id,
                        },
                    )
                return "pending_approval", "approval required", None, approval.id, False

            try:
                result = self._execute(request)
                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=request.tool,
                    action=request.action,
                    repo=request.repo,
                    risk_level=decision.risk_level,
                    status="executed",
                    request_payload=request_payload,
                    response_payload=result,
                    message="executed",
                )
                if idempotency_key:
                    self._record_idempotency(
                        db,
                        key=idempotency_key,
                        request_hash=request_hash,
                        response_payload={
                            "status": "executed",
                            "message": "executed",
                            "result": result,
                            "approval_id": None,
                        },
                    )
                return "executed", "executed", result, None, False
            except Exception as exc:  # pragma: no cover
                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=request.tool,
                    action=request.action,
                    repo=request.repo,
                    risk_level=decision.risk_level,
                    status="error",
                    request_payload=request_payload,
                    message=str(exc),
                )
                if idempotency_key:
                    self._record_idempotency(
                        db,
                        key=idempotency_key,
                        request_hash=request_hash,
                        response_payload={
                            "status": "error",
                            "message": str(exc),
                            "result": None,
                            "approval_id": None,
                        },
                    )
                return "error", str(exc), None, None, False

    def list_pending_approvals(self) -> list[Approval]:
        with self.session_factory() as db:
            rows = db.scalars(
                select(Approval)
                .where(Approval.status == "pending")
                .order_by(Approval.created_at.asc())
            ).all()
            return rows

    def get_approval(self, approval_id: int) -> Approval | None:
        with self.session_factory() as db:
            return db.get(Approval, approval_id)

    def approve(self, approval_id: int, approver: str, reason: str) -> tuple[str, dict | None]:
        with self.session_factory() as db:
            approval = db.get(Approval, approval_id)
            if not approval:
                return "not_found", None
            if approval.status != "pending":
                return "invalid_state", None

            approval.status = "approved"
            approval.reason = reason
            db.commit()

            request_payload = json.loads(approval.request_payload)
            request = ToolCallRequest(**request_payload)

            self._audit(
                db,
                agent_id=approver,
                tool=approval.tool,
                action=approval.action,
                repo=approval.repo,
                risk_level=approval.risk_level,
                status="approved",
                request_payload=request_payload,
                approval_id=approval.id,
                message=reason or "approved",
            )

            try:
                result = self._execute(request)
                approval.status = "executed"
                approval.result_payload = json.dumps(result)
                db.commit()
                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=approval.tool,
                    action=approval.action,
                    repo=approval.repo,
                    risk_level=approval.risk_level,
                    status="executed",
                    request_payload=request_payload,
                    response_payload=result,
                    approval_id=approval.id,
                    message="executed after approval",
                )
                return "executed", result
            except Exception as exc:  # pragma: no cover
                approval.status = "failed"
                approval.result_payload = json.dumps({"error": str(exc)})
                db.commit()
                self._audit(
                    db,
                    agent_id=request.agent_id,
                    tool=approval.tool,
                    action=approval.action,
                    repo=approval.repo,
                    risk_level=approval.risk_level,
                    status="error",
                    request_payload=request_payload,
                    approval_id=approval.id,
                    message=str(exc),
                )
                return "error", {"error": str(exc)}

    def deny(self, approval_id: int, approver: str, reason: str) -> str:
        with self.session_factory() as db:
            approval = db.get(Approval, approval_id)
            if not approval:
                return "not_found"
            if approval.status != "pending":
                return "invalid_state"

            approval.status = "denied"
            approval.reason = reason
            db.commit()

            request_payload = json.loads(approval.request_payload)
            self._audit(
                db,
                agent_id=approver,
                tool=approval.tool,
                action=approval.action,
                repo=approval.repo,
                risk_level=approval.risk_level,
                status="denied_by_human",
                request_payload=request_payload,
                approval_id=approval.id,
                message=reason or "denied",
            )
            return "denied"

    def list_audit_logs(self) -> list[AuditLog]:
        with self.session_factory() as db:
            rows = db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
            return rows
