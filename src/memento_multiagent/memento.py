from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .config import Agent, Config


def _home_for_agent(agent: Agent) -> str:
    memory_root = Path(agent.memory_root).expanduser()
    if memory_root.name == ".memento":
        return str(memory_root.parent)
    return str(memory_root)


def run_memento(config: Config, agent: Agent, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = _home_for_agent(agent)
    env["MEMENTO_AGENT_NAME"] = agent.id
    return subprocess.run(
        [config.memento_command, *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

