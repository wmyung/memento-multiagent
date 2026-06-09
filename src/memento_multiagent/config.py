from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


APP_DIR_ENV = "MEMENTO_MULTIAGENT_HOME"


def app_home() -> Path:
    custom = os.environ.get(APP_DIR_ENV)
    if custom:
        return Path(custom).expanduser()
    return Path.home() / ".memento-multiagent"


def config_path() -> Path:
    return app_home() / "config.json"


@dataclass
class Agent:
    id: str
    type: str
    transport: str = "cli"
    memory_root: str = "~/.memento"
    skill_roots: list[str] = field(default_factory=list)
    instructions_files: list[str] = field(default_factory=list)
    capabilities: list[str] = field(
        default_factory=lambda: ["recall", "remember", "decide", "artifact", "experience", "skills"]
    )


@dataclass
class Config:
    version: int = 1
    bind_host: str = "127.0.0.1"
    bind_port: int = 4173
    memento_command: str = "memento"
    agents: dict[str, Agent] = field(default_factory=dict)


def _agent_from_json(value: dict[str, Any]) -> Agent:
    return Agent(
        id=value["id"],
        type=value["type"],
        transport=value.get("transport", "cli"),
        memory_root=value.get("memory_root", "~/.memento"),
        skill_roots=list(value.get("skill_roots", [])),
        instructions_files=list(value.get("instructions_files", [])),
        capabilities=list(value.get("capabilities", ["recall", "remember", "decide", "artifact", "experience", "skills"])),
    )


def load_config() -> Config:
    path = config_path()
    if not path.exists():
        return Config()
    data = json.loads(path.read_text())
    agents = {key: _agent_from_json(value) for key, value in data.get("agents", {}).items()}
    return Config(
        version=int(data.get("version", 1)),
        bind_host=data.get("bind_host", "127.0.0.1"),
        bind_port=int(data.get("bind_port", 4173)),
        memento_command=data.get("memento_command", "memento"),
        agents=agents,
    )


def save_config(config: Config) -> None:
    home = app_home()
    home.mkdir(parents=True, exist_ok=True)
    data = asdict(config)
    Path(config_path()).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def ensure_config() -> Config:
    config = load_config()
    save_config(config)
    return config

