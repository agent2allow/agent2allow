# ExecPlan: OSS/Open-Core Repository Hardening for Agent2Allow

## Scope
This plan upgrades the existing `agent2allow/agent2allow` repository to a professional OSS/open-core baseline with community standards, contribution flow, and CI security hygiene.

Current state: repository already exists and is populated. Repo creation steps are therefore **not required**.

## Goals
- Enforce a consistent OSS project front door (`README`, `LICENSE`, `SECURITY`, `CONTRIBUTING`, `CODE_OF_CONDUCT`).
- Add GitHub collaboration workflows (issue templates, PR template, dependency updates).
- Add CI skeleton checks including a lightweight secret scanning gate.
- Ensure required structure remains clean and discoverable.
- Apply minimal GitHub repo settings via `gh` CLI where possible.

## File-by-file Changes
1. `README.md`
- Set exact required product positioning as first line:
  - `Agent2Allow — Ship AI agents safely to production in 10 minutes — with deny-by-default permissions, human approvals, and auditable tool calls.`
- Keep concise architecture overview and quickstart placeholder references.

2. `LICENSE`
- Replace MIT text with Apache License 2.0 text.

3. `SECURITY.md`
- Keep responsible disclosure and supported versions section.
- Ensure language is clear for public OSS contributors.

4. `CONTRIBUTING.md`
- Add local dev setup, test commands, PR requirements, and explicit no-secrets policy.

5. `CODE_OF_CONDUCT.md`
- Add Contributor Covenant (v2.1) adapted for this repository.

6. `docs/*`
- Ensure required docs exist and are coherent:
  - `docs/quickstart.md`
  - `docs/concepts/policies.md`
  - `docs/concepts/approvals.md`
  - `docs/concepts/audit.md`
  - `docs/deployment/docker.md`
- Keep this plan in `docs/PLANS.md`.

7. `.github/workflows/ci.yml`
- Add/keep baseline jobs:
  - gateway tests
  - UI tests
  - secret-pattern scan (`GITHUB_TOKEN=`, `ghp_`, `github_pat_`, private key headers)
  - lint placeholder with concrete roadmap note if full linters are not yet standardized

8. `.github` collaboration files
- Add:
  - `.github/ISSUE_TEMPLATE/bug_report.yml`
  - `.github/ISSUE_TEMPLATE/feature_request.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.github/dependabot.yml`
  - `.github/CODEOWNERS` (minimal)
  - `.github/FUNDING.yml` (optional placeholder)

9. `gateway/README.md`
- Add gateway module overview and scaffold orientation.

10. Scaffold validation (already present, keep tidy)
- `docker-compose.yml`
- `gateway/src/` scaffold
- `sdk/js`, `sdk/python` scaffold
- `examples/github-triage-agent/README.md`

11. `MANUAL_SETUP.md`
- Add only if some GitHub settings cannot be automated via CLI (discussion toggle/branch protection details).

## GitHub Settings via CLI
Attempt through `gh`:
- Confirm default branch = `main`.
- Ensure labels exist: `bug`, `feature`, `security`, `good first issue`.
- Enable discussions.
- Attempt branch protection on `main` requiring PRs.

If any command is blocked by permissions/plan limits, document exact UI click-path in `MANUAL_SETUP.md`.

