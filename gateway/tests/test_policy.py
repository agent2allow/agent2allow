from src.policy import PolicyEngine


def test_policy_allow_and_approval(tmp_path):
    policy = tmp_path / "policy.yml"
    policy.write_text(
        """
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list]
    repo: acme/*
    risk: read
    allow: true
  - tool: github
    actions: [issues.set_labels]
    repo: acme/*
    risk: medium
    allow: true
""".strip(),
        encoding="utf-8",
    )

    engine = PolicyEngine(str(policy))

    read = engine.decide("github", "issues.list", "acme/repo")
    assert read.allowed is True
    assert read.approval_required is False

    write = engine.decide("github", "issues.set_labels", "acme/repo")
    assert write.allowed is True
    assert write.approval_required is True

    denied = engine.decide("github", "issues.create_comment", "acme/repo")
    assert denied.allowed is False
