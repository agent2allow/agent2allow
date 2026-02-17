# Agent2Allow ExecPlan (MVP)

## 1. Ziel und Scope
MVP liefert ein OSS-first Open-Core Agent Gateway mit deny-by-default Enforcement, optionalem Human Approval für riskante Aktionen und auditierbaren Tool-Calls.
Hero Use Case: GitHub Triage Agent (Issues lesen, labeln, kommentieren).

## 2. Architektur
- `gateway/` (FastAPI): Policy-Enforcer, Tool-Execution-Pipeline, Approval-Flow, Audit-Storage/Export.
- `connectors/github/`: GitHub Connector + Mock GitHub API für lokale Demo.
- `ui/` (React/Vite): Pending Approvals (Approve/Deny) + Audit Log Viewer.
- `sdk/js` und `sdk/python`: dünne Clients gegen Gateway HTTP API.
- `examples/github-triage-agent`: Demo-Agent-Skript.
- `docker-compose.yml`: gateway + ui + mock-github.

## 3. Datenmodell (SQLite)
Tabellen:
- `approvals`
  - `id`, `status(pending|approved|denied|executed|failed)`, `tool`, `action`, `repo`, `risk_level`, `request_payload`, `result_payload`, `reason`, `created_at`, `updated_at`
- `audit_logs`
  - `id`, `timestamp`, `agent_id`, `tool`, `action`, `repo`, `risk_level`, `status(allowed|denied|pending_approval|executed|error|approved|denied_by_human)`, `request_payload`, `response_payload`, `approval_id`, `message`

## 4. Policy DSL (YAML)
Schema MVP:
- `version`
- `defaults.deny_by_default`
- `rules[]`
  - `tool`
  - `actions[]`
  - `repo` (glob)
  - `risk` (`read|low|medium|high`)
  - `allow` (bool)
  - `approval_required` (bool, optional; sonst aus Risk-Level abgeleitet)

Regeln:
- Kein Match => deny.
- `allow: false` => deny.
- `medium/high` => approval required, sofern nicht explizit überschrieben.

## 5. API Endpoints
Gateway:
- `GET /health`
- `POST /v1/tool-calls`
  - Request: `agent_id, tool, action, repo, params`
  - Response:
    - denied
    - allowed executed result
    - pending approval + `approval_id`
- `GET /v1/approvals/pending`
- `POST /v1/approvals/{approval_id}/approve`
- `POST /v1/approvals/{approval_id}/deny`
- `GET /v1/audit`
- `GET /v1/audit/export` (JSONL)

Mock GitHub API:
- `GET /repos/{owner}/{repo}/issues`
- `POST /repos/{owner}/{repo}/issues/{number}/labels`
- `POST /repos/{owner}/{repo}/issues/{number}/comments`

## 6. Dateipfade
- `gateway/src/main.py` App/Routes
- `gateway/src/models.py` SQLAlchemy Models
- `gateway/src/schemas.py` Pydantic Schemas
- `gateway/src/policy.py` Policy Loader/Matcher
- `gateway/src/service.py` Tool-Execution, Approval, Audit
- `gateway/src/connectors/github_client.py`
- `gateway/config/default-policy.yml`
- `gateway/config/tools/github.tool.json`
- `gateway/tests/test_policy.py`
- `gateway/tests/test_integration.py`
- `connectors/github/mock_server.py`
- `ui/src/*`
- `ui/tests/*`
- `sdk/js/*`
- `sdk/python/*`
- `examples/github-triage-agent/triage.py`

## 7. Testplan
Unit:
- Policy matching (allow/deny, repo scope, risk + approval).

Integration:
- Tool call denied ohne passende Policy.
- Read action erlaubt und ausgeführt.
- Write action erzeugt pending approval.
- Approve führt Action aus + audit logs.
- Deny schreibt deny audit event.

UI smoke:
- Approvals list rendern.
- Audit list rendern.

## 8. Demo-Flow (10 Minuten)
1. `docker compose up --build -d`
2. Healthcheck prüfen.
3. `npm run demo` startet Triage gegen Gateway.
4. Demo zeigt:
   - denied call (falsches Repo)
   - allowed read
   - pending approvals für label/comment
5. Approvals per API/UI freigeben.
6. Audit im UI und JSONL Export prüfen.

## 9. Security & Compliance
- deny-by-default als Hard Default.
- Kein Secret Commit; Token nur via Env.
- Least-privilege Connector actions.
- Threat model kurz dokumentieren.
- Responsible disclosure in `SECURITY.md`.

## 10. Release-Checklist
- [ ] Tests grün (gateway + ui)
- [ ] Demo im Mock-Mode funktioniert
- [ ] Optionaler Real-Mode dokumentiert
- [ ] README + docs vollständig
- [ ] CI grün
- [ ] Keine toten Links
- [ ] Maximal 5 konkrete TODOs
