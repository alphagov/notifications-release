import os

from dotenv import load_dotenv

load_dotenv()

# Repos users are allowed to browse, regardless of what their GitHub token can access.
ALLOWED_REPOS = [
    "alphagov/notifications-api",
    "alphagov/notifications-admin",
]

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
