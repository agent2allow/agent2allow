# How to Add a Connector

## 1. Define actions
Add actions and default risk metadata to a tool descriptor:
- `gateway/config/tools/<tool>.tool.json`

## 2. Implement connector client
Create a connector in `gateway/src/connectors/` with explicit methods per action.

## 3. Wire execution
Map the new tool/actions in `gateway/src/service.py::_execute`.

## 4. Add policy rules
Update YAML policy to allow required actions and scopes.

## 5. Test
- Unit-test policy behavior for new action names.
- Integration-test gateway endpoint with mocked upstream API.

## 6. Demo and docs
- Add an example in `examples/`.
- Update quickstart and security notes.
