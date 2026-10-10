"""Exceptions raised by gixo."""


class GixoError(Exception):
    """Base class for all gixo errors."""


class ConfigurationError(GixoError):
    """A rule or setting is invalid, e.g. a regex that does not compile."""
