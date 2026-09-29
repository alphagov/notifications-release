import os

from dotenv import load_dotenv

load_dotenv()

class Environment:
    id: str
    name: str
    url: str

class Repo:
    id: str
    name: str
    repo: str

# Repos users are allowed to browse, regardless of what their GitHub token can access.
ALLOWED_REPOS: list[Repo] = [
    { "id": "notifications-admin", "name": "Admin", "repo": "alphagov/notifications-admin" },
    { "id": "notifications-antivirus", "name": "Antivirus", "repo": "alphagov/notifications-antivirus" },
    { "id": "notifications-api", "name": "API", "repo": "alphagov/notifications-api" },
    { "id": "notifications-aws", "name": "AWS", "repo": "alphagov/notifications-aws", "private": True },
    { "id": "notifications-aws-account-wide-terraform", "name": "AWS Account Wide Terraform", "repo": "alphagov/notifications-aws-account-wide-terraform", "private": True },
    { "id": "notifications-concourse", "name": "Concourse", "repo": "alphagov/notifications-concourse" },
    { "id": "notifications-concourse-deployment", "name": "Concourse Deployment", "repo": "alphagov/notifications-concourse-deployment" },
    { "id": "notifications-credentials", "name": "Credentials", "repo": "alphagov/notifications-credentials", "private": True },
    { "id": "document-download-api", "name": "Document Download API", "repo": "alphagov/document-download-api" },
    { "id": "document-download-frontend", "name": "Document Download Frontend", "repo": "alphagov/document-download-frontend" },
    { "id": "notifications-email-provider-stub", "name": "Email Provider Stub", "repo": "alphagov/notifications-email-provider-stub" },
    { "id": "notifications-functional-tests", "name": "Functional Tests", "repo": "alphagov/notifications-functional-tests" },
    { "id": "notifications-go-client", "name": "Go Client", "repo": "alphagov/notifications-go-client" },
    { "id": "notifications-java-client", "name": "Java Client", "repo": "alphagov/notifications-java-client" },
    { "id": "notifications-local", "name": "Local", "repo": "alphagov/notifications-local" },
    { "id": "notifications-net-client", "name": ".NET Client", "repo": "alphagov/notifications-net-client" },
    { "id": "notifications-node-client", "name": "Node Client", "repo": "alphagov/notifications-node-client" },
    { "id": "notifications-performance-tests", "name": "Performance Tests", "repo": "alphagov/notifications-performance-tests", "private": True },
    { "id": "notifications-php-client", "name": "PHP Client", "repo": "alphagov/notifications-php-client" },
    { "id": "notifications-private-assets", "name": "Private Assets", "repo": "alphagov/notifications-private-assets", "private": True },
    { "id": "notifications-python-client", "name": "Python Client", "repo": "alphagov/notifications-python-client" },
    { "id": "notifications-release", "name": "Release", "repo": "alphagov/notifications-release" },
    { "id": "notifications-ruby-client", "name": "Ruby Client", "repo": "alphagov/notifications-ruby-client" },
    { "id": "notifications-sms-provider-stub", "name": "SMS Provider Stub", "repo": "alphagov/notifications-sms-provider-stub" },
    { "id": "notifications-tech-docs", "name": "Tech Docs", "repo": "alphagov/notifications-tech-docs" },
    { "id": "notifications-template-preview", "name": "Template Preview", "repo": "alphagov/notifications-template-preview" },
    { "id": "notifications-tools", "name": "Tools", "repo": "alphagov/notifications-tools", "private": True },
    { "id": "notifications-utils", "name": "Utils", "repo": "alphagov/notifications-utils" },
]

ENVIRONMENTS: list[Environment] = [
    { "id": "production", "name": "Production", "url": "www.notifications.service.gov.uk" },
    { "id": "staging", "name": "Staging", "url": "www.staging-notify.works" },
]

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
