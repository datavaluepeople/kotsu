import pytest

from kotsu import registration


def fake_entity_factory(param_1, param_2):
    assert param_1 == "PARAM_1"
    assert param_2 == "PARAM_2"


class FakeEntity:
    def __init__(self, param_1, param_2):
        assert param_1 == "PARAM_1"
        assert param_2 == "PARAM_2"


@pytest.mark.parametrize(
    "entry_point",
    [
        fake_entity_factory,
        FakeEntity,
        "tests.test_registration:fake_entity_factory",
        "tests.test_registration:FakeEntity",
    ],
)
def test_registration(entry_point):
    registry = registration._Registry()

    registry.register(
        id="SomeEntity-v0",
        entry_point=entry_point,
        kwargs={"param_1": "PARAM_1", "param_2": "PARAM_2"},
    )

    registry.register(
        id="SomeEntity-v1",
        entry_point=entry_point,
        kwargs={"param_1": "WRONG_PARAM_1", "param_2": "PARAM_2"},
    )

    # We can't use mocks, since we want to test importing via strings
    # So we run the asserts in the function
    # But we protect against the function never being run (and the test silently passing)
    # by also asserting that there _is_ a failure if we run with the wrong parameters
    registry.make(id="SomeEntity-v0")
    with pytest.raises(AssertionError):
        registry.make(id="SomeEntity-v1")

    all_specs = list(registry.all())
    assert len(all_specs) == 2
    assert all_specs[0].id == "SomeEntity-v0"
    assert all_specs[1].id == "SomeEntity-v1"


def test_register_duplicate_id():
    registry = registration._Registry()

    registry.register("Entity-v0")
    with pytest.raises(ValueError, match=r"Cannot re-register ID"):
        registry.register("Entity-v0")


def test_make_missing_entity():
    registry = registration._Registry()

    with pytest.raises(KeyError, match=r"No registered entity with ID"):
        registry.make("Entity-v0")


def test_make_deprecated_entity():
    registry = registration._Registry()

    registry.register("Entity-v0", entry_point=None)
    with pytest.raises(ValueError, match=r"Attempting to make deprecated entity"):
        registry.make("Entity-v0")


@pytest.mark.parametrize(
    "bad_id",
    [
        "EntityMissingVersionName",
        "EntityNoDashBetweenVersionv0",
        "user1/user2/EntityTwoUsers-v0",
        "EntityNaughty$ymbols-v0",
    ],
)
def test_malformed_entity_id(bad_id):
    registry = registration._Registry()

    with pytest.raises(ValueError, match=r"Attempted to register malformed entity ID"):
        registry.register(bad_id)
