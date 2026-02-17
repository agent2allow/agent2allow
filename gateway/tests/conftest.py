import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _build_test_env(tmp_path: Path) -> dict[str, str]:
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list]
    repo: acme/roadrunner
    risk: read
    allow: true
  - tool: github
    actions: [issues.set_labels, issues.create_comment]
    repo: acme/roadrunner
    risk: medium
    allow: true
""".strip(),
        encoding="utf-8",
    )
    return {
        "DATABASE_URL": f"sqlite:///{tmp_path / 'test.db'}",
        "POLICY_PATH": str(policy_path),
        "GITHUB_BASE_URL": "https://api.github.test",
    }


@pytest.fixture()
def client(tmp_path: Path):
    env = _build_test_env(tmp_path)
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)

    from src.main import app

    with TestClient(app) as test_client:
        yield test_client

    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
