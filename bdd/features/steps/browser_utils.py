import os
import re
from html import unescape
from typing import Optional

from playwright.sync_api import expect, sync_playwright

# Fragalysis Stack hostname (i.e. example.com) and credentials for a CAS user
_STACK_HOSTNAME: Optional[str] = os.environ.get("BEHAVIOUR_STACK_HOSTNAME")
_STACK_USERNAME: Optional[str] = os.environ.get("BEHAVIOUR_STACK_USERNAME")
_STACK_PASSWORD: Optional[str] = os.environ.get("BEHAVIOUR_STACK_PASSWORD")
_STACK_CLIENT_ID_SECRET: Optional[str] = os.environ.get(
    "BEHAVIOUR_STACK_CLIENT_ID_SECRET"
)

# How to find the session ID from the /api/token page...
_RE_SESSION_ID = re.compile(r"\"sessionid\": \"([a-z0-9]+)\"")


def get_stack_client_id_secret() -> str:
    """Returns the configured Client ID secret"""
    if not _STACK_CLIENT_ID_SECRET:
        raise ValueError("BEHAVIOUR_STACK_CLIENT_ID_SECRET is not set")
    return _STACK_CLIENT_ID_SECRET


def login() -> str:
    """Login to a Fragalysis Stack (with assumed CAS authentication)"""
    if not _STACK_HOSTNAME:
        raise ValueError("BEHAVIOUR_STACK_HOSTNAME is not set (e.g. example.com)")
    if not _STACK_USERNAME:
        raise ValueError("BEHAVIOUR_STACK_USERNAME is not set")
    if not _STACK_PASSWORD:
        raise ValueError("BEHAVIOUR_STACK_PASSWORD is not set")

    with sync_playwright() as spw:
        session_id_value: str = _run_login_logic_for_cas(
            spw,
            host=_STACK_HOSTNAME,
            user=_STACK_USERNAME,
            password=_STACK_PASSWORD,
        )
    return session_id_value


def _run_login_logic_for_cas(spw: sync_playwright, *, host, user, password) -> str:
    """Playwright logic to manage a login via CAS, returning the session ID"""
    browser = spw.chromium.launch()
    page = browser.new_page()

    base_url = f"https://{host}"
    login_url = f"{base_url}/accounts/login"
    print(f"Logging in using CAS to '{login_url}' (as '{user}')...")

    page.goto(login_url)
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_role("textbox", name="Username:").fill(user)
    page.get_by_role("textbox", name="Password:").fill(password)
    page.get_by_role("button", name="Login").click()

    print("Checking we're logged in...")
    landing_page = f"{base_url}/viewer/react/landing"
    page.goto(landing_page)
    expect(page.get_by_text("You're logged in")).to_be_visible()

    print("We're logged in!")

    print("Getting Session ID...")
    resp = page.goto(f"{base_url}/api/token")
    raw_text = unescape(resp.text())
    session_id_value: str = _RE_SESSION_ID.search(raw_text).group(1)
    print(f"Got Session ID")

    browser.close()

    return session_id_value


if __name__ == "__main__":
    session_id = login()
    print(session_id)