from typing import Dict

from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template
from behave import given
from browser_utils import get_stack_client_id_secret

# To create a stack we need to know the names of templates (in the AWX server)
# that are responsible for its creation and destruction: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = "User (%(username)s) Developer Fragalysis Stack"
_AWX_STACK_WIPE_JOB_TEMPLATE: str = (
    "User (%(username)s) Developer Fragalysis Stack [WIPE]"
)


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
