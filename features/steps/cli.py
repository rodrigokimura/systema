import os

from behave import then, when

from systema.__version__ import VERSION

# ruff: noqa: F811


@when("I execute command in shell to show version")
def step_impl(context):
    with os.popen("python -m systema version") as c:
        context.version = c.read().strip()


@then("shell should display current version")
def step_impl(context):
    assert context.version == VERSION
