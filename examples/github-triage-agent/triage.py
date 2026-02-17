import json
import os

import httpx


GATEWAY_URL = os.getenv("AGENT2ALLOW_URL", "http://localhost:8000")
REPO = os.getenv("GITHUB_REPO", "acme/roadrunner")
TRIAGE_TEMPLATE_PATH = os.getenv(
    "TRIAGE_TEMPLATE_PATH", "examples/github-triage-agent/triage-template.json"
)
TRIAGE_DRY_RUN = os.getenv("TRIAGE_DRY_RUN", "false").lower() == "true"
TRIAGE_AUTO_APPROVE = os.getenv("TRIAGE_AUTO_APPROVE", "true").lower() == "true"


def tool_call(action: str, repo: str, params: dict) -> dict:
    payload = {
        "agent_id": "github-triage-agent",
        "tool": "github",
        "action": action,
        "repo": repo,
        "params": params,
    }
    response = httpx.post(f"{GATEWAY_URL}/v1/tool-calls", json=payload, timeout=20.0)
    response.raise_for_status()
    return response.json()


def load_template(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def classify(issue: dict, template: dict) -> tuple[str, str]:
    text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
    for rule in template.get("rules", []):
        keywords = [k.lower() for k in rule.get("keywords", [])]
        if any(keyword in text for keyword in keywords):
            return str(rule["label"]), str(rule["comment"])

    default = template.get("default", {})
    return str(default.get("label", "needs-info")), str(
        default.get("comment", "Thanks for opening this. We marked as needs-info to collect more details.")
    )


def main() -> None:
    print("== Agent2Allow Demo: GitHub Triage Agent ==")
    template = load_template(TRIAGE_TEMPLATE_PATH)
    print(f"Template loaded: {TRIAGE_TEMPLATE_PATH}")

    try:
        denied = tool_call("issues.list", "forbidden/repo", {"state": "open"})
    except httpx.ConnectError:
        print("Gateway not reachable. Start services first: docker compose up --build -d")
        raise SystemExit(1)

    print("1) Deny-by-default check:", denied["status"], "-", denied["message"])

    read = tool_call("issues.list", REPO, {"state": "open"})
    print("2) Read call:", read["status"])
    issues = read.get("result", {}).get("issues", [])
    print(f"   Found {len(issues)} issues")

    planned_writes = 0
    for issue in issues:
        label, comment = classify(issue, template)
        print(f"   Issue #{issue['number']} classified as: {label}")
        if TRIAGE_DRY_RUN:
            continue

        label_result = tool_call(
            "issues.set_labels",
            REPO,
            {"issue_number": issue["number"], "labels": [label]},
        )
        comment_result = tool_call(
            "issues.create_comment",
            REPO,
            {"issue_number": issue["number"], "body": comment},
        )
        print(
            f"3) Issue #{issue['number']} write calls:",
            label_result["status"],
            "/",
            comment_result["status"],
        )
        planned_writes += 2

    if TRIAGE_DRY_RUN:
        print(f"3) Dry run enabled, no write calls executed. Planned writes: {len(issues) * 2}")
        return

    pending = httpx.get(f"{GATEWAY_URL}/v1/approvals/pending", timeout=20.0)
    pending.raise_for_status()
    approvals = pending.json()
    print(f"4) Pending approvals: {len(approvals)}")

    if TRIAGE_AUTO_APPROVE:
        for item in approvals:
            approved = httpx.post(
                f"{GATEWAY_URL}/v1/approvals/{item['id']}/approve",
                json={"approver": "demo-operator", "reason": "demo approve"},
                timeout=20.0,
            )
            approved.raise_for_status()
        print(f"5) Approved {len(approvals)} actions")
    else:
        print("5) Auto-approve disabled; approve pending actions via UI/API.")

    audit = httpx.get(f"{GATEWAY_URL}/v1/audit", timeout=20.0)
    audit.raise_for_status()
    audit_rows = audit.json()
    print(f"6) Audit events total: {len(audit_rows)}")
    print(f"Summary: issues={len(issues)} planned_writes={planned_writes} approvals={len(approvals)}")


if __name__ == "__main__":
    main()
