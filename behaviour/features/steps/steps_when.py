import requests
from api_utils import upload_target_experiment
from awx_utils import get_stack_url
from behave import when
from s3_utils import get_object

_REQUEST_TIMEOUT: int = 8


@when("I call {method} on the {stack_name} stack")  # pylint: disable=not-callable
def step_impl(context, method, stack_name) -> None:
    """Calls an API method on the stack, and sets up the following context members: -
    - status_code
    - response_count (optional)
    """
    assert context.failed is False
    context.stack_url = get_stack_url(stack_name.lower())
    print(context.stack_url)
    resp = requests.get(context.stack_url + method, timeout=_REQUEST_TIMEOUT)
    context.status_code = resp.status_code
    if isinstance(resp.json(), dict) and "count" in resp.json():
        context.response_count = resp.json().get("count")


@when("I get the {ext} encoded file {bucket_object}")  # pylint: disable=not-callable
def step_impl(
    context, ext, bucket_object
) -> None:  # pylint: disable=function-redefined
    """Download a file (assumes we have a bucket).
    We append ".{ext}" to the bucket_object.
    We set the following context members: -
    - target_file"""
    assert context.failed is False
    assert hasattr(context, "bucket_name")

    print(f"Getting object ({bucket_object}) [{ext}]...")
    target_file = f"{bucket_object}.{ext.lower()}"
    get_object(context.bucket_name, target_file, "/tmp")
    print("Got it")

    context.target_file = target_file


@when("I load it using target access string {tas}")  # pylint: disable=not-callable
def step_impl(context, tas) -> None:  # pylint: disable=function-redefined
    """Loads a previously downloaded file into the stack using the given TAS.
    We set the following context members: -
    - status_code
    """
    assert context.failed is False
    assert hasattr(context, "target_file")
    assert hasattr(context, "session_id")

    stack_url = get_stack_url(context.stack_name)
    print(f"Loading to {tas} at {stack_url}...")
    resp: requests.Response = upload_target_experiment(
        base_url=stack_url,
        session_id=context.session_id,
        tas=tas,
        file_directory="/tmp",
        file_name=context.target_file,
    )
    print(f"Loaded ({resp.status_code})")
    context.status_code = resp.status_code
