import pytest

from truman import agent_registration


def fake_agent_factory(env, param_1, param_2):
    assert env == "FAKE_ENVIRONMENT"
    assert param_1 == "PARAM_1"
    assert param_2 == "PARAM_2"


class FakeAgent:
    def __init__(self, env, param_1, param_2):
        assert env == "FAKE_ENVIRONMENT"
        assert param_1 == "PARAM_1"
        assert param_2 == "PARAM_2"


@pytest.mark.parametrize(
    "entry_point",
    [
        fake_agent_factory,
        FakeAgent,
        "tests.test_agent_registration:fake_agent_factory",
        "tests.test_agent_registration:FakeAgent",
    ],
)
def test_registration(entry_point):
    registry = agent_registration.AgentRegistry()

    registry.register(
        id="SomeAgent-v0",
        entry_point=entry_point,
        kwargs={"param_1": "PARAM_1", "param_2": "PARAM_2"},
    )

    # We can't use mocks, since we want to test importing via strings
    # So we run the asserts in the function
    # But we protect against the function never being run (and the test silently passing)
    # by also asserting that there _is_ a failure if we run with the wrong environment
    registry.make(id="SomeAgent-v0", env="FAKE_ENVIRONMENT")
    with pytest.raises(AssertionError):
        registry.make(id="SomeAgent-v0", env="WRONG_ENVIRONMENT")

    all_specs = list(registry.all())
    assert len(all_specs) == 1
    assert all_specs[0].id == "SomeAgent-v0"


def test_register_duplicate_id():
    registry = agent_registration.AgentRegistry()

    registry.register("Agent-v0")
    with pytest.raises(ValueError, match=r"Cannot re-register ID"):
        registry.register("Agent-v0")


def test_make_missing_agent():
    registry = agent_registration.AgentRegistry()

    with pytest.raises(KeyError, match=r"No registered agent with ID"):
        registry.make("Agent-v0")


def test_make_deprecated_agent():
    registry = agent_registration.AgentRegistry()

    registry.register("Agent-v0", entry_point=None)
    with pytest.raises(ValueError, match=r"Attempting to make deprecated agent"):
        registry.make("Agent-v0")


@pytest.mark.parametrize(
    "bad_id",
    [
        "AgentMissingVersionName",
        "AgentNoDashBetweenVersionv0",
        "user1/user2/AgentTwoUsers-v0",
        "AgentNaughty$ymbols-v0",
    ],
)
def test_malformed_agent_id(bad_id):
    registry = agent_registration.AgentRegistry()

    with pytest.raises(ValueError, match=r"Attempted to register malformed agent ID"):
        registry.register(bad_id)
