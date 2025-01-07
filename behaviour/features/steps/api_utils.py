import os
from typing import Optional
from urllib.parse import urljoin

import requests
from requests import Response
from requests_toolbelt import MultipartEncoder

LANDING_PAGE_METHOD: str = "/viewer/react/landing/"

# this needs to be kept more or less up to date
USER_AGENT: str = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def call_api(*, base_url: str, method: str, session_id: Optional[str]) -> Response:
    """Calls thge GET REST endpoint for an API method using an optional session ID.
    The base url is the root of the apu, i.e. https://example.com. The method is the
    API method to call, i.e. /api/job_config and the session ID is the session ID to
    use for the call."""

    with requests.Session() as session:

        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Referer": urljoin(base_url, LANDING_PAGE_METHOD),
                "Referrer-policy": "same-origin",
            }
        )
        session.get(base_url)  # A GET sets any csrftoken
        if csrftoken := session.cookies.get("csrftoken", None):
            session.headers.update(
                {
                    "X-CSRFToken": csrftoken,
                    "User-Agent": USER_AGENT,
                }
            )
        if session_id:
            session.cookies.update(
                {
                    "sessionid": session_id,
                }
            )
        return session.get(urljoin(base_url, method))


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

        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Referer": urljoin(base_url, LANDING_PAGE_METHOD),
                "Referrer-policy": "same-origin",
            }
        )
        session.get(base_url)  # A GET sets any csrftoken
        if csrftoken := session.cookies.get("csrftoken", None):
            session.headers.update(
                {
                    "X-CSRFToken": csrftoken,
                    "User-Agent": USER_AGENT,
                }
            )
        session.cookies.update(
            {
                "sessionid": session_id,
            }
        )

        encoder = MultipartEncoder(
            fields={
                "target_access_string": tas,
                "file": (
                    file_name,
                    open(os.path.join(file_directory, file_name), "rb"),
                    "application/octet-stream",
                ),
            }
        )

        url = urljoin(base_url, "/api/upload_target_experiments")
        print(f"Uploading to {url}...")
        response = session.post(url, data=encoder)
        print(f"Uploaded ({response.status_code})")

        return response
