"""Behaviour (behave) step definitions.

This file contains all the feature step definitions
rather than a separate file for given, when, then. This is because some steps
might be used (legitimately) for multiple types of steps (i.e. given and then).
"""

# Step Style Guide: -
#
# 1.    Implementation function names should be descriptive and unique
#       (to simplify navigation in editors like VS Code). An example might be
#       'the_length_of_the_list_in_the_response_should_be_x(context, count)',
#       using x, y, and z for the step variables (then m, n).
#
# 2.    Step string variables should normally be enclosed in double quotes,
#       i.e. "this is a string". This applies to the target access string
#       and any _naturel_ string like a title. Certainly anything that can contain spaces!

import http
import json
import os
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from api_utils import (
    api_get_request,
    create_session_project,
    create_snapshot,
    initiate_job_file_transfer,
    upload_target_experiment,
)
from awx_utils import get_stack_url, get_stack_username, launch_awx_job_template
from behave import given, then, when
from browser_utils import get_stack_client_id_secret, get_stack_name, login
from config import REQUEST_POLL_PERIOD_S, REQUEST_TIMEOUT
from s3_utils import check_bucket, get_object

# To create a stack we need to know the names of templates (in the AWX server)
# that are responsible for its creation and destruction: -
_AWX_STACK_CREATE_JOB_TEMPLATE: str = "User (%(username)s) Developer Fragalysis Stack"
_AWX_STACK_WIPE_JOB_TEMPLATE: str = (
    "User (%(username)s) Developer Fragalysis Stack [WIPE]"
)

_DOWNLOAD_PATH = "."


@given("an empty stack using the image tag {image_tag}")  # pylint: disable=not-callable
def an_empty_stack_using_the_image_tag_x(context, image_tag) -> None:
    """Wipe any existing stack content and create a new (empty) one.
    The user can pass in a JSON-encoded set of extra variables
    via the context.text attribute. This appears as a string.

    If successful it sets the following context members: -
    - stack_name (e.g. 'behaviour')
    - stack_url (e.g. https://example.com)
    """
    assert context.failed is False

    stack_name = get_stack_name()
    print(f"Creating stack '{stack_name}'...")

    # The stack Client ID can be manufactured.
    # For developer stacks it looks like this: -
    #  "fragalysis-[awx-username]-[stack-name]-xchem-dev"
    #
    # So alan's behaviour stack client ID will be: -
    #  "fragalysis-alan-behaviour-xchem-dev"

    stack_oidc_rp_client_id: str = (
        f"fragalysis-{get_stack_username().lower()}-{stack_name}-xchem-dev"
    )

    extra_vars: Dict[str, str] = {
        "stack_name": stack_name,
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

    context.stack_name = stack_name
    # The URL does not end with '/', so paths will need to start with '/'
    context.stack_url = get_stack_url(stack_name)

    print(f"Created stack '{stack_name}'")


@given("I can login")  # pylint: disable=not-callable
def i_can_login(context) -> None:
    """Sets the context members: -
    - stack_name
    - session_id"""
    assert context.failed is False

    context.stack_name = get_stack_name()
    context.session_id = login(get_stack_url(context.stack_name))
    assert context.session_id


@given("I do not login")  # pylint: disable=not-callable
def i_do_not_login(context) -> None:
    """Sets the context members: -
    - stack_name"""
    assert context.failed is False

    context.stack_name = get_stack_name()


@given('I can access the "{bucket_name}" bucket')  # pylint: disable=not-callable
def i_can_access_the_x_bucket(context, bucket_name) -> None:
    """Just make sure we can access the bucket and ets the context members: -
    - bucket_name"""
    assert context.failed is False

    check_bucket(bucket_name)
    context.bucket_name = bucket_name


@given('can get the "{title}" Target ID')  # pylint: disable=not-callable
def can_get_the_x_target_id(context, title) -> None:
    """Checks a Target exists and records its ID and relies on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - target_id"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    session_id = context.session_id if hasattr(context, "session_id") else None
    url_encoded_title = urllib.parse.quote(title)
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/targets?{url_encoded_title}",
        session_id=session_id,
    )
    assert resp.status_code == 200

    target_id = resp.json()["results"][0]["id"]
    print(f"target_id={target_id}")
    context.target_id = target_id


@given('can get the "{title}" Project ID')  # pylint: disable=not-callable
def can_get_the_x_project_id(context, title) -> None:
    """Checks a Project exists and records its ID and relies on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - project_id"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    session_id = context.session_id if hasattr(context, "session_id") else None
    url_encoded_title = urllib.parse.quote(title)
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/projects?{url_encoded_title}",
        session_id=session_id,
    )
    assert resp.status_code == 200

    project_id = resp.json()["results"][0]["id"]
    print(f"project_id={project_id}")
    context.project_id = project_id


