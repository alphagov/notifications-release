from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Flask, abort, redirect, render_template, session, url_for, send_from_directory
import humanize
import datetime as dt

from app import config, github_client

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

@app.template_filter()
def humanize_date(value):
    dt_value = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return humanize.naturaltime(dt.datetime.now() - dt_value)

oauth = OAuth(app)
oauth.register(
    name="github",
    client_id=config.GITHUB_CLIENT_ID,
    client_secret=config.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    client_kwargs={"scope": "repo read:user"},
)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("github_token"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def require_allowed_repo(owner, repo):
    if f"{owner}/{repo}" not in config.ALLOWED_REPOS:
        abort(403)

@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(app.static_folder + "/govuk/assets/", filename)

## AUTH ROUTES

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)


@app.route("/callback")
def auth_callback():
    token = oauth.github.authorize_access_token()
    profile = github_client.get_authenticated_user(token["access_token"])
    session["github_token"] = token["access_token"]
    session["github_user"] = profile["login"]
    return redirect(url_for("repos"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


## APPLICATION ROUTES

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session.get("github_user"))


@app.route("/repos")
@login_required
def repos():
    return render_template("repos.html", repos=config.ALLOWED_REPOS)


@app.route("/repos/<owner>/<repo>/commits")
@login_required
def repo_commits(owner, repo):
    require_allowed_repo(owner, repo)
    commits = github_client.list_commits(session["github_token"], owner, repo)
    return render_template("commits.html", owner=owner, repo=repo, commits=commits)

