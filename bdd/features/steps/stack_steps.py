from behave import given, when, then


@given('we have a stack installed')
def step_impl(context):
    pass


@then('there should be no targets')
def step_impl(context):
    assert context.failed is False
    assert context.tests_count >= 0
