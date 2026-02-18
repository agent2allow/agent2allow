#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATES = {
    "triage-readonly": {
        "read_actions": ["issues.list"],
        "write_actions": [],
    },
    "triage-standard": {
        "read_actions": ["issues.list"],
        "write_actions": ["issues.set_labels", "issues.create_comment"],
    },
}


def render_policy(template_name: str, repo: str) -> str:
    if template_name not in TEMPLATES:
        raise ValueError(f"unknown template: {template_name}")

    cfg = TEMPLATES[template_name]
    read_actions = cfg["read_actions"]
    write_actions = cfg["write_actions"]

    lines = [
        "version: 1",
        "defaults:",
        "  deny_by_default: true",
        "rules:",
        "  - tool: github",
        f"    actions: [{', '.join(read_actions)}]",
        f"    repo: {repo}",
        "    risk: read",
        "    allow: true",
    ]

    if write_actions:
        lines.extend(
            [
                "  - tool: github",
                f"    actions: [{', '.join(write_actions)}]",
                f"    repo: {repo}",
                "    risk: medium",
                "    allow: true",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate starter policy templates")
    parser.add_argument(
        "--template",
        required=True,
        choices=sorted(TEMPLATES.keys()),
        help="Template name",
    )
    parser.add_argument("--repo", required=True, help="Repo scope, e.g. acme/roadrunner")
    parser.add_argument(
        "--out",
        required=True,
        help="Output file path",
    )
    args = parser.parse_args()

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_policy(args.template, args.repo), encoding="utf-8")
    print(f"OK: wrote policy template to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
