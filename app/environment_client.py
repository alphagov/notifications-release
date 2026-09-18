from app import config
import http.client
import json as JSON
import ssl
import certifi

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

def get_all_environments():
    return config.ENVIRONMENTS

def get_status_for_all_environments():
    environments = get_all_environments()
    transformed_environments = []

    for environment in environments:
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
            conn.close()
            transformed_environments.append({
                "id": environment.get("id"),
                "url": environment.get("url"),
                "name": environment.get("name"),
                "status": environment.get("status").get("status"),
                "api": {
                    "git_commit": environment.get("status", {}).get("api", {}).get("git_commit"),
                    "build_time": environment.get("status", {}).get("api", {}).get("build_time"),
                    "db_version": environment.get("status", {}).get("api", {}).get("db_version"),
                    "db_bulk_version": environment.get("status", {}).get("api", {}).get("db_bulk_version"),
                    "status": environment.get("status", {}).get("api", {}).get("status")
                },
                "admin": {
                    "git_commit": environment.get("status", {}).get("git_commit"),
                    "build_time": environment.get("status", {}).get("build_time"),
                    "status": environment.get("status", {}).get("status"),
                },
            })

    return transformed_environments
