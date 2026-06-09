from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .config import Agent, ensure_config, load_config, save_config
from .instructions import instruction_block
from .memento import run_memento
from .web import serve


def _agent(config, agent_id: str) -> Agent:
    agent = config.agents.get(agent_id)
    if not agent:
        raise SystemExit(f"Unknown agent: {agent_id}")
    return agent


def cmd_init(args) -> int:
    config = ensure_config()
    if args.memento_command:
        config.memento_command = args.memento_command
        save_config(config)
    print("Initialized memento-multiagent.")
    return 0


def cmd_status(args) -> int:
    config = ensure_config()
    print(json.dumps({
        "agents": len(config.agents),
        "bind_host": config.bind_host,
        "bind_port": config.bind_port,
        "memento_command": config.memento_command,
    }, indent=2, sort_keys=True))
    return 0


def cmd_agent_add(args) -> int:
    config = ensure_config()
    skill_roots = list(args.skill_root or [])
    instructions = list(args.instructions or [])
    config.agents[args.id] = Agent(
        id=args.id,
        type=args.type,
        transport=args.transport,
        memory_root=args.memory_root,
        skill_roots=skill_roots,
        instructions_files=instructions,
    )
    save_config(config)
    print(f"Added agent: {args.id}")
    return 0


def cmd_agent_list(args) -> int:
    config = ensure_config()
    for agent in config.agents.values():
        print(f"{agent.id}\t{agent.type}\t{agent.transport}\t{agent.memory_root}")
    return 0


def cmd_agent_doctor(args) -> int:
    config = ensure_config()
    agent = _agent(config, args.id)
    command_ok = shutil.which(config.memento_command) is not None
    memory_root = Path(agent.memory_root).expanduser()
    print(json.dumps({
        "agent": agent.id,
        "type": agent.type,
        "transport": agent.transport,
        "memento_command_found": command_ok,
        "memory_root": str(memory_root),
        "memory_root_exists": memory_root.exists(),
        "skill_roots": agent.skill_roots,
    }, indent=2, sort_keys=True))
    return 0 if command_ok else 2


def _proxy(agent_id: str, memento_args: list[str]) -> int:
    config = ensure_config()
    agent = _agent(config, agent_id)
    result = run_memento(config, agent, memento_args)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def cmd_recall(args) -> int:
    return _proxy(args.agent, ["recall", args.query])


def cmd_deep_recall(args) -> int:
    return _proxy(args.agent, ["deep-recall", args.query])


def cmd_remember(args) -> int:
    command = ["remember", args.fact]
    if args.category:
        command += ["--category", args.category]
    if args.keywords:
        command += ["--keywords", args.keywords]
    return _proxy(args.agent, command)


def cmd_decide(args) -> int:
    command = ["decide", args.topic, args.decision]
    if args.rationale:
        command += ["--rationale", args.rationale]
    return _proxy(args.agent, command)


def cmd_instructions_print(args) -> int:
    print(instruction_block(args.agent))
    return 0


def cmd_web(args) -> int:
    config = ensure_config()
    serve(config, host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memento-multiagent")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--memento-command")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("web")
    p.add_argument("--host")
    p.add_argument("--port", type=int)
    p.set_defaults(func=cmd_web)

    agent = sub.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="agent_command", required=True)
    p = agent_sub.add_parser("add")
    p.add_argument("id")
    p.add_argument("--type", required=True)
    p.add_argument("--transport", default="cli")
    p.add_argument("--memory-root", default="~/.memento")
    p.add_argument("--skill-root", action="append")
    p.add_argument("--instructions", action="append")
    p.set_defaults(func=cmd_agent_add)
    p = agent_sub.add_parser("list")
    p.set_defaults(func=cmd_agent_list)
    p = agent_sub.add_parser("doctor")
    p.add_argument("id")
    p.set_defaults(func=cmd_agent_doctor)

    p = sub.add_parser("recall")
    p.add_argument("query")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_recall)

    p = sub.add_parser("deep-recall")
    p.add_argument("query")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_deep_recall)

    p = sub.add_parser("remember")
    p.add_argument("fact")
    p.add_argument("--agent", required=True)
    p.add_argument("--category", default="")
    p.add_argument("--keywords", default="")
    p.set_defaults(func=cmd_remember)

    p = sub.add_parser("decide")
    p.add_argument("topic")
    p.add_argument("decision")
    p.add_argument("--agent", required=True)
    p.add_argument("--rationale", default="")
    p.set_defaults(func=cmd_decide)

    instructions = sub.add_parser("instructions")
    instructions_sub = instructions.add_subparsers(dest="instructions_command", required=True)
    p = instructions_sub.add_parser("print")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_instructions_print)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

