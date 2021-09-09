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
Validation = Callable[[Model], Results]

# Validations can also take a Model _and_ an artefact directory, which is a string, which
# Validations may use as the location to write any artefacts/data objects output by the Validation.
# For storing Model artefacts (e.g. saving model state, or saving training history), Validations
# should pass the `artefact_directory` to Models directly within the Validation, and Models should
# be implemented such to use this arg as their output artefact store location.
ValidationWithOutputArtefacts = Callable[[Model, str], Results]
