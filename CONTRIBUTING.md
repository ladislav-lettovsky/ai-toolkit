# Contributing

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ladislav-lettovsky/ai-toolkit.git
cd ai-toolkit

# Install with dev dependencies
uv sync --extra dev

# Install the CLI locally so `ai ...` works
uv pip install -e .

# Install pre-commit hooks (runs ruff, ty, and hygiene checks on every commit)
just install-hooks
```

`ai-toolkit` requires no API keys or `.env` file to run its own tests
(see [AGENTS.md](./AGENTS.md) invariant #4).

## Project Layout

`ai-toolkit` is a scaffolder, not a library or application. Files under
`src/ai_cli/templates/` are **product code** — they are rendered verbatim
into generated projects and must not be imported, executed, or type-checked
as part of the scaffolder itself. See [AGENTS.md](./AGENTS.md) invariants
#1 and #2.

| Directory | Purpose |
|:---|:---|
| `src/ai_cli/commands/` | One Click command per file (the 9 CLI commands) |
| `src/ai_cli/generators/` | Per-template rendering logic |
| `src/ai_cli/templates/` | Product code — copied verbatim into generated projects |
| `src/ai_cli/constants.py` | `PROJECTS_ROOT`, `TEMPLATES_DIR` (monkeypatched in tests) |
| `src/ai_cli/utils.py` | Cross-command helpers |
| `tests/` | Pytest test suite — structural tests only, no API calls |

## Branch Conventions

| Branch | Purpose |
|:---|:---|
| `main` | Production-ready code. All CI must pass before merging. |
| `feat/<name>` | New features (e.g., `feat/rag-template`) |
| `fix/<name>` | Bug fixes (e.g., `fix/upgrade-dead-config-var`) |
| `refactor/<name>` | Internal restructuring with no behavior change |
| `chore/<name>` | Tooling, config, dependencies — no runtime behavior change |
| `docs/<name>` | Documentation-only updates |
| `test/<name>` | Test additions or fixes |

Use [Conventional Commits](https://www.conventionalcommits.org/) for
commit messages; one logical change per commit.

## Running Tests

```bash
# Run all tests (fast — no API keys, no network)
just test

# Or equivalently
uv run pytest

# Run a specific test file
uv run pytest tests/test_cli_structure.py -v
```

## Quality Gate

`just check` is the canonical command. It runs the same set of checks that
CI runs, in the same order:

```bash
just check
```

Under the hood:
1. All 10 pre-commit hooks (branch guard, hygiene, ruff, ty)
2. `uv run ty check` — full type check
3. `uv run pytest` — all tests

Commits on non-`main` branches are allowed only after `just check` passes.
Never commit directly to `main` (the `no-commit-to-branch` pre-commit hook
will block you, and `.claude/settings.json` denies the equivalent tool calls).

## Adding a new CLI command

1. Add `src/ai_cli/commands/<name>.py` exposing a Click command
2. Import and register it in `src/ai_cli/main.py`
3. Extend the `expected` set in `tests/test_cli_structure.py::test_cli_group_has_all_commands`
4. Update [AGENTS.md](./AGENTS.md) invariant #3 — the 9-command list is load-bearing
5. Update the CLI table in [README.md](./README.md)

## Adding a new template

1. Add files under `src/ai_cli/templates/<name>/` — product code
2. Add `src/ai_cli/generators/<name>_generator.py`
3. Register it in `src/ai_cli/commands/templates.py` (the `TEMPLATES` dict)
4. Add a `test_templates_contains_<name>` test to `tests/test_cli_structure.py`
5. Template dependencies go in the template's own `pyproject.toml`, never
   in the scaffolder's (AGENTS.md invariant #2)

## Key Architectural Invariants

See [AGENTS.md](./AGENTS.md) for the full list with rationale. Summary:

1. **Templates are product code, copied verbatim into generated projects.**
2. **Dependencies of generated projects do not belong to the scaffolder's `pyproject.toml`.**
3. **The 9-command CLI surface is a stable contract** (alias + deprecate + major bump).
4. **The scaffolder's own tests require zero API keys and zero network.**

## CI

GitHub Actions runs on every push to `main` and on pull requests. The
workflow is a thin wrapper that runs `just check` — same command as local,
no rule duplication. See `.github/workflows/ci.yml`.
