import os
from pathlib import Path

import pytest

from src.connectors.github_client import GithubClient
from src.policy import PolicyEngine

REQUIRES_REAL_MODE = not (
    os.getenv("REAL_GITHUB_ENABLE_TESTS", "").lower() == "true"
    and os.getenv("REAL_GITHUB_TOKEN")
    and os.getenv("REAL_GITHUB_REPO")
)

pytestmark = pytest.mark.skipif(
    REQUIRES_REAL_MODE,
    reason="set REAL_GITHUB_ENABLE_TESTS=true + REAL_GITHUB_TOKEN + REAL_GITHUB_REPO",
)


def test_real_mode_read_only_issue_list_call():
    token = os.environ["REAL_GITHUB_TOKEN"]
    repo = os.environ["REAL_GITHUB_REPO"]
    client = GithubClient(
        "https://api.github.com",
        token=token,
        retry_attempts=2,
        retry_backoff_ms=100,
    )

    payload = client.list_issues(repo, state="open")
    assert "issues" in payload
    assert isinstance(payload["issues"], list)


def test_real_mode_policy_template_denies_write(tmp_path: Path):
    repo = os.environ["REAL_GITHUB_REPO"]
    policy_path = tmp_path / "readonly.yml"
    policy_path.write_text(
        f"""
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list]
    repo: {repo}
    risk: read
    allow: true
""".strip(),
        encoding="utf-8",
    )

    engine = PolicyEngine(str(policy_path))
    read = engine.decide("github", "issues.list", repo)
    write = engine.decide("github", "issues.set_labels", repo)

    assert read.allowed is True
    assert write.allowed is False
