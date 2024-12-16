"""Behaviour test fixtures for AWX servers.

For these fixtures to work you will need to provide sensitive credentials and
host names using a number of environment variables.

There are fixtures here to deploy and wipe Fragalysis Stack instances using
Job Templates configured on the corresponding AWX server. Creating stacks will take
some time (typically 3 to 4 minutes).
"""
from datetime import datetime
import os
from typing import Optional

import awxkit
from awxkit.api import job_templates, jobs
from behave import fixture

# For AWX-based stack deployment to work we'll need a number of variables: -
_AWX_HOSTNAME: Optional[str] = os.environ.get('STACKTEST_AWX_HOSTNAME')
_AWX_USERNAME: Optional[str] = os.environ.get('STACKTEST_AWX_USERNAME')
_AWX_PASSWORD: Optional[str] = os.environ.get('STACKTEST_AWX_PASSWORD')
_AWX_STACK_CREATE_JOB: Optional[str] = os.environ.get('STACKTEST_AWX_STACK_CREATE_JOB', 'User (Alan) Developer Fragalysis Stack')
_AWX_STACK_WIPE_JOB: Optional[str] = os.environ.get('STACKTEST_AWX_STACK_WIPE_JOB', 'User (Alan) Developer Fragalysis Stack [WIPE]')

if not _AWX_HOSTNAME:
    raise ValueError("STACKTEST_AWX_HOSTNAME is not set (e.g. example.com)")
if not _AWX_USERNAME:
    raise ValueError("STACKTEST_AWX_USERNAME is not set")
if not _AWX_PASSWORD:
    raise ValueError("STACKTEST_AWX_PASSWORD is not set")


def _launch_test_stack():
    """Use AWX and the named JobTemplate to create a stack."""

    awxkit.config.base_url = f"https://{_AWX_HOSTNAME}"
    awxkit.config.credentials = awxkit.utils.PseudoNamespace(
        {'default': {'username': _AWX_USERNAME, 'password': _AWX_PASSWORD}}
    )
    awx_api = awxkit.api.Api()
    awx_api.load_session().get()
    awx_client = awx_api.available_versions.v2.get()
    assert awx_client
    job_template = awx_client.job_templates.get(name=_AWX_STACK_CREATE_JOB).results[0]
    assert job_template

    print(f"Creating the test stack ({datetime.now()})...")
    _ = job_templates.JobTemplate.launch(job_template)
    job_running = True
    job_success = True
    while job_running and job_success:
        # Get the job status
        status = jobs.JobEvent.get(job_template).status
        if  status == "successful":
            print("Job completed Successful")
            job_running = False
        elif status == "failed":
            print("Stack launch failed. Check the AWX server")
            job_success = False
    print(f"Test stack is ready ({datetime.now()})")


def _wipe_test_stack():
    """Use AWX and the named JobTemplate to wipe a stack."""

    awxkit.config.base_url = f"https://{_AWX_HOSTNAME}"
    awxkit.config.credentials = awxkit.utils.PseudoNamespace(
        {'default': {'username': _AWX_USERNAME, 'password': _AWX_PASSWORD}}
    )
    awx_api = awxkit.api.Api()
    awx_api.load_session().get()
    awx_client = awx_api.available_versions.v2.get()
    assert awx_client
    job_template = awx_client.job_templates.get(name=_AWX_STACK_WIPE_JOB).results[0]
    assert job_template

    print(f"Wiping the test stack ({datetime.now()})...")
    _ = job_templates.JobTemplate.launch(job_template)
    job_running = True
    job_success = True
    while job_running and job_success:
        # Get the job status
        status = jobs.JobEvent.get(job_template).status
        if  status == "successful":
            print("Job completed Successful")
            job_running = False
        elif status == "failed":
            print("Stack wipe failed. Check the AWX server")
            job_success = False
    assert job_success
    print(f"Test stack wiped ({datetime.now()})")


@fixture
def create_stack(context):
    """Wipes and then creates an empty stack prior to yielding to the test
    (leaving the stack deployed).
    """

    # Setup
    _wipe_test_stack()
    _launch_test_stack()
    context.stack_url = 'https://example.com'

    yield context.stack_url

    # Teardown
