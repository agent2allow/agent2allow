# Contributing

Thanks for contributing to Agent2Allow.

## Development Setup
1. Start local services:
   - `docker compose up --build -d`
2. Run gateway tests:
   - `cd gateway && pytest`
3. Run UI tests:
   - `cd ui && npm ci && npm test`

## Pull Request Rules
- Keep changes focused and documented.
- Add or update tests for behavior changes.
- Include security impact notes when relevant.
- Update docs for API/policy/workflow changes.

## Security Hygiene
- Never commit secrets, tokens, private keys, or `.env` files.
- Use environment variables for credentials.
- Redact sensitive values from logs and screenshots.
