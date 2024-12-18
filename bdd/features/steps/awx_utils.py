"""AWX utilities for steps."""

import os
import shlex
import subprocess
import tempfile
from typing import Optional

import yaml

# For stack testing to work we'll need a number of variables.
# The AWX host (without a protocol, i.e. 'example.com') and
# a user that can run the templates we'll be using (set in steps.py).
_CONTROLLER_HOST: Optional[str] = os.environ.get("CONTROLLER_HOST")
_CONTROLLER_USERNAME: Optional[str] = os.environ.get("CONTROLLER_USERNAME")
_CONTROLLER_PASSWORD: Optional[str] = os.environ.get("CONTROLLER_PASSWORD")


def get_stack_url(name: str) -> str:
    """Returns the AWX username."""
    if not _CONTROLLER_USERNAME:
        raise ValueError("CONTROLLER_USERNAME is not set")
    return f"https://fragalysis-{_CONTROLLER_USERNAME}-{name}.xchem-dev.diamond.ac.uk"


def get_stack_username() -> str:
    """Returns the AWX username."""
    if not _CONTROLLER_USERNAME:
        raise ValueError("CONTROLLER_USERNAME is not set")
    return _CONTROLLER_USERNAME


def launch_awx_job_template(template, *, extra_vars) -> None:
    """A utility to launch the named AWX JobTemplate
    while also providing extra variables via a temporary file.
    """

    if not _CONTROLLER_HOST:
        raise ValueError("CONTROLLER_HOST is not set (e.g. example.com)")
    if not _CONTROLLER_USERNAME:
        raise ValueError("CONTROLLER_USERNAME is not set")
    if not _CONTROLLER_PASSWORD:
        raise ValueError("CONTROLLER_PASSWORD is not set")

    print(f"Launching AWX JobTemplate '{template}'...")
    print(f"AWX JobTemplate extra_vars={extra_vars}")

    cmd = f'awx job_templates launch --wait "{template}"'

    # Put any extra_vars into a temporary YAML file
    if extra_vars:
        fp = tempfile.NamedTemporaryFile(
            suffix=".tmp",
            dir=".",
            mode="w",
            delete_on_close=False,
        )
        yaml.dump(extra_vars, fp)
        fp.close()

        cmd += f" --extra_vars @{fp.name}"

    # We need the environment to be set for sensitive AWX API material: -
    #
    # export CONTROLLER_HOST=https://example.com
    # export CONTROLLER_USERNAME=username
    # export CONTROLLER_PASSWORD=password

    cmd_as_sequence = shlex.split(cmd)
    _ = subprocess.run(cmd_as_sequence, check=True)

    print(f"Successfully launched AWX JobTemplate '{template}'...")
