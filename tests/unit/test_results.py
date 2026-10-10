import dataclasses

import pytest

from gixo.results import ValidationResult, Violation


def test_ok_is_valid() -> None:
    result = ValidationResult.ok()
    assert result.is_valid
    assert result.violations == ()
    assert result.message == "OK"


def test_fail_has_one_violation() -> None:
    result = ValidationResult.fail("branch.pattern", "Bad name.")
    assert not result.is_valid
    assert result.violations == (Violation("branch.pattern", "Bad name."),)
    assert result.message == "Bad name."


def test_message_joins_multiple_violations() -> None:
    result = ValidationResult((Violation("a", "First."), Violation("b", "Second.")))
    assert result.message == "First.\nSecond."


def test_result_is_immutable() -> None:
    result = ValidationResult.ok()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.violations = ()  # type: ignore[misc]
