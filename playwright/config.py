"""
Common config for the playwright test steps.
Essentially all the environment variables we need to run the tests.

PLEASE: Coordinate any environment variable changes with the behaviour tests.
"""

import os
from typing import Optional

# All of our environment variables have this prefix...
ENV_PREFIX = "PLAYWRIGHT_"


def get_env_name(name: str) -> str:
    """Get the name of the environment variable for the given name"""
    return f"{ENV_PREFIX}{name}"


def _get(name: str, default_value: Optional[str] = None) -> Optional[str]:
    return os.environ.get(f"{ENV_PREFIX}{name}", default_value)


STACK_HOSTNAME: Optional[str] = _get("STACK_HOSTNAME")
STACK_USERNAME: Optional[str] = _get("STACK_USERNAME")
STACK_PASSWORD: Optional[str] = _get("STACK_PASSWORD")
STACK_KC_USERNAME: Optional[str] = _get("STACK_KC_USERNAME")
STACK_KC_PASSWORD: Optional[str] = _get("STACK_KC_PASSWORD")

if not STACK_HOSTNAME:
    raise ValueError(get_env_name("STACK_HOSTNAME") + " is not set (e.g. example.com)")
if not STACK_USERNAME:
    raise ValueError(get_env_name("STACK_USERNAME") + " is not set")
if not STACK_PASSWORD:
    raise ValueError(get_env_name("STACK_PASSWORD") + " is not set")
if not STACK_KC_USERNAME:
    raise ValueError(get_env_name("STACK_KC_USERNAME") + " is not set")
if not STACK_KC_PASSWORD:
    raise ValueError(get_env_name("STACK_KC_PASSWORD") + " is not set")
