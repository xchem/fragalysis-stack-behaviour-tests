from typing import Dict

import requests
from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template
from behave import given, then, when
from browser_utils import get_stack_client_id_secret, login

# To create a stack we need to know the names of templates (in the AWX server)
# that are responsible for its creation and destruction: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = "User (%(username)s) Developer Fragalysis Stack"
_AWX_STACK_WIPE_JOB_TEMPLATE: str = (
    "User (%(username)s) Developer Fragalysis Stack [WIPE]"
)

_REQUEST_TIMEOUT: int = 8


@given("an empty {stack_name} stack tagged {image_tag}")
def step_impl_00(context, stack_name, image_tag) -> None:
    """Wipe any existing stack content and create a new (empty) one.
    If successful it sets the following context members: -
    stack_name [e.g. 'behaviour']
    stack_url [e.g. https://example.com]
    """

    lower_stack_name = stack_name.lower()
    print(f"Creating stack '{lower_stack_name}'...")

    # The stack Client ID can be manufactured.
    # For developer stacks it looks like this: -
    #  "fragalysis-[awx-username]-[stack-name]-xchem-dev"
    #
    # So alan's behaviour stack client ID will be: -
    #  "fragalysis-alan-behaviour-xchem-dev"

    stack_oidc_rp_client_id: str = (
        f"fragalysis-{get_stack_username()}-{lower_stack_name}-xchem-dev"
    )

    extra_vars: Dict[str, str] = {
        "stack_name": lower_stack_name,
        "stack_image_tag": image_tag,
        "stack_oidc_rp_client_id": stack_oidc_rp_client_id,
        "stack_oidc_rp_client_secret": get_stack_client_id_secret(),
    }

    wipe_jt = _AWX_STACK_WIPE_JOB_TEMPLATE % {
        "username": get_stack_username().capitalize()
    }
    launch_awx_job_template(wipe_jt, extra_vars=extra_vars)

    create_jt = _AWX_STACK_CREATE_JOB_TEMPLATE % {
        "username": get_stack_username().capitalize()
    }
    launch_awx_job_template(create_jt, extra_vars=extra_vars)

    context.stack_name = lower_stack_name
    # The URL does not end with '/', so paths will need to start with '/'
    context.stack_url = get_stack_url(lower_stack_name)

    print(f"Created stack '{lower_stack_name}'")


@then("the stack landing page should return http {status_code:d}")
def step_impl_01(context, status_code) -> None:
    assert context.failed is False
    resp = requests.get(context.stack_url, timeout=_REQUEST_TIMEOUT)
    assert resp
    assert resp.status_code == status_code


@when("I call {method} on the {stack_name} stack")
def step_impl_02(context, method, stack_name) -> None:
    """Calls an API method on the stack, and sets up the following context members: -
    status_code
    response_count (optional)
    """
    assert context.failed is False
    context.stack_url = get_stack_url(stack_name.lower())
    print(context.stack_url)
    resp = requests.get(context.stack_url + method, timeout=_REQUEST_TIMEOUT)
    context.status_code = resp.status_code
    if isinstance(resp.json(), dict) and "count" in resp.json():
        context.response_count = resp.json().get("count")


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
    context.session_id = login()
    assert context.session_id
