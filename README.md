# ai-toolkit

A local-first AI project toolkit for creating and managing agent and RAG projects.

---

## Overview

`ai-toolkit` is a CLI that helps you build structured AI projects with:

- isolated environments per project (via `uv`)
- reproducible configuration (`config.json`)
- secure secrets (`.env`)
- built-in evaluation, logging, and inspection tools
- metadata-aware project lifecycle

It is designed for **rapid experimentation** and **clean project structure**.

---

## What it does

`ai-toolkit` provides a CLI for:

- creating new projects from templates
- running generated projects
- evaluating generated projects
- inspecting project state
- cleaning project state
- running health checks
- upgrading older projects with metadata-aware fixes

---

## Available Templates

*(Additional templates will be added over time)*

- `agent` — tool-using local agent with memory, logs, evals, and safe note writing
- `rag` — local retrieval-augmented generation project with ingestion and querying

---

## CLI

```bash
uv run ai templates
uv run ai new agent my-agent
uv run ai new rag my-rag
uv run ai list
uv run ai inspect my-agent
uv run ai run my-agent
uv run ai eval my-agent
uv run ai doctor my-agent
uv run ai clean my-agent
uv run ai upgrade my-agent
```

---

## Requirements

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv)

---

## Installation (Development)

```bash
git clone <your-repo-url>
cd ai-toolkit

uv sync
uv pip install -e .
```

---

## Example Workflow

```bash
# Create project
uv run ai new agent my-agent

# Enter project
cd ~/projects/ai/my-agent

# Configure environment
cp .env.example .env
nano .env

# Run project
uv run python scripts/run.py

# Run tests
uv run python -m pytest
```

---

## Design Philosophy

- local-first execution
- explicit configuration over magic
- reproducible environments
- separation of config and secrets
- simple templates, extensible over time

---

## Status

Early-stage but fully functional local AI development toolkit.

---

## License

MIT License
