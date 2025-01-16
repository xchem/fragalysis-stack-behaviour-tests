"""
A collection of functions to simplify access to the stack's REST API,
used primarily to reduce the number of lines in the step file.
"""

import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests import Response
from requests_toolbelt import MultipartEncoder

# Trailing slashes are important!
LANDING_PAGE_ENDPOINT: str = "/viewer/react/landing/"
UPLOAD_ENDPOINT = "/api/upload_target_experiments/"

# this needs to be kept more or less up to date
USER_AGENT: str = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def api_get_request(
    *,
    base_url: str,
    endpoint: str,
    session_id: Optional[str],
    params: Optional[Dict[str, Any]] = None,
) -> Response:
    """Calls the GET REST endpoint using an optional session ID.
    The base url is the root of the apu, i.e. https://example.com. The method is the
    API method to call, i.e. /api/job_config and the session ID is the session ID to
    use for the call."""
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.get(urljoin(base_url, endpoint), params=params)


def api_delete_request(
    *, base_url: str, endpoint: str, session_id: Optional[str]
) -> Response:
    """Calls the DELETE REST endpoint using an optional session ID.
    The base url is the root of the apu, i.e. https://example.com. The method is the
    API method to call, i.e. /api/job_config and the session ID is the session ID to
    use for the call."""
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.delete(urljoin(base_url, endpoint))


def api_post_request(
    *,
    base_url: str,
    endpoint: str,
    session_id: Optional[str],
    data: Optional[Dict[str, Any]],
) -> Response:
    """Calls the POST REST endpoint using an optional session ID and data payload.
    The base url is the root of the apu, i.e. https://example.com. The method is the
    API method to call, i.e. /api/job_config and the session ID is the session ID to
    use for the call."""
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.post(urljoin(base_url, endpoint), json=data)


def create_session_project(
    *, base_url: str, session_id: str, target_id: int, title: str
) -> Response:
    """Creates a new Session Project using the given session ID."""
    data = {
        "title": title,
        "description": "Auto-generated behaviour test SessionProject",
        "target": target_id,
    }
    print(f"Creating SessionProject with data: {data}...")
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.post(urljoin(base_url, "/api/session-projects/"), json=data)


def create_snapshot(
    *, base_url: str, session_id: str, session_project_id: int, title: str
) -> Response:
    """Creates a new Snapshot using the given session project ID."""
    data = {
        "title": title,
        "description": "Auto-generated behaviour test Snapshot",
        "session_project": session_project_id,
        "data": "[]",
        "type": "INIT",
        "children": [],
    }
    print(f"Creating Snapshot with data: {data}...")
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.post(urljoin(base_url, "/api/snapshots/"), json=data)


def upload_target_experiment(
    *,
    base_url: str,
    session_id: str,
    tas: str,
    file_directory: str,
    file_name: str,
) -> Response:
    """Uploads target data to the stack using the given TAS and file path."""
    with requests.Session() as session:

        _prepare_session(session, base_url=base_url, session_id=session_id)

        encoder = MultipartEncoder(
            fields={
                "target_access_string": tas,
                "file": (
                    file_name,
                    open(  # pylint: disable=consider-using-with
                        os.path.join(file_directory, file_name), "rb"
                    ),
                    "application/octet-stream",
                ),
            }
        )

        content_type = encoder.content_type
        session.headers.update({"Content-Type": content_type})
        url = urljoin(base_url, UPLOAD_ENDPOINT)
        return session.post(url, data=encoder, stream=True)


def initiate_job_file_transfer(
    *,
    base_url: str,
    session_id: str,
    tas_id: int,
    target_id: int,
    snapshot_id: int,
    session_project_id: int,
    proteins: str,
    compounds: str,
):
    """Transfers file to Squonk."""
    data = {
        "access": tas_id,
        "target": target_id,
        "snapshot": snapshot_id,
        "session_project": session_project_id,
        "proteins": proteins,
        "compounds": compounds,
    }
    print(f"Initiating Squonk file transfer with data: {data}...")
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.post(urljoin(base_url, "/api/job_file_transfer/"), json=data)


def initiate_job_request(
    *,
    base_url: str,
    session_id: str,
    tas_id: int,
    target_id: int,
    snapshot_id: int,
    session_project_id: int,
    job_name: str,
    job_spec: Dict[str, Any],
    job_sub_path: str,
):
    """Runs a Job in Squonk."""

    # Convert the Job specification to a string
    # and then replace all the occurrences of `{SUB_PATH}` with the job_sub_path
    job_spec_str = json.dumps(job_spec)
    job_spec_str = job_spec_str.replace("{SUB_PATH}", job_sub_path)

    data = {
        "access": tas_id,
        "target": target_id,
        "snapshot": snapshot_id,
        "session_project": session_project_id,
        "squonk_job_name": job_name,
        "squonk_job_spec": job_spec_str,
    }
    print(f"Initiating Squonk file transfer with data: {data}...")
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.post(urljoin(base_url, "/viewer/job_request/"), json=data)


def get_job_config(
    *,
    base_url: str,
    session_id: str,
    job_collection: str,
    job_name: str,
    job_version: str,
):
    """Gets a JobConfig."""

    params = {
        "job_collection": job_collection,
        "job_name": job_name,
        "job_version": job_version,
    }
    print(f"Getting JobConfig with params: {params}...")
    with requests.Session() as session:
        _prepare_session(session, base_url=base_url, session_id=session_id)
        return session.get(urljoin(base_url, "/viewer/job_request/"), params=params)


# Local functions


def _prepare_session(session, *, base_url: str, session_id: str) -> None:
    """Prepares a session for use with the stack."""
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Referer": urljoin(base_url, LANDING_PAGE_ENDPOINT),
            "Referrer-policy": "same-origin",
        }
    )
    session.get(base_url)  # A GET sets any csrftoken
    if csrftoken := session.cookies.get("csrftoken", None):
        session.headers.update({"X-CSRFToken": csrftoken, "User-Agent": USER_AGENT})
    if session_id:
        session.cookies.update({"sessionid": session_id})
