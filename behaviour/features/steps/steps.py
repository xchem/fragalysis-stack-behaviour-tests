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
#       and any _natural_ string like a title, e.g.: -
#
#           And I can get the "A71EV2A" Target ID
#
#       Certainly this applies anything that can contain spaces!

import ast
import http
import os
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from api_utils import (
    api_delete_request,
    api_get_request,
    api_post_request,
    create_session_project,
    create_snapshot,
    initiate_job_file_transfer,
    initiate_job_request,
    upload_target_experiment,
)
from awx_utils import launch_awx_job_template
from behave import given, then, when
from browser_utils import login
from config import (
    AWX_STACK_CREATE_JOB_TEMPLATE,
    AWX_STACK_WIPE_JOB_TEMPLATE,
    DJANGO_SUPERUSER_PASSWORD,
    REQUEST_POLL_PERIOD_S,
    REQUEST_TIMEOUT,
    get_stack_client_id_secret,
    get_stack_name,
    get_stack_url,
    get_stack_username,
)
from s3_utils import check_bucket, get_object

_DOWNLOAD_PATH = "."


@given(  # pylint: disable=not-callable
    'a new stack using the image tag "{stack_image_tag}"'
)
def a_new_stack_using_the_image_tag_x(context, stack_image_tag) -> None:
    """Wipe any existing stack content and create a new (empty) one.
    The user can pass in a Dictionary encoded set of extra variables
    via the context.text attribute. This appears as a string.

    The step relies on the image and tag from the Job Template,
    or the content of any step Doc-string variables.

    If successful it sets the following context members: -
    - stack_name (e.g. 'behaviour')
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

    assert DJANGO_SUPERUSER_PASSWORD
    extra_vars: Dict[str, str] = {
        "stack_django_superuser_password": DJANGO_SUPERUSER_PASSWORD,
        "stack_name": stack_name,
        "stack_image_tag": stack_image_tag,
        "stack_oidc_rp_client_id": stack_oidc_rp_client_id,
        "stack_oidc_rp_client_secret": get_stack_client_id_secret(),
    }

    # If the user has passed in extra variables, merge them in.
    if context.text:
        print(context.text)
        step_vars = ast.literal_eval(context.text)
        extra_vars |= step_vars
        print(f"Using step text as extra variables: {step_vars}")

    wipe_jt = AWX_STACK_WIPE_JOB_TEMPLATE % {
        "username": get_stack_username().capitalize()
    }
    launch_awx_job_template(wipe_jt, extra_vars=extra_vars)

    create_jt = AWX_STACK_CREATE_JOB_TEMPLATE % {
        "username": get_stack_username().capitalize()
    }
    launch_awx_job_template(create_jt, extra_vars=extra_vars)

    context.stack_name = stack_name
    print(f"Created stack '{stack_name}'")


@given("I can login")  # pylint: disable=not-callable
@when("I login")  # pylint: disable=not-callable
def i_can_login(context) -> None:
    """Sets the context members: -
    - stack_name
    - session_id"""
    assert context.failed is False

    context.stack_name = get_stack_name()
    context.session_id = login(get_stack_url(context.stack_name))
    assert context.session_id


@given("I can login as a superuser")  # pylint: disable=not-callable
def i_can_login_as_a_superuser(context) -> None:
    """The super user is the django admin user.
    Sets the context members: -
    - stack_name
    """
    assert context.failed is False

    context.stack_name = get_stack_name()
    context.session_id = login(
        get_stack_url(context.stack_name), login_type="superuser"
    )


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


@given('I can get the "{title}" Target ID')  # pylint: disable=not-callable
def i_can_get_the_x_target_id(context, title) -> None:
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


@given("I can get the last JobFileTransfer ID")  # pylint: disable=not-callable
def i_can_get_the_last_job_file_transfer_id(context) -> None:
    """Checks a JobFileTransfer record exists and records its ID and relies on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - job_file_transfer_id"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    session_id = context.session_id if hasattr(context, "session_id") else None
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint="/api/job_file_transfer/",
        session_id=session_id,
    )
    assert resp.status_code == 200

    # We only call this if we expect at least one JobFileTransfer record.
    assert resp.json()["count"] > 0
    job_file_transfer_id = resp.json()["results"][-1]["id"]
    print(f"job_file_transfer_id={job_file_transfer_id}")
    context.job_file_transfer_id = job_file_transfer_id


