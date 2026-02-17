# Python SDK

Minimal client for the Agent2Allow gateway.

## Install
```bash
cd sdk/python
pip install -e .
```

## Copy-paste usage
```python
from agent2allow_sdk import Agent2AllowClient

client = Agent2AllowClient("http://localhost:8000")

read = client.tool_call(
    {
        "agent_id": "triage-agent",
        "tool": "github",
        "action": "issues.list",
        "repo": "acme/roadrunner",
        "params": {"state": "open"},
    },
    idempotency_key="read-issues-1",
)

write = client.tool_call(
    {
        "agent_id": "triage-agent",
        "tool": "github",
        "action": "issues.set_labels",
        "repo": "acme/roadrunner",
        "params": {"issue_number": 1, "labels": ["bug"]},
    },
    idempotency_key="label-issue-1",
)

if write["status"] == "pending_approval":
    client.approve(write["approval_id"], approver="operator", reason="safe change")
```

`idempotent_replay=True` in a response means the same idempotency key was replayed and the cached result was returned.
