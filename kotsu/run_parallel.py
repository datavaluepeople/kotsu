"""Interface for parallelising running of registry of models on registry of validations."""
from typing import Optional

import csv
import functools
import logging
import multiprocessing as mp
import os

import numpy as np
import pandas as pd

from kotsu import run
from kotsu.registration import ModelRegistry, ValidationRegistry


logger = logging.getLogger(__name__)


# TODO maybe handle logging in the consumer process as well somehow?
# does consumer process have access to global variable logger? if we pass it?
def _results_writer(q, results_file, fieldnames, append=False):
    # n.b. a major advantage of using pandas is not having to deal with string conversion
    # currently we handle None/nan, but have no sophisticated treatment of e.g. dicts
    # TODO check behaviour if saving a dict field
    with open(results_file, "a" if append else "w", newline="") as csvfile:
        # any unexpected keys will just be ignored totally (extrasaction).
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        if not append:
            # logger.info does not automatically surface to main process so use print for now
            print(f"Creating csvfile {results_file} with columns {fieldnames}", flush=True)
            writer.writeheader()
        while True:
            val_res = q.get()
            if val_res == "kill":
                break
            logger.info(
                f"Appending result {val_res['model_id']}, {val_res['validation_id']}",
                flush=True,
            )

            def is_null(val):
                return val is None or (isinstance(val, float) and np.isnan(val))

            keys_to_drop = [k for k, v in val_res.items() if is_null(v)]
            for k in keys_to_drop:
                del val_res[k]
            writer.writerow(val_res)
            csvfile.flush()  # unsure if necessary


def _run_model_on_validation(
    q,
    model_spec,
    validation_spec,
    artefacts_directory=None,
    run_params=None,
):
    validation = validation_spec.make()
    model = model_spec.make()
    if artefacts_directory is not None:
        validation = functools.partial(validation, artefacts_directory=artefacts_directory)

    run_params = run_params or {}
    run_params["verbose"] = False  # hide tqdm
    results, elapsed_secs = run._run_validation_model(validation, model, run_params)
    results = run._add_meta_data_to_results(results, elapsed_secs, validation_spec, model_spec)
    q.put(results)
    return results


def run_parallel(
    model_registry: ModelRegistry,
    validation_registry: ValidationRegistry,
    results_path: str = "./validation_results.csv",
    skip_if_prior_result: bool = True,
    artefacts_store_directory: Optional[str] = None,
    run_params: Optional[dict] = None,
    n_procs: Optional[int] = None,
):
    """Run a registry of models on a registry of validations, parallelising across n_procs cores.

    https://stackoverflow.com/questions/13446445/python-multiprocessing-safely-writing-to-a-file

    Args:
        model_registry: A ModelRegistry containing the registry of models to be run through
            validations.
        validation_registry: A ValidationRegistry containing the registry of validations to run
            each model through.
        results_path: The file path to which the results will be written to, and results from prior
            runs will be read from.
        skip_if_prior_result: Flag, if True then will not run validation-model combinations
            that are found in the results at given results_path. If False then all combinations
            will be ran and any prior results in results_path will be completely overwritten.
        artefacts_store_directory: A directory path or URI location to store extra output
            artefacts of the validations and models.
        run_params: A dictionary of optional run parameters.
        n_procs: Number of cores (if None use all).
    """
    n_procs = n_procs or mp.cpu_count()
    fieldnames = ["validation_id", "model_id", "runtime_secs"]
    fieldnames += validation_registry.output_cols

    results_df = pd.DataFrame(columns=["validation_id", "model_id", "runtime_secs"])
    results_df["runtime_secs"] = results_df["runtime_secs"].astype(int)

    if skip_if_prior_result:
        try:
            results_df = pd.read_csv(results_path)
        except FileNotFoundError:
            pass

    results_df = results_df.set_index(["validation_id", "model_id"], drop=False)

    # must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()
    print(f"using a pool of {n_procs} workers")
    pool = mp.Pool(n_procs)
    jobs = []

    writer_res = pool.apply_async(
        _results_writer, (q, results_path, fieldnames), {"append": skip_if_prior_result}
    )

    for validation_spec in validation_registry.all():
        for model_spec in model_registry.all():
            if skip_if_prior_result and (validation_spec.id, model_spec.id) in results_df.index:
                logger.info(
                    f"Skipping validation - model: {validation_spec.id} - {model_spec.id}"
                    ", as found prior result in results."
                )
                continue

            artefacts_directory = None  # type: Optional[str]
            if artefacts_store_directory is not None:
                artefacts_directory = str(
                    os.path.join(
                        artefacts_store_directory, f"{validation_spec.id}/{model_spec.id}/"
                    )
                )
                os.makedirs(artefacts_directory, exist_ok=True)

            job_kwargs = {"artefacts_directory": artefacts_directory, "run_params": run_params}
            jobs.append(
                pool.apply_async(
                    _run_model_on_validation, (q, model_spec, validation_spec), job_kwargs
                )
            )

    for job in jobs:
        # get is blocking so for loop ends once all jobs have results
        job.get()

    q.put("kill")  # send signal that listener should break
    # N.B. calling get ensures that listener finishes and any exceptions are surfaced
    writer_res.get(timeout=10)

    # not sure what these do
    pool.close()
    pool.join()
