#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import yaml


def _load_policy(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML object")
    rules = data.get("rules")
    if not isinstance(rules, list):
        raise ValueError(f"{path} must contain a list at rules")
    return data


def _normalize_rule(rule: dict) -> dict:
    actions = rule.get("actions", [])
    normalized_actions = sorted(str(action) for action in actions)
    return {
        "tool": str(rule.get("tool", "")),
        "actions": normalized_actions,
        "repo": str(rule.get("repo", "")),
        "risk": str(rule.get("risk", "")),
        "allow": bool(rule.get("allow", False)),
        "approval_required": rule.get("approval_required"),
    }


def _rule_key(rule: dict) -> str:
    return json.dumps(_normalize_rule(rule), sort_keys=True, separators=(",", ":"))


def compare_policies(old: dict, new: dict) -> dict:
    old_rules = {_rule_key(rule): _normalize_rule(rule) for rule in old.get("rules", [])}
    new_rules = {_rule_key(rule): _normalize_rule(rule) for rule in new.get("rules", [])}
    old_keys = set(old_rules)
    new_keys = set(new_rules)

    changes: dict[str, object] = {
        "version_changed": old.get("version") != new.get("version"),
        "old_version": old.get("version"),
        "new_version": new.get("version"),
        "deny_by_default_changed": old.get("defaults", {}).get("deny_by_default")
        != new.get("defaults", {}).get("deny_by_default"),
        "old_deny_by_default": old.get("defaults", {}).get("deny_by_default"),
        "new_deny_by_default": new.get("defaults", {}).get("deny_by_default"),
        "added_rules": [new_rules[key] for key in sorted(new_keys - old_keys)],
        "removed_rules": [old_rules[key] for key in sorted(old_keys - new_keys)],
    }
    changes["changed"] = bool(
        changes["version_changed"]
        or changes["deny_by_default_changed"]
        or changes["added_rules"]
        or changes["removed_rules"]
    )
    return changes


def _print_human(changes: dict) -> None:
    print("Policy Diff")
    print(f"- version: {changes['old_version']} -> {changes['new_version']}")
    print(
        "- deny_by_default: "
        f"{changes['old_deny_by_default']} -> {changes['new_deny_by_default']}"
    )
    print(f"- added rules: {len(changes['added_rules'])}")
    print(f"- removed rules: {len(changes['removed_rules'])}")
    if not changes["changed"]:
        print("No effective policy changes detected.")
        return
    for rule in changes["added_rules"]:
        print(f"+ {json.dumps(rule, sort_keys=True)}")
    for rule in changes["removed_rules"]:
        print(f"- {json.dumps(rule, sort_keys=True)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two Agent2Allow policy files")
    parser.add_argument("old_policy", type=Path)
    parser.add_argument("new_policy", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable diff")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when any policy change is detected",
    )
    args = parser.parse_args()

    old_policy = _load_policy(args.old_policy)
    new_policy = _load_policy(args.new_policy)
    changes = compare_policies(old_policy, new_policy)

    if args.json:
        print(json.dumps(changes, indent=2, sort_keys=True))
    else:
        _print_human(changes)

    if args.strict and changes["changed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
