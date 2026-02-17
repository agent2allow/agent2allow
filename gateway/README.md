# Gateway

FastAPI service for policy enforcement, approvals, and audit logging.

## Structure
- `src/main.py`: API entrypoint
- `src/policy.py`: deny-by-default policy evaluation
- `src/service.py`: tool execution and approval orchestration
- `src/models.py`: SQLite models
- `tests/`: unit and integration tests
