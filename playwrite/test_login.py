import os
from typing import Optional

from playwright.sync_api import Page, expect

_STACK_HOSTNAME: Optional[str] = os.environ.get("BEHAVIOUR_STACK_HOSTNAME")
_STACK_USERNAME: Optional[str] = os.environ.get("BEHAVIOUR_STACK_USERNAME")
_STACK_PASSWORD: Optional[str] = os.environ.get("BEHAVIOUR_STACK_PASSWORD")
_STACK_KC_USERNAME: Optional[str] = os.environ.get("BEHAVIOUR_STACK_KC_USERNAME")
_STACK_KC_PASSWORD: Optional[str] = os.environ.get("BEHAVIOUR_STACK_KC_PASSWORD")

if not _STACK_HOSTNAME:
    raise ValueError("BEHAVIOUR_STACK_HOSTNAME is not set (e.g. example.com)")
if not _STACK_USERNAME:
    raise ValueError("BEHAVIOUR_STACK_USERNAME is not set")
if not _STACK_PASSWORD:
    raise ValueError("BEHAVIOUR_STACK_PASSWORD is not set")
if not _STACK_KC_USERNAME:
    raise ValueError("BEHAVIOUR_STACK_KC_USERNAME is not set")
if not _STACK_KC_PASSWORD:
    raise ValueError("BEHAVIOUR_STACK_KC_PASSWORD is not set")


def _cas_login(page: Page) -> None:

    page.goto(f"https://{_STACK_HOSTNAME}/accounts/login")
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_role("textbox", name="Username:").fill(_STACK_USERNAME)
    page.get_by_role("textbox", name="Password:").fill(_STACK_PASSWORD)
    page.get_by_role("button", name="Login").click()

    page.goto(f"https://{_STACK_HOSTNAME}/viewer/react/landing")
    expect(page.get_by_text("You're logged in")).to_be_visible()


def _keycloak_login(page: Page) -> None:

    page.goto(f"https://{_STACK_HOSTNAME}/accounts/login")
    page.get_by_role("textbox", name="Username or email").fill(_STACK_KC_USERNAME)
    page.get_by_role("textbox", name="Password").fill(_STACK_KC_PASSWORD)
    page.get_by_role("button", name="Sign In").click()

    page.goto(f"https://{_STACK_HOSTNAME}/viewer/react/landing")
    expect(page.get_by_text("You're logged in")).to_be_visible()


def test_cas_login(page: Page) -> None:
    _cas_login(page)


def test_keycloak_login(page: Page) -> None:
    _keycloak_login(page)
