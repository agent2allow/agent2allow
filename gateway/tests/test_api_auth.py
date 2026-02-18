import pytest

from src.api_auth import ApprovalApiKeyAuth


def test_api_auth_disabled_allows_missing_key():
    auth = ApprovalApiKeyAuth(enabled=False, keys_json="")
    allowed, identity = auth.authenticate(None)
    assert allowed is True
    assert identity == ""


def test_api_auth_enabled_requires_valid_key():
    auth = ApprovalApiKeyAuth(enabled=True, keys_json='{"k1":"alice"}')

    missing = auth.authenticate(None)
    invalid = auth.authenticate("wrong")
    valid = auth.authenticate("k1")

    assert missing == (False, "missing approval api key")
    assert invalid == (False, "invalid approval api key")
    assert valid == (True, "alice")


def test_api_auth_invalid_config_raises():
    with pytest.raises(ValueError):
        ApprovalApiKeyAuth(enabled=True, keys_json='["not-an-object"]')
