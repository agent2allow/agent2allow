import json
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .connectors.github_client import GithubClient
from .models import Approval, AuditLog
from .policy import PolicyDecision, PolicyEngine
from .schemas import ToolCallRequest


class Agent2AllowService:
    def __init__(
        self,
        session_factory: Callable[[], Session],
        policy_engine: PolicyEngine,
        github_client: GithubClient,
    ):
        self.session_factory = session_factory
        self.policy_engine = policy_engine
        self.github_client = github_client

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
            status=status,
            request_payload=json.dumps(request_payload),
            response_payload=json.dumps(response_payload or {}),
            approval_id=approval_id,
            message=message,
        )
        db.add(entry)
        db.commit()

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

    def handle_tool_call(
        self, request: ToolCallRequest
    ) -> tuple[str, str, dict | None, int | None]:
        decision: PolicyDecision = self.policy_engine.decide(
            request.tool, request.action, request.repo
        )

        with self.session_factory() as db:
            request_payload = request.model_dump()

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
                return "denied", decision.message, None, None

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
                return "pending_approval", "approval required", None, approval.id

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
                return "executed", "executed", result, None
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
                return "error", str(exc), None, None

    def list_pending_approvals(self) -> list[Approval]:
        with self.session_factory() as db:
            rows = db.scalars(
                select(Approval)
                .where(Approval.status == "pending")
                .order_by(Approval.created_at.asc())
            ).all()
            return rows

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
