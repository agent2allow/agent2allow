# Incident Response (MVP)

## Severity Levels
- Sev 1: active unauthorized writes or credential exposure.
- Sev 2: policy bypass or approval flow failure without confirmed abuse.
- Sev 3: reliability-only degradation with no security impact.

## Initial Response
1. Freeze risky automation:
- disable write policy rules or set strict deny.

2. Rotate exposed credentials:
- revoke `GITHUB_TOKEN` and issue a new token.

3. Preserve evidence:
- export audit log (`GET /v1/audit/export`) and secure copy.

## Containment Actions
- Stop affected services if exploitation is active.
- Re-run policy validation and compare against known-good templates.
- Confirm `main` CI status and last trusted commit.

## Recovery
- Deploy patched version.
- Validate with smoke demo and targeted incident test.
- Communicate timeline and impact in the security report.

## Post-Incident
- Add regression tests for incident class.
- Update threat model and changelog.
- Track follow-up tasks in roadmap/issues.
