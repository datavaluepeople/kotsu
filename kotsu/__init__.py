"""Init."""

from importlib.metadata import version

from kotsu import (
    registration,  # noqa: F401
    run,  # noqa: F401
)


__version__ = version("kotsu")
