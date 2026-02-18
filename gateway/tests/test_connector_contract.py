import pytest

from src.connectors.contracts import GithubConnectorContract
from src.connectors.github_client import GithubClient
from src.policy import PolicyEngine
from src.service import Agent2AllowService


def test_github_client_satisfies_connector_contract():
    client = GithubClient("https://api.github.test")
    assert isinstance(client, GithubConnectorContract)


def test_service_rejects_non_compliant_connector(tmp_path):
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """
version: 1
defaults:
  deny_by_default: true
rules: []
""".strip(),
        encoding="utf-8",
    )

    class BadConnector:
        pass

    with pytest.raises(TypeError):
        Agent2AllowService(
            session_factory=lambda: None,
            policy_engine=PolicyEngine(str(policy_path)),
            github_client=BadConnector(),
        )
