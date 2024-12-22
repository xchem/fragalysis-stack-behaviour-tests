import requests
from awx_utils import get_stack_url
from behave import when

_REQUEST_TIMEOUT: int = 8


@when("I call {method} on the {stack_name} stack")
def step_impl_00(context, method, stack_name) -> None:
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
