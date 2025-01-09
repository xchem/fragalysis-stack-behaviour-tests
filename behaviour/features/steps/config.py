"""Common config for the behaviour test steps.
Essentially all the environment variables we need to run the tests.
"""

import os
from typing import Optional

_ENV_PREFIX = "BEHAVIOUR_"


def get_env_name(name: str) -> str:
    """Get the name of the environment variable for the given name"""
    return f"{_ENV_PREFIX}{name}"


def _get(name: str) -> Optional[str]:
    return os.environ.get(f"{_ENV_PREFIX}{name}")


# In order to deploy production-like stacks (to kubernetes) we'll need a number of variables.
# The AWX host (without a protocol, i.e. 'example.com') and
# a user that can run the Job Templates we'll be using.
AWX_HOST: Optional[str] = _get("AWX_HOST")
AWX_USERNAME: Optional[str] = _get("AWX_USERNAME")
AWX_PASSWORD: Optional[str] = _get("AWX_PASSWORD")

# Required config
# The key must provide read access to the chosen bucket
S3_ACCESS_KEY_ID = _get("AWS_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = _get("AWS_SECRET_ACCESS_KEY")
# Optional config
S3_DEFAULT_REGION = _get("AWS_DEFAULT_REGION")
S3_ENDPOINT_URL = _get("AWS_ENDPOINT_URL")

# Fragalysis Stack name (used to form the stack's URL), and credentials for a CAS user.
# The username is also used to form the stack's URL by the AWX Job Template.
STACK_NAME: Optional[str] = _get("STACK_NAME")
STACK_USERNAME: Optional[str] = _get("STACK_USERNAME")
STACK_PASSWORD: Optional[str] = _get("STACK_PASSWORD")
STACK_CLIENT_ID_SECRET: Optional[str] = _get("STACK_CLIENT_ID_SECRET")

REQUEST_POLL_PERIOD_S: int = 4
REQUEST_TIMEOUT: int = 8
