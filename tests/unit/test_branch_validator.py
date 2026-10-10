import pytest

from gixo.exceptions import ConfigurationError
from gixo.validators.branch import validate_branch

PATTERN = r"^(feature|bugfix)/[A-Z]+-\d+-.+$"


@pytest.mark.parametrize(
    "name",
    ["feature/PROJ-123-add-login", "bugfix/ABC-42-fix-timeout"],
)
def test_valid_names(name: str) -> None:
    result = validate_branch(name, pattern=PATTERN)
    assert result.is_valid
    assert result.violations == ()


@pytest.mark.parametrize(
    ("name", "rule"),
    [
        ("main", "branch.pattern"),
        ("feature/add-login", "branch.pattern"),
        ("", "branch.empty"),
        ("   ", "branch.empty"),
        ("feature/PROJ-1-add login", "branch.whitespace"),
        (" feature/PROJ-1-x", "branch.whitespace"),
        ("feature/PROJ-1-x\n", "branch.whitespace"),
    ],
)
def test_invalid_names(name: str, rule: str) -> None:
    result = validate_branch(name, pattern=PATTERN)
    assert not result.is_valid
    assert [v.rule for v in result.violations] == [rule]


def test_message_names_the_pattern() -> None:
    result = validate_branch("main", pattern=PATTERN)
    assert "main" in result.message
    assert PATTERN in result.message


def test_unanchored_pattern_requires_full_match() -> None:
    assert validate_branch("feature/a", pattern=r"feature/.+").is_valid
    assert not validate_branch("xfeature/a", pattern=r"feature/.+").is_valid


def test_invalid_regex_raises_configuration_error() -> None:
    with pytest.raises(ConfigurationError, match="Invalid branch pattern"):
        validate_branch("main", pattern="(unclosed")


def test_invalid_regex_raises_even_for_empty_name() -> None:
    with pytest.raises(ConfigurationError):
        validate_branch("", pattern="[")


def test_public_import() -> None:
    from gixo import validate_branch as exported

    assert exported is validate_branch
