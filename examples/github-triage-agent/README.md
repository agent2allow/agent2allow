# GitHub Triage Agent Example

This example calls Agent2Allow for GitHub triage actions.

## Run
1. Start stack: `docker compose up --build -d`
2. Execute demo: `npm run demo`

## Customize triage rules
- Default template: `examples/github-triage-agent/triage-template.json`
- Override at runtime:
  - `export TRIAGE_TEMPLATE_PATH=examples/github-triage-agent/triage-template.json`
  - `export TRIAGE_DRY_RUN=true` to test classification without write calls
  - `export TRIAGE_AUTO_APPROVE=false` to leave approvals pending for manual UI review

## Behavior
- tries a denied repo call first
- reads issues from allowed repo
- submits label + comment actions (pending approvals)
- approves pending actions
- prints audit event count
