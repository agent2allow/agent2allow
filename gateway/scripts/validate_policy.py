#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

VALID_RISKS = {"read", "low", "medium", "high"}


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_policy(payload: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["policy root must be a mapping"]

    version = payload.get("version")
    if version != 1:
        _fail(errors, "version must be 1")

    defaults = payload.get("defaults")
    if not isinstance(defaults, dict):
        _fail(errors, "defaults must be a mapping")
    else:
        deny = defaults.get("deny_by_default")
        if not isinstance(deny, bool):
            _fail(errors, "defaults.deny_by_default must be a boolean")

    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        _fail(errors, "rules must be a non-empty list")
        return errors

    for idx, rule in enumerate(rules):
        prefix = f"rules[{idx}]"
        if not isinstance(rule, dict):
            _fail(errors, f"{prefix} must be a mapping")
            continue

        tool = rule.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            _fail(errors, f"{prefix}.tool must be a non-empty string")

        actions = rule.get("actions")
        if not isinstance(actions, list) or not actions:
            _fail(errors, f"{prefix}.actions must be a non-empty list")
        else:
            for action in actions:
                if not isinstance(action, str) or not action.strip():
                    _fail(errors, f"{prefix}.actions entries must be non-empty strings")
                    break

        repo = rule.get("repo")
        if not isinstance(repo, str) or not repo.strip():
            _fail(errors, f"{prefix}.repo must be a non-empty string")

        risk = rule.get("risk")
        if risk not in VALID_RISKS:
            _fail(errors, f"{prefix}.risk must be one of: {', '.join(sorted(VALID_RISKS))}")

        allow = rule.get("allow")
        if not isinstance(allow, bool):
            _fail(errors, f"{prefix}.allow must be a boolean")

        approval_required = rule.get("approval_required")
        if approval_required is not None and not isinstance(approval_required, bool):
            _fail(errors, f"{prefix}.approval_required must be boolean when provided")

        if risk in {"medium", "high"} and allow and approval_required is False:
            _fail(errors, f"{prefix} cannot disable approval for medium/high risk")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent2Allow policy YAML")
    parser.add_argument("policy", help="Path to policy YAML file")
    args = parser.parse_args()

    path = Path(args.policy)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML: {exc}", file=sys.stderr)
        return 1

    errors = validate_policy(payload)
    if errors:
        print("ERROR: invalid policy")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK: policy valid ({path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
