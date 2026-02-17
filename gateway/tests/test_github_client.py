import httpx
import pytest
import respx
from httpx import Response

from src.connectors.github_client import GithubClient


@respx.mock
def test_list_issues_retries_on_500(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    route = respx.get("https://api.github.test/repos/acme/road/issues")
    route.side_effect = [
        Response(500, json={"message": "upstream error"}),
        Response(200, json=[{"number": 1}]),
    ]

    client = GithubClient("https://api.github.test", retry_attempts=3, retry_backoff_ms=1)
    payload = client.list_issues("acme/road")

    assert payload == {"issues": [{"number": 1}]}
    assert route.call_count == 2


@respx.mock
def test_set_labels_retries_on_429(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    route = respx.post("https://api.github.test/repos/acme/road/issues/1/labels")
    route.side_effect = [
        Response(429, json={"message": "rate limited"}),
        Response(200, json=["bug"]),
    ]

    client = GithubClient("https://api.github.test", retry_attempts=3, retry_backoff_ms=1)
    payload = client.set_labels("acme/road", 1, ["bug"])

    assert payload == {"labels": ["bug"]}
    assert route.call_count == 2


@respx.mock
def test_create_comment_raises_after_max_retries(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    route = respx.post("https://api.github.test/repos/acme/road/issues/1/comments")
    route.side_effect = httpx.ConnectError("network down")

    client = GithubClient("https://api.github.test", retry_attempts=2, retry_backoff_ms=1)

    with pytest.raises(httpx.ConnectError):
        client.create_comment("acme/road", 1, "hi")

    assert route.call_count == 2