@given("I can get the last JobFileTransfer SUB_PATH")  # pylint: disable=not-callable
def i_can_get_the_last_job_file_transfer_sub_path(context) -> None:
    """Checks a JobFileTransfer record exists and records its sub-path,
    and relies on the context members: -
    - session_id
    - stack_name
    Sets the context members: -
    - job_file_transfer_sub_path"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    session_id = context.session_id if hasattr(context, "session_id") else None
    resp = api_get_request(
        base_url=get_stack_url(context.stack_name),
        endpoint="/api/job_file_transfer/",
        session_id=session_id,
    )
    assert resp.status_code == 200

    # We only call this if we expect at least one JobFileTransfer record.
    assert resp.json()["count"] > 0
    sub_path = resp.json()["results"][-1]["sub_path"]
    print(f"job_file_transfer_sub_path={sub_path}")
    context.job_file_transfer_sub_path = sub_path


@given('I can get the "{title}" Project ID')  # pylint: disable=not-callable
def i_can_get_the_x_project_id(context, title) -> None:
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


@given('I can get the "{title}" SessionProject ID')  # pylint: disable=not-callable
def i_can_get_the_x_session_project_id(context, title) -> None:
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


@when("I delete the SessionProject")  # pylint: disable=not-callable
def i_delete_the_session_project(context) -> None:
    """Deletes a Snapshot relying on the context members: -
    - session_id
    - stack_name
    - session_project_id
    And sets: -
    - status_code"""
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_project_id")

    print(f"Deleting SessionProject ID {context.session_project_id}...")
    resp = api_delete_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/session-projects/{context.session_project_id}",
        session_id=context.session_id,
    )
    context.status_code = resp.status_code


@given('I can get the "{title}" Snapshot ID')  # pylint: disable=not-callable
def i_can_get_the_x_snapshot_id(context, title) -> None:
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
    assert resp.status_code == 200, f"Expected 200, was {resp.status_code}"

    snapshot_id = resp.json()["results"][0]["id"]
    print(f"Got snapshot_id={snapshot_id}")
    context.snapshot_id = snapshot_id


@when("I delete the Snapshot")  # pylint: disable=not-callable
def i_delete_the_snapshot(context) -> None:
    """Deletes a Snapshot relying on the context members: -
    - session_id
    - stack_name
    - snapshot_id
    And sets: -
    - status_code"""
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_name")
    assert hasattr(context, "snapshot_id")

    print(f"Deleting Snapshot ID {context.snapshot_id}...")
    resp = api_delete_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/snapshots/{context.snapshot_id}",
        session_id=context.session_id,
    )
    context.status_code = resp.status_code


@when("I delete the JobFileTransfer")  # pylint: disable=not-callable
def i_delete_the_job_file_transfer(context) -> None:
    """Deletes a JobFileTransfer relying on the context members: -
    - session_id
    - stack_name
    - job_file_transfer_id
    And sets: -
    - status_code"""
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_name")
    assert hasattr(context, "job_file_transfer_id")

    print(f"Deleting JobFileTransfer ID {context.job_file_transfer_id}...")
    resp = api_delete_request(
        base_url=get_stack_url(context.stack_name),
        endpoint=f"/api/job_file_transfer/{context.job_file_transfer_id}",
        session_id=context.session_id,
    )
    context.status_code = resp.status_code


@when(  # pylint: disable=not-callable
    'I run "{job_name}" from the "{collection_name}" collection with the following variables'
)
def i_run_x_with_the_following_variables(context, job_name, collection_name) -> None:
    """Run a given Job replacing each occurrence of {SUB_PATH} in the Job specification
    with the sub-path used by the file transfer logic. It relies on context members: -
    - stack_name
    - session_id
    - project_id
    - target_id
    - snapshot_id
    - session_project_id
    - job_file_transfer_sub_path
    And sets: -
    - response
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "project_id")
    assert hasattr(context, "target_id")
    assert hasattr(context, "snapshot_id")
    assert hasattr(context, "session_project_id")
    assert hasattr(context, "job_file_transfer_sub_path")

    # We expect a dictionary in the step's doc string.
    # It will contain the Job variables.
    assert context.text is not None
    variables: Dict[str, Any] = ast.literal_eval(context.text)
    spec = {
        "collection": collection_name,
        "job": job_name,
        "version": "1.0.0",
        "variables": variables,
    }

    print("Initiating JobRequest...")
    stack_url = get_stack_url(context.stack_name)
    resp = initiate_job_request(
        base_url=stack_url,
        session_id=context.session_id,
        tas_id=context.project_id,
        target_id=context.target_id,
        snapshot_id=context.snapshot_id,
        session_project_id=context.session_project_id,
        job_name="Behaviour Test",
        job_spec=spec,
        job_sub_path=context.job_file_transfer_sub_path,
    )
    if resp.status_code != http.HTTPStatus["ACCEPTED"].value:
        print(f"resp.text={resp.text}")

    context.status_code = resp.status_code
    context.response = resp


