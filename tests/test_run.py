from unittest import mock

import kotsu


class FakeRegistry:
    def __init__(self, ids):
        self.ids = ids

    def all(self):
        entitys = []
        for id_ in self.ids:
            entity = mock.Mock()
            entity.id = id_
            entitys.append(entity)
        return entitys


def test_run(mocker):
    patched_run_validation_model = mocker.patch(
        "kotsu.run._run_validation_model",
        side_effect=[({"test_result": "result"}, 10), ({"test_result": "result"}, 10)],
    )
    patched_store_write = mocker.patch("kotsu.store.write")

    store_directory = "test_dir"
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
