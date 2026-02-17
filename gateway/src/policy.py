import fnmatch
from dataclasses import dataclass
from pathlib import Path

import yaml

RISK_LEVELS_REQUIRING_APPROVAL = {"medium", "high"}


@dataclass
class PolicyDecision:
    allowed: bool
    approval_required: bool
    risk_level: str
    message: str


@dataclass
class PolicyRule:
    tool: str
    actions: list[str]
    repo: str
    risk: str
    allow: bool
    approval_required: bool | None


class PolicyEngine:
    def __init__(self, policy_path: str):
        self.policy_path = Path(policy_path)
        self._loaded_mtime = 0.0
        self.rules: list[PolicyRule] = []
        self.deny_by_default = True
        self.load()

    def load(self) -> None:
        if not self.policy_path.exists():
            self.rules = []
            self.deny_by_default = True
            return

        mtime = self.policy_path.stat().st_mtime
        if mtime == self._loaded_mtime:
            return

        payload = yaml.safe_load(self.policy_path.read_text(encoding="utf-8")) or {}
        defaults = payload.get("defaults", {})
        self.deny_by_default = bool(defaults.get("deny_by_default", True))

        parsed: list[PolicyRule] = []
        for item in payload.get("rules", []):
            parsed.append(
                PolicyRule(
                    tool=item["tool"],
                    actions=item.get("actions", []),
                    repo=item.get("repo", "*"),
                    risk=item.get("risk", "read"),
                    allow=bool(item.get("allow", False)),
                    approval_required=item.get("approval_required"),
                )
            )
        self.rules = parsed
        self._loaded_mtime = mtime

    def decide(self, tool: str, action: str, repo: str) -> PolicyDecision:
        self.load()

        for rule in self.rules:
            if rule.tool != tool:
                continue
            if not any(fnmatch.fnmatch(action, pattern) for pattern in rule.actions):
                continue
            if not fnmatch.fnmatch(repo, rule.repo):
                continue

            if not rule.allow:
                return PolicyDecision(False, False, rule.risk, "policy denies action")

            if rule.approval_required is None:
                approval_required = rule.risk in RISK_LEVELS_REQUIRING_APPROVAL
            else:
                approval_required = bool(rule.approval_required)

            return PolicyDecision(True, approval_required, rule.risk, "policy allows action")

        if self.deny_by_default:
            return PolicyDecision(False, False, "unknown", "no matching allow rule")
        return PolicyDecision(True, False, "low", "default allow")