## Commit Plan
1. **Commit 1: Community and governance baseline**
- `README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `gateway/README.md`

2. **Commit 2: GitHub collaboration scaffolding**
- `.github/ISSUE_TEMPLATE/*`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/dependabot.yml`, `.github/CODEOWNERS`, `.github/FUNDING.yml`

3. **Commit 3: CI/security hygiene and settings docs**
- `.github/workflows/ci.yml`, `MANUAL_SETUP.md` (if needed), minor doc alignment

## Definition of Done Checklist
- [ ] README starts with exact required positioning sentence.
- [ ] License is Apache-2.0.
- [ ] SECURITY + CONTRIBUTING + CODE_OF_CONDUCT present and clear.
- [ ] Required docs and scaffolds are present and non-chaotic.
- [ ] Issue templates + PR template + Dependabot config present.
- [ ] CI runs tests and secret scan checks.
- [ ] GitHub labels include: `bug`, `feature`, `security`, `good first issue`.
- [ ] Discussions enabled or documented manual fallback.
- [ ] Branch protection applied or documented manual fallback.
- [ ] TODO count in repository stays within requested limits.

---

## Iteration 1 (2026-02-17): DX Quickstart + Triage/Audit UX

### Goal
Improve first-run confidence and operator clarity for the hero use-case.

### Scope
- Quick Win: actionable README quickstart + smoke demo script + CI smoke execution.
- Moat Builder: triage rule template and richer audit viewer filters/details.

### Non-goals
- No connector protocol redesign.
- No multi-tenant/RBAC expansion in this iteration.

### Files to change
- `README.md`, `docs/quickstart.md`, `examples/github-triage-agent/README.md`
- `scripts/smoke_mock_demo.sh`
- `.github/workflows/ci.yml`
- `examples/github-triage-agent/triage.py`
- `examples/github-triage-agent/triage-template.yml`
- `ui/src/App.jsx`, `ui/src/styles.css`, `ui/tests/app.test.jsx`
- `docs/TEST_REPORTS/2026-02-17-iteration1.md`
- `docs/PR_DRAFTS/2026-02-17-iteration1.md`

### Risks and mitigations
- Risk: CI time increase from smoke job.
  - Mitigation: run only gateway + mock-github services in smoke script.
- Risk: UI complexity drift.
  - Mitigation: keep filter UX minimal and keyboard-friendly.

### Rollback plan
- Revert smoke job and UI changes independently if instability appears.

---

## Iteration 2 (2026-02-17): Reliability Hardening + Denied-Call Troubleshooting

### Goal
Reduce transient GitHub connector failures and improve operator self-service for denied tool calls.

### Scope
- Quick Win: Add a concrete denied-call troubleshooting section.
- Moat Builder: Add retry/backoff in GitHub connector with dedicated tests.

### Non-goals
- No queue architecture changes.
- No idempotency implementation in this iteration.

### Files to change
- `gateway/src/settings.py`
- `gateway/src/connectors/github_client.py`
- `gateway/tests/test_github_client.py`
- `docs/quickstart.md`
- `docs/concepts/policies.md`
- `docs/TEST_REPORTS/2026-02-17-iteration2.md`
- `docs/PR_DRAFTS/2026-02-17-iteration2.md`

### Risks and mitigations
- Risk: retries could hide persistent misconfiguration.
  - Mitigation: retry only transient statuses/network failures; preserve clear final errors.
- Risk: increased latency under failure.
  - Mitigation: small capped attempts and bounded backoff.

### Rollback plan
- Revert connector retry helper and restore direct request behavior.

---

## Iteration 3 (2026-02-17): Idempotency Keys + SDK Approval Snippets

### Goal
Make write-path tool calls safe to retry from clients and improve SDK onboarding for approval-aware usage.

### Scope
- Quick Win: add copy-paste JS/Python SDK snippets that show denied/pending-approved flows.
- Moat Builder: add optional idempotency key support for `/v1/tool-calls` with response replay.

### Non-goals
- No distributed cache or cross-instance idempotency store.
- No API version bump.

### Files to change
- `gateway/src/schemas.py`
- `gateway/src/db.py`
- `gateway/src/main.py`
- `gateway/tests/test_gateway.py`
- `sdk/js/README.md`
- `sdk/python/README.md`
- `docs/quickstart.md`
- `docs/TEST_REPORTS/2026-02-17-iteration3.md`
- `docs/PR_DRAFTS/2026-02-17-iteration3.md`

### Risks and mitigations
- Risk: replaying stale errors could confuse users.
  - Mitigation: replay exact stored result with explicit `idempotent_replay=true` metadata.
- Risk: key collision across different request payloads.
  - Mitigation: bind key to request fingerprint and reject conflicts.

### Rollback plan
- Remove idempotency table and header handling; keep endpoint behavior unchanged.

---

## Iteration 4 (2026-02-18): Dev Helper + Policy Validation Guardrail

### Goal
Reduce local setup friction and prevent invalid policy files from reaching runtime.

### Scope
- Quick Win: add a root script that runs core checks in a stable order.
- Moat Builder: add policy validation CLI with strict checks and tests.

### Non-goals
- No full policy compiler.
- No policy migration/versioning system.

### Files to change
- `scripts/dev_check.sh`
- `gateway/scripts/validate_policy.py`
- `gateway/tests/test_policy_validate.py`
- `.github/workflows/ci.yml`
- `docs/quickstart.md`
- `docs/concepts/policies.md`
- `docs/TEST_REPORTS/2026-02-18-iteration4.md`
- `docs/PR_DRAFTS/2026-02-18-iteration4.md`

### Risks and mitigations
- Risk: overly strict validation blocks existing policy variants.
  - Mitigation: start with clear MVP schema and explicit error messages.
- Risk: local script drift from CI.
  - Mitigation: keep command set aligned with CI checks.

### Rollback plan
- Remove validator script from CI and keep runtime parser behavior unchanged.

---

## Iteration 5 (2026-02-18): Approval UX Bulk Actions + Audit Schema Versioning

### Goal
Speed up operator approval handling and make audit payloads explicitly versioned for future compatibility.

### Scope
- Quick Win: bulk approve/deny controls in UI and clearer status labels.
- Moat Builder: add `schema_version` to audit events and export, with SQLite-safe migration path.

### Non-goals
- No redesign of approval permissions model.
- No multi-version audit translation layer.

### Files to change
- `ui/src/App.jsx`
- `ui/src/styles.css`
- `ui/tests/app.test.jsx`
- `gateway/src/models.py`
- `gateway/src/db.py`
- `gateway/src/service.py`
- `gateway/src/schemas.py`
- `gateway/src/main.py`
- `gateway/tests/test_integration.py`
- `docs/concepts/audit.md`
- `docs/quickstart.md`
- `docs/TEST_REPORTS/2026-02-18-iteration5.md`
- `docs/PR_DRAFTS/2026-02-18-iteration5.md`

### Risks and mitigations
- Risk: existing SQLite files may miss new audit column.
  - Mitigation: add startup migration that creates missing column before requests.
- Risk: bulk UI actions may hide per-item failures.
  - Mitigation: execute actions sequentially and show first error immediately.

### Rollback plan
- Remove bulk controls from UI and stop emitting `schema_version` in responses.

---

## Iteration 6 (2026-02-18): Connector Authoring Guide + Contract Checks

### Goal
Make connector contributions faster and safer with explicit implementation guidance and contract verification.

### Scope
- Quick Win: strengthen connector docs and add a connector skeleton template.
- Moat Builder: define runtime-checkable connector contract and tests for GitHub connector compliance.

### Non-goals
- No connector plugin loader.
- No new production connector in this iteration.

### Files to change
- `docs/concepts/connectors.md`
- `docs/quickstart.md`
- `connectors/template/README.md`
- `gateway/src/connectors/contracts.py`
- `gateway/src/service.py`
- `gateway/tests/test_connector_contract.py`
- `docs/TEST_REPORTS/2026-02-18-iteration6.md`
- `docs/PR_DRAFTS/2026-02-18-iteration6.md`

### Risks and mitigations
- Risk: runtime protocol checks may be too generic.
  - Mitigation: keep explicit required method list and action mapping expectations in docs.
- Risk: docs/template drift from actual service behavior.
  - Mitigation: align template with `service._execute` action names and contract tests.

### Rollback plan
- Remove contract checks and keep docs-only guidance.

---

## Iteration 7 (2026-02-18): Bulk Approval API + Roadmap Refresh

### Goal
Reduce approval round-trips with a single bulk endpoint and keep roadmap signal aligned with shipped work.

### Scope
- Quick Win: update roadmap to reflect completed iterations and next priorities.
- Moat Builder: add `/v1/approvals/bulk` endpoint and switch UI bulk actions to use it.

### Non-goals
- No queue-based asynchronous approval executor.
- No role-based approval permissions in this iteration.

### Files to change
- `gateway/src/schemas.py`
- `gateway/src/main.py`
- `gateway/tests/test_integration.py`
- `ui/src/App.jsx`
- `docs/ROADMAP.md`
- `docs/quickstart.md`
- `docs/TEST_REPORTS/2026-02-18-iteration7.md`
- `docs/PR_DRAFTS/2026-02-18-iteration7.md`

### Risks and mitigations
- Risk: partial failures in bulk operations.
  - Mitigation: return per-ID outcomes and keep endpoint deterministic.
- Risk: UI and API drift.
  - Mitigation: UI relies on bulk response contract and falls back to refresh.

### Rollback plan
- Revert UI back to per-item approval calls and remove bulk endpoint.

---

## Iteration 8 (2026-02-18): Approval Reason Presets + Policy Wizard CLI Scaffold

### Goal
Increase approval speed and reduce policy authoring friction with safe templates.

### Scope
- Quick Win: add approval reason presets in UI for single and bulk decisions.
- Moat Builder: add a minimal CLI to generate policy templates for common scenarios.

### Non-goals
- No interactive TUI.
- No full policy editor or policy merge logic.

### Files to change
- `ui/src/App.jsx`
- `ui/src/styles.css`
- `ui/tests/app.test.jsx`
- `gateway/scripts/policy_wizard.py`
- `gateway/tests/test_policy_wizard.py`
- `docs/concepts/policies.md`
- `docs/quickstart.md`
- `docs/TEST_REPORTS/2026-02-18-iteration8.md`
- `docs/PR_DRAFTS/2026-02-18-iteration8.md`

### Risks and mitigations
- Risk: preset text may be too opinionated.
  - Mitigation: keep presets short and editable before submission.
- Risk: wizard-generated policy may be over-permissive.
  - Mitigation: generated templates keep deny-by-default and explicit repo scope.

### Rollback plan
- Remove presets and wizard script while keeping core approval/policy flows unchanged.

---

## Iteration 9 (2026-02-18): Health/Readiness Probes + Real-Mode Safety Tests

### Goal
Improve operational readiness signals and provide optional safety checks for real GitHub mode.

### Scope
- Quick Win: add `/ready` endpoint and compose healthchecks.
- Moat Builder: add optional real-mode integration tests gated by explicit env vars.

### Non-goals
- No production-grade synthetic monitoring stack.
- No destructive real-mode write tests.

### Files to change
- `gateway/src/main.py`
- `gateway/tests/test_integration.py`
- `gateway/tests/test_real_mode_safety.py`
- `connectors/github/mock_server.py`
- `docker-compose.yml`
- `scripts/smoke_mock_demo.sh`
- `docs/quickstart.md`
- `docs/deployment/docker.md`
- `docs/TEST_REPORTS/2026-02-18-iteration9.md`
- `docs/PR_DRAFTS/2026-02-18-iteration9.md`

### Risks and mitigations
- Risk: readiness checks may create false negatives in slower environments.
  - Mitigation: bounded retry loops and lightweight DB/policy checks only.
- Risk: real-mode tests could accidentally run in CI.
  - Mitigation: strict env gate (`REAL_GITHUB_ENABLE_TESTS=true` + token + repo).

### Rollback plan
- Revert `/ready` and compose healthcheck additions; keep `/health` unchanged.

---

## Iteration 10 (2026-02-18): UI Status Banner + Local Doctor Diagnostics

### Goal
Provide immediate runtime visibility in UI and a single local command to diagnose environment/setup issues.

### Scope
- Quick Win: add a status banner in UI using `/health` + `/ready` checks.
- Moat Builder: add `scripts/doctor.sh` for local diagnostics (docker, endpoints, policy validation, compose config).

### Non-goals
- No remote monitoring integration.
- No automatic remediation in doctor command.

### Files to change
- `ui/src/App.jsx`
- `ui/src/styles.css`
- `ui/tests/app.test.jsx`
- `scripts/doctor.sh`
- `docs/quickstart.md`
- `docs/deployment/docker.md`
- `docs/TEST_REPORTS/2026-02-18-iteration10.md`
- `docs/PR_DRAFTS/2026-02-18-iteration10.md`

### Risks and mitigations
- Risk: status banner may show transient false negatives during startup.
  - Mitigation: explicit loading/unknown state and clear refresh action.
- Risk: doctor command may fail in WSL without Docker integration.
  - Mitigation: treat missing/unusable docker as warning and continue checks.

### Rollback plan
- Remove status banner and doctor script while keeping `/health` and `/ready` endpoints.
