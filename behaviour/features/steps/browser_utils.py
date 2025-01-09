#!/usr/bin/env python
import re
from html import unescape

from awx_utils import get_stack_url
from config import (
    STACK_CLIENT_ID_SECRET,
    STACK_NAME,
    STACK_PASSWORD,
    STACK_USERNAME,
    get_env_name,
)

from playwright.sync_api import expect, sync_playwright

# How to find the session ID from the /api/token page...
_RE_SESSION_ID = re.compile(r"\"sessionid\": \"([a-z0-9]+)\"")


def get_stack_client_id_secret() -> str:
    """Returns the configured Client ID secret"""
    if not STACK_CLIENT_ID_SECRET:
        raise ValueError(get_env_name("STACK_CLIENT_ID_SECRET") + " is not set")
    return STACK_CLIENT_ID_SECRET


def get_stack_name() -> str:
    """Returns the configured stack name (lower case)"""
    if not STACK_NAME:
        raise ValueError(get_env_name("STACK_NAME") + " is not set")
    return STACK_NAME.lower()


def login(host_url: str) -> str:
    """Login to a Fragalysis Stack (with assumed CAS authentication)
    given a host url(i.e. https://example.com)"""
    if not STACK_USERNAME:
        raise ValueError(get_env_name("STACK_USERNAME") + " is not set")
    if not STACK_PASSWORD:
        raise ValueError(get_env_name("STACK_PASSWORD") + " is not set")

    with sync_playwright() as spw:
        session_id_value: str = _run_login_logic_for_cas(
            spw,
            host_url=host_url,
            user=STACK_USERNAME,
            password=STACK_PASSWORD,
        )
    return session_id_value


def _run_login_logic_for_cas(spw: sync_playwright, *, host_url, user, password) -> str:
    """Playwright logic to manage a login via CAS, returning the session ID.
    We're given a host URL (i.e. https://example.com), a user and a password."""
    browser = spw.chromium.launch()
    page = browser.new_page()

    login_url = f"{host_url}/accounts/login"
    print(f"Logging in using CAS to '{login_url}' (as '{user}')...")

    page.goto(login_url)
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_role("textbox", name="Username:").fill(user)
    page.get_by_role("textbox", name="Password:").fill(password)
    page.get_by_role("button", name="Login").click()

    print("Checking we're logged in...")
    landing_page = f"{host_url}/viewer/react/landing"
    page.goto(landing_page)
    expect(page.get_by_text("You're logged in")).to_be_visible()

    print("We're logged in!")

    print("Getting Session ID...")
    resp = page.goto(f"{host_url}/api/token")
    raw_text = unescape(resp.text())
    session_id_value: str = _RE_SESSION_ID.search(raw_text).group(1)
    print(f"Got Session ID ({session_id_value})")

    browser.close()

    return session_id_value


if __name__ == "__main__":
    session_id = login(get_stack_url("behaviour"))
    print(session_id)
