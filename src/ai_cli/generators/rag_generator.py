import os
import subprocess


def create_rag_project(name: str, base_path: str) -> None:
    """
    Create a new self-contained RAG project.

    Project folder name: kebab-case
    Python module name: snake_case
    """
    print(f"🚀 Creating RAG project: {name}")

    module_name = name.replace("-", "_")
    target = os.path.join(base_path, name)

    os.makedirs(target, exist_ok=True)
    os.makedirs(os.path.join(target, "src", module_name), exist_ok=True)
    os.makedirs(os.path.join(target, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(target, "tests"), exist_ok=True)
    os.makedirs(os.path.join(target, "data", "docs"), exist_ok=True)
    os.makedirs(os.path.join(target, "data", "index"), exist_ok=True)
    os.makedirs(os.path.join(target, "notes"), exist_ok=True)

    with open(os.path.join(target, ".ai-project.json"), "w") as f:
        f.write(
            '''{
  "project_type": "rag",
  "template_version": "1.0",
  "created_by": "ai-toolkit"
}
'''
        )

    with open(os.path.join(target, "src", module_name, "__init__.py"), "w") as f:
        f.write("")

    with open(os.path.join(target, "src", module_name, "retriever.py"), "w") as f:
        f.write(
            '''import json
from pathlib import Path


def load_index(index_path: Path) -> list[dict]:
    if not index_path.exists():
        return []
    with index_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def retrieve(query: str, index_path: Path, top_k: int = 3) -> list[dict]:
    chunks = load_index(index_path)
    query_terms = set(query.lower().split())

    scored = []
    for chunk in chunks:
        text_terms = set(chunk["text"].lower().split())
        score = len(query_terms.intersection(text_terms))
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
'''
        )

    with open(os.path.join(target, "src", module_name, "agent.py"), "w") as f:
        f.write(
            '''import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .retriever import retrieve


class RagAgent:
    def __init__(self, name: str, project_root: Path):
        self.name = name
        self.project_root = project_root
        self.index_path = project_root / "data" / "index" / "chunks.json"
        self.config_path = project_root / "config.json"

        load_dotenv(project_root / ".env")
        self.config = self._load_config()

        self.model_name = self.config.get("model_name", "gpt-4.1-mini")
        self.top_k = int(self.config.get("top_k", 3))
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are a helpful RAG assistant. Answer only from retrieved context when possible.",
        )

        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def answer(self, query: str) -> str:
        chunks = retrieve(query, self.index_path, top_k=self.top_k)
        if not chunks:
            return "No relevant context found."

        context = "\\n\\n".join(
            f"[Source: {chunk['source']}]\\n{chunk['text']}" for chunk in chunks
        )

        if not self.client:
            return f"Retrieved context:\\n\\n{context}"

        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"Question: {query}\\n\\nRetrieved context:\\n{context}",
                },
            ],
        )
        return response.output_text
'''
        )

    with open(os.path.join(target, "scripts", "ingest.py"), "w") as f:
        f.write(
            f'''import json
from pathlib import Path


DOCS_DIR = Path(__file__).resolve().parents[1] / "data" / "docs"
INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "index"
INDEX_PATH = INDEX_DIR / "chunks.json"


def chunk_text(text: str, chunk_size: int = 400) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


def main() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []

    for path in DOCS_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_text(text), start=1):
            all_chunks.append(
                {{
                    "source": path.name,
                    "chunk_id": idx,
                    "text": chunk,
                }}
            )

    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Indexed {{len(all_chunks)}} chunks into {{INDEX_PATH}}")


if __name__ == "__main__":
    main()
'''
        )

    with open(os.path.join(target, "scripts", "run.py"), "w") as f:
        f.write(
            f'''import argparse
from pathlib import Path

from {module_name}.agent import RagAgent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        type=str,
        default="What is this knowledge base about?",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    agent = RagAgent("{name}", project_root=project_root)

    print(agent.answer(args.query))


if __name__ == "__main__":
    main()
'''
        )

    with open(os.path.join(target, "config.json"), "w") as f:
        f.write(
            f'''{{
  "agent_name": "{name}",
  "model_name": "gpt-4.1-mini",
  "top_k": 3,
  "system_prompt": "You are a helpful RAG assistant. Answer from retrieved context when possible."
}}
'''
        )

    with open(os.path.join(target, ".env.example"), "w") as f:
        f.write("OPENAI_API_KEY=your-api-key-here\n")

    with open(os.path.join(target, ".gitignore"), "w") as f:
        f.write(
            ".venv/\n"
            ".env\n"
            "__pycache__/\n"
            "*.pyc\n"
        )

    with open(os.path.join(target, "README.md"), "w") as f:
        f.write(
            f"# {name}\n\n"
            "## RAG workflow\n\n"
            "1. Put `.txt` files into `data/docs/`\n"
            "2. Run ingestion\n"
            "3. Run queries\n\n"
            "## Commands\n\n"
            "    uv run python scripts/ingest.py\n"
            "    uv run python scripts/run.py --query \"your question here\"\n"
        )

    with open(os.path.join(target, "tests", "test_rag.py"), "w") as f:
        f.write(
            f'''import json
from pathlib import Path

from {module_name}.retriever import retrieve


def test_retrieve_returns_matching_chunks(tmp_path: Path):
    index_path = tmp_path / "chunks.json"
    data = [
        {{"source": "a.txt", "chunk_id": 1, "text": "Deep work improves focus and productivity."}},
        {{"source": "b.txt", "chunk_id": 1, "text": "Kayaking is a fun outdoor sport."}},
    ]
    index_path.write_text(json.dumps(data), encoding="utf-8")

    results = retrieve("deep work focus", index_path, top_k=2)

    assert len(results) >= 1
    assert results[0]["source"] == "a.txt"
'''
        )

    with open(os.path.join(target, "data", "docs", "welcome.txt"), "w") as f:
        f.write(
            "This knowledge base contains notes about productivity, deep work, and focused execution."
        )

    with open(os.path.join(target, "pyproject.toml"), "w") as f:
        f.write(
            f'''[project]
name = "{name}"
version = "0.1.0"
description = "Generated RAG project"
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

    child_env = os.environ.copy()
    child_env.pop("VIRTUAL_ENV", None)

    subprocess.run(["uv", "venv"], cwd=target, check=True, env=child_env)
    subprocess.run(["uv", "sync", "--dev"], cwd=target, check=True, env=child_env)

    print(f"✅ RAG project created at {target}")
