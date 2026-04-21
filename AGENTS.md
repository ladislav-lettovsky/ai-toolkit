# ai-toolkit — AI Agent Memory

## What this is
A command-line scaffolder (`ai-cli`) that creates and manages per-project AI
templates. It is a generator, not a library — generated projects live
independently under `~/projects/ai/<name>/` and do not import from `ai_cli`
at runtime.

Entry point: `ai = "ai_cli.main:cli"` (see `pyproject.toml`).

## Stack
- Python 3.12+, `uv` for dependency management, `just` as the task runner
- `click` for the CLI surface
- `python-dotenv` for loading generated projects' `.env` files during `ai-cli run`
- Testing: pytest 9 with `click.testing.CLIRunner`
- Linting: ruff; Type checking: `ty` (Astral); Pre-commit hooks enabled

Notably NOT in the scaffolder's dependencies: `openai`, `langchain`,
`langgraph`, `chromadb`, or any other ML/LLM library. Those belong to
individual templates' own `pyproject.toml` files — see invariant #2.

## Commands you can run without asking
- `just fmt` — format code
- `just lint` — ruff check
- `just lint-fix` — ruff check with --fix
- `just type` — ty check
- `just test` — full pytest run
- `just check` — pre-commit + type + test (the same command CI runs)
- `uv sync`, `uv sync --extra dev`
- `uv run ai --help`, `uv run ai list`, `uv run ai templates`
- Read-only git: `git status`, `git diff`, `git log`, `git branch`

## Commands with preconditions
- `git commit` is allowed on a non-`main` branch **only after `just check`
  passes with no errors**. On `main`, always ask first.

## Commands that need explicit approval
- `uv add`, `uv remove` (dependency changes — but see invariant #2 before
  reaching for `uv add` at all)
- `git push`, `git reset --hard`
- `gh pr create`, `gh pr merge`
- Anything touching `.env`, `.github/workflows/`, or `src/ai_cli/templates/`

## Architectural invariants (do not violate without explicit discussion)

1. **Templates are product code, copied verbatim into generated projects.**
   Files under `src/ai_cli/templates/` are not imported, executed, or
   type-checked as part of the scaffolder — they are rendered into
   `~/projects/ai/<name>/` where they become the generated project's source.
   Changes to templates propagate to every future generated project, so they
   must be treated as product code, not scaffolder code. If you find yourself
   running `ty check` against a template file and "fixing" the errors by
   adjusting the template's imports or adding packages to the scaffolder,
   stop — those errors are expected, because the template imports packages
   that only exist in generated projects. Add the path to
   `[tool.ty.src].exclude` instead of "fixing" it.

2. **Dependencies of generated projects do not belong to the scaffolder's
   `pyproject.toml`.** If you find yourself adding dependencies of *generated
   projects* into `pyproject.toml`, e.g. `uv add <library>`, stop — that
   `<library>` belongs to the template's own `pyproject.toml`. If you add
   the dependency to the scaffolder, it will ship to *every* user via
   `uv tool install ai-toolkit`, triggering forced updates and creating
   version conflicts with other globally-installed tools that share the
   scaffolder's Python environment.

3. **The 9-command CLI surface is a stable contract.** The commands exposed
   by `ai-cli` — `clean`, `doctor`, `eval`, `inspect`, `list`, `new`, `run`,
   `templates`, `upgrade` — are registered in `src/ai_cli/main.py` and
   asserted in `tests/test_cli_structure.py::test_cli_group_has_all_commands`.
   Downstream users script against these names; renaming or removing one
   will silently fail their `just bootstrap` weeks later. If you find
   yourself renaming a command to "clean up the naming," stop — add the new
   name as an alias, emit a `DeprecationWarning`, and remove the old name
   only in the next major version.

