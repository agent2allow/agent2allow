import httpx

from .openapi_types import ApprovalView, ToolCallRequest, ToolCallResponse

class Agent2AllowClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def tool_call(
        self, payload: ToolCallRequest, idempotency_key: str | None = None
    ) -> ToolCallResponse:
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        response = httpx.post(
            f"{self.base_url}/v1/tool-calls",
            json=payload,
            headers=headers,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def pending_approvals(self) -> list[ApprovalView]:
        response = httpx.get(f"{self.base_url}/v1/approvals/pending", timeout=20.0)
        response.raise_for_status()
        return response.json()

    def approve(self, approval_id: int, approver: str = "human", reason: str = "") -> dict:
        response = httpx.post(
            f"{self.base_url}/v1/approvals/{approval_id}/approve",
            json={"approver": approver, "reason": reason},
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def deny(self, approval_id: int, approver: str = "human", reason: str = "") -> dict:
        response = httpx.post(
            f"{self.base_url}/v1/approvals/{approval_id}/deny",
            json={"approver": approver, "reason": reason},
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    def bulk_approval(
        self,
        ids: list[int],
        decision: str,
        approver: str = "human",
        reason: str = "",
    ) -> dict:
        response = httpx.post(
            f"{self.base_url}/v1/approvals/bulk",
            json={"ids": ids, "decision": decision, "approver": approver, "reason": reason},
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()
