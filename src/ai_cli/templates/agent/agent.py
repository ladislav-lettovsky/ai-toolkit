import json
import os
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


class BaseAgent:
    """
    Self-contained base agent with:
    - config.json support
    - .env support
    - CLI override support
    - precedence: CLI > env > config > defaults
    - tool registry
    - persistent JSON memory
    - append-only JSONL run logging
    - optional LLM backend
    - tool-aware LLM routing
    - recent conversation history injection
    """

    def __init__(self, name: str, overrides: dict[str, Any] | None = None):
        project_root = Path(__file__).resolve().parents[2]
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.memory_file = self.data_dir / "memory.json"
        self.runs_file = self.data_dir / "runs.jsonl"
        self.config_file = project_root / "config.json"

        self.data_dir.mkdir(parents=True, exist_ok=True)

        load_dotenv(project_root / ".env")
        self.config = self._load_config()
        self.overrides = overrides or {}

        self.name = self._get_setting("AGENT_NAME", "agent_name", name)
        self.system_prompt = self._get_setting(
            "SYSTEM_PROMPT",
            "system_prompt",
            "You are a helpful local AI agent. Use tools when helpful.",
        )
        self.enable_time_tool = self._get_bool_setting(
            "ENABLE_TIME_TOOL",
            "enable_time_tool",
            True,
        )
        self.enable_llm = self._get_bool_setting(
            "ENABLE_LLM",
            "enable_llm",
            True,
        )
        self.model_name = self._get_setting(
            "MODEL_NAME",
            "model_name",
            "gpt-4.1-mini",
        )
        self.memory_window = self._get_int_setting(
            "MEMORY_WINDOW",
            "memory_window",
            4,
        )

        self.tools: dict[str, Callable[..., Any]] = {}
        self.tool_schemas: list[dict[str, Any]] = []
        self.tool_calls: list[dict[str, Any]] = []
        self.memory: list[dict[str, Any]] = self._load_memory()

        api_key = self._get_setting("OPENAI_API_KEY", "openai_api_key", "")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _load_config(self) -> dict[str, Any]:
        if not self.config_file.exists():
            return {}

        try:
            with self.config_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _get_setting(self, env_key: str, config_key: str, default: Any) -> Any:
        if config_key in self.overrides and self.overrides[config_key] is not None:
            return self.overrides[config_key]

        env_value = os.getenv(env_key)
        if env_value not in (None, ""):
            return env_value

        return self.config.get(config_key, default)

    def _get_bool_setting(self, env_key: str, config_key: str, default: bool) -> bool:
        if config_key in self.overrides and self.overrides[config_key] is not None:
            override_value = self.overrides[config_key]
            if isinstance(override_value, bool):
                return override_value
            if isinstance(override_value, str):
                return override_value.lower() in {"1", "true", "yes", "on"}
            return bool(override_value)

        env_value = os.getenv(env_key)
        if env_value not in (None, ""):
            return env_value.lower() in {"1", "true", "yes", "on"}

        config_value = self.config.get(config_key, default)
        if isinstance(config_value, bool):
            return config_value
        if isinstance(config_value, str):
            return config_value.lower() in {"1", "true", "yes", "on"}
        return bool(config_value)

    def _get_int_setting(self, env_key: str, config_key: str, default: int) -> int:
        if config_key in self.overrides and self.overrides[config_key] is not None:
            try:
                return int(self.overrides[config_key])
            except (TypeError, ValueError):
                return default

        env_value = os.getenv(env_key)
        if env_value not in (None, ""):
            try:
                return int(env_value)
            except ValueError:
                return default

        config_value = self.config.get(config_key, default)
        try:
            return int(config_value)
        except (TypeError, ValueError):
            return default

    def _load_memory(self) -> list[dict[str, Any]]:
        if not self.memory_file.exists():
            return []

        try:
            with self.memory_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_memory(self) -> None:
        with self.memory_file.open("w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def _recent_memory_context(self) -> str:
        if not self.memory:
            return "No prior conversation history."

        recent = self.memory[-self.memory_window :]
        lines: list[str] = []

        for i, item in enumerate(recent, start=1):
            user_input = item.get("input", "")
            output = item.get("output", "")
            lines.append(f"Turn {i} user: {user_input}")
            lines.append(f"Turn {i} agent: {output}")

        return "\n".join(lines)

    def _llm_messages(self, input_text: str) -> list[dict[str, str]]:
        history = self._recent_memory_context()
        return [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "system",
                "content": (
                    "Recent conversation history follows. "
                    "Use it for continuity when relevant.\n\n"
                    f"{history}"
                ),
            },
            {"role": "user", "content": input_text},
        ]

    def _log_run(
        self,
        input_text: str,
        thought: str,
        output: str,
        tools_used: list[dict[str, Any]],
    ) -> None:
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": self.name,
            "model": self.model_name,
            "system_prompt": self.system_prompt,
            "memory_window": self.memory_window,
            "input": input_text,
            "thought": thought,
            "output": output,
            "tools_used": tools_used,
        }

        with self.runs_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def register_tool(
        self,
        name: str,
        func: Callable[..., Any],
        description: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self.tools[name] = func
        self.tool_schemas.append(
            {
                "type": "function",
                "name": name,
                "description": description,
                "parameters": parameters
                or {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
            }
        )

    def use_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool not registered: {name}")

        result = self.tools[name](*args, **kwargs)
        self.tool_calls.append(
            {
                "tool": name,
                "args": args,
                "kwargs": kwargs,
                "result": result,
            }
        )
        return result

    def call_llm(self, input_text: str) -> str:
        if not self.client:
            return f"[{self.name}] LLM unavailable: OPENAI_API_KEY not set"

        response = self.client.responses.create(
            model=self.model_name,
            input=self._llm_messages(input_text),
        )
        return response.output_text

    def call_llm_with_tools(self, input_text: str) -> str:
        if not self.client:
            return f"[{self.name}] LLM unavailable: OPENAI_API_KEY not set"

        response = self.client.responses.create(
            model=self.model_name,
            tools=self.tool_schemas if self.tool_schemas else None,
            input=self._llm_messages(input_text),
        )

        tool_outputs = []

        for item in response.output:
            if item.type == "function_call":
                tool_name = item.name
                raw_args = item.arguments or "{}"
                parsed_args = json.loads(raw_args)

                tool_result = self.use_tool(tool_name, **parsed_args)

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": str(tool_result),
                    }
                )

        if tool_outputs:
            followup = self.client.responses.create(
                model=self.model_name,
                input=tool_outputs,
                previous_response_id=response.id,
            )
            return followup.output_text

        return response.output_text or f"[{self.name}] No response generated"

    def think(self, input_text: str) -> str:
        return f"[{self.name}] {self.system_prompt} | reasoning over: {input_text}"

    def act(self, thought: str, input_text: str) -> str:
        if self.enable_llm and self.tool_schemas:
            llm_result = self.call_llm_with_tools(input_text)
            return f"[{self.name}] llm+tools:{self.model_name} -> {llm_result}"

        if self.enable_llm:
            llm_result = self.call_llm(input_text)
            return f"[{self.name}] llm:{self.model_name} -> {llm_result}"

        return f"[{self.name}] executing: {thought}"

    def run(self, input_text: str) -> str:
        self.tool_calls = []

        thought = self.think(input_text)
        result = self.act(thought, input_text)

        memory_entry = {
            "input": input_text,
            "thought": thought,
            "output": result,
        }
        self.memory.append(memory_entry)
        self._save_memory()
        self._log_run(
            input_text=input_text,
            thought=thought,
            output=result,
            tools_used=self.tool_calls,
        )
        return result


class Agent(BaseAgent):
    pass
