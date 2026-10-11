# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-10

### Added

- `validate_branch()` for checking branch names against a regex pattern.
- `validate_commit_message()` for checking commit messages against Conventional
  Commits, with configurable types, subject length, and ticket requirement.
- `ValidationResult`, `Violation`, `GixoError`, and `ConfigurationError` public types.
- `py.typed` marker so type checkers use gixo's type hints.

### Fixed

- `gixo.__version__` now matches the installed package version (it reported
  `0.1.0` in the 0.0.1 release).

## [0.0.1] - 2026-10-09

### Added

- Package skeleton with pytest, Ruff, and mypy configuration. Placeholder
  release to reserve the package name on PyPI.
