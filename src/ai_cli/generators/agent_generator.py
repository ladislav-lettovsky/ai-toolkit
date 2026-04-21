import os
import shutil
import subprocess

from ai_cli.constants import TEMPLATES_DIR


def create_agent(name: str, base_path: str) -> None:
    """
    Create a new self-contained AI agent project.

    Project folder name: kebab-case
    Python module name: snake_case
    """
    print(f"🚀 Creating AI Agent: {name}")

    module_name = name.replace("-", "_")
    target = os.path.join(base_path, name)

    os.makedirs(target, exist_ok=True)
    os.makedirs(os.path.join(target, "src", module_name), exist_ok=True)
    os.makedirs(os.path.join(target, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(target, "tests"), exist_ok=True)
    os.makedirs(os.path.join(target, "data"), exist_ok=True)
    os.makedirs(os.path.join(target, "notes"), exist_ok=True)

    template_src = TEMPLATES_DIR / "agent" / "agent.py"
    shutil.copy(template_src, os.path.join(target, "src", module_name, "agent.py"))

    with open(os.path.join(target, "src", module_name, "__init__.py"), "w") as f:
        f.write("")

    with open(os.path.join(target, "config.json"), "w") as f:
        f.write(
            f'''{{
  "agent_name": "{name}",
  "enable_time_tool": true,
  "enable_word_count_tool": true,
  "enable_save_note_tool": true,
  "enable_llm": true,
  "model_name": "gpt-4.1-mini",
  "memory_window": 4,
  "system_prompt": "You are a helpful local AI agent. Use tools when helpful and maintain continuity across turns."
}}
'''
        )

    with open(os.path.join(target, ".env.example"), "w") as f:
        f.write("OPENAI_API_KEY=your-api-key-here\n")

    with open(os.path.join(target, ".gitignore"), "w") as f:
        f.write(".venv/\n.env\n__pycache__/\n*.pyc\ndata/memory.json\ndata/runs.jsonl\n")

    with open(os.path.join(target, ".ai-project.json"), "w") as f:
        f.write(
            """{
  "project_type": "agent",
  "template_version": "1.0",
  "created_by": "ai-toolkit"
}
"""
        )

    with open(os.path.join(target, "pyproject.toml"), "w") as f:
        f.write(
            f'''[project]
name = "{name}"
version = "0.1.0"
description = "Generated AI agent project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "openai>=1.0.0",
    "python-dotenv>=1.0.0",
]

[dependency-groups]
dev = [
    "pytest>=9.0.0",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]
'''
        )

    with open(os.path.join(target, "README.md"), "w") as f:
        f.write(
            f"# {name}\n\n"
            "## Configuration precedence\n\n"
            "1. CLI args\n"
            "2. Environment variables / .env\n"
            "3. config.json\n"
            "4. Code defaults\n\n"
            "## Run\n\n"
            "    uv run python scripts/run.py\n"
            "    uv run python scripts/run.py --memory-window 2\n"
        )

    with open(os.path.join(target, "scripts", "run.py"), "w") as f:
        f.write(
            f'''import argparse
import re
from datetime import datetime
from pathlib import Path

from {module_name}.agent import Agent


def get_time() -> str:
    return datetime.now().isoformat(timespec="seconds")


def word_count(text: str) -> str:
    count = len(text.split())
    return f"Word count: {{count}}"


def save_note(text: str, filename: str | None = None) -> str:
    notes_dir = Path(__file__).resolve().parents[1] / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    if filename:
        raw_name = Path(filename).name
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", raw_name)
        safe_name = safe_name.lstrip("._")

        if not safe_name:
            safe_name = f"note_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    else:
        safe_name = f"note_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"

    if not safe_name.endswith(".txt"):
        safe_name += ".txt"

    path = notes_dir / safe_name
    path.write_text(text, encoding="utf-8")
    return f"Saved note to {{path}}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", dest="model_name", type=str, default=None)
    parser.add_argument("--system-prompt", dest="system_prompt", type=str, default=None)
    parser.add_argument("--memory-window", dest="memory_window", type=int, default=None)

    parser.add_argument("--enable-llm", dest="enable_llm", action="store_true")
    parser.add_argument("--disable-llm", dest="enable_llm", action="store_false")
    parser.set_defaults(enable_llm=None)

    parser.add_argument("--enable-time-tool", dest="enable_time_tool", action="store_true")
    parser.add_argument("--disable-time-tool", dest="enable_time_tool", action="store_false")
    parser.set_defaults(enable_time_tool=None)

    args = parser.parse_args()

    overrides = {{
        "model_name": args.model_name,
        "system_prompt": args.system_prompt,
        "memory_window": args.memory_window,
        "enable_llm": args.enable_llm,
        "enable_time_tool": args.enable_time_tool,
    }}

    agent = Agent("{name}", overrides=overrides)

    if agent.enable_time_tool:
        agent.register_tool(
            "get_time",
            get_time,
            description="Get the current local time as an ISO timestamp.",
            parameters={{
                "type": "object",
                "properties": {{}},
                "required": [],
                "additionalProperties": False,
            }},
        )

    if agent.config.get("enable_word_count_tool", True):
        agent.register_tool(
            "word_count",
            word_count,
            description="Count the number of words in a piece of text.",
            parameters={{
                "type": "object",
                "properties": {{
                    "text": {{
                        "type": "string",
                        "description": "The text to count words in."
                    }}
                }},
                "required": ["text"],
                "additionalProperties": False,
            }},
        )

    if agent.config.get("enable_save_note_tool", True):
        agent.register_tool(
            "save_note",
            save_note,
            description="Save a note to a local text file inside the notes folder.",
            parameters={{
                "type": "object",
                "properties": {{
                    "text": {{
                        "type": "string",
                        "description": "The note content to save."
                    }},
                    "filename": {{
                        "type": "string",
                        "description": "Optional filename for the note."
                    }}
                }},
                "required": ["text"],
                "additionalProperties": False,
            }},
        )

    print(agent.run("What time is it right now?"))
    print(agent.run("Count the words in this sentence: Deep work in the morning improves focus."))
    print(agent.run("Save a short note reminding me to protect my deep work hours in the morning."))
    print(f"Memory entries: {{len(agent.memory)}}")
    print(f"Runs log: {{agent.runs_file}}")
    print(
        f"Resolved config -> model={{agent.model_name}}, "
        f"enable_llm={{agent.enable_llm}}, "
        f"enable_time_tool={{agent.enable_time_tool}}, "
        f"memory_window={{agent.memory_window}}"
    )


if __name__ == "__main__":
    main()
'''
        )

    with open(os.path.join(target, "tests", "test_agent.py"), "w") as f:
        f.write(
            f'''from pathlib import Path

from {module_name}.agent import Agent
from scripts.run import save_note


def fake_time() -> str:
    return "2026-01-01T12:00:00"


def fake_word_count(text: str) -> str:
    return f"Word count: {{len(text.split())}}"


def test_agent_can_use_registered_tool_directly():
    agent = Agent("{name}")
    agent.enable_llm = False
    agent.register_tool(
        "get_time",
        fake_time,
        description="Get current time.",
    )

    result = agent.use_tool("get_time")

    assert result == "2026-01-01T12:00:00"


def test_agent_can_use_typed_argument_tool_directly():
    agent = Agent("{name}")
    agent.enable_llm = False
    agent.register_tool(
        "word_count",
        fake_word_count,
        description="Count words in text.",
        parameters={{
            "type": "object",
            "properties": {{
                "text": {{"type": "string"}}
            }},
            "required": ["text"],
            "additionalProperties": False,
        }},
    )

    result = agent.use_tool("word_count", text="deep work wins")

    assert result == "Word count: 3"


def test_save_note_writes_file_and_content():
    result = save_note("Protect deep work hours.", "deep_work_test")
    assert "Saved note to" in result

    path_str = result.replace("Saved note to ", "")
    path = Path(path_str)

    assert path.exists()
    assert path.name == "deep_work_test.txt"
    assert path.read_text(encoding="utf-8") == "Protect deep work hours."


def test_save_note_sanitizes_filename():
    result = save_note("Note content", "../bad name?")
    path_str = result.replace("Saved note to ", "")
    path = Path(path_str)

    assert path.exists()
    assert ".." not in path.name
    assert " " not in path.name
    assert "?" not in path.name
    assert path.suffix == ".txt"


def test_agent_memory_window_override():
    agent = Agent("{name}", overrides={{"memory_window": 2}})
    assert agent.memory_window == 2
'''
        )

    child_env = os.environ.copy()
    child_env.pop("VIRTUAL_ENV", None)

    subprocess.run(["uv", "venv"], cwd=target, check=True, env=child_env)
    subprocess.run(["uv", "sync", "--dev"], cwd=target, check=True, env=child_env)

    print(f"✅ Agent created at {target}")
