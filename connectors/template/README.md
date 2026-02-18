# Connector Template

Use this template when adding a new connector.

## 1. Define actions
Create `gateway/config/tools/<tool>.tool.json` and define action IDs.

## 2. Implement connector client
Add `gateway/src/connectors/<tool>_client.py` with explicit methods for each action.

Minimum pattern:
```python
class ExampleClient:
    def action_one(self, resource: str, **params) -> dict:
        # call upstream API and return structured dict
        return {"ok": True}
```

## 3. Wire action execution
Update `gateway/src/service.py::_execute` to map action IDs to connector methods.

## 4. Add policy rules
Add allow rules in policy YAML for tool/action/repo scope and risk.

## 5. Validate
- Add connector unit tests.
- Add integration tests hitting `/v1/tool-calls` with mocked upstream responses.
- Run `./scripts/dev_check.sh`.
