#!/usr/bin/env python
"""Utilities for interacting with the fragalysis UI that are normally accomplished
via a browser, such as logging in. Underlying logic is handled by playwright.
"""
import re
from html import unescape

from awx_utils import get_stack_url
from config import (
    DJANGO_SUPERUSER_PASSWORD,
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


def login(host_url: str, login_type: str = "cas") -> str:
    """Login to a Fragalysis Stack (with assumed CAS authentication)
    given a host url(i.e. https://example.com)."""
    if not STACK_USERNAME:
        raise ValueError(get_env_name("STACK_USERNAME") + " is not set")
    if not STACK_PASSWORD:
        raise ValueError(get_env_name("STACK_PASSWORD") + " is not set")

    assert login_type in {"cas", "django"}

    session_id_value: str = ""
    with sync_playwright() as spw:
        if login_type == "cas":
            session_id_value = _run_login_logic_for_cas(
                spw,
                host_url=host_url,
                user=STACK_USERNAME,
                password=STACK_PASSWORD,
            )
        elif login_type == "django":
            session_id_value = _run_login_logic_for_django(
                spw,
                host_url=host_url,
                user="admin",
                password=DJANGO_SUPERUSER_PASSWORD,
            )
        else:
            raise ValueError(f"Unknown login type: {login_type}")

    return session_id_value


# Local functions --------------------------------------------------------------


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


def _run_login_logic_for_django(
    spw: sync_playwright, *, host_url, user, password
) -> str:
    """Playwright logic to manage a login via the Django admin panel.
    There is no session here."""
    browser = spw.chromium.launch()
    page = browser.new_page()

    login_url = f"{host_url}/admin/login"
    print(f"Logging in using Django admin to '{login_url}' (as '{user}')...")

    page.goto(login_url)
    page.get_by_role("textbox", name="Username:").fill(user)
    page.get_by_role("textbox", name="Password:").fill(password)
    page.get_by_role("button", name="Log in").click()

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
