from unittest import mock

import pytest

import kotsu


class FakeRegistry:
    def __init__(self, ids):
        self.ids = ids
        entitys = []
        instances = []
        for id_ in ids:
            entity = mock.Mock()
            entity.id = id_
            entitys.append(entity)
            instance = mock.Mock()
            instance.return_value = {}
            entity.make.return_value = instance
            instances.append(instance)
        self.entitys = entitys
        self.instances = instances

    def all(self):
        return self.entitys


def test_form_results(mocker):
    patched_run_validation_model = mocker.patch(
        "kotsu.run._run_validation_model",
        side_effect=[({"test_result": "result"}, 10), ({"test_result": "result"}, 10)],
    )
    patched_store_write = mocker.patch("kotsu.store.write")

    store_directory = "test_dir/"
    models = ["model_1", "model_2"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    kotsu.run.run(model_registry, validation_registry, store_directory)

    results = [
        {
            "test_result": "result",
            "validation_id": "validation_1",
            "model_id": "model_1",
            "runtime_secs": 10,
        },
        {
            "test_result": "result",
            "validation_id": "validation_1",
            "model_id": "model_2",
            "runtime_secs": 10,
        },
    ]

    assert patched_run_validation_model.call_count == 2
    patched_store_write.assert_called_with(results, store_directory, to_front_cols=mock.ANY)


@pytest.mark.parametrize("pass_artefacts_directory", [True, False])
def test_validation_calls(pass_artefacts_directory, mocker):
    _ = mocker.patch("kotsu.store.write")

    store_directory = "test_dir/"
    models = ["model_1", "model_2"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    kotsu.run.run(
        model_registry,
        validation_registry,
        store_directory,
        pass_artefacts_directory=pass_artefacts_directory,
    )
    if pass_artefacts_directory is True:
        validation_registry.instances[0].assert_has_calls(
            [
                mock.call(
                    model_registry.instances[0],
                    artefacts_directory=f"{store_directory}validation_1/model_1/",
                ),
                mock.call(
                    model_registry.instances[1],
                    artefacts_directory=f"{store_directory}validation_1/model_2/",
                ),
            ]
        )
    else:
        validation_registry.instances[0].assert_has_calls(
            [
                mock.call(
                    model_registry.instances[0],
                ),
                mock.call(
                    model_registry.instances[1],
                ),
            ]
        )
