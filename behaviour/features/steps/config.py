"""
Common config for the behaviour test steps.
Essentially all the environment variables we need to run the tests.
"""

import os
from typing import Optional

# All of our environment variables have this prefix...
_ENV_PREFIX = "BEHAVIOUR_"


def get_env_name(name: str) -> str:
    """Get the name of the environment variable for the given name"""
    return f"{_ENV_PREFIX}{name}"


def _get(name: str, default_value: Optional[str] = None) -> Optional[str]:
    return os.environ.get(f"{_ENV_PREFIX}{name}", default_value)


# The AWX host (without a protocol, i.e. 'example.com') and
# a user that can run the Job Templates we'll be using.
# The user must be the owner of the Stack deployment Job Template we'll be using.
AWX_HOST: Optional[str] = _get("AWX_HOST", "awx.xchem-dev.diamond.ac.uk")
AWX_USERNAME: Optional[str] = _get("AWX_USERNAME")
AWX_PASSWORD: Optional[str] = _get("AWX_PASSWORD")

# The password for the Django superuser
DJANGO_SUPERUSER_PASSWORD: Optional[str] = _get(
    "DJANGO_SUPERUSER_USERNAME", "ocherous-autotomy-zig"
)

# Required S3 config
# The key must provide read access to the chosen bucket
S3_ACCESS_KEY_ID = _get("AWS_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = _get("AWS_SECRET_ACCESS_KEY")
# Optional config
S3_DEFAULT_REGION = _get("AWS_DEFAULT_REGION")
S3_ENDPOINT_URL = _get("AWS_ENDPOINT_URL")

# Fragalysis Stack name (used to form the stack's URL), and credentials for a CAS user.
# The username is also used to form the stack's URL.
STACK_NAME: Optional[str] = _get("STACK_NAME", "behaviour")
STACK_USERNAME: Optional[str] = _get("STACK_USERNAME")
STACK_PASSWORD: Optional[str] = _get("STACK_PASSWORD")
STACK_CLIENT_ID_SECRET: Optional[str] = _get("STACK_CLIENT_ID_SECRET")

# General constants

REQUEST_POLL_PERIOD_S: int = 2
REQUEST_TIMEOUT: int = 8

# To create a stack we need to know the names of templates (in the AWX server)
# that are responsible for its creation and destruction.
# These templates are expected to be owned by the given AWX_USERNAME.
AWX_STACK_CREATE_JOB_TEMPLATE: str = "User (%(username)s) Developer Fragalysis Stack"
AWX_STACK_WIPE_JOB_TEMPLATE: str = (
    "User (%(username)s) Developer Fragalysis Stack [WIPE]"
)
