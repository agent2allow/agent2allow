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
