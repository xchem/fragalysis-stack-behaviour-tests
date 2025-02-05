from config import (
    STACK_HOSTNAME,
    STACK_KC_PASSWORD,
    STACK_KC_USERNAME,
    STACK_PASSWORD,
    STACK_USERNAME,
)

from playwright.sync_api import Page, expect


def test_cas_login(page: Page) -> None:
    _cas_login(page)


def test_keycloak_login(page: Page) -> None:
    _keycloak_login(page)


# Local functions follow


def _cas_login(page: Page) -> None:

    page.goto(f"https://{STACK_HOSTNAME}/accounts/login")
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_role("textbox", name="Username:").fill(STACK_USERNAME)
    page.get_by_role("textbox", name="Password:").fill(STACK_PASSWORD)
    page.get_by_role("button", name="Login").click()

    page.goto(f"https://{STACK_HOSTNAME}/viewer/react/landing")
    expect(page.get_by_text("You're logged in")).to_be_visible()


def _keycloak_login(page: Page) -> None:

    page.goto(f"https://{STACK_HOSTNAME}/accounts/login")
    page.get_by_role("textbox", name="Username or email").fill(STACK_KC_USERNAME)
    page.get_by_role("textbox", name="Password").fill(STACK_KC_PASSWORD)
    page.get_by_role("button", name="Sign In").click()

    page.goto(f"https://{STACK_HOSTNAME}/viewer/react/landing")
    expect(page.get_by_text("You're logged in")).to_be_visible()
