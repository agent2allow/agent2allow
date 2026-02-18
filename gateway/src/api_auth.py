import json


class ApprovalApiKeyAuth:
    def __init__(self, *, enabled: bool, keys_json: str):
        self.enabled = enabled
        self.keys = self._parse_keys(keys_json)

    @staticmethod
    def _parse_keys(raw: str) -> dict[str, str]:
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("approval_api_keys must be a JSON object of key->identity")
        keys: dict[str, str] = {}
        for key, identity in parsed.items():
            if not isinstance(key, str) or not isinstance(identity, str):
                raise ValueError("approval_api_keys values must be strings")
            if not key:
                raise ValueError("approval_api_keys cannot contain an empty key")
            keys[key] = identity
        return keys

    def authenticate(self, provided_key: str | None) -> tuple[bool, str]:
        if not self.enabled:
            return True, ""
        if not provided_key:
            return False, "missing approval api key"
        identity = self.keys.get(provided_key, "")
        if not identity:
            return False, "invalid approval api key"
        return True, identity
