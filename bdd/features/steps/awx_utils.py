"""AWX utilities for steps."""

import os
import subprocess
import tempfile
from typing import Optional

import yaml

# For stack testing to work we'll need a number of variables: -
_AWX_HOSTNAME: Optional[str] = os.environ.get("STACKTEST_AWX_HOSTNAME")
_AWX_USERNAME: Optional[str] = os.environ.get("STACKTEST_AWX_USERNAME")
_AWX_PASSWORD: Optional[str] = os.environ.get("STACKTEST_AWX_PASSWORD")


def get_stack_url(name: str) -> str:
    """Returns the AWX username."""
    if not _AWX_USERNAME:
        raise ValueError("STACKTEST_AWX_USERNAME is not set")
    return f"https://fragalysis-{_AWX_USERNAME}-{name}.xchem-dev.diamond.ac.uk"


def get_stack_username() -> str:
    """Returns the AWX username."""
    if not _AWX_USERNAME:
        raise ValueError("STACKTEST_AWX_USERNAME is not set")
    return _AWX_USERNAME


def launch_awx_job_template(template, *, extra_vars) -> None:
    """A utility to launch the named AWX JobTemplate
    while also providing extra variables via a temporary file.
    """

    if not _AWX_HOSTNAME:
        raise ValueError("STACKTEST_AWX_HOSTNAME is not set (e.g. example.com)")
    if not _AWX_USERNAME:
        raise ValueError("STACKTEST_AWX_USERNAME is not set")
    if not _AWX_PASSWORD:
        raise ValueError("STACKTEST_AWX_PASSWORD is not set")

    print(f"Launching AWX JobTemplate '{template}'...")
    print(f"AWX JobTemplate extra_vars={extra_vars}")

    cmd = f'awx job_templates launch --wait "{template}"'

    # Put any extra_vars into a temporary YAML file
    if extra_vars:
        fp = tempfile.NamedTemporaryFile(mode="w", delete_on_close=False)
        yaml.dump(extra_vars, fp)
        fp.close()

        cmd += f" --extra_vars @{fp.name}"

    # Use the environment for sensitive AWX API material
    my_env = os.environ.copy()
    my_env["CONTROLLER_HOST"] = f"https://{_AWX_HOSTNAME}"
    my_env["CONTROLLER_USERNAME"] = _AWX_USERNAME
    my_env["CONTROLLER_PASSWORD"] = _AWX_PASSWORD

    _ = subprocess.run(cmd, shell=True, check=True, env=my_env, capture_output=True)

    print(f"Successfully launched AWX JobTemplate '{template}'...")
