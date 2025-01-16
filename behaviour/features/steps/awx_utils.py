"""
AWX utilities for steps.
Logic that allows us to run AWX Job Templates (to wipe and create stacks).
"""

import os
import shlex
import subprocess
import tempfile

import yaml
from config import AWX_HOST, AWX_PASSWORD, AWX_USERNAME, get_env_name


def get_stack_url(name: str) -> str:
    """Returns the stack URL (i.e. https://example.com) that is expected to have been
    created by the AWX Job Template for the AWX user."""
    if not AWX_USERNAME:
        raise ValueError(get_env_name("AWX_USERNAME") + " is not set")
    return f"https://fragalysis-{AWX_USERNAME.lower()}-{name.lower()}.xchem-dev.diamond.ac.uk"


def get_stack_username() -> str:
    """Returns the AWX username - tha author of the stack."""
    if not AWX_USERNAME:
        raise ValueError(get_env_name("AWX_USERNAME") + " is not set")
    return AWX_USERNAME


def launch_awx_job_template(template, *, extra_vars) -> None:
    """A utility to launch the named AWX JobTemplate
    while also providing extra variables via a temporary file.
    """

    if not AWX_HOST:
        raise ValueError(get_env_name("AWX_HOST") + " is not set")
    if not AWX_USERNAME:
        raise ValueError(get_env_name("AWX_USERNAME") + " is not set")
    if not AWX_PASSWORD:
        raise ValueError(get_env_name("AWX_PASSWORD") + " is not set")

    print(f"Launching AWX JobTemplate '{template}'...")
    print(f"AWX JobTemplate extra_vars={extra_vars}")

    cmd = "awx job_templates launch --wait"

    # Put any extra_vars into a local temporary YAML file
    fp = None
    if extra_vars:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
            yaml.dump(extra_vars, fp)

        cmd += f" --extra_vars @{fp.name}"

    cmd += f' "{template}"'

    # Split the command into a sequence for subprocess.run()
    # and inject the required environment variables.

    split_cmd = shlex.split(cmd)

    env = os.environ.copy()
    env["CONTROLLER_HOST"] = f"https://{AWX_HOST}"
    env["CONTROLLER_USERNAME"] = AWX_USERNAME
    env["CONTROLLER_PASSWORD"] = AWX_PASSWORD

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
