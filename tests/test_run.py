import logging
from unittest import mock

import pandas as pd
import pytest

import kotsu


logger = logging.getLogger(__name__)


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


def test_form_results(mocker, tmpdir):
    patched_run_validation_model = mocker.patch(
        "kotsu.run._run_validation_model",
        side_effect=[({"test_result": "result"}, 10), ({"test_result": "result_2"}, 20)],
    )
    patched_store_write = mocker.patch("kotsu.store.write")

    models = ["model_1", "model_2"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    results_path = str(tmpdir) + "validation_results.csv"
    kotsu.run.run(model_registry, validation_registry, results_path=results_path)

    results_df = pd.DataFrame(
        [
            {
                "validation_id": "validation_1",
                "model_id": "model_1",
                "runtime_secs": 10,
                "test_result": "result",
            },
            {
                "validation_id": "validation_1",
                "model_id": "model_2",
                "runtime_secs": 20,
                "test_result": "result_2",
            },
        ]
    )

    assert patched_run_validation_model.call_count == 2
    pd.testing.assert_frame_equal(
        patched_store_write.call_args[0][0],
        results_df,
    )
    assert patched_store_write.call_args[0][1] == results_path


@pytest.mark.parametrize("artefacts_store_directory", [None, "test_dir/"])
def test_validation_calls(artefacts_store_directory, mocker):
    _ = mocker.patch("kotsu.store.write")

    models = ["model_1", "model_2"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    kotsu.run.run(
        model_registry,
        validation_registry,
        artefacts_store_directory=artefacts_store_directory,
    )
    if artefacts_store_directory is not None:
        validation_registry.instances[0].assert_has_calls(
            [
                mock.call(
                    model_registry.instances[0],
                    artefacts_directory=f"{artefacts_store_directory}validation_1/model_1/",
                ),
                mock.call(
                    model_registry.instances[1],
                    artefacts_directory=f"{artefacts_store_directory}validation_1/model_2/",
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


@pytest.mark.parametrize("skip_if_prior_result", [True, False])
def test_skip_if_prior_result(skip_if_prior_result, mocker, tmpdir):
    patched_run_validation_model = mocker.patch(
        "kotsu.run._run_validation_model",
        side_effect=[
            ({"test_result": "result"}, 10),
            ({"test_result": "result_2"}, 20),
            ({"test_result": "result_3"}, 30),
        ],
    )

    models = ["model_1"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    results_path = str(tmpdir) + "validation_results.csv"
    kotsu.run.run(
        model_registry,
        validation_registry,
        results_path=results_path,
        skip_if_prior_result=skip_if_prior_result,
    )

    results_df = pd.DataFrame(
        [
            {
                "validation_id": "validation_1",
                "model_id": "model_1",
                "runtime_secs": 10,
                "test_result": "result",
            },
            {
                "validation_id": "validation_1",
                "model_id": "model_2",
                "runtime_secs": 20,
                "test_result": "result_2",
            },
        ]
    )

    out_df = pd.read_csv(results_path)

    assert patched_run_validation_model.call_count == 1
    pd.testing.assert_frame_equal(out_df, results_df.iloc[:1])

    models = ["model_1", "model_2"]
    model_registry = FakeRegistry(models)

    kotsu.run.run(
        model_registry,
        validation_registry,
        results_path=results_path,
        skip_if_prior_result=skip_if_prior_result,
    )

    out_df = pd.read_csv(results_path)

    if skip_if_prior_result:
        assert patched_run_validation_model.call_count == 2
        pd.testing.assert_frame_equal(out_df, results_df)
    elif not skip_if_prior_result:
        results_df = pd.DataFrame(
            [
                {
                    "validation_id": "validation_1",
                    "model_id": "model_1",
                    "runtime_secs": 20,
                    "test_result": "result_2",
                },
                {
                    "validation_id": "validation_1",
                    "model_id": "model_2",
                    "runtime_secs": 30,
                    "test_result": "result_3",
                },
            ]
        )
        assert patched_run_validation_model.call_count == 3
        pd.testing.assert_frame_equal(out_df, results_df)


@pytest.mark.parametrize(
    "result",
    [
        ({"validation_id": "_", "test_result": "result"}, 10),
        ({"model_id": "_", "test_result": "result_2"}, 20),
        ({"runtime_secs": "_", "test_result": "result_3"}, 30),
    ],
)
def test_raise_if_valiation_returns_privilidged_key_name(result, mocker, tmpdir):
    _ = mocker.patch("kotsu.run._run_validation_model", side_effect=[result])
    models = ["model_1"]
    model_registry = FakeRegistry(models)
    validations = ["validation_1"]
    validation_registry = FakeRegistry(validations)

    results_path = str(tmpdir) + "validation_results.csv"

    with pytest.raises(ValueError):
        kotsu.run.run(
            model_registry,
            validation_registry,
            results_path=results_path,
        )
