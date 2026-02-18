import subprocess
import sys


def test_policy_diff_detects_changes(tmp_path):
    old_policy = tmp_path / "old.yml"
    new_policy = tmp_path / "new.yml"

    old_policy.write_text(
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
""".strip(),
        encoding="utf-8",
    )
    new_policy.write_text(
        """
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list, issues.create_comment]
    repo: acme/roadrunner
    risk: medium
    allow: true
""".strip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/policy_diff.py", str(old_policy), str(new_policy), "--strict"],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "added rules: 1" in result.stdout
    assert "removed rules: 1" in result.stdout


def test_policy_diff_no_changes_returns_zero(tmp_path):
    old_policy = tmp_path / "old.yml"
    new_policy = tmp_path / "new.yml"
    content = """
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list]
    repo: acme/roadrunner
    risk: read
    allow: true
""".strip()
    old_policy.write_text(content, encoding="utf-8")
    new_policy.write_text(content, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/policy_diff.py", str(old_policy), str(new_policy), "--strict"],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "No effective policy changes detected." in result.stdout
