"""Registration of agents.

Enables registering specifications of agents and parameters combinations, under a unique ID,
which can be passed to Truman's run interface.

Based on: https://github.com/openai/gym/blob/master/gym/envs/registration.py
"""
from typing import Callable, Optional, Union
from truman.typing import Agent

import importlib
import logging
import re

from gym import Env


logger = logging.getLogger(__name__)

# A unique ID for an agent; a name followed by a version number.
# Agent-name is group 1, version is group 2.
# [username/](agent-name)-v(version)
agent_id_re = re.compile(r"^(?:[\w:-]+\/)?([\w:.-]+)-v(\d+)$")


def _load(name: str):
    """Load a python object from string.

    Args:
        name: of the form `path.to.module:object`
    """
    mod_name, attr_name = name.split(":")
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr_name)
    return fn


class AgentSpec:
    """A specification for a particular instance of an agent.

    Used to register agent and parameters full specification for evaluations.

    Args:
        id: A unique agent ID
            Required format; [username/](agent-name)-v(version)
            [username/] is optional.
        entry_point: The python entrypoint of the agent class. Should be one of:
            - the string path to the python object (e.g.module.name:factory_func, or
              module.name:Class)
            - the python object (class or factory) itself
            Should be set to `None` to denote that the agent is now defunct, replaced by a newer
            version.
        nondeterministic: Whether this agent is non-deterministic even after seeding
        kwargs: The kwargs to pass to the agent entry point when instantiating the agent
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

        match = agent_id_re.search(id)
        if not match:
            raise ValueError(
                f"Attempted to register malformed agent ID: {id}. "
                f"(Currently all IDs must be of the form {agent_id_re.pattern}.)"
            )

    def make(self, env: Optional[Env] = None, **kwargs) -> Agent:
        """Instantiates an instance of the agent compatible with given env."""
        if self.entry_point is None:
            raise ValueError(
                f"Attempting to make deprecated agent {self.id}. "
                "(HINT: is there a newer registered version of this agent?)"
            )
        _kwargs = self._kwargs.copy()
        _kwargs.update(kwargs)
        if callable(self.entry_point):
            factory = self.entry_point
        else:
            factory = _load(self.entry_point)
        agent = factory(env, **_kwargs)

        return agent

    def __repr__(self):
        return "AgentSpec({})".format(self.id)


class AgentRegistry:
    """Register an agent by ID.

    IDs should remain stable over time and should be guaranteed to resolve to the same agent
    dynamics (or be desupported).
    """

    def __init__(self):
        self.agent_specs = {}

    def make(self, id: str, env: Optional[Env] = None, **kwargs) -> Agent:
        """Instantiate an instance of an agent of the given ID compatible with the given env."""
        logging.info(f"Making new agent: {id} ({kwargs})")
        try:
            return self.agent_specs[id].make(env, **kwargs)
        except KeyError:
            raise KeyError(f"No registered agent with ID {id}")

    def all(self):
        """Return all the agents in the registry."""
        return self.agent_specs.values()

    def register(
        self,
        id: str,
        entry_point: Optional[Union[Callable, str]] = None,
        nondeterministic: bool = False,
        kwargs: Optional[dict] = None,
    ):
        """Register an agent.

        Args:
            id: A unique agent ID
                Required format; [username/](agent-name)-v(version)
                [username/] is optional.
            entry_point: The python entrypoint of the agent class. Should be one of:
                - the string path to the python object (e.g.module.name:factory_func, or
                  module.name:Class)
                - the python object (class or factory) itself
                Should be set to `None` to denote that the agent is now defunct, replaced by a
                newer version.
            nondeterministic: Whether this agent is non-deterministic even after seeding
            kwargs: The kwargs to pass to the agent entry point when instantiating the agent
        """
        if id in self.agent_specs:
            raise ValueError(f"Cannot re-register ID {id}")
        self.agent_specs[id] = AgentSpec(id, entry_point, nondeterministic, kwargs)
