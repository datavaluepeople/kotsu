"""An end to end example and test."""

from typing import Callable

import pickle

from sklearn import datasets, svm
from sklearn.model_selection import cross_validate

import kotsu


model_registry = kotsu.registration.ModelRegistry()

model_registry.register(
    id="SVC-v1",
    entry_point=svm.SVC,
    kwargs={"kernel": "linear", "C": 1, "random_state": 1},
)

model_registry.register(
    id="SVC-v2",
    entry_point=svm.SVC,
    kwargs={"kernel": "linear", "C": 0.5, "random_state": 1},
)

validation_registry = kotsu.registration.ValidationRegistry()


def factory_iris_cross_val(folds: int) -> Callable:
    """Factory for iris cross validation."""

    def iris_cross_val(model, validation_artefacts_dir=None, model_artefacts_dir=None) -> dict:
        """Iris classification cross validation."""
        X, y = datasets.load_iris(return_X_y=True)
        scores = cross_validate(model, X, y, cv=folds, return_estimator=True)

        if model_artefacts_dir:
            # Save the trained models from each fold
            for fold_idx, model in enumerate(scores["estimator"]):
                with open(model_artefacts_dir + f"model_from_fold_{fold_idx}.pk", "wb") as f:
                    pickle.dump(model, f)

        results = {f"fold_{i}_score": score for i, score in enumerate(scores["test_score"])}
        results["mean_score"] = scores["test_score"].mean()
        results["std_score"] = scores["test_score"].std()
        return results

    return iris_cross_val


validation_registry.register(
    id="iris_cross_val-v1",
    entry_point=factory_iris_cross_val,
    kwargs={"folds": 5},
)

validation_registry.register(
    id="iris_cross_val-v2",
    entry_point=factory_iris_cross_val,
    kwargs={"folds": 10},
)


def test_run(tmpdir):
    kotsu.run.run(
        model_registry, validation_registry, results_path=str(tmpdir) + "/validation_results.csv"
    )


def test_run_save_models(tmpdir):
    kotsu.run.run(
        model_registry,
        validation_registry,
        results_path=str(tmpdir) + "/validation_results.csv",
        artefacts_store_dir=str(tmpdir),
    )
