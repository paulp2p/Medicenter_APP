from behave import given

@given("aplicación está abierta")
def step_impl(context):
    assert context.driver is not None
