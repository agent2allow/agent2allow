# GitHub Triage Agent Example

This example calls Agent2Allow for GitHub triage actions.

## Run
1. Start stack: `docker compose up --build -d`
2. Execute demo: `npm run demo`

## Behavior
- tries a denied repo call first
- reads issues from allowed repo
- submits label + comment actions (pending approvals)
- approves pending actions
- prints audit event count
