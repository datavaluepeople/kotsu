"""Init."""

from kotsu import registration  # noqa: F401
from kotsu import run  # noqa: F401

from ._version import get_versions


__version__ = get_versions()["version"]
del get_versions
