import json
from typing import Dict

from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template
from behave import given
from browser_utils import get_stack_client_id_secret, login
from s3_utils import check_bucket

# To create a stack we need to know the names of templates (in the AWX server)
# that are responsible for its creation and destruction: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = "User (%(username)s) Developer Fragalysis Stack"
_AWX_STACK_WIPE_JOB_TEMPLATE: str = (
    "User (%(username)s) Developer Fragalysis Stack [WIPE]"
)


@given("an empty {stack_name} stack tagged {image_tag}")  # pylint: disable=not-callable
def step_impl(context, stack_name, image_tag) -> None:
    """Wipe any existing stack content and create a new (empty) one.
    The user can pass in a JSON-encoded set of extra variables
    via the context.text attribute. This appears as a string.

    If successful it sets the following context members: -
    - stack_name (e.g. 'behaviour')
    - stack_url (e.g. https://example.com)
    """
    assert context.failed is False

    lower_stack_name = stack_name.lower()
    print(f"Creating stack '{lower_stack_name}'...")

    # The stack Client ID can be manufactured.
    # For developer stacks it looks like this: -
    #  "fragalysis-[awx-username]-[stack-name]-xchem-dev"
    #
    # So alan's behaviour stack client ID will be: -
    #  "fragalysis-alan-behaviour-xchem-dev"

    stack_oidc_rp_client_id: str = (
        f"fragalysis-{get_stack_username().lower()}-{lower_stack_name}-xchem-dev"
    )

    extra_vars: Dict[str, str] = {
        "stack_name": lower_stack_name,
        "stack_image_tag": image_tag,
        "stack_oidc_rp_client_id": stack_oidc_rp_client_id,
        "stack_oidc_rp_client_secret": get_stack_client_id_secret(),
    }

    # If the user has passed in extra variables, merge them in.
    if context.text:
        print(context.text)
        step_vars = json.loads(context.text)
        extra_vars |= step_vars
        print(f"Using step text as extra variables: {step_vars}")

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


@given("I can login to the {stack_name} stack")  # pylint: disable=not-callable
def step_impl(context, stack_name) -> None:  # pylint: disable=function-redefined
    """Sets the context members: -
    - stack_name
    - session_id"""
    assert context.failed is False

    context.stack_name = stack_name.lower()
    context.session_id = login(get_stack_url(context.stack_name))
    assert context.session_id


@given("I do not login to the {stack_name} stack")  # pylint: disable=not-callable
def step_impl(context, stack_name) -> None:  # pylint: disable=function-redefined
    """Sets the context members: -
    - stack_name"""
    assert context.failed is False

    context.stack_name = stack_name.lower()


@given("I can access the {bucket_name} bucket")  # pylint: disable=not-callable
def step_impl(context, bucket_name) -> None:  # pylint: disable=function-redefined
    """Just make sure we can access the bucket and ets the context members: -
    - bucket_name"""
    assert context.failed is False

    check_bucket(bucket_name)
    context.bucket_name = bucket_name
