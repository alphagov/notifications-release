# GOVUK Notify Release app

This application allows users to see information about releases on GOVUK Notify.

## Getting started

### Set up virtual environment

```
make venv
```

### Configure GitHub login

1. Register an OAuth App at https://github.com/settings/developers with an
   Authorization callback URL of `http://127.0.0.1:5000/callback`.
2. Copy `.env.example` to `.env` and fill in `GITHUB_CLIENT_ID`,
   `GITHUB_CLIENT_SECRET`, and a random `FLASK_SECRET_KEY`.
3. Add the repos users are allowed to view to `ALLOWED_REPOS` in
   `app/config.py`.

### Run the application

```
make run
```