4. **The scaffolder's own test suite must run with zero API keys and zero
   network.** Tests live in `tests/` and exercise only the CLI's structural
   behavior (command registration, template enumeration, file generation
   into a tmp dir) — they must not call OpenAI, HuggingFace, or any hosted
   service. The scaffolder ships to users who run `just check` in CI
   environments without secrets; a test that silently requires
   `OPENAI_API_KEY` turns green locally (where you have it set) and red in
   every fork's CI. If you find yourself writing a test that imports
   `openai` or reads `os.environ["OPENAI_API_KEY"]`, stop — that test
   belongs in the generated project's test suite, not the scaffolder's.

## Where things live
- `src/ai_cli/` — scaffolder package (src layout)
  - `main.py` — Click group; registers all 9 commands
  - `commands/` — one file per CLI command (`clean.py`, `doctor.py`, `eval.py`,
    `inspect.py`, `list.py`, `new.py`, `run.py`, `templates.py`, `upgrade.py`)
  - `generators/` — per-template generators (`agent_generator.py`, etc.)
  - `templates/` — **product code** (see invariant #1). Files here are
    rendered verbatim into generated projects
  - `constants.py` — `PROJECTS_ROOT`, `TEMPLATES_DIR`; monkeypatch these in
    tests rather than hardcoding paths
  - `utils.py` — cross-command helpers
- `tests/` — pytest tests using `click.testing.CLIRunner` (structural only)
- `.github/workflows/ci.yml` — single job, runs `just check`
- `gold-standard/` — not in this repo; see `ai-portfolio-modernization.md`
  in the Obsidian vault for the canonical templates

## Adding a new CLI subcommand
1. Add `src/ai_cli/commands/<name>.py` exposing a Click command
2. Import and register it in `src/ai_cli/main.py`
3. Extend the `expected` set in `tests/test_cli_structure.py::test_cli_group_has_all_commands`
4. Update this AGENTS.md — the command list in invariant #3 is load-bearing

## Adding a new template
1. Add files under `src/ai_cli/templates/<name>/` — treat these as **product
   code** (invariant #1)
2. Add `src/ai_cli/generators/<name>_generator.py`
3. Register it in `src/ai_cli/commands/templates.py` (the `TEMPLATES` dict)
   so `test_templates_contains_*` and the `templates` CLI see it
4. Template dependencies go in that template's own `pyproject.toml`, **never**
   in the scaffolder's (invariant #2)

## Code conventions
- **Absolute imports only** — e.g. `from ai_cli.commands.new import new`,
  never relative
- **One Click command per module** under `commands/`, registered in `main.py`
- **Route path constants through `ai_cli.constants`** (`PROJECTS_ROOT`,
  `TEMPLATES_DIR`) so tests can monkeypatch them — see
  `test_list_handles_missing_directory` for the pattern

## Testing conventions
- Tests live in `tests/` and are discovered by pytest with no custom config
- Use `click.testing.CLIRunner`, mirroring `tests/test_cli_structure.py`
- When a command reads module-level constants, monkeypatch them on **both**
  `ai_cli.constants` and the importing module — see
  `test_list_handles_missing_directory`
- Add a test alongside every new subcommand or template
- Invariant #4 applies: no API keys, no network

## Secrets & config
- Generated projects use `.env` for secrets and optionally `config.json` for
  configuration; `.env` is gitignored, `.env.example` is the template contract
- The scaffolder itself has no secrets and must run without API keys
  (invariant #4)

## Ephemeral / scratch work
Use `.scratch/` at the repo root for exploratory, diagnostic, or throwaway
work. The directory is git-ignored.

- Create on demand: `mkdir -p .scratch`
- Do NOT place exploratory files at the repo root — always use `.scratch/`

## Before saying "done"
1. `just check` passes (pre-commit + ty + pytest)
2. Any new CLI command is registered in `main.py`, tested in
   `test_cli_structure.py`, and listed in invariant #3
3. Any new template has a generator, is registered in `TEMPLATES`, and its
   deps live in the template's own `pyproject.toml` (not the scaffolder's)
4. No new dependencies added to the scaffolder's `pyproject.toml` unless
   the scaffolder itself imports them
5. Diff against `main` looks like what you'd want in a PR review
