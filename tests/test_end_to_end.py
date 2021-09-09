"""An end to end example and test."""
from typing import Callable

from sklearn import datasets, svm
from sklearn.model_selection import cross_val_score

from kotsu import run
from kotsu.registration import ModelRegistry, ValidationRegistry


model_registry = ModelRegistry()

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

validation_registry = ValidationRegistry()


def factory_iris_cross_val(folds: int) -> Callable:
    """Factory for iris cross validation."""

    def iris_cross_val(model) -> dict:
        """Iris classification cross validation."""
        X, y = datasets.load_iris(return_X_y=True)
        scores = cross_val_score(model, X, y, cv=folds)
        results = {f"fold_{i}_score": score for i, score in enumerate(scores)}
        results["mean_score"] = scores.mean()
        results["std_score"] = scores.std()
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
    run.run(model_registry, validation_registry, tmpdir)
