# gixo

gixo validates Git branch names and commit messages against configurable rules.

## Usage

### Branch names

```python
from gixo import validate_branch

result = validate_branch(
    "feature/PROJ-123-add-login",
    pattern=r"^(feature|bugfix)/[A-Z]+-\d+-.+$",
)

if not result.is_valid:
    print(result.message)
```

`validate_branch` takes the branch name as an argument; it never runs Git
itself. It returns a `ValidationResult`:

- `is_valid` is `True` when no rules failed.
- `message` is `"OK"`, or a human-readable explanation of what failed.
- `violations` is a tuple of `Violation(rule, message)` with a stable rule id:

| Rule | Fails when |
|---|---|
| `branch.empty` | The name is empty or only whitespace. |
| `branch.whitespace` | The name contains any whitespace. Names are not trimmed. |
| `branch.pattern` | The name does not match `pattern`. |

Behavior:

- The **whole** name must match the pattern (`re.fullmatch`), so `^` and `$`
  anchors are optional.
- Checks stop at the first failure, in the order listed above.
- An invalid regex raises `gixo.ConfigurationError`, even when the name is
  empty, so configuration mistakes are never reported as validation failures.

### Commit messages

```python
from gixo import validate_commit_message

result = validate_commit_message(
    "feat(api): add login endpoint",
    allowed_types=["feat", "fix", "docs"],
    max_subject_length=72,
    require_ticket=False,
)

for violation in result.violations:
    print(f"[{violation.rule}] {violation.message}")
```

Messages follow [Conventional Commits](https://www.conventionalcommits.org/):
the first line (the subject) is `type(scope)!: description`, where the scope
and `!` are optional.

| Setting | Default | Meaning |
|---|---|---|
| `convention` | `"conventional"` | The only supported convention so far. |
| `allowed_types` | `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `chore` | Accepted types. Case-sensitive. |
| `max_subject_length` | `72` | Maximum length of the subject line. |
| `require_ticket` | `False` | Require a ticket id somewhere in the message. |
| `ticket_pattern` | `[A-Z][A-Z0-9]+-\d+` | Regex for a ticket id, e.g. `PROJ-123`. |
| `allow_merge_commits` | `True` | Accept `Merge ...` subjects without other checks. |
| `allow_revert_commits` | `True` | Accept `Revert "..."` subjects without other checks. |

| Rule | Fails when |
|---|---|
| `commit.empty` | The message is empty or only whitespace. No other rules run. |
| `commit.whitespace` | The subject starts with whitespace. |
| `commit.format` | The subject is not `type(scope)!: description`. |
| `commit.type` | The type is not in `allowed_types`. |
| `commit.subject_length` | The subject is longer than `max_subject_length`. |
| `commit.body_separator` | A body follows the subject without a blank line between them. |
| `commit.ticket` | `require_ticket` is on and `ticket_pattern` appears nowhere in the message. |

Behavior:

- Every failing rule is reported, not just the first. When the subject starts
  with whitespace, `commit.format` and `commit.type` are skipped.
- Subject length counts the **whole first line, including the `type(scope): `
  prefix**, matching what `git log --oneline` shows.
- Trailing whitespace and newlines are ignored; leading whitespace is rejected.
- The ticket may appear in the subject, body, or a footer such as
  `Refs: PROJ-123`.
- Merge and revert commits, when allowed, skip **all** rules, including the
  ticket rule. Release commits have no special case; write them as
  `chore(release): v1.2.0`.
- Git comment lines (`# ...`) are not stripped; pass the final message text.
- Invalid settings raise `gixo.ConfigurationError` before the message is
  checked.

## Development

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
mypy src
```
