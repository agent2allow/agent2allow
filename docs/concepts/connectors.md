# How to Add a Connector

## Design rules
- Keep connector methods explicit and action-focused.
- Return structured dictionaries only (no raw HTTP responses).
- Treat write actions as high-friction by default (policy + approval aware).

## 1. Define actions
Add action IDs to `gateway/config/tools/<tool>.tool.json`.

## 2. Implement connector client
Create `gateway/src/connectors/<tool>_client.py` with one method per action.

Example method shape:
```python
def issues_list(self, repo: str, state: str = "open") -> dict:
    return {"issues": []}
```

## 3. Satisfy connector contract
- GitHub connector must satisfy `gateway/src/connectors/contracts.py::GithubConnectorContract`.
- Service construction rejects non-compliant connectors.

## 4. Wire execution
Map tool/action IDs to connector calls in `gateway/src/service.py::_execute`.

## 5. Policy and risk mapping
- Add rules to policy YAML with explicit `tool`, `actions`, `repo`, `risk`, and `allow`.
- Keep deny-by-default; require approval for medium/high risk actions.

## 6. Test requirements
- Connector unit tests for upstream interactions.
- Integration tests for `/v1/tool-calls` behavior (allow/deny/pending/executed).
- Contract test for required methods (`gateway/tests/test_connector_contract.py`).

## 7. Docs and example
- Add or update `examples/<your-agent>/`.
- Update quickstart and concept docs.
- Use `connectors/template/README.md` as baseline checklist.
