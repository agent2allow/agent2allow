from typing import Any

import httpx


class GithubClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def list_issues(self, repo: str, state: str = "open") -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{self.base_url}/repos/{owner}/{name}/issues",
                params={"state": state},
                headers=self._headers(),
            )
            response.raise_for_status()
            return {"issues": response.json()}

    def set_labels(self, repo: str, issue_number: int, labels: list[str]) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/repos/{owner}/{name}/issues/{issue_number}/labels",
                json={"labels": labels},
                headers=self._headers(),
            )
            response.raise_for_status()
            return {"labels": response.json()}

    def create_comment(self, repo: str, issue_number: int, body: str) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/repos/{owner}/{name}/issues/{issue_number}/comments",
                json={"body": body},
                headers=self._headers(),
            )
            response.raise_for_status()
            return {"comment": response.json()}
