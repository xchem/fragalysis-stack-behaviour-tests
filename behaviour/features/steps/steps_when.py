import os

import requests
from api_utils import upload_target_experiment
from awx_utils import get_stack_url
from behave import when
from s3_utils import get_object

_DOWNLOAD_PATH = "."
_REQUEST_TIMEOUT: int = 8


@when("I call {method}")  # pylint: disable=not-callable
def step_impl(context, method) -> None:
    """Calls an API method on the stack, and sets up the following context members: -
    - stack_url
    - status_code
    - response
    - response_count (optional)
    """
    assert context.failed is False
    assert hasattr(context, "stack_name")

    context.stack_url = get_stack_url(context.stack_name)
    print(context.stack_url)
    resp = requests.get(context.stack_url + method, timeout=_REQUEST_TIMEOUT)
    context.response = resp
    context.status_code = resp.status_code
    if isinstance(resp.json(), dict) and "count" in resp.json():
        context.response_count = resp.json().get("count")


@when("I get the {ext} encoded file {bucket_object}")  # pylint: disable=not-callable
def step_impl(  # pylint: disable=function-redefined
    context, ext, bucket_object
) -> None:
    """Download a file (assumes we have a bucket).
    We append ".{ext}" to the bucket_object.
    We set the following context members: -
    - target_file"""
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


@when("I load it using target access string {tas}")  # pylint: disable=not-callable
def step_impl(context, tas) -> None:  # pylint: disable=function-redefined
    """Loads a previously downloaded file into the stack using the given TAS.
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
