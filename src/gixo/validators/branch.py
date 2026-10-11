"""Branch-name validation."""

from gixo._regex import compile_pattern
from gixo.results import ValidationResult


def validate_branch(name: str, *, pattern: str) -> ValidationResult:
    """Check a branch name against a required regex pattern.

    The whole name must match (``re.fullmatch``), so ``^``/``$`` anchors are
    optional. Empty names and names containing whitespace are always invalid.

    Args:
        name: The branch name to check, e.g. ``"feature/PROJ-123-add-login"``.
        pattern: Regular expression the whole name must match.

    Returns:
        A ``ValidationResult`` with at most one violation, whose rule is
        ``branch.empty``, ``branch.whitespace``, or ``branch.pattern``.

    Raises:
        ConfigurationError: If ``pattern`` is not a valid regular expression.
    """
    regex = compile_pattern(pattern, "branch pattern")

    if not name.strip():
        return ValidationResult.fail("branch.empty", "Branch name is empty.")
    if any(ch.isspace() for ch in name):
        return ValidationResult.fail(
            "branch.whitespace", f"Branch name {name!r} contains whitespace."
        )
    if regex.fullmatch(name) is None:
        return ValidationResult.fail(
            "branch.pattern",
            f"Branch name {name!r} does not match required pattern '{pattern}'.",
        )
    return ValidationResult.ok()
