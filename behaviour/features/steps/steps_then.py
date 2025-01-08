import http
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from api_utils import api_get_request
from behave import then

_REQUEST_TIMEOUT: int = 8
_REQUEST_POLL_PERIOD_S: int = 4


@then(  # pylint: disable=not-callable
    "the landing page response should be {status_code_name}"
)
def step_impl(context, status_code_name) -> None:
    """Just make sure the stack is up"""
    assert context.failed is False
    resp = requests.get(context.stack_url, timeout=_REQUEST_TIMEOUT)
    assert resp
    assert resp.status_code == http.HTTPStatus[status_code_name].value


@then(  # pylint: disable=not-callable
    "the length of the returned list should be {count:d}"
)
def step_impl(context, count) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    response_count"""
    assert context.failed is False
    assert context.response_count == count


@then("the response should be {status_code_name}")  # pylint: disable=not-callable
def step_impl(context, status_code_name) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    status_code"""
    assert context.failed is False
    print(f"Have status code {http.HTTPStatus(context.status_code).name}")
    assert context.status_code == http.HTTPStatus[status_code_name].value


@then("I should get a Task status endpoint")  # pylint: disable=not-callable
def step_impl(context) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    - response
    And creates the following context properties: -
    - task_status_url
    """
    assert context.failed is False
    assert hasattr(context, "response")

    data: Dict[str, Any] = context.response.json()
    assert "task_status_url" in data
    task_status_url: str = data["task_status_url"]
    assert task_status_url.startswith("/viewer/task_status/")

    print(f"Got task status URL ({task_status_url})")
    context.task_status_url = task_status_url


@then(
    "the Task status should have a value of {status} within {timeout_m:d} minutes"
)  # pylint: disable=not-callable
def step_impl(context, status, timeout_m) -> None:  # pylint: disable=function-redefined
    """Relies on context members: -
    - session_id
    - stack_url
    - task_status_url
    """
    assert timeout_m > 0

    assert context.failed is False
    assert hasattr(context, "session_id")
    assert hasattr(context, "stack_url")
    assert hasattr(context, "task_status_url")

    start_time = datetime.now()
    timeout_period = timedelta(minutes=timeout_m)

    print(f"Waiting for task at {context.task_status_url} [{start_time}]...")

    done: bool = False
    data: Optional[Dict[str, Any]] = None
    now: datetime = start_time
    while not done:
        # Get the task status.
        # The response normally contains the following properties: -
        # - started
        # - finished
        # - status
        # - messages
        resp = api_get_request(
            base_url=context.stack_url,
            endpoint=context.task_status_url,
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
            time.sleep(_REQUEST_POLL_PERIOD_S)

    print(f"Finished waiting [{now}]")

    assert data
    assert "status" in data
    task_status = data["status"]
    print(f"Task status is {task_status}")
    assert task_status == status
