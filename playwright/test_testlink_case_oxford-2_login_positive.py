"""A test case from the M2MS Fragalysis Test Plan Execution Report.

Test Project: Fragalysis
Test Plan: Regression Test 4
Printed by TestLink on 11/14/2024
"""

from config import STACK_HOSTNAME, STACK_PASSWORD, STACK_USERNAME

from playwright.sync_api import Page, expect


def test_case(page: Page) -> None:

    # 1
    page.goto(f"https://{STACK_HOSTNAME}")
    page.get_by_role("button", name="Menu").click()
    page.get_by_role("button", name="Login").click()

    # 2
    page.get_by_role("link", name="Diamond CAS").click()
    page.get_by_role("textbox", name="Username:").fill(STACK_USERNAME)
    page.get_by_role("textbox", name="Password:").fill(STACK_PASSWORD)
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("You're logged in")).to_be_visible()
