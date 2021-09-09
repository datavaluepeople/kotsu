"""Interface for running a registry of models on a registry of validations."""
from typing import Tuple
from kotsu.typing import Model, Results, Validation

import functools
import logging
import time

from kotsu import store
from kotsu.registration import ModelRegistry, ValidationRegistry


logger = logging.getLogger(__name__)


def run(
    model_registry: ModelRegistry,
    validation_registry: ValidationRegistry,
    store_directory: str,
    pass_artefacts_directory: bool = False,
    run_params: dict = {},
):
    """Run a registry of models on a registry of validations.

    Args:
        model_registry: A ModelRegistry containing the registry of models to be run through
            validations.
        validation_registry: A ValidationRegistry containing the registry of validations to run
            each model through.
        store_directory: A file path or URI location to store the validation results and any extra
            output artefacts of the validations and models.
        pass_artefacts_directory: Flag, if True then Validations will be passed an
            `artefacts_directory: str` kwarg along with Model arg.
        run_params: A dictionary of optional run parameters.
    """
    results_list = []
    for validation_spec in validation_registry.all():
        for model_spec in model_registry.all():
            logger.info(f"Running validation - model: {validation_spec.id} - {model_spec.id}")

            validation = validation_spec.make()
            if pass_artefacts_directory is True:
                artefacts_directory = store_directory + f"{validation_spec.id}/{model_spec.id}/"
                validation = functools.partial(validation, artefacts_directory=artefacts_directory)

            model = model_spec.make()

            results, elapsed_secs = _run_validation_model(validation, model, run_params)
            results.update(
                {
                    "validation_id": validation_spec.id,
                    "model_id": model_spec.id,
                    "runtime_secs": elapsed_secs,
                }
            )
            results_list.append(results)
    store.write(
        results_list, store_directory, to_front_cols=["validation_id", "model_id", "runtime_secs"]
    )


def _run_validation_model(
    validation: Validation, model: Model, run_params: dict = {}
) -> Tuple[Results, float]:
    """Run given validation on given model, and store the results.

    Returns:
        A tuple of (dict of results: Results type, elapsed time in seconds)
    """
    start_time = time.time()
    results = validation(model)
    elapsed_secs = time.time() - start_time
    return results, elapsed_secs
