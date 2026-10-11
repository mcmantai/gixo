"""Commit-message validation."""

import re
from collections.abc import Iterable

from gixo._regex import compile_pattern
from gixo.exceptions import ConfigurationError
from gixo.results import ValidationResult, Violation

DEFAULT_TYPES = ("feat", "fix", "docs", "refactor", "test", "build", "chore")
DEFAULT_TICKET_PATTERN = r"[A-Z][A-Z0-9]+-\d+"
SUPPORTED_CONVENTIONS = ("conventional",)

_TYPE = re.compile(r"[A-Za-z]+")
_HEADER = re.compile(
    r"(?P<type>[A-Za-z]+)"
    r"(?:\((?P<scope>[^()\s]+)\))?"
    r"(?P<breaking>!)?"
    r": (?P<description>\S.*)"
)


def validate_commit_message(
    message: str,
    *,
    convention: str = "conventional",
    allowed_types: Iterable[str] = DEFAULT_TYPES,
    max_subject_length: int = 72,
    require_ticket: bool = False,
    ticket_pattern: str = DEFAULT_TICKET_PATTERN,
    allow_merge_commits: bool = True,
    allow_revert_commits: bool = True,
) -> ValidationResult:
    """Check a commit message against Conventional Commit rules.

    The subject is the first line, written as ``type(scope)!: description``,
    where the scope and ``!`` are optional. Trailing whitespace is ignored;
    leading whitespace on the subject is rejected. The subject length includes
    the ``type(scope): `` prefix. All violations are reported, not just the
    first.

    Args:
        message: The full commit message, including any body.
        convention: Commit convention to enforce. Only ``"conventional"`` is
            supported.
        allowed_types: Commit types accepted in the subject. Case-sensitive.
        max_subject_length: Maximum length of the subject line.
        require_ticket: Require ``ticket_pattern`` somewhere in the message.
        ticket_pattern: Regex for a ticket id, e.g. ``PROJ-123``.
        allow_merge_commits: Accept subjects starting with ``Merge `` without
            further checks.
        allow_revert_commits: Accept subjects starting with ``Revert "``
            without further checks.

    Returns:
        A ``ValidationResult`` whose violation rules are any of
        ``commit.empty``, ``commit.whitespace``, ``commit.format``,
        ``commit.type``, ``commit.subject_length``, ``commit.body_separator``,
        and ``commit.ticket``.

    Raises:
        ConfigurationError: If any setting is invalid.
    """
    types = _check_types(allowed_types)
    if convention not in SUPPORTED_CONVENTIONS:
        raise ConfigurationError(
            f"Unsupported commit convention '{convention}'. "
            f"Supported: {', '.join(SUPPORTED_CONVENTIONS)}."
        )
    if max_subject_length < 1:
        raise ConfigurationError(
            f"max_subject_length must be at least 1, got {max_subject_length}."
        )
    ticket_re = compile_pattern(ticket_pattern, "ticket pattern")

    text = message.rstrip()
    if not text.strip():
        return ValidationResult.fail("commit.empty", "Commit message is empty.")

    subject, *rest = text.splitlines()
    subject = subject.rstrip()
    if allow_merge_commits and subject.startswith("Merge "):
        return ValidationResult.ok()
    if allow_revert_commits and subject.startswith('Revert "'):
        return ValidationResult.ok()

    violations: list[Violation] = []
    if subject != subject.lstrip():
        violations.append(
            Violation("commit.whitespace", "Commit subject starts with whitespace.")
        )
    elif (match := _HEADER.fullmatch(subject)) is None:
        violations.append(
            Violation(
                "commit.format",
                f"Commit subject {subject!r} does not follow Conventional Commits; "
                "expected 'type(scope): description'.",
            )
        )
    elif match["type"] not in types:
        violations.append(
            Violation(
                "commit.type",
                f"Commit type '{match['type']}' is not allowed. "
                f"Allowed types: {', '.join(types)}.",
            )
        )
    if len(subject) > max_subject_length:
        violations.append(
            Violation(
                "commit.subject_length",
                f"Commit subject is {len(subject)} characters; "
                f"the maximum is {max_subject_length}.",
            )
        )
    if rest and rest[0].strip():
        violations.append(
            Violation(
                "commit.body_separator",
                "Add a blank line between the commit subject and body.",
            )
        )
    if require_ticket and ticket_re.search(text) is None:
        violations.append(
            Violation(
                "commit.ticket",
                f"Commit message must reference a ticket matching '{ticket_pattern}'.",
            )
        )
    return ValidationResult(tuple(violations))


def _check_types(allowed_types: Iterable[str]) -> tuple[str, ...]:
    if isinstance(allowed_types, str):
        raise ConfigurationError(
            f"allowed_types must be a list of types, not the string '{allowed_types}'."
        )
    types = tuple(dict.fromkeys(allowed_types))
    if not types:
        raise ConfigurationError("allowed_types must contain at least one type.")
    for commit_type in types:
        if not isinstance(commit_type, str) or not _TYPE.fullmatch(commit_type):
            raise ConfigurationError(
                f"Invalid commit type {commit_type!r}; types must be letters only."
            )
    return types
