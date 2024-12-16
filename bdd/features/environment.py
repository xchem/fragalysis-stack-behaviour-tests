"""Logic to connect fixture tags to fixtures.

See https://behave.readthedocs.io/en/latest/tutorial/#environmental-controls
"""
from behave import use_fixture

from awx_fixtures import create_stack


def before_tag(context, tag):
    if tag == "fixture.create.stack":
        return use_fixture(create_stack, context)
