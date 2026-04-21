![CI](https://github.com/ladislav-lettovsky/ai-toolkit/actions/workflows/ci.yml/badge.svg)
# ai-toolkit

A local-first CLI scaffolder for creating and managing AI agent and RAG
projects. `ai-toolkit` generates standalone Python projects under
`~/projects/ai/<name>/`; each generated project is fully independent and
does not import from the toolkit at runtime.

---

## What it does

`ai-toolkit` exposes a single command, `ai`, with nine subcommands that
cover the project lifecycle:

| Command     | Purpose                                              |
|-------------|------------------------------------------------------|
| `new`       | Scaffold a new project from a template               |
| `templates` | List available templates                             |
| `list`      | List all projects under `~/projects/ai/`             |
| `inspect`   | Show a project's metadata and structure              |
| `run`       | Run a generated project                              |
| `eval`      | Run a generated project's evaluation suite           |
| `doctor`    | Check a project's health (config, deps, files)       |
| `clean`     | Remove generated runtime artifacts from a project    |
| `upgrade`   | Apply metadata-aware fixes to older generated projects |

The toolkit itself has minimal dependencies (`click`, `python-dotenv`); all
ML/LLM libraries (`openai`, `langgraph`, `chromadb`, etc.) live in the
generated projects' own `pyproject.toml` files, never the scaffolder's.

---

## Available templates

- `agent` — tool-using local agent with memory, logs, evals, and safe note writing

*(Additional templates will be added over time.)*

---

## Requirements

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv)
- [`just`](https://github.com/casey/just) (optional but recommended — the
  canonical task runner for dev commands)

---

## Installation

```bash
git clone https://github.com/ladislav-lettovsky/ai-toolkit.git
cd ai-toolkit

uv sync --extra dev
uv pip install -e .
```

For global install (recommended once released):

```bash
uv tool install ai-toolkit
```

---

## Example workflow

```bash
# 1. Scaffold a new agent project
uv run ai new agent my-agent

# 2. Enter the generated project (lives outside the toolkit repo)
cd ~/projects/ai/my-agent

# 3. Configure environment
cp .env.example .env
# edit .env with your API keys

# 4. Run the project
uv run python scripts/run.py

# 5. Run its tests
uv run pytest
```

---

## Project structure

```
ai-toolkit/
├── src/
│   └── ai_cli/                          # Scaffolder package (src layout)
│       ├── main.py                      # Click group — registers all 9 commands
│       ├── constants.py                 # PROJECTS_ROOT, TEMPLATES_DIR (monkeypatched in tests)
│       ├── utils.py                     # Cross-command helpers
│       ├── commands/                    # One Click command per file
│       │   ├── clean.py                 # `ai clean`
│       │   ├── doctor.py                # `ai doctor`
│       │   ├── eval.py                  # `ai eval`
│       │   ├── inspect.py               # `ai inspect`
│       │   ├── list.py                  # `ai list`
│       │   ├── new.py                   # `ai new`
│       │   ├── run.py                   # `ai run`
│       │   ├── templates.py             # `ai templates` — also exports TEMPLATES dict
│       │   └── upgrade.py               # `ai upgrade`
│       ├── generators/                  # Per-template generation logic
│       │   ├── agent_generator.py       # Renders templates/agent/ → generated project
│       │   └── rag_generator.py         # (rag template planned)
│       └── templates/                   # PRODUCT CODE — copied verbatim into generated projects
│           └── agent/                   # Agent template source files
├── tests/                               # 4 pytest tests (structural only — no API calls)
├── .scratch/                            # Sanctioned scratchpad for AI agents (git-ignored contents)
├── .claude/                             # Claude Code project config
│   └── settings.json
├── .cursor/                             # Cursor IDE rules
│   └── rules/
│       ├── 00-always.mdc                # Always-on invariants + check gate
│       ├── scaffolder.mdc               # Scaffolder-vs-product-code boundary rules
│       ├── tests.mdc                    # Pytest conventions (scoped to tests/)
│       └── writing-rules.mdc            # Meta-guide for rule authoring
├── .github/workflows/ci.yml             # GitHub Actions CI — runs `just check`
├── AGENTS.md                            # AI agent memory — invariants, architecture, pitfalls
├── CLAUDE.md                            # Claude Code entry point → AGENTS.md
├── CONTRIBUTING.md                      # Contribution guide
├── LICENSE                              # MIT
├── README.md                            # You are here
├── justfile                             # Task runner — `just check` = full quality gate
├── pyproject.toml                       # Project metadata, deps, ruff/ty/pytest config
├── uv.lock                              # Reproducible dependency lockfile
├── .pre-commit-config.yaml              # 10 hooks (branch guard + hygiene + ruff + ty)
└── .gitignore
```

The scaffolder has no `.env` or `.env.example` — it requires no secrets to
run its own test suite (see AGENTS.md invariant #4). Secrets belong to
*generated projects*, which ship their own `.env.example`.

---

## Development

All dev commands go through `just` — the same commands CI runs.

```bash
just install-hooks    # one-time after cloning
just fmt              # format (ruff)
just lint             # lint (ruff check)
just type             # type check (ty)
just test             # pytest
just check            # full gate — pre-commit + ty + pytest
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full workflow and
[AGENTS.md](./AGENTS.md) for architectural invariants.

---

## Design philosophy

- **Local-first execution** — no cloud services required to develop or run
- **Scaffolder isolation** — generated projects do not import from the toolkit
- **Explicit configuration over magic** — `.env` and `config.json`, no auto-discovery
- **Stable CLI contract** — the 9-command surface is versioned; renames go
  through a deprecation cycle (see AGENTS.md invariant #3)
- **Minimal scaffolder deps** — ML libraries live in templates, not the toolkit

---

## Status

Early-stage but functional. CI is green; 4 structural tests pass. Current
focus is on template coverage (adding `rag`) and end-to-end tests that
spawn a generated project and run its own `just check`.

---

## License

MIT License
