import time
from typing import Any

import httpx


class GithubClient:
    transient_status_codes = {429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        retry_attempts: int = 3,
        retry_backoff_ms: int = 200,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.retry_attempts = retry_attempts
        self.retry_backoff_ms = retry_backoff_ms

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.request(
                        method,
                        f"{self.base_url}{path}",
                        headers=self._headers(),
                        **kwargs,
                    )
                if (
                    response.status_code in self.transient_status_codes
                    and attempt < self.retry_attempts
                ):
                    time.sleep((self.retry_backoff_ms / 1000.0) * attempt)
                    continue
                response.raise_for_status()
                return response
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt < self.retry_attempts:
                    time.sleep((self.retry_backoff_ms / 1000.0) * attempt)
                    continue
                raise
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if (
                    exc.response.status_code in self.transient_status_codes
                    and attempt < self.retry_attempts
                ):
                    time.sleep((self.retry_backoff_ms / 1000.0) * attempt)
                    continue
                raise
        raise RuntimeError(f"GitHub request failed after retries: {last_error}")

    def list_issues(self, repo: str, state: str = "open") -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        response = self._request("GET", f"/repos/{owner}/{name}/issues", params={"state": state})
        return {"issues": response.json()}

    def set_labels(self, repo: str, issue_number: int, labels: list[str]) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        response = self._request(
            "POST",
            f"/repos/{owner}/{name}/issues/{issue_number}/labels",
            json={"labels": labels},
        )
        return {"labels": response.json()}

    def create_comment(self, repo: str, issue_number: int, body: str) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        response = self._request(
            "POST",
            f"/repos/{owner}/{name}/issues/{issue_number}/comments",
            json={"body": body},
        )
        return {"comment": response.json()}