@then(  # pylint: disable=not-callable
    "the landing page response should be {status_code_name}"
)
def the_landing_page_response_should_be_x(context, status_code_name) -> None:
    """Just make sure the stack is up, and relies on context members: -
    - stack_name"""
    assert context.failed is False
    assert hasattr(context, "stack_name")

    resp = requests.get(get_stack_url(context.stack_name), timeout=REQUEST_TIMEOUT)
    assert resp

    expected_code = http.HTTPStatus[status_code_name].value
    if resp.status_code != expected_code:
        print(f"Expected status code {expected_code}, got {resp.status_code}")
        assert resp.status_code == expected_code


@when("remember the count")  # pylint: disable=not-callable
def remember_the_count(context) -> None:
    """Relies on context members: -
    - response_count
    Sets the following context members: -
    - remembered_response_count
    """
    assert context.failed is False
    assert hasattr(context, "response_count")

    context.remembered_response_count = context.response_count


@then(  # pylint: disable=not-callable
    "the count must be one larger than the remembered count"
)
def the_count_must_be_one_larger_than_the_remembered_count(context) -> None:
    """Relies on the context members: -
    - response_count
    - remembered_response_count"""
    assert context.failed is False
    assert hasattr(context, "response_count")
    assert hasattr(context, "remembered_response_count")

    assert context.response_count == context.remembered_response_count + 1


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
    assert (
        context.status_code == expected_status_code
    ), f"Expected {expected_status_code}, got {context.status_code}"


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


@then("the response should contain a JobRequest ID")  # pylint: disable=not-callable
def the_response_should_contain_a_job_request_id(context) -> None:
    """Relies on context members: -
    - response
    And Sets the context properties: -
    - job_request_id
    """
    assert context.failed is False
    assert hasattr(context, "response")

    data: Dict[str, Any] = context.response.json()
    assert "id" in data
    context.job_request_id = data["id"]