@given('can get the "{title}" SessionProject ID')  # pylint: disable=not-callable
def can_get_the_x_session_project_id(context, title) -> None:
    """Checks a SessionProject exists and records its ID relying on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - session_project_id"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    print(f"Getting SessionProject ID for '{title}'...")
    session_id = context.session_id if hasattr(context, "session_id") else None
    url_encoded_title = urllib.parse.quote(title)
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/session-projects?{url_encoded_title}",
        session_id=session_id,
    )
    assert resp.status_code == 200

    session_project_id = resp.json()["results"][0]["id"]
    print(f"Got session_project_id={session_project_id}")
    context.session_project_id = session_project_id


@given('can get the "{title}" Snapshot ID')  # pylint: disable=not-callable
def can_get_the_x_snapshot_id(context, title) -> None:
    """Checks a Snapshot exists and records its ID relying on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - snapshot_id"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    print(f"Getting Snapshot ID for '{title}'...")
    session_id = context.session_id if hasattr(context, "session_id") else None
    url_encoded_title = urllib.parse.quote(title)
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/snapshots?{url_encoded_title}",
        session_id=session_id,
    )
    assert resp.status_code == 200

    snapshot_id = resp.json()["results"][0]["id"]
    print(f"Got snapshot_id={snapshot_id}")
    context.snapshot_id = snapshot_id


@then(  # pylint: disable=not-callable
    "the landing page response should be {status_code_name}"
)
def the_landing_page_response_should_be_x(context, status_code_name) -> None:
    """Just make sure the stack is up, and relies on context members: -
    - stack_url"""
    assert context.failed is False
    assert hasattr(context, "stack_url")

    resp = requests.get(context.stack_url, timeout=REQUEST_TIMEOUT)
    assert resp

    expected_code = http.HTTPStatus[status_code_name].value
    if resp.status_code != expected_code:
        print(f"Expected status code {expected_code}, got {resp.status_code}")
        assert resp.status_code == expected_code


@then(  # pylint: disable=not-callable
    "the length of the list in the response should be {count:d}"
)
def the_length_of_the_list_in_the_response_should_be_x(context, count) -> None:
    """Relies on context members: -
    - response_count"""
    assert context.failed is False
    assert hasattr(context, "response_count")

    if context.response_count != count:
        print(f"Expected response list size of {count}, got {context.response_count}")
        assert context.response_count == count


@then("the response should be {status_code_name}")  # pylint: disable=not-callable
def the_response_should_be_x(context, status_code_name) -> None:
    """Relies on context members: -
    - status_code"""
    assert context.failed is False
    assert hasattr(context, "status_code")

    expected_status_code = http.HTTPStatus[status_code_name].value
    if context.status_code != expected_status_code:
        print(
            f"Expected status code {expected_status_code} ({status_code_name}),"
            f" got {context.status_code}"
        )
        assert context.status_code == expected_status_code


@then(  # pylint: disable=not-callable
    "the response should contain a task status endpoint"
)
def the_response_should_contain_a_task_status_endpoint(context) -> None:
    """Relies on context members: -
    - response
    And Sets the context properties: -
    - task_status_endpoint
    """
    assert context.failed is False
    assert hasattr(context, "response")

    data: Dict[str, Any] = context.response.json()
    assert "task_status_url" in data
    task_status_endpoint: str = data["task_status_url"]
    assert task_status_endpoint.startswith("/viewer/task_status/")

    print(f"Got task status URL ({task_status_endpoint})")
    context.task_status_endpoint = task_status_endpoint


@then(  # pylint: disable=not-callable
    "the task status should have a value of {status} within {timeout_m:d} minutes"
)
def the_task_should_have_a_value_of_x_within_y_minutes(
    context, status, timeout_m
) -> None:
    """Relies on context members: -
    - session_id
    - stack_url
    - task_status_endpoint
    """
    assert timeout_m > 0

    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_url")
    assert hasattr(context, "task_status_endpoint")

    start_time = datetime.now()
    timeout_period = timedelta(minutes=timeout_m)

    print(f"Waiting for task at {context.task_status_endpoint} [{start_time}]...")

    done: bool = False
    data: Optional[Dict[str, Any]] = None
    now: datetime = start_time
    while not done:

        # Get the task status.
        # The response normally contains the following properties: -
        # - started (boolean)
        # - finished (boolean)
        # - status (i.e. RUNNING, SUCCESS)
        # - messages (a list of strings)
        resp = api_get_request(
            base_url=context.stack_url,
            endpoint=context.task_status_endpoint,
            session_id=context.session_id,
        )
        assert resp.status_code == http.HTTPStatus["OK"].value

        data = resp.json()
        if "finished" in data and data["finished"]:
            print("Task upload has finished")
            done = True
        else:
            now = datetime.now()
            assert now - start_time <= timeout_period
            time.sleep(REQUEST_POLL_PERIOD_S)

    print(f"Finished waiting [{now}]")

    assert data
    assert "status" in data
    task_status = data["status"]
    print(f"Task status is {task_status}")
    assert task_status == status


