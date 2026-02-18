# JavaScript SDK

Minimal client for the Agent2Allow gateway.

## Install
```bash
cd sdk/js
npm install
```

## Optional typed OpenAPI sync
```bash
npm run openapi:sync
```

This exports the gateway OpenAPI schema and regenerates `openapi-types.d.ts`.

## Copy-paste usage
```js
import { Agent2AllowClient } from "./client.js";

const client = new Agent2AllowClient("http://localhost:8000", {
  approvalApiKey: process.env.APPROVAL_API_KEY || ""
});

const read = await client.toolCall(
  {
    agent_id: "triage-agent",
    tool: "github",
    action: "issues.list",
    repo: "acme/roadrunner",
    params: { state: "open" }
  },
  { idempotencyKey: "read-issues-1" }
);

const write = await client.toolCall(
  {
    agent_id: "triage-agent",
    tool: "github",
    action: "issues.set_labels",
    repo: "acme/roadrunner",
    params: { issue_number: 1, labels: ["bug"] }
  },
  { idempotencyKey: "label-issue-1" }
);

if (write.status === "pending_approval") {
  await client.approve(write.approval_id, "operator", "safe change");
}

await client.bulkApproval([1, 2], "deny", "operator", "out of scope");
```

`idempotent_replay=true` in a response means the same idempotency key was replayed and the cached result was returned.
