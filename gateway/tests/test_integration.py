import respx
from httpx import Response


def test_health_and_ready(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    ready = client.get("/ready")
    assert ready.status_code == 200
    payload = ready.json()
    assert payload["ready"] is True
    assert payload["checks"]["service"] is True
    assert payload["checks"]["database"] is True
    assert payload["checks"]["policy_file"] is True


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
    assert audit.status_code == 200
    assert all(entry["schema_version"] == 1 for entry in audit.json())
    statuses = [row["status"] for row in audit.json()]
    assert "pending_approval" in statuses
    assert "approved" in statuses
    assert "executed" in statuses

    exported = client.get("/v1/audit/export")
    assert exported.status_code == 200
    lines = exported.json()["lines"]
    assert lines
    assert all('"schema_version": 1' in line for line in lines)


@respx.mock
def test_tool_call_idempotency_replays_response(client):
    route = respx.get("https://api.github.test/repos/acme/roadrunner/issues").mock(
        return_value=Response(200, json=[{"number": 1, "title": "bug: crash", "labels": []}])
    )
    payload = {
        "agent_id": "triage-agent",
        "tool": "github",
        "action": "issues.list",
        "repo": "acme/roadrunner",
        "params": {"state": "open"},
    }

    first = client.post("/v1/tool-calls", json=payload, headers={"X-Idempotency-Key": "demo-123"})
    second = client.post("/v1/tool-calls", json=payload, headers={"X-Idempotency-Key": "demo-123"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "executed"
    assert second.json()["status"] == "executed"
    assert first.json()["idempotent_replay"] is False
    assert second.json()["idempotent_replay"] is True
    assert route.call_count == 1

    audit = client.get("/v1/audit")
    statuses = [row["status"] for row in audit.json()]
    assert "idempotent_replay" in statuses


@respx.mock
def test_tool_call_idempotency_conflict_returns_409(client):
    respx.get("https://api.github.test/repos/acme/roadrunner/issues").mock(
        return_value=Response(200, json=[{"number": 1, "title": "bug: crash", "labels": []}])
    )
    first_payload = {
        "agent_id": "triage-agent",
        "tool": "github",
        "action": "issues.list",
        "repo": "acme/roadrunner",
        "params": {"state": "open"},
    }
    second_payload = {
        "agent_id": "triage-agent",
        "tool": "github",
        "action": "issues.list",
        "repo": "acme/roadrunner",
        "params": {"state": "closed"},
    }

    first = client.post(
        "/v1/tool-calls",
        json=first_payload,
        headers={"X-Idempotency-Key": "conflict-123"},
    )
    conflict = client.post(
        "/v1/tool-calls",
        json=second_payload,
        headers={"X-Idempotency-Key": "conflict-123"},
    )

    assert first.status_code == 200
    assert conflict.status_code == 409


@respx.mock
def test_bulk_approval_endpoint_executes_multiple_pending(client):
    route_issue_1 = respx.post("https://api.github.test/repos/acme/roadrunner/issues/1/labels").mock(
        return_value=Response(200, json=["bug"])
    )
    route_issue_2 = respx.post("https://api.github.test/repos/acme/roadrunner/issues/2/labels").mock(
        return_value=Response(200, json=["question"])
    )

    write_1 = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.set_labels",
            "repo": "acme/roadrunner",
            "params": {"issue_number": 1, "labels": ["bug"]},
        },
    )
    write_2 = client.post(
        "/v1/tool-calls",
        json={
            "agent_id": "triage-agent",
            "tool": "github",
            "action": "issues.set_labels",
            "repo": "acme/roadrunner",
            "params": {"issue_number": 2, "labels": ["question"]},
        },
    )
    id_1 = write_1.json()["approval_id"]
    id_2 = write_2.json()["approval_id"]

    bulk = client.post(
        "/v1/approvals/bulk",
        json={
            "ids": [id_1, id_2],
            "decision": "approve",
            "approver": "alice",
            "reason": "safe labels",
        },
    )
    assert bulk.status_code == 200
    payload = bulk.json()
    assert len(payload["results"]) == 2
    assert {row["status"] for row in payload["results"]} == {"executed"}
    assert route_issue_1.called
    assert route_issue_2.called