@when("I do a {method} request at {endpoint}")  # pylint: disable=not-callable
def i_do_a_x_request_at_y(context, method, endpoint) -> None:
    """Makes a REST request on an endpoint. Relies on context members: -
    - stack_name
    Sets the following context members: -
    - stack_url
    - status_code
    - response
    - response_count (optional)
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")

    context.stack_url = get_stack_url(context.stack_name)
    print(f"stack_url={context.stack_url}")

    resp = requests.request(
        method, context.stack_url + endpoint, timeout=REQUEST_TIMEOUT
    )
    context.response = resp
    context.status_code = resp.status_code
    if isinstance(resp.json(), dict) and "count" in resp.json():
        context.response_count = resp.json().get("count")


@when(  # pylint: disable=not-callable
    "I get the {ext} encoded file {bucket_object} from the bucket"
)
def i_get_the_x_encoded_file_y_from_the_bucket(context, ext, bucket_object) -> None:
    """Download a file (assumes we have a bucket) and relies on context members: -
    - bucket_name
    We append ".{ext}" to the bucket_object and set the following context members: -
    - target_file (i.e. 'file.tgz')"""
    assert context.failed is False
    assert hasattr(context, "bucket_name")

    target_file = f"{bucket_object}.{ext.lower()}"
    target_path = f"{_DOWNLOAD_PATH}/{target_file}"

    # Do nothing if the destination file exists
    if os.path.exists(target_path) and os.path.isfile(target_path):
        print(f"Target file {target_file} already exists")
        context.target_file = target_file
        return

    print(f"Getting object ({bucket_object}) [{ext}]...")
    get_object(context.bucket_name, target_file, _DOWNLOAD_PATH)
    print("Got it")

    context.target_file = target_file


@when('load it against target access string "{tas}"')  # pylint: disable=not-callable
def load_it_against_target_access_string_x(context, tas) -> None:
    """Loads a previously downloaded file into the stack using the given TAS.
    Relies on context members: -
    - target_file
    - session_id
    We set the following context members: -
    - response
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "target_file")
    assert hasattr(context, "session_id")

    stack_url = get_stack_url(context.stack_name)
    print(f"Loading under {tas} at {stack_url}...")
    resp: requests.Response = upload_target_experiment(
        base_url=stack_url,
        session_id=context.session_id,
        tas=tas,
        file_directory=_DOWNLOAD_PATH,
        file_name=context.target_file,
    )

    print(f"Loaded ({resp.status_code})")
    context.response = resp
    context.status_code = resp.status_code


@when(
    'I create a new SessionProject with the title "{title}"'
)  # pylint: disable=not-callable
def i_create_a_new_sessionproject_with_the_title_x(context, title) -> None:
    """Relies on context members: -
    - stack_name
    - session_id
    We set the following context members: -
    - response
    - status_code
    - session_project_id
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")

    print(f"Creating new SessionProject (title='{title}')...")
    stack_url = get_stack_url(context.stack_name)
    resp = create_session_project(
        base_url=stack_url, session_id=context.session_id, target_id=1, title=title
    )
    assert resp.status_code == 201, f"Expected 201, was {resp.status_code}"

    context.status_code = resp.status_code
    context.response = resp
    session_project_id = resp.json()["id"]
    print(f"Created new SessionProject ({session_project_id})")
    context.session_project_id = session_project_id


@when(
    'I create a new Snapshot with the title "{title}"'
)  # pylint: disable=not-callable
def i_create_a_new_snapshot_with_the_title_x(context, title) -> None:
    """Relies on context members: -
    - stack_name
    - session_id
    - session_project_id
    We set the following context members: -
    - response
    - status_code
    - snapshot_id
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "session_project_id")

    print(f"Creating new Snapshot (title='{title}')...")
    stack_url = get_stack_url(context.stack_name)
    resp = create_snapshot(
        base_url=stack_url,
        session_id=context.session_id,
        session_project_id=context.session_project_id,
        title=title,
    )
    assert resp.status_code == 201, f"Expected 201, was {resp.status_code}"

    context.status_code = resp.status_code
    context.response = resp
    snapshot_id = resp.json()["id"]
    print(f"Created new Snapshot ({snapshot_id})")
    context.snapshot_id = snapshot_id


@when("I transfer Snapshot files to Squonk")  # pylint: disable=not-callable
def i_transfer_snapshot_files_to_squonk(context) -> None:
    """Relies on context members: -
    - stack_name
    - session_id
    - project_id
    - target_id
    - snapshot_id
    - session_project_id
    We set the following context members: -
    - response
    - status_code
    - job_transfer_id
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "project_id")
    assert hasattr(context, "target_id")
    assert hasattr(context, "snapshot_id")
    assert hasattr(context, "session_project_id")

    print("Initiating file transfer...")
    stack_url = get_stack_url(context.stack_name)
    resp = initiate_job_file_transfer(
        base_url=stack_url,
        session_id=context.session_id,
        tas_id=context.project_id,
        target_id=context.target_id,
        snapshot_id=context.snapshot_id,
        session_project_id=context.session_project_id,
    )
    assert resp.status_code == 200, f"Expected 200, was {resp.status_code}"

    context.status_code = resp.status_code
    context.response = resp
    job_transfer_id = resp.json()["id"]
    print(f"Started file transfer ({job_transfer_id})")
    context.job_transfer_id = job_transfer_id
