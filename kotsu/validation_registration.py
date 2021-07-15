"""Registration of validations.

Enables registering specifications of validations and parameters combinations, under a unique ID,
which can be passed to kotsu's run interface.
"""
from kotsu import _registration


ValidationSpec = _registration.EntitySpec
ValidationRegistry = _registration.EntityRegistry
