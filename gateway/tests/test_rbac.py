import pytest

from src.rbac import ApprovalRBAC


def test_rbac_disabled_allows_all_decisions():
    rbac = ApprovalRBAC(
        enabled=False,
        role_bindings_json="",
        approve_roles_csv="reviewer,admin",
        deny_roles_csv="reviewer,admin",
        high_risk_approve_roles_csv="admin",
    )
    allowed, reason = rbac.authorize(decision="approve", approver="anyone", risk_level="high")
    assert allowed is True
    assert reason == ""


def test_rbac_restricts_high_risk_approvals_to_admin():
    rbac = ApprovalRBAC(
        enabled=True,
        role_bindings_json='{"alice":"reviewer","bob":"admin"}',
        approve_roles_csv="reviewer,admin",
        deny_roles_csv="reviewer,admin",
        high_risk_approve_roles_csv="admin",
    )
    reviewer_allowed, _ = rbac.authorize(
        decision="approve",
        approver="alice",
        risk_level="high",
    )
    admin_allowed, _ = rbac.authorize(
        decision="approve",
        approver="bob",
        risk_level="high",
    )
    assert reviewer_allowed is False
    assert admin_allowed is True


def test_rbac_blocks_unmapped_approver():
    rbac = ApprovalRBAC(
        enabled=True,
        role_bindings_json='{"bob":"admin"}',
        approve_roles_csv="admin",
        deny_roles_csv="admin",
        high_risk_approve_roles_csv="admin",
    )
    allowed, reason = rbac.authorize(decision="deny", approver="alice", risk_level="medium")
    assert allowed is False
    assert "no mapped RBAC role" in reason


def test_rbac_rejects_invalid_role_bindings_json():
    with pytest.raises(ValueError):
        ApprovalRBAC(
            enabled=True,
            role_bindings_json='["bad"]',
            approve_roles_csv="admin",
            deny_roles_csv="admin",
            high_risk_approve_roles_csv="admin",
        )
