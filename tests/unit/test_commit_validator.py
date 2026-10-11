from typing import Any

import pytest

from gixo.exceptions import ConfigurationError
from gixo.validators.commit import validate_commit_message


def rules(message: str, **settings: Any) -> list[str]:
    result = validate_commit_message(message, **settings)
    return [v.rule for v in result.violations]


@pytest.mark.parametrize(
    "message",
    [
        "feat(api): add login endpoint",
        "fix: handle missing user",
        "feat!: drop Python 3.10",
        "refactor(core)!: rename settings",
        "docs: explain hooks\n\nLonger body text.\n\nRefs: PROJ-1",
        "fix: trailing newline from git\n",
        "chore(release): v0.1.0",
    ],
)
def test_valid_messages(message: str) -> None:
    result = validate_commit_message(message)
    assert result.is_valid, result.message


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("", ["commit.empty"]),
        ("  \n\n ", ["commit.empty"]),
        ("unknown: change behavior", ["commit.type"]),
        ("Feat: add login", ["commit.type"]),
        ("add login endpoint", ["commit.format"]),
        ("feat(my api): add login", ["commit.format"]),
        ("feat:no space", ["commit.format"]),
        ("feat: ", ["commit.format"]),
        ("feat(): empty scope", ["commit.format"]),
        (" feat: leading space", ["commit.whitespace"]),
        ("feat: add login\nbody without blank line", ["commit.body_separator"]),
    ],
)
def test_invalid_messages(message: str, expected: list[str]) -> None:
    assert rules(message) == expected


def test_type_message_lists_allowed_types() -> None:
    result = validate_commit_message("wip: x", allowed_types=["feat", "fix"])
    assert (
        result.message == "Commit type 'wip' is not allowed. Allowed types: feat, fix."
    )


def test_custom_allowed_types() -> None:
    assert rules("perf: faster", allowed_types=["perf"]) == []
    assert rules("feat: x", allowed_types=["perf"]) == ["commit.type"]


class TestSubjectLength:
    def test_exactly_at_limit_passes(self) -> None:
        subject = "feat: " + "x" * 66
        assert len(subject) == 72
        assert rules(subject) == []

    def test_one_over_limit_fails(self) -> None:
        subject = "feat: " + "x" * 67
        result = validate_commit_message(subject)
        assert [v.rule for v in result.violations] == ["commit.subject_length"]
        assert "73 characters" in result.message
        assert "maximum is 72" in result.message

    def test_prefix_counts_toward_length(self) -> None:
        # The description alone is 10 characters; the full subject is 20.
        assert rules("feat(scope): 1234567", max_subject_length=19) == [
            "commit.subject_length"
        ]
        assert rules("feat(scope): 1234567", max_subject_length=20) == []

    def test_trailing_whitespace_does_not_count(self) -> None:
        assert rules("feat: abc   \n", max_subject_length=9) == []

    def test_only_subject_line_is_measured(self) -> None:
        assert rules("feat: x\n\n" + "y" * 200, max_subject_length=10) == []


class TestTicket:
    def test_missing_ticket_fails_when_required(self) -> None:
        result = validate_commit_message("feat: add login", require_ticket=True)
        assert [v.rule for v in result.violations] == ["commit.ticket"]
        assert "[A-Z][A-Z0-9]+-\\d+" in result.message

    def test_ticket_in_subject(self) -> None:
        assert rules("feat: PROJ-123 add login", require_ticket=True) == []

    def test_ticket_in_body(self) -> None:
        message = "feat: add login\n\nRefs: PROJ-123"
        assert rules(message, require_ticket=True) == []

    def test_custom_ticket_pattern(self) -> None:
        settings: dict[str, Any] = {"require_ticket": True, "ticket_pattern": r"#\d+"}
        assert rules("fix: crash (#42)", **settings) == []
        assert rules("fix: crash PROJ-1", **settings) == ["commit.ticket"]

    def test_not_required_by_default(self) -> None:
        assert rules("feat: add login") == []


class TestMergeAndRevert:
    MERGE = "Merge branch 'main' into feature/x"
    REVERT = 'Revert "feat: add login"\n\nThis reverts commit abc123.'

    def test_merge_allowed_by_default(self) -> None:
        assert rules(self.MERGE) == []

    def test_merge_skips_ticket_rule(self) -> None:
        assert rules(self.MERGE, require_ticket=True) == []

    def test_merge_rejected_when_disabled(self) -> None:
        assert rules(self.MERGE, allow_merge_commits=False) == ["commit.format"]

    def test_revert_allowed_by_default(self) -> None:
        assert rules(self.REVERT) == []

    def test_revert_rejected_when_disabled(self) -> None:
        assert rules(self.REVERT, allow_revert_commits=False) == ["commit.format"]


def test_reports_every_violation_in_order() -> None:
    message = "wip: " + "x" * 100 + "\nno blank line"
    assert rules(message, require_ticket=True) == [
        "commit.type",
        "commit.subject_length",
        "commit.body_separator",
        "commit.ticket",
    ]


def test_windows_line_endings() -> None:
    assert rules("feat: x\r\n\r\nbody\r\n") == []


@pytest.mark.parametrize(
    ("settings", "match"),
    [
        ({"convention": "angular"}, "Unsupported commit convention"),
        ({"max_subject_length": 0}, "max_subject_length"),
        ({"allowed_types": []}, "at least one type"),
        ({"allowed_types": "feat"}, "not the string"),
        ({"allowed_types": ["feat", "ci-cd"]}, "Invalid commit type"),
        ({"ticket_pattern": "(unclosed"}, "Invalid ticket pattern"),
    ],
)
def test_invalid_settings_raise(settings: dict[str, Any], match: str) -> None:
    with pytest.raises(ConfigurationError, match=match):
        validate_commit_message("feat: x", **settings)


def test_invalid_settings_raise_even_for_empty_message() -> None:
    with pytest.raises(ConfigurationError):
        validate_commit_message("", max_subject_length=0)


def test_public_import() -> None:
    from gixo import validate_commit_message as exported

    assert exported is validate_commit_message
