import subprocess
import sys


def test_policy_validator_accepts_default_policy():
    result = subprocess.run(
        [sys.executable, "scripts/validate_policy.py", "config/default-policy.yml"],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "OK: policy valid" in result.stdout


def test_policy_validator_rejects_invalid_policy(tmp_path):
    invalid = tmp_path / "invalid-policy.yml"
    invalid.write_text(
        """
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.set_labels]
    repo: acme/roadrunner
    risk: high
    allow: true
    approval_required: false
""".strip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/validate_policy.py", str(invalid)],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "cannot disable approval for medium/high risk" in result.stdout
