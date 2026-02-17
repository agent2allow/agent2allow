# Competitive Notes (2026-02-17)

## Sources reviewed
- AgentGateway docs and feature pages
- MCP Gateway Registry (agentic-community) repository and issues list
- Gravitee MCP proxy blog
- WSO2 MCP gateway overview

## 10 Frictions and smallest winning moves
1. Friction: Many gateway projects optimize breadth over first-run clarity.
- Why it matters: teams abandon setup if first run is noisy.
- Smallest win: deterministic smoke script that asserts expected outcomes.
- Impacted component: `README.md`, CI smoke workflow, `scripts/`.

2. Friction: Policy docs often explain concepts but not copy-paste defaults.
- Why it matters: policy adoption stalls without templates.
- Smallest win: triage template config + policy examples.
- Impacted component: `examples/github-triage-agent/`.

3. Friction: Approval UX is often hard to scan at a glance.
- Why it matters: operator fatigue and delayed approvals.
- Smallest win: status/repo/action filters + event details drawer.
- Impacted component: `ui/src/App.jsx`.

4. Friction: Audit logs are present but hard to inspect quickly.
- Why it matters: incident triage requires fast correlation.
- Smallest win: structured detail view and export shortcut in UI.
- Impacted component: `ui/src/App.jsx` and `docs/concepts/audit.md`.

5. Friction: Dependency/security hygiene differs between stacks.
- Why it matters: confidence drops when lint/test posture feels uneven.
- Smallest win: enforce lint for Python + UI in one CI pipeline.
- Impacted component: `.github/workflows/ci.yml`.

6. Friction: Error messages in demos can be generic.
- Why it matters: onboarding slows on first failure.
- Smallest win: stronger demo diagnostics with clear next actions.
- Impacted component: `examples/github-triage-agent/triage.py`.

7. Friction: MCP/governance products rely on enterprise controls not available to OSS users.
- Why it matters: OSS users need immediate value without enterprise setup.
- Smallest win: opinionated local-first defaults and templates.
- Impacted component: docs + examples.

8. Friction: Queueing/approval semantics can be unclear.
- Why it matters: operators don't know if action executed or still pending.
- Smallest win: explicit status labels and reason fields in UI.
- Impacted component: `ui/src/App.jsx`.

9. Friction: Reliability concerns (timeouts/retries) appear in issue threads.
- Why it matters: transient failures look like policy failures.
- Smallest win: retry/backoff roadmap item with clear acceptance tests.
- Impacted component: backlog and future gateway connector work.

10. Friction: “Safe by default” claims are not always test-proven.
- Why it matters: trust requires executable proof.
- Smallest win: include deny-by-default check in smoke protocol and report.
- Impacted component: test reports + smoke script.
