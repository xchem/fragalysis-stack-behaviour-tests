import requests
from behave import then

_REQUEST_TIMEOUT: int = 8


@then(
    "the stack landing page should return http {status_code:d}"
)  # pylint: disable=not-callable
def step_impl(context, status_code) -> None:
    """Just make sure the stack is up"""
    assert context.failed is False
    resp = requests.get(context.stack_url, timeout=_REQUEST_TIMEOUT)
    assert resp
    assert resp.status_code == status_code


@then(
    "the length of the returned list should be {count:d}"
)  # pylint: disable=not-callable
def step_impl(context, count) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    response_count"""
    assert context.failed is False
    assert context.response_count == count


@then("I should get http {status_code:d}")  # pylint: disable=not-callable
def step_impl(context, status_code) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    status_code"""
    assert context.failed is False
    assert context.status_code == status_code
