import httpx


class Agent2AllowClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def tool_call(self, payload: dict) -> dict:
        response = httpx.post(f"{self.base_url}/v1/tool-calls", json=payload, timeout=20.0)
        response.raise_for_status()
        return response.json()

    def pending_approvals(self) -> list[dict]:
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
