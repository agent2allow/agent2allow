# Security Policy

## Supported Versions
This project is pre-1.0. Security fixes are made on `main`.

## Responsible Disclosure
Please do not open public issues for vulnerabilities.

- Email: security@agent2allow.dev
- Include: reproduction steps, impact, suggested mitigation
- Response target: acknowledgement within 3 business days

## Safe Defaults
- Deny-by-default policy enforcement
- Write actions can require human approval
- Full audit trail for every tool call outcome
- No credentials in repository; secrets must come from environment variables

## Threat Model (MVP)
- Prompt/tool injection attempts to trigger unauthorized actions
- Over-scoped credentials used by agent runtime
- Missing traceability for sensitive operations

Mitigations in MVP:
- Central policy enforcement before connector execution
- Repo-scoped allow rules and risk-based approval gates
- SQLite audit log and JSONL export for post-incident analysis
