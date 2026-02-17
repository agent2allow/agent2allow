# Policies

Agent2Allow uses a YAML policy DSL.

## Structure
```yaml
version: 1
defaults:
  deny_by_default: true
rules:
  - tool: github
    actions: [issues.list]
    repo: acme/roadrunner
    risk: read
    allow: true
  - tool: github
    actions: [issues.set_labels, issues.create_comment]
    repo: acme/roadrunner
    risk: medium
    allow: true
```

## Evaluation
1. Match by `tool`, `action`, and `repo` glob.
2. If no rule matches: deny.
3. `medium/high` risk requires approval unless explicitly disabled.

## Denied-call checklist
- `tool` mismatch: ensure request uses `github` when targeting GitHub connector actions.
- `action` mismatch: use exact action IDs (`issues.list`, `issues.set_labels`, `issues.create_comment`).
- `repo` mismatch: verify `owner/repo` scope matches policy rule (or explicit glob).
- implicit deny: no matching rule means deny-by-default by design.
- approval expectation: `risk: medium|high` can be allowed but still require approval before execution.

When troubleshooting, prefer checking the corresponding audit event first: it captures `decision`, `risk`, and error details for each tool call.