@then(  # pylint: disable=not-callable
    "the task status should have a value of {status} within {timeout:d} {timeout_units}"
)
def the_task_should_have_a_value_of_x_within_y_z(
    context, status, timeout, timeout_units
) -> None:
    """Relies on context members: -
    - session_id
    - task_status_endpoint
    """
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "task_status_endpoint")

    assert timeout > 0

    start_time = datetime.now()

    assert timeout_units in ["minute", "minutes", "second", "seconds"]
    if timeout_units.startswith("minute"):
        timeout_period = timedelta(minutes=timeout)
    else:
        timeout_period = timedelta(seconds=timeout)

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
            base_url=get_stack_url(context.stack_name),
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
    - status_code
    - response
    - response_count (optional)
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")

    stack_url = get_stack_url(context.stack_name)
    print(f"stack_url={stack_url}")

    # Django POST needs a trailing '/'.
    # Add one in case the user forgot
    if method == "POST" and not endpoint.endswith("/"):
        endpoint += "/"

    resp = requests.request(method, stack_url + endpoint, timeout=REQUEST_TIMEOUT)
    context.response = resp
    context.status_code = resp.status_code
    if (
        "application/json" in resp.headers.get("Content-Type", "")
        and isinstance(resp.json(), dict)
        and "count" in resp.json()
    ):
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


@when(  # pylint: disable=not-callable
    'I load the file against target access string "{tas}"'
)
def i_load_the_file_against_target_access_string_x(context, tas) -> None:
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


@when(  # pylint: disable=not-callable
    'I create a new SessionProject with the title "{title}"'
)
def i_create_a_new_session_project_with_the_title_x(context, title) -> None:
    """Relies on context members: -
    - stack_name
    - session_id
    We set the following context members: -
    - response
    - status_code
    - session_project_id (optional)
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")

    print(f"Creating new SessionProject (title='{title}')...")
    stack_url = get_stack_url(context.stack_name)
    resp = create_session_project(
        base_url=stack_url, session_id=context.session_id, target_id=1, title=title
    )

    context.status_code = resp.status_code
    context.response = resp
    if (
        "application/json" in resp.headers.get("Content-Type", "")
        and isinstance(resp.json(), dict)
        and "id" in resp.json()
    ):
        session_project_id = resp.json()["id"]
        print(f"Created new SessionProject ({session_project_id})")
        context.session_project_id = session_project_id


@when(  # pylint: disable=not-callable
    'I create a new Snapshot with the title "{title}"'
)
def i_create_a_new_snapshot_with_the_title_x(context, title) -> None:
    """Relies on context members: -
    - stack_name
    - session_id
    - session_project_id
    We set the following context members: -
    - response
    - status_code
    - snapshot_id (optional)
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
    if resp.status_code != 201:
        print(f"resp.text={resp.text}")

    context.status_code = resp.status_code
    context.response = resp
    if (
        "application/json" in resp.headers.get("Content-Type", "")
        and isinstance(resp.json(), dict)
        and "id" in resp.json()
    ):
        snapshot_id = resp.json()["id"]
        print(f"Created new Snapshot ({snapshot_id})")
        context.snapshot_id = snapshot_id


