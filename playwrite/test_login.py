import os
from typing import Optional

from playwright.sync_api import Page, expect


_STACK_HOSTNAME: Optional[str] = os.environ.get('STACKTEST_STACK_HOSTNAME')
_STACK_USERNAME: Optional[str] = os.environ.get('STACKTEST_STACK_USERNAME')
_STACK_PASSWORD: Optional[str] = os.environ.get('STACKTEST_STACK_PASSWORD')

if not _STACK_HOSTNAME:
    raise ValueError("STACKTEST_STACK_HOSTNAME is not set (e.g. example.com)")
if not _STACK_USERNAME:
    raise ValueError("STACKTEST_STACK_USERNAME is not set")
if not _STACK_PASSWORD:
    raise ValueError("STACKTEST_STACK_PASSWORD is not set")


def _cas_login(page: Page) -> None:
    page.goto(f"https://{_STACK_HOSTNAME}/viewer/react/landing")
    page.get_by_role("button", name="Menu").click()
    page.get_by_role("button", name="Login").click()
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_label("Username:").fill(_STACK_USERNAME)
    page.get_by_label("Password: Toggle Password").click()
    page.get_by_label("Password: Toggle Password").fill(_STACK_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.get_by_role("button", name="Menu").click()
    expect(page.get_by_role("button", name="Logout")).to_be_visible()


def test_cas_login(page: Page) -> None:
    _cas_login(page)
