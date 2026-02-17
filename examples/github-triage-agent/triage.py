import os

import httpx


GATEWAY_URL = os.getenv("AGENT2ALLOW_URL", "http://localhost:8000")
REPO = os.getenv("GITHUB_REPO", "acme/roadrunner")


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


def classify(issue: dict) -> tuple[str, str]:
    text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
    if "bug" in text or "crash" in text or "error" in text:
        return "bug", "Thanks for the report. We marked this as bug and will investigate."
    if "how" in text or "question" in text or issue.get("title", "").strip().endswith("?"):
        return "question", "Thanks for the question. We marked this as question and will follow up."
    return "needs-info", "Thanks for opening this. We marked as needs-info to collect more details."


def main() -> None:
    print("== Agent2Allow Demo: GitHub Triage Agent ==")

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

    for issue in issues:
        label, comment = classify(issue)
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

    pending = httpx.get(f"{GATEWAY_URL}/v1/approvals/pending", timeout=20.0)
    pending.raise_for_status()
    approvals = pending.json()
    print(f"4) Pending approvals: {len(approvals)}")

    for item in approvals:
        approved = httpx.post(
            f"{GATEWAY_URL}/v1/approvals/{item['id']}/approve",
            json={"approver": "demo-operator", "reason": "demo approve"},
            timeout=20.0,
        )
        approved.raise_for_status()

    print(f"5) Approved {len(approvals)} actions")

    audit = httpx.get(f"{GATEWAY_URL}/v1/audit", timeout=20.0)
    audit.raise_for_status()
    print(f"6) Audit events total: {len(audit.json())}")


if __name__ == "__main__":
    main()
