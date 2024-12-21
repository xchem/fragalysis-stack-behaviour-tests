import requests
from behave import then
from browser_utils import login

_REQUEST_TIMEOUT: int = 8


@then("the stack landing page should return http {status_code:d}")
def step_impl_01(context, status_code) -> None:
    assert context.failed is False
    resp = requests.get(context.stack_url, timeout=_REQUEST_TIMEOUT)
    assert resp
    assert resp.status_code == status_code


@then("the length of the returned list should be {count:d}")
def step_impl_03(context, count) -> None:
    """Relies on context members: -
    response_count"""
    assert context.failed is False
    assert context.response_count == count


@then("I should get http {status_code:d}")
def step_impl_04(context, status_code) -> None:
    """Relies on context members: -
    status_code"""
    assert context.failed is False
    assert context.status_code == status_code


@then("I can login")
def step_impl_05(context) -> None:
    """Relies on context members: -
    status_code"""
    assert context.failed is False
    context.session_id = login("1234")
    assert context.session_id
