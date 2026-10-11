import json

from app import config, environment_client


def make_environment():
    return {
        "id": "production",
        "name": "Production",
        "url": "production.example.com",
    }


def test_get_all_environments_returns_configured_environments(monkeypatch):
    environments = [make_environment()]
    monkeypatch.setattr(config, "ENVIRONMENTS", environments)

    assert environment_client.get_all_environments() is environments


def test_get_status_for_all_environments_transforms_successful_response(monkeypatch):
    environment = make_environment()
    payload = {
        "status": "ok",
        "git_commit": "admin-commit",
        "build_time": "admin-build-time",
        "api": {
            "git_commit": "api-commit",
            "build_time": "api-build-time",
            "db_version": "db-version",
            "db_bulk_version": "db-bulk-version",
            "status": "ok",
        },
    }
    connection_calls = {}

    class Response:
        status = 200

        def read(self):
            return json.dumps(payload).encode()

    class Connection:
        def __init__(self, host, timeout, context):
            connection_calls.update(host=host, timeout=timeout, context=context)

        def request(self, method, path):
            connection_calls.update(method=method, path=path)

        def getresponse(self):
            return Response()

        def close(self):
            connection_calls["closed"] = True

    monkeypatch.setattr(config, "ENVIRONMENTS", [environment])
    monkeypatch.setattr(environment_client.http.client, "HTTPSConnection", Connection)

    result = environment_client.get_status_for_all_environments()

    assert result == [
        {
            "id": "production",
            "url": "production.example.com",
            "name": "Production",
            "status": "ok",
            "api": {
                "git_commit": "api-commit",
                "build_time": "api-build-time",
                "db_version": "db-version",
                "db_bulk_version": "db-bulk-version",
                "status": "ok",
            },
            "admin": {
                "git_commit": "admin-commit",
                "build_time": "admin-build-time",
                "status": "ok",
            },
        }
    ]
    assert connection_calls == {
        "host": "production.example.com",
        "timeout": 5,
        "context": environment_client.SSL_CONTEXT,
        "method": "GET",
        "path": "/_status",
        "closed": True,
    }


def test_get_status_for_all_environments_marks_non_200_response_unavailable(
    monkeypatch,
):
    environment = make_environment()
    connection_state = {}

    class Response:
        status = 503

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args):
            pass

        def getresponse(self):
            return Response()

        def close(self):
            connection_state["closed"] = True

    monkeypatch.setattr(config, "ENVIRONMENTS", [environment])
    monkeypatch.setattr(environment_client.http.client, "HTTPSConnection", Connection)

    result = environment_client.get_status_for_all_environments()

    assert result == [
        {
            "id": "production",
            "url": "production.example.com",
            "name": "Production",
            "status": "unavailable",
            "api": {
                "git_commit": None,
                "build_time": None,
                "db_version": None,
                "db_bulk_version": None,
                "status": None,
            },
            "admin": {"git_commit": None, "build_time": None, "status": None},
        }
    ]
    assert connection_state == {"closed": True}


def test_get_status_for_all_environments_marks_connection_errors(monkeypatch, capsys):
    environment = make_environment()
    connection_state = {}

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args):
            raise OSError("connection failed")

        def close(self):
            connection_state["closed"] = True

    monkeypatch.setattr(config, "ENVIRONMENTS", [environment])
    monkeypatch.setattr(environment_client.http.client, "HTTPSConnection", Connection)

    result = environment_client.get_status_for_all_environments()

    assert result[0]["status"] == "error"
    assert result[0]["api"] == {
        "git_commit": None,
        "build_time": None,
        "db_version": None,
        "db_bulk_version": None,
        "status": None,
    }
    assert result[0]["admin"] == {
        "git_commit": None,
        "build_time": None,
        "status": None,
    }
    assert connection_state == {"closed": True}
    assert (
        "Environment production is unavailable due to an exception"
        in capsys.readouterr().out
    )
