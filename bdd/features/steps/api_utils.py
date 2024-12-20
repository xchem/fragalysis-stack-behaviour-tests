from typing import Optional
from urllib.parse import urljoin

import requests
from requests import Response

LANDING_PAGE_METHOD: str = "/viewer/react/landing/"

# this needs to be kept more or less up to date
USER_AGENT: str = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def call_api(*, base_url: str, method: str, session_id: Optional[str]) -> Response:
    """Calls an API method using an optional session ID. The base url is
    the root of the apu, i.e. https://example.com. The method is the API method to call,
    i.e. /api/job_config and the session ID is the session ID to use for the call."""

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
