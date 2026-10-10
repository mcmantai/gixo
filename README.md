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
