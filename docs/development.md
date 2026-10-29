# Development

The project uses `uv` for dependencies, `ruff` for formatting and linting, `pyrefly` for
types, `pytest` for tests and `mkdocs-material` for this site.

## Setup

```bash
make
```

`make` runs `uv sync` and installs the pre-commit hooks. The manual equivalent:

```bash
uv sync --all-extras --dev
uv run pre-commit install
```

Python 3.11 or newer is required; CI runs 3.11 - 3.15.

## Checks

Run the same order as CI:

```bash
uv run pyrefly check
uv run ruff check
uv run pytest
```

`make lint` runs the first two, `make test` runs pytest. Pytest defaults come from
`pyproject.toml`: `-xsv tests.py`, so the suite stops on the first failure. The suite runs once
per async library (`asyncio`, `trio`, `curio`) through `pytest-aio`. A focused run:

```bash
uv run pytest tests.py::test_login_state_signature
```

`ruff` covers `muffin_oauth`, `tests.py` and `example.py`; `pyrefly` checks `muffin_oauth` only.
The docs are excluded from both.

## Example

```bash
make example
# or
uv run --group example uvicorn example:app --reload --port 5000
```

Open <http://localhost:5000> and log in with GitHub or Google. The example contains a test
client id and secret, so a real round trip only works for the accounts those application
credentials belong to.

## Documentation

```bash
make docs        # build into ./site, fails on warnings
make docs-serve  # live reload on http://127.0.0.1:8000
```

Pages live in `docs/`, navigation in `mkdocs.yml`. The README is the short entry point; details
belong in `docs/`.

## Release

```bash
make release            # minor by default
make release RELEASE=patch
```

The target checks out `master`, merges `develop`, bumps the version with
`uvx bump-my-version` (configuration lives in `pyproject.toml`), regenerates `uv.lock`, commits,
tags, and pushes both branches and the tag. Publishing is done by the `release` GitHub workflow
with `uv build` + `uv publish` once `tests` passed on `master`.

## Layout

```
muffin_oauth/
  __init__.py     exports OAuthPlugin (OAuth, Plugin) and OAuthError
  plugin.py       the whole plugin: client registry, authorize, login, refresh, sign
tests.py          pytest suite (root level, configured in pyproject.toml)
example.py        runnable GitHub + Google example
docs/             this documentation
```
