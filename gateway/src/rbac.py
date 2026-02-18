import json


class ApprovalRBAC:
    def __init__(
        self,
        *,
        enabled: bool,
        role_bindings_json: str,
        approve_roles_csv: str,
        deny_roles_csv: str,
        high_risk_approve_roles_csv: str,
    ):
        self.enabled = enabled
        self.role_bindings = self._parse_role_bindings(role_bindings_json)
        self.approve_roles = self._parse_roles(approve_roles_csv)
        self.deny_roles = self._parse_roles(deny_roles_csv)
        self.high_risk_approve_roles = self._parse_roles(high_risk_approve_roles_csv)

    @staticmethod
    def _parse_roles(raw: str) -> set[str]:
        roles = {item.strip() for item in raw.split(",") if item.strip()}
        return roles

    @staticmethod
    def _parse_role_bindings(raw: str) -> dict[str, str]:
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("approval_role_bindings must be a JSON object")
        bindings: dict[str, str] = {}
        for user, role in parsed.items():
            if not isinstance(user, str) or not isinstance(role, str):
                raise ValueError("approval_role_bindings values must be strings")
            bindings[user] = role
        return bindings

    def _resolve_role(self, approver: str) -> str:
        return self.role_bindings.get(approver, "")

    def authorize(self, *, decision: str, approver: str, risk_level: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, ""

        role = self._resolve_role(approver)
        if not role:
            return False, "approver has no mapped RBAC role"

        if decision == "approve":
            allowed = self.approve_roles
            if risk_level == "high":
                allowed = self.high_risk_approve_roles
        elif decision == "deny":
            allowed = self.deny_roles
        else:
            return False, "unsupported decision"

        if role not in allowed:
            return False, f"role '{role}' is not allowed to {decision} {risk_level}-risk approvals"
        return True, ""
