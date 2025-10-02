# kotsu: lightweight framework for structuring model validation

![lint-test status](https://github.com/datavaluepeople/kotsu/actions/workflows/run-ci.yml/badge.svg?branch=main&label=Test)
[![codecov](https://codecov.io/gh/datavaluepeople/kotsu/branch/main/graph/badge.svg?token=3W8T5OSRZZ)](https://codecov.io/gh/datavaluepeople/kotsu)
[![PyPI version](https://img.shields.io/pypi/v/kotsu.svg)](https://pypi.org/project/kotsu/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/kotsu.svg?label=pypi%20downloads)](https://pypi.org/project/kotsu/)
[![conda-forge version](https://img.shields.io/conda/vn/conda-forge/kotsu.svg)](https://anaconda.org/conda-forge/kotsu)
[![conda-forge downloads](https://img.shields.io/conda/dn/conda-forge/kotsu.svg?label=conda%20downloads)](https://anaconda.org/conda-forge/kotsu)

## What is it?

**kotsu** is Python package that provides a lightweight and flexible framework to structure
validating and comparing machine learning models. It aims to provide the skeleton on which to
develop models and to validate them in a robust and repeatable way, **minimizing
bloat or overhead**. Its flexibility allows usage with **any model interface** and any
validation technique, no matter how complex. The structure it provides **avoids
common pitfalls** that occur when attempting to make fair comparisons between models.

## Main Features

  - Register a model with hyperparameters to a unique ID
  - Register validations to a unique ID
  - Run all registered models through all registered validations, and have the results compiled and
    stored as a CSV
  - Optionally passes an `artefacts_store_dir` to your validations, for storing of outputs
    for further analysis, e.g. trained models or model predictions on test data sets
  - Doesn't enforce any constraints or requirements on your models' interfaces
  - Pure Python package, with no other setup or configuration of other systems required

## Where to get it

The source code is currently hosted on GitHub at: https://github.com/datavaluepeople/kotsu

The latest released version of the package can be installed from PyPI with:

```sh
pip install kotsu
```

The package is also published on conda-forge:

```sh
conda install -c conda-forge kotsu
```

## Usage

The following demonstrates a simple usage of kotsu to register and validate multiple models over
multiple validations.

**Import kotsu and your packages for modelling:**

```python
import kotsu
from sklearn import datasets, svm
from sklearn.model_selection import cross_val_score
```

**Register your competing models:**

Here we register two Support Vector Classifiers with different hyper-parameters.

```python
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
```

**Instantiate a registered model:**

If you want to use your registries outside of `kotsu.run`, you can create model
instances directly from their registered IDs. This is useful if you want to run
an ad-hoc validation or interact with a model in an interactive environment
without running the full benchmarking loop.

```python
model_instance = model_registry.make("SVC-v1")
```

**Register your validations:**

You can register multiple validations if you want to compare models in different scenarios, e.g. on
different datasets. Your validations should take an instance of your models as an argument, then
return a dictionary containing the results from validation of that model. Here we register two
Cross-Validation validations with different numbers of folds.

```python
validation_registry = kotsu.registration.ValidationRegistry()


def factory_iris_cross_validation(folds: int):
    """Factory for iris cross validation."""

    def iris_cross_validation(model) -> dict:
        """Iris classification cross validation."""
        X, y = datasets.load_iris(return_X_y=True)
        scores = cross_val_score(model, X, y, cv=folds)
        results = {f"fold_{i}_score": score for i, score in enumerate(scores)}
        results["mean_score"] = scores.mean()
        results["std_score"] = scores.std()
        return results

    return iris_cross_validation


validation_registry.register(
    id="iris_cross_validation-v1",
    entry_point=factory_iris_cross_validation,
    kwargs={"folds": 5},
)

validation_registry.register(
    id="iris_cross_validation-v2",
    entry_point=factory_iris_cross_validation,
    kwargs={"folds": 10},
)
```

**Run the models through the validations:**

We choose the current directory as the location for writing the results.

```python
kotsu.run(model_registry, validation_registry)
```

Then find the results from each model-validation combination in a CSV written to the current
directory.

### Documentation on interfaces

See [kotsu.typing](https://github.com/datavaluepeople/kotsu/blob/main/kotsu/typing.py) for
documentation on the main entities; Models, Validations, and Results, and their interfaces.

### Comprehensive example

See the [end to end test](https://github.com/datavaluepeople/kotsu/blob/main/tests/test_end_to_end.py)
for a more comprehensive example usage of kotsu, which includes storing the trained models from
each model-validation run.

## Releasing

### Updating the conda-forge feedstock

kotsu is distributed on conda-forge through the
[kotsu-feedstock repository](https://github.com/conda-forge/kotsu-feedstock).
Maintainers (`@DBCerigo`, `@ali-tny`, and `@alex-hh`) can publish new releases by:

1. Releasing the desired version to PyPI (push a new version tag) so that the source distribution
   is available.
2. Creating a branch on `conda-forge/kotsu-feedstock` and updating `recipe/meta.yaml`:
   - set the `version` variable to the new package version and reset the `number` field to `0`.
   - update the `sha256` checksum for the source archive. You can obtain it with:
     ```sh
     curl -L https://pypi.io/packages/source/k/kotsu/kotsu-<version>.tar.gz | shasum -a 256
     ```
3. If dependencies change, ask the conda-forge bots to rerender by commenting
   `@conda-forge-admin, please rerender` on the pull request (or run
   `conda smithy rerender` locally).
4. Open a pull request to the feedstock and merge it once CI passes and the maintainers approve.

Once merged, conda-forge will publish the new build automatically.

## License

[MIT](LICENSE.txt)

