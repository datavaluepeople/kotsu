"""Registration of entities (models, or validations).

Enables registering specifications of entities and parameters combinations, under a unique ID,
which can be passed to kotsu's run interface.

Based on: https://github.com/openai/gym/blob/master/gym/envs/registration.py
"""
from typing import Callable, Generic, List, Optional, TypeVar, Union
from kotsu.typing import Model, Validation

import importlib
import logging
import re


logger = logging.getLogger(__name__)


Entity = TypeVar("Entity")

# A unique ID for an entity; a name followed by a version number.
# Entity-name is group 1, version is group 2.
# [username/](entity-name)-v(version)
entity_id_re = re.compile(r"^(?:[\w:-]+\/)?([\w:.-]+)-v(\d+)$")


def _load(name: str):
    """Load a python object from string.

    Args:
        name: of the form `path.to.module:object`
    """
    mod_name, attr_name = name.split(":")
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr_name)
    return fn


class _Spec(Generic[Entity]):
    """A specification for a particular instance of an entity.

    Used to register entity and parameters full specification for evaluations.

    Args:
        id: A unique entity ID
            Required format; [username/](entity-name)-v(version)
            [username/] is optional.
        entry_point: The python entrypoint of the entity class. Should be one of:
            - the string path to the python object (e.g.module.name:factory_func, or
              module.name:Class)
            - the python object (class or factory) itself
            Should be set to `None` to denote that the entity is now defunct, replaced by a newer
            version.
        nondeterministic: Whether this entity is non-deterministic even after seeding
        kwargs: The kwargs to pass to the entity entry point when instantiating the entity
    """

    def __init__(
        self,
        id: str,
        entry_point: Optional[Union[Callable, str]] = None,
        nondeterministic: bool = False,
        kwargs: Optional[dict] = None,
    ):
        self.id = id
        self.entry_point = entry_point
        self.nondeterministic = nondeterministic
        self._kwargs = {} if kwargs is None else kwargs

        match = entity_id_re.search(id)
        if not match:
            raise ValueError(
                f"Attempted to register malformed entity ID: {id}. "
                f"(Currently all IDs must be of the form {entity_id_re.pattern}.)"
            )

    def make(self, **kwargs) -> Entity:
        """Instantiates an instance of the entity."""
        if self.entry_point is None:
            raise ValueError(
                f"Attempting to make deprecated entity {self.id}. "
                "(HINT: is there a newer registered version of this entity?)"
            )
        _kwargs = self._kwargs.copy()
        _kwargs.update(kwargs)
        if callable(self.entry_point):
            factory = self.entry_point
        else:
            factory = _load(self.entry_point)
        entity = factory(**_kwargs)

        return entity

    def __repr__(self):
        return "Spec({})".format(self.id)


class ValidationSpec(_Spec[Validation]):
    """Validation specification. output_cols attribute specifies results fields to store."""

    def __init__(self, *args, output_cols=["result"], **kwargs):
        super().__init__(*args, **kwargs)
        self.output_cols = output_cols


class _Registry(Generic[Entity]):
    """Register an entity by ID.

    IDs should remain stable over time and should be guaranteed to resolve to the same entity
    dynamics (or be desupported).
    """

    specClass = _Spec

    def __init__(self):
        self.entity_specs = {}

    def make(self, id: str, **kwargs) -> Entity:
        """Instantiate an instance of an entity of the given ID."""
        logging.info(f"Making new entity: {id} ({kwargs})")
        try:
            return self.entity_specs[id].make(**kwargs)
        except KeyError:
            raise KeyError(f"No registered entity with ID {id}")

    def all(self):
        """Return all the entitys in the registry."""
        return self.entity_specs.values()

    def register(
        self,
        id: str,
        entry_point: Optional[Union[Callable, str]] = None,
        nondeterministic: bool = False,
        kwargs: Optional[dict] = None,
    ):
        """Register an entity.

        Args:
            id: A unique entity ID
                Required format; [username/](entity-name)-v(version)
                [username/] is optional.
            entry_point: The python entrypoint of the entity class. Should be one of:
                - the string path to the python object (e.g.module.name:factory_func, or
                  module.name:Class)
                - the python object (class or factory) itself
                Should be set to `None` to denote that the entity is now defunct, replaced by a
                newer version.
            nondeterministic: Whether this entity is non-deterministic even after seeding
            kwargs: The kwargs to pass to the entity entry point when instantiating the entity
        """
        if id in self.entity_specs:
            raise ValueError(f"Cannot re-register ID {id}")
        self.entity_specs[id] = self.specClass(id, entry_point, nondeterministic, kwargs)


class ValidationRegistry(_Registry[Validation]):
    """Validation registry.

    Property output_cols determines what fields to create in output csv.
    """

    specClass = ValidationSpec

    @property
    def output_cols(self):
        """Return all unique output cols in child specifications.

        Downstream this determines what fields to create in output csv.
        """
        val_ids = sorted(self.entity_specs.keys())
        output_cols = []
        for val_id in val_ids:
            output_cols += [
                c for c in self.entity_specs[val_id].output_cols if c not in output_cols
            ]
        return output_cols

    def register(
        self,
        id: str,
        entry_point: Optional[Union[Callable, str]] = None,
        nondeterministic: bool = False,
        kwargs: Optional[dict] = None,
        output_cols: List[str] = ["result"],
    ):
        """Register an entity.

        Args:
            id: A unique entity ID
                Required format; [username/](entity-name)-v(version)
                [username/] is optional.
            entry_point: The python entrypoint of the entity class. Should be one of:
                - the string path to the python object (e.g.module.name:factory_func, or
                  module.name:Class)
                - the python object (class or factory) itself
                Should be set to `None` to denote that the entity is now defunct, replaced by a
                newer version.
            nondeterministic: Whether this entity is non-deterministic even after seeding
            kwargs: The kwargs to pass to the entity entry point when instantiating the entity
            output_cols: The fields in the validation results object which should be saved.
        """
        if id in self.entity_specs:
            raise ValueError(f"Cannot re-register ID {id}")
        self.entity_specs[id] = self.specClass(
            id, entry_point, nondeterministic, kwargs, output_cols=output_cols
        )


ModelSpec = _Spec[Model]
ModelRegistry = _Registry[Model]
