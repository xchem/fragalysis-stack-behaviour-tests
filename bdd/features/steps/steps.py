from behave import given, when, then

from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template

# For stack testing to work we'll need a number of variables: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = 'User (%(username)s) Developer Fragalysis Stack'
_AWX_STACK_WIPE_JOB_TEMPLATE: str = 'User (%(username)s) Developer Fragalysis Stack [WIPE]'



@given('an empty {stack_name} stack')
def step_impl(context, stack_name) -> None:
    """Wipe any existing stack content and create a new (empty) one."""

    lower_stack_name = stack_name.lower()
    print(f"Initialising stack '{lower_stack_name}'...")

    wipe_jt = _AWX_STACK_WIPE_JOB_TEMPLATE % {"username": get_stack_username().capitalize()}
    launch_awx_job_template(wipe_jt, extra_vars={"stack_name": lower_stack_name})

    create_jt = _AWX_STACK_CREATE_JOB_TEMPLATE % {"username": get_stack_username().capitalize()}
    launch_awx_job_template(create_jt, extra_vars={"stack_name": lower_stack_name})

    context.stack_name = lower_stack_name
    context.stack_url = get_stack_url(lower_stack_name)


@given('we have a stack installed')
def step_impl(context) -> None:
    print(context)
    pass


@then('there should be {number:d} targets')
def step_impl(context, number) -> None:
    print(context)
    assert context.failed is False
