"""Registration of models.

Enables registering specifications of models and parameters combinations, under a unique ID,
which can be passed to kotsu's run interface.
"""
from kotsu import _registration


ModelSpec = _registration.EntitySpec
ModelRegistry = _registration.EntityRegistry