@when("I transfer the following files to Squonk")  # pylint: disable=not-callable
def i_transfer_the_following_files_to_squonk(context) -> None:
    """This step requires the files to be identified in the step 'doc string',
    a dictionary containing a 'proteins' key that's a lits of files.
    It relies on context members: -
    - stack_name
    - session_id
    - project_id
    - target_id
    - snapshot_id
    - session_project_id
    We set the following context members: -
    - response
    - status_code
    - job_transfer_id (optional)
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "project_id")
    assert hasattr(context, "target_id")
    assert hasattr(context, "snapshot_id")
    assert hasattr(context, "session_project_id")

    # We expect a dictionary in the step's doc string.
    # It will contain a list of proteins and compounds.
    # We pass these lists to the API as a comma-separated string.
    assert context.text is not None
    text_map: Dict[str, Any] = ast.literal_eval(context.text)
    assert "proteins" in text_map
    assert "compounds" in text_map

    assert isinstance(text_map["proteins"], list)
    num_proteins = len(text_map["proteins"])
    assert num_proteins > 0
    proteins: str = ",".join(text_map["proteins"])

    assert isinstance(text_map["compounds"], list)
    num_compounds = len(text_map["compounds"])
    assert num_compounds > 0
    compounds: str = ",".join(text_map["compounds"])

    print(f"Initiating file transfer ({num_proteins} & {num_compounds})...")
    stack_url = get_stack_url(context.stack_name)
    resp = initiate_job_file_transfer(
        base_url=stack_url,
        session_id=context.session_id,
        tas_id=context.project_id,
        target_id=context.target_id,
        snapshot_id=context.snapshot_id,
        session_project_id=context.session_project_id,
        proteins=proteins,
        compounds=compounds,
    )
    if resp.status_code != http.HTTPStatus["ACCEPTED"].value:
        print(f"resp.text={resp.text}")

    context.status_code = resp.status_code
    context.response = resp
    if (
        "application/json" in resp.headers.get("Content-Type", "")
        and isinstance(resp.json(), dict)
        and "id" in resp.json()
    ):
        job_file_transfer_id = resp.json()["id"]
        print(f"Started file transfer ({job_file_transfer_id})")
        context.job_file_transfer_id = job_file_transfer_id


@then(  # pylint: disable=not-callable
    "the file transfer status should have a value of {status} within {timeout:d} {timeout_units}"
)
def the_file_transfer_status_should_have_a_value_of_x_within_y_z(
    context, status, timeout, timeout_units
) -> None:
    """Waits until the known job transfer ID has the given status.
    It relies on context members: -
    - stack_name
    - session_id
    - job_file_transfer_id
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "job_file_transfer_id")

    assert timeout > 0

    start_time = datetime.now()

    assert timeout_units in ["minute", "minutes", "second", "seconds"]
    if timeout_units.startswith("minute"):
        timeout_period = timedelta(minutes=timeout)
    else:
        timeout_period = timedelta(seconds=timeout)

    print(
        f"Waiting for job file transfer {context.job_file_transfer_id} [{start_time}]..."
    )

    done: bool = False
    data: Optional[Dict[str, Any]] = None
    now: datetime = start_time
    while not done:

        # Get the Job File Transfer status.
        # The response normally contains the following properties: -
        # - transfer_status (i.e. SUCCESS, FAILURE)
        # - transfer_datetime (the time the transfer finished)
        resp = api_get_request(
            base_url=get_stack_url(context.stack_name),
            endpoint=f"/api/job_file_transfer/{context.job_file_transfer_id}",
            session_id=context.session_id,
        )
        assert resp.status_code == http.HTTPStatus["OK"].value

        if "application/json" in resp.headers.get("Content-Type", "") and isinstance(
            resp.json(), dict
        ):
            data = resp.json()
            if "transfer_datetime" in data and data["transfer_datetime"]:
                print("Job file transfer finished")
                done = True
        else:
            now = datetime.now()
            assert now - start_time <= timeout_period
            time.sleep(REQUEST_POLL_PERIOD_S)

    print(f"Finished waiting [{now}]")

    assert isinstance(data, dict)
    assert "transfer_status" in data
    assert (
        data["transfer_status"] == status
    ), f"Expected {status}, got {data['transfer_status']}"


