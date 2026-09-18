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

    return environments
