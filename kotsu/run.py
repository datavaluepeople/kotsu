"""Interface for running a registry of models on a registry of validations."""
from typing import Tuple

import time

from kotsu.registration import ModelRegistry, ValidationRegistry


def run(
    model_registry: ModelRegistry,
    validation_registry: ValidationRegistry,
    store_directory: str,
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
        run_params: A dictionary of optional run parameters.
    """
    for validation_spec in validation_registry.all():
        for model_spec in model_registry.all():
            validation = validation_spec.make()
            model = model_spec.make()
            results, elapsed_secs = _run_validation_model(validation, model, run_params)


def _run_validation_model(validation, model, run_params: dict = {}) -> Tuple[dict, float]:
    """Run given validation on given model, and store the results.

    Returns:
        A tuple of (dict of results, elapsed time in seconds)
    """
    start_time = time.time()
    results = validation(model)
    elapsed_secs = time.time() - start_time
    return results, elapsed_secs
