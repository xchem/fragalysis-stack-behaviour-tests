"""AWX utilities for steps."""

import os
import shlex
import subprocess
import tempfile
from typing import Optional

import yaml

# In order to deploy production-like stacks (to kubernetes) we'll need a number of variables.
# The AWX host (without a protocol, i.e. 'example.com') and
# a user that can run the Job Templates we'll be using.
_AWX_HOST: Optional[str] = os.environ.get("BEHAVIOUR_AWX_HOST")
_AWX_USERNAME: Optional[str] = os.environ.get("BEHAVIOUR_AWX_USERNAME")
_AWX_PASSWORD: Optional[str] = os.environ.get("BEHAVIOUR_AWX_PASSWORD")


def get_stack_url(name: str) -> str:
    """Returns the stack URL (i.e. https://example.com) that is expected to have been
    created by the AWX Job Template for the AWX user."""
    if not _AWX_USERNAME:
        raise ValueError("BEHAVIOUR_AWX_USERNAME is not set")
    return f"https://fragalysis-{_AWX_USERNAME.lower()}-{name.lower()}.xchem-dev.diamond.ac.uk"


def get_stack_username() -> str:
    """Returns the AWX username - tha author of the stack."""
    if not _AWX_USERNAME:
        raise ValueError("BEHAVIOUR_AWX_USERNAME is not set")
    return _AWX_USERNAME


def launch_awx_job_template(template, *, extra_vars) -> None:
    """A utility to launch the named AWX JobTemplate
    while also providing extra variables via a temporary file.
    """

    if not _AWX_HOST:
        raise ValueError("BEHAVIOUR_AWX_HOST is not set (e.g. example.com)")
    if not _AWX_USERNAME:
        raise ValueError("BEHAVIOUR_AWX_USERNAME is not set")
    if not _AWX_PASSWORD:
        raise ValueError("BEHAVIOUR_AWX_PASSWORD is not set")

    print(f"Launching AWX JobTemplate '{template}'...")
    print(f"AWX JobTemplate extra_vars={extra_vars}")

    cmd = "awx job_templates launch --wait"

    # Put any extra_vars into a local temporary YAML file
    fp = None
    if extra_vars:
        fp = tempfile.NamedTemporaryFile(mode="w", delete=False)
        yaml.dump(extra_vars, fp)
        fp.close()

        cmd += f" --extra_vars @{fp.name}"

    cmd += f' "{template}"'

    # Split the command into a sequence for subprocess.run()
    # and inject the required environment variables.

    split_cmd = shlex.split(cmd)

    env = os.environ.copy()
    env["CONTROLLER_HOST"] = f"https://{_AWX_HOST}"
    env["CONTROLLER_USERNAME"] = _AWX_USERNAME
    env["CONTROLLER_PASSWORD"] = _AWX_PASSWORD

    cmd_process = subprocess.run(split_cmd, capture_output=True, check=False, env=env)
    if cmd_process.returncode != 0:
        print(f"Error launching AWX JobTemplate '{template}'")
        print(f"process.returncode: {cmd_process.returncode}")
        print(f"STDOUT:\n{cmd_process.stdout}")
        print(f"STDERR:\n{cmd_process.stderr}")
        assert False

    print(f"Successfully launched AWX JobTemplate '{template}'...")

    if fp:
        os.remove(fp.name)
