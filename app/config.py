import os

from dotenv import load_dotenv

load_dotenv()

# Repos users are allowed to browse, regardless of what their GitHub token can access.
ALLOWED_REPOS = [
    { "id": "api", "name": "Notifications API", "repo": "alphagov/notifications-api" },
    { "id": "admin", "name": "Notifications Admin", "repo": "alphagov/notifications-admin" },
]

ENVIRONMENTS = [
    { "id": "production", "name": "Production", "url": "www.notifications.service.gov.uk" },
    { "id": "staging", "name": "Staging", "url": "www.staging-notify.works" }
]

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
