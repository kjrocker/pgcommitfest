import json

import pytest

from pgcommitfest.commitfest.models import CommitFest

pytestmark = pytest.mark.django_db


def assert_json_error(response, status):
    assert response.status_code == status
    assert response["Content-Type"] == "application/json"
    assert response["Access-Control-Allow-Origin"] == "*"
    data = json.loads(response.content)
    assert set(data) == {"error"}
    assert data["error"]
    return data["error"]


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/commitfests/999999/patches",
        "/api/v1/patches/999999/threads",
    ],
)
def test_missing_object_returns_json_404(client, path):
    assert_json_error(client.get(path), 404)


def test_unknown_api_url_returns_json_404(client):
    error = assert_json_error(client.get("/api/v1/nope"), 404)
    assert error == "Not found"


def test_non_api_404_is_still_html(client, commitfests):
    response = client.get("/patch/999999/")
    assert response.status_code == 404
    assert response["Content-Type"].startswith("text/html")


def test_unhandled_exception_returns_json_500(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("secret detail")

    monkeypatch.setattr(CommitFest.objects, "order_by", boom)
    client.raise_request_exception = False

    error = assert_json_error(client.get("/api/v1/commitfests"), 500)
    assert error == "Internal server error"
