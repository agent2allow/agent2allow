import respx
from httpx import Response


def test_denied_without_matching_repo(client):
    response = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.list",
            "repo": "other/repo",
            "params": {},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "denied"


@respx.mock
def test_read_executes_and_write_requires_approval(client):
    respx.get("https://api.github.test/repos/acme/roadrunner/issues").mock(
        return_value=Response(200, json=[{"number": 1, "title": "bug: crash", "labels": []}])
    )

    read = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.list",
            "repo": "acme/roadrunner",
            "params": {"state": "open"},
        },
    )
    assert read.status_code == 200
    assert read.json()["status"] == "executed"

    write = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.set_labels",
            "repo": "acme/roadrunner",
            "params": {"issue_number": 1, "labels": ["bug"]},
        },
    )
    assert write.status_code == 200
    assert write.json()["status"] == "pending_approval"


@respx.mock
def test_approve_executes_pending_action(client):
    respx.post("https://api.github.test/repos/acme/roadrunner/issues/1/labels").mock(
        return_value=Response(200, json=["bug"])
    )

    write = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.set_labels",
            "repo": "acme/roadrunner",
            "params": {"issue_number": 1, "labels": ["bug"]},
        },
    )
    approval_id = write.json()["approval_id"]

    approved = client.post(
        f"/v1/approvals/{approval_id}/approve",
        json={"approver": "alice", "reason": "looks good"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "executed"

    audit = client.get("/v1/audit")
    statuses = [row["status"] for row in audit.json()]
    assert "pending_approval" in statuses
    assert "approved" in statuses
    assert "executed" in statuses
