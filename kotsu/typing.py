"""Define types and protocols for core interfaces for kotsu.

Mainly for documentation purposes.
"""
from typing import Any, Callable, Dict, Union


# The results from a validation run on a particular model.
# Each Results dict will become one row of a combined results dataframe. Each key within the
# Results dict will become a column of that dataframe, with values for matching keys across Results
# put into the same matching column.
# An example result from a 3-fold cross validation might be:
# `{"average_score": _, "standard_deviation_scores": _, "fold_1_score": _, "fold_2_score"...}`
Results = Dict[str, Union[float, str]]

# Models within kotsu are not constrained in any way. It is up to the user to write Models that
# have an interface compatible with their Validations.
Model = Any

# A Validation is a callable (e.g. function) that takes a Model, and returns a Results.
Validation = Callable[..., Results]

# Validations can also take a Model and two artefacts directory kwargs; `validation_artefacts_dir`
# and`model_artefacts_dir`. Each can be used to write any artefacts/data objects formed by the
# Validation or Model respectively. Passing `model_artefacts_dir` to Models is recommended for them
# to use to store output artefacts (e.g. saving model state, or saving training history) to
# directly.
ValidationWithOutputArtefacts = Callable[[Model, str, str], Results]
