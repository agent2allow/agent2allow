# North Star

## KPIs
1. Mock demo success rate in CI: >= 99% over last 30 runs.
2. Time-to-first-successful-demo (fresh checkout): <= 10 minutes.
3. Policy clarity score: all policy concepts covered with copy-paste examples.
4. Security gate coverage: lint + tests + secret-scan always required on main.
5. Operator UX efficiency: approvals and audit filtering in <= 2 clicks.

## Prioritized Backlog (max 12)
### DX (4)
1. Deterministic smoke demo script and README integration.
2. Improve quickstart troubleshooting section.
3. SDK copy-paste snippets for JS/Python with approval examples.
4. One-command local dev helper script.

### Security/Reliability (4)
5. Retry/backoff policy for GitHub connector calls.
6. Idempotency keys for `/v1/tool-calls`.
7. Audit event schema versioning.
8. Policy schema validation command.

### Docs/Examples (2)
9. Triage template config with rule customization.
10. Add “how to debug denied calls” guide.

### Competitive edge (2)
11. Audit viewer filters and event detail panel.
12. Minimal policy wizard CLI scaffold.

## Iteration Selection (2026-02-17)
- Quick Win: #1 Deterministic smoke demo + README quickstart lift.
- Moat Builder: #9/#11 Triage template + audit viewer improvements.

## Iteration Selection (2026-02-17, iteration 2)
- Quick Win: #10 Add denied-call troubleshooting guide.
- Moat Builder: #5 Retry/backoff in GitHub connector.

## Iteration Selection (2026-02-17, iteration 3)
- Quick Win: #3 SDK copy-paste snippets with approval flow examples.
- Moat Builder: #6 Idempotency keys for `/v1/tool-calls`.

## Iteration Selection (2026-02-18, iteration 4)
- Quick Win: #4 One-command local dev check helper script.
- Moat Builder: #8 Policy schema validation command and CI integration.
