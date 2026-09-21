from app import config
import http.client
import json as JSON
import ssl
import certifi
from typing import TypedDict

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

class APIStatus(TypedDict):
    git_commit: str
    build_time: str
    db_version: str
    db_bulk_version: str
    status: str


class AdminStatus(TypedDict):
    git_commit: str
    build_time: str
    status: str


class Environment(TypedDict):
    id: str
    url: str
    name: str
    status: str
    api: APIStatus
    admin: AdminStatus

def get_all_environments() -> list[config.Environment]:
    return config.ENVIRONMENTS

def get_status_for_all_environments() -> list[Environment]:
    environments = get_all_environments()
    transformed_environments = []

    for environment in environments:
        conn = None
        try:
            conn = http.client.HTTPSConnection(environment["url"], context=SSL_CONTEXT)
            conn.request("GET", "/_status")
            response = conn.getresponse()

            if response.status == 200:
                environment["status"] = JSON.loads(response.read())
            else:
                environment["status"] = "unavailable"
        except Exception as e:
            environment["status"] = "error"
            print(e)
            print(f"Environment {environment['id']} is unavailable due to an exception")
        finally:
            if conn is not None:
                conn.close()

        status = environment.get("status")
        available = status not in ("error", "unavailable")

        transformed_environments.append({
            "id": environment.get("id"),
            "url": environment.get("url"),
            "name": environment.get("name"),
            "status": status.get("status") if available else status,
            "api": {
                "git_commit": status.get("api", {}).get("git_commit") if available else None,
                "build_time": status.get("api", {}).get("build_time") if available else None,
                "db_version": status.get("api", {}).get("db_version") if available else None,
                "db_bulk_version": status.get("api", {}).get("db_bulk_version") if available else None,
                "status": status.get("api", {}).get("status") if available else None,
            },
            "admin": {
                "git_commit": status.get("git_commit") if available else None,
                "build_time": status.get("build_time") if available else None,
                "status": status.get("status") if available else None,
            },
        })

    return transformed_environments
