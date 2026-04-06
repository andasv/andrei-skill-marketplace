"""Eltern-Portal authentication and session management."""

import os

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

_session: requests.Session | None = None


def _get_config() -> tuple[str, str, str]:
    url = os.environ.get("ELTERNPORTAL_URL", "").rstrip("/")
    user = os.environ.get("ELTERNPORTAL_USER", "")
    password = os.environ.get("ELTERNPORTAL_PASSWORD", "")
    if not url or not user or not password:
        raise RuntimeError(
            "Missing ELTERNPORTAL_URL, ELTERNPORTAL_USER, or ELTERNPORTAL_PASSWORD environment variables"
        )
    return url, user, password


def get_base_url() -> str:
    url, _, _ = _get_config()
    return url


def _login(session: requests.Session) -> None:
    url, user, password = _get_config()

    resp = session.get(url + "/")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf"})
    if not csrf_input:
        raise RuntimeError("Could not find CSRF token on login page")

    resp = session.post(
        url + "/includes/project/auth/login.php",
        data={
            "csrf": csrf_input["value"],
            "username": user,
            "password": password,
            "go_to": "",
        },
        headers={"Referer": url + "/", "Origin": url},
        allow_redirects=True,
    )
    resp.raise_for_status()
    if "form-signin" in resp.text:
        raise RuntimeError("Login failed — check credentials")


def _is_session_valid(session: requests.Session) -> bool:
    url = get_base_url()
    resp = session.get(url + "/", allow_redirects=False)
    return "form-signin" not in resp.text


def get_session() -> requests.Session:
    global _session
    if _session is not None and _is_session_valid(_session):
        return _session

    _session = requests.Session()
    _session.headers.update(_HEADERS)
    _login(_session)
    return _session


def reset_session() -> None:
    global _session
    _session = None
