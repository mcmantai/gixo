"""Compile user-supplied regular expressions with clear configuration errors."""

import re
from functools import lru_cache

from gixo.exceptions import ConfigurationError


@lru_cache(maxsize=64)
def compile_pattern(pattern: str, label: str) -> re.Pattern[str]:
    """Compile ``pattern``, raising ``ConfigurationError`` if it is invalid.

    ``label`` names the setting in the error, e.g. ``"branch pattern"``.
    """
    try:
        return re.compile(pattern)
    except re.error as err:
        raise ConfigurationError(f"Invalid {label} '{pattern}': {err}") from err