@then(  # pylint: disable=not-callable
    "the JobRequest should have {a_an} {property_name} value of {property_value} within {timeout:d} {timeout_units}"
)
def the_job_request_should_have_a_x_value_of_y_within_z_m(
    context, a_an, property_name, property_value, timeout, timeout_units
) -> None:
    """Waits until the known job request ID property name has the given value.
    It relies on context members: -
    - stack_name
    - session_id
    - job_request_id
    """
    del a_an  # Unused

    assert context.failed is False
    assert hasattr(context, "stack_name")
    assert hasattr(context, "session_id")
    assert hasattr(context, "job_request_id")

    assert timeout > 0

    start_time = datetime.now()

    assert timeout_units in ["minute", "minutes", "second", "seconds"]
    if timeout_units.startswith("minute"):
        timeout_period = timedelta(minutes=timeout)
    else:
        timeout_period = timedelta(seconds=timeout)

    print(f"Waiting for job request {context.job_request_id} [{start_time}]...")

    done: bool = False
    data: Optional[Dict[str, Any]] = None
    now: datetime = start_time
    while not done:

        # Get the Job File Transfer status.
        # The response normally contains the following properties: -
        # - transfer_status (i.e. SUCCESS, FAILURE)
        # - transfer_datetime (the time the transfer finished)
        resp = api_get_request(
            base_url=get_stack_url(context.stack_name),
            endpoint="/api/job_request/",
            session_id=context.session_id,
        )
        assert (
            resp.status_code == http.HTTPStatus["OK"].value
        ), f"Expected 200, was {resp.status_code}"

        # Find our JobRequest in the response,
        # and wait until it has the expected status.
        assert "results" in resp.json()
        data = next(
            (
                jr_response
                for jr_response in resp.json()["results"]
                if jr_response["id"] == context.job_request_id
            ),
            None,
        )
        assert data, f"JobRequest {context.job_request_id} not found"
        if data[property_name] == property_value:
            print(f"Job request {property_name} status satisfied")
            done = True
        else:
            now = datetime.now()
            current_value = data[property_name]
            assert (
                now - start_time <= timeout_period
            ), f"Timed out waiting for {property_name} '{property_value}', currently '{current_value}'"
            time.sleep(REQUEST_POLL_PERIOD_S)

    print(f"Finished waiting [{now}]")


@when(  # pylint: disable=not-callable
    "I provide the following JobOverride file from {repo_name}"
)
def i_provide_the_following_job_override_file_from_x(context, repo_name) -> None:
    """The user is expected to provide a path to a RAW file in a GitHub repository.
    The path should not be prefixed with '/'. Typically it might
    be something like this for the production branch of the repository:
    "production/viewer/squonk/day-1-job-override.json".
    We prefix with the repo name and 'refs/heads/'.
    Relies on context members: -
    - session_id
    - stack_name
    We set the following context members: -
    - response
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_name")

    # We expect a path to an over-ride file in the step's doc string.
    # We will prefix it with github and the repo name.
    assert context.text is not None
    job_override_path: str = context.text.strip()
    assert job_override_path
    assert not job_override_path.startswith("/")

    # Get the JobOverride text from the (GitHub) repository...
    url = f"https://raw.githubusercontent.com/{repo_name}/refs/heads/"
    resp = api_get_request(
        base_url=url,
        endpoint=job_override_path,
        session_id=context.session_id,
    )
    print(f"Got status_code ({resp.status_code})")
    assert resp.status_code == http.HTTPStatus["OK"].value

    # Now POST the JobOverride text to the stack...
    stack_url = get_stack_url(context.stack_name)
    resp = api_post_request(
        base_url=stack_url,
        endpoint="/api/job_override/",
        session_id=context.session_id,
        data={"override": resp.text},
    )

    context.status_code = resp.status_code
    context.response = resp


@when(  # pylint: disable=not-callable
    "I get the JobConfig {collection}|{job}|{version}"
)
def i_get_the_job_config_x_y_z(context, collection, job, version) -> None:
    """Get the JobConfig from the stack and relies on context members: -
    - session_id
    - stack_name
    Sets the following context members: -
    - response
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_name")

    params = {"job_collection": collection, "job_name": job, "job_version": version}

    stack_url = get_stack_url(context.stack_name)
    print(f"Getting JobConfig (params={params})...")
    resp = api_get_request(
        base_url=stack_url,
        endpoint="/api/job_config/",
        session_id=context.session_id,
        params=params,
    )

    context.response = resp
    context.status_code = resp.status_code


@when("I reset the stack")  # pylint: disable=not-callable
def i_reset_the_stack(context) -> None:
    """Does a POST at /api/reset, relying on: -
    - session_id (optional)
    - stack_name
    Sets the following context members: -
    - response
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")

    stack_url = get_stack_url(context.stack_name)
    session_id = context.session_id if hasattr(context, "session_id") else None
    print("Trying to reset the stack...")
    resp = api_post_request(
        base_url=stack_url,
        endpoint="/api/reset/",
        session_id=session_id,
    )

    context.response = resp
    context.status_code = resp.status_code
