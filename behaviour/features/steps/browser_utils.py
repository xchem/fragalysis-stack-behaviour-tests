#!/usr/bin/env python
"""Utilities for interacting with the fragalysis UI that are normally accomplished
via a browser, such as logging in. Underlying logic is handled by playwright.
"""
import os
import re
from html import unescape

from config import (
    DJANGO_SUPERUSER_PASSWORD,
    ENV_PREFIX,
    STACK_PASSWORD,
    STACK_USERNAME,
    get_env_name,
)
from playwright.sync_api import expect, sync_playwright

# The playwright launch channel (i.e. Google Chrome?)
_PW_LAUNCH_CHANNEL: str = "chrome"

# How to find the session ID from the /api/token page...
_RE_SESSION_ID = re.compile(r"\"sessionid\": \"([a-z0-9]+)\"")


def login(
    host_url: str, *, login_type: str = "cas", login_username: str = "DEFAULT"
) -> str:
    """Login to a Fragalysis Stack (with assumed CAS authentication)
    given a host url(i.e. https://example.com).

    The default user is encapsulated int the 'STACK' environment variables
    'BEHAVIOUR_STACK_USERNAME' and 'BEHAVIOUR_STACK_PASSWORD'.
    If a username is supplied, that user's PASSWORD environment variable must be set
    using 'BEHAVIOUR_USER_<username>_PASSWORD' (e.g. the password for user 'a-b-c'
    is expected in 'BEHAVIOUR_USER_A_B_C_PASSWORD').

    You can also login using Keycloak's authentication system, using the login_type
    of 'keycloak' (or 'keycloak-fragalysis' if using the custom fragalysis Login theme).

    A 'superuser' login type is also supported. This logs in via the Django built-in
    authentication mechanism (the admin panel). It has a built-in username of 'admin'
    and a password that can be found in 'BEHAVIOUR_DJANGO_SUPERUSER_PASSWORD'.
    The login_username is ignored if the login_type is 'superuser'.
    """
    if not STACK_USERNAME:
        raise ValueError(get_env_name("STACK_USERNAME") + " is not set")
    if not STACK_PASSWORD:
        raise ValueError(get_env_name("STACK_PASSWORD") + " is not set")
    if not DJANGO_SUPERUSER_PASSWORD:
        raise ValueError(get_env_name("DJANGO_SUPERUSER_PASSWORD") + " is not set")

    assert login_type in {"cas", "keycloak", "keycloak-fragalysis", "superuser"}

    password: str = ""
    username: str = ""
    if login_type == "superuser":
        print("Logging in as 'admin'...")
        username = "admin"
        password = DJANGO_SUPERUSER_PASSWORD
    elif login_username == "DEFAULT":
        print("Logging in as 'DEFAULT'...")
        username = STACK_USERNAME
        password = STACK_PASSWORD
    elif login_username:
        print(f"Logging in as '{login_username}'...")
        username = login_username
        # Password ENV is the upper-case username
        # with hyphens replaced by under-bars.
        password_env: str = f"{ENV_PREFIX}USER_{username.upper()}_PASSWORD".replace(
            "-", "_"
        )
        password = os.environ.get(password_env)
        if not password:
            raise ValueError(f"{password_env} is not set")
    assert username
    assert password

    session_id_value: str = ""
    with sync_playwright() as spw:
        if login_type == "cas":
            session_id_value = _run_login_logic_for_cas(
                spw,
                host_url=host_url,
                user=username,
                password=password,
            )
        elif login_type == "keycloak":
            session_id_value = _run_login_logic_for_keycloak(
                spw,
                host_url=host_url,
                user=username,
                password=password,
            )
        elif login_type == "keycloak-fragalysis":
            session_id_value = _run_login_logic_for_keycloak_fragalysis(
                spw,
                host_url=host_url,
                user=username,
                password=password,
            )
        elif login_type == "superuser":
            session_id_value = _run_login_logic_for_superuser(
                spw,
                host_url=host_url,
                user=username,
                password=password,
            )
        else:
            raise ValueError(f"Unknown login type: {login_type}")

    return session_id_value


# Local functions --------------------------------------------------------------


def _run_login_logic_for_cas(spw: sync_playwright, *, host_url, user, password) -> str:
    """Playwright logic to manage a login via the keycloak federated authentication service
    CAS, returning the session ID. We're given a host URL (i.e. https://example.com),
    a user and a password."""
    browser = spw.chromium.launch(channel=_PW_LAUNCH_CHANNEL)
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


def _run_login_logic_for_keycloak(
    spw: sync_playwright, *, host_url, user, password
) -> str:
    """Playwright logic to manage a login via Keycloak (directly), returning the session ID.
    We're given a host URL (i.e. https://example.com), a user and a password."""
    browser = spw.chromium.launch(channel=_PW_LAUNCH_CHANNEL)
    page = browser.new_page()

    login_url = f"{host_url}/accounts/login"
    print(f"Logging in using Keycloak to '{login_url}' (as '{user}')...")

    page.goto(login_url)
    page.get_by_role("textbox", name="Username or email").fill(user)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Sign In").click()

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


def _run_login_logic_for_keycloak_fragalysis(
    spw: sync_playwright, *, host_url, user, password
) -> str:
    """Playwright logic to manage a login via our custom Keycloak theme, returning the session ID.
    We're given a host URL (i.e. https://example.com), a user and a password."""
    browser = spw.chromium.launch(channel=_PW_LAUNCH_CHANNEL)
    page = browser.new_page()

    login_url = f"{host_url}/accounts/login"
    print(f"Logging in using Keycloak to '{login_url}' (as '{user}')...")

    page.goto(login_url)
    page.get_by_text("Or click here to sign in with Keycloak...").click()
    page.get_by_role("textbox", name="username").fill(user)
    page.get_by_role("textbox", name="password").fill(password)
    page.get_by_role("button", name="Sign In").click()

    print("Checking we're logged in...")
    expect(page.get_by_text("You're logged in")).to_be_visible()

    print("We're logged in!")

    print("Getting Session ID...")
    resp = page.goto(f"{host_url}/api/token")
    raw_text = unescape(resp.text())
    session_id_value: str = _RE_SESSION_ID.search(raw_text).group(1)
    print(f"Got Session ID ({session_id_value})")

    browser.close()

    return session_id_value


def _run_login_logic_for_superuser(
    spw: sync_playwright, *, host_url, user, password
) -> str:
    """Playwright logic to manage a login via the Django admin panel.
    There is no session here."""
    browser = spw.chromium.launch(channel=_PW_LAUNCH_CHANNEL)
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
