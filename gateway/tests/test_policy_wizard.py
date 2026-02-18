import subprocess
import sys


def test_policy_wizard_generates_standard_template(tmp_path):
    output = tmp_path / "policy.yml"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/policy_wizard.py",
            "--template",
            "triage-standard",
            "--repo",
            "acme/roadrunner",
            "--out",
            str(output),
        ],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    content = output.read_text(encoding="utf-8")
    assert "deny_by_default: true" in content
    assert "issues.list" in content
    assert "issues.set_labels" in content
    assert "issues.create_comment" in content


def test_policy_wizard_generates_readonly_template(tmp_path):
    output = tmp_path / "readonly.yml"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/policy_wizard.py",
            "--template",
            "triage-readonly",
            "--repo",
            "acme/roadrunner",
            "--out",
            str(output),
        ],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    content = output.read_text(encoding="utf-8")
    assert "issues.list" in content
    assert "issues.set_labels" not in content
    assert "issues.create_comment" not in content
