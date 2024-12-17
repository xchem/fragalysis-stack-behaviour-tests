import os
from typing import Optional

from behave import given, when, then

from awx_utils import launch_awx_job_template

# For stack testing to work we'll need a number of variables: -
_AWX_STACK_CREATE_JOB: Optional[str] = os.environ.get('STACKTEST_AWX_STACK_CREATE_JOB', 'User (Alan) Developer Fragalysis Stack')
_AWX_STACK_WIPE_JOB: Optional[str] = os.environ.get('STACKTEST_AWX_STACK_WIPE_JOB', 'User (Alan) Developer Fragalysis Stack [WIPE]')


@given('an empty {name} stack')
def step_impl(context, name):
    print(f"Wiping and creating stack '{name}'...")
    launch_awx_job_template(_AWX_STACK_WIPE_JOB, {"stack_name": name})
    launch_awx_job_template(_AWX_STACK_CREATE_JOB, {"stack_name": name})


@given('we have a stack installed')
def step_impl(context):
    pass


@then('there should be no targets')
def step_impl(context):
    assert context.failed is False
