from typing import Optional

from behave import given, when, then
import requests

from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template

# For stack testing to work we'll need a number of variables: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = 'User (%(username)s) Developer Fragalysis Stack'
_AWX_STACK_WIPE_JOB_TEMPLATE: str = 'User (%(username)s) Developer Fragalysis Stack [WIPE]'

_REST_TIMEOUT: int = 8


@given("an empty {stack_name} stack")
def step_impl(context, stack_name) -> None:
    """Wipe any existing stack content and create a new (empty) one."""

    lower_stack_name = stack_name.lower()
    print(f"Initialising stack '{lower_stack_name}'...")

    wipe_jt = _AWX_STACK_WIPE_JOB_TEMPLATE % {"username": get_stack_username().capitalize()}
    launch_awx_job_template(wipe_jt, extra_vars={"stack_name": lower_stack_name})

    create_jt = _AWX_STACK_CREATE_JOB_TEMPLATE % {"username": get_stack_username().capitalize()}
    launch_awx_job_template(create_jt, extra_vars={"stack_name": lower_stack_name})

    context.stack_name = lower_stack_name
    # The URL does not end with '/', so paths will need to start with '/'
    context.stack_url = get_stack_url(lower_stack_name)


@given("the stack is responding")
def step_impl_00(context) -> None:
    resp = requests.get(context.stack_url, timeout=_REST_TIMEOUT)
    assert resp.status_code == 200


@then("there should be {number:d} targets")
def step_impl_01(context, number) -> None:
    assert context.failed is False
    path: str = "/api/targets/"
    resp = requests.get(context.stack_url + path, timeout=_REST_TIMEOUT)
    count: Optional[int] = resp.json().get("count")
    assert count == number
