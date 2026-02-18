from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GithubConnectorContract(Protocol):
    def list_issues(self, repo: str, state: str = "open") -> dict[str, Any]:
        ...

    def set_labels(self, repo: str, issue_number: int, labels: list[str]) -> dict[str, Any]:
        ...

    def create_comment(self, repo: str, issue_number: int, body: str) -> dict[str, Any]:
        ...
