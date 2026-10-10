"""The result type shared by all gixo validators."""

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Violation:
    """A single failed rule.

    Attributes:
        rule: Stable identifier for the rule, e.g. ``"branch.pattern"``.
        message: Human-readable explanation of what failed.
    """

    rule: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a validation. Valid when there are no violations."""

    violations: tuple[Violation, ...] = ()

    @property
    def is_valid(self) -> bool:
        """``True`` when no rules failed."""
        return not self.violations

    @property
    def message(self) -> str:
        """``"OK"`` when valid, otherwise each violation message on its own line."""
        if self.is_valid:
            return "OK"
        return "\n".join(v.message for v in self.violations)

    @classmethod
    def ok(cls) -> Self:
        """Return a passing result."""
        return cls()

    @classmethod
    def fail(cls, rule: str, message: str) -> Self:
        """Return a result with a single violation."""
        return cls((Violation(rule, message),))
