# memento-multiagent

**Local-first multi-agent memory and skill control plane for Codex, Claude, Hermes, OpenClaude-style agents, and any CLI/HTTP agent.**

MEMENTO is a lightweight memory core. `memento-multiagent` is the optional layer that lets several agents use that memory safely together.

It solves two operational problems that appear as soon as you use more than one agent seriously:

1. **Memory is fragmented.** Codex remembers one thing, Claude remembers another, Hermes has a different wiki, and the next agent starts from zero.
2. **Memory and skills get polluted.** Agents accumulate stale facts, duplicated instructions, broken skills, old project assumptions, and private context that should never be exported.

Install `memento-multiagent`, connect your agents, and run the same kind of shared memory system used in a real multi-agent workflow: shared recall, shared decisions, skill inventory, cleanup queues, and privacy gates.

No vector database required. No cloud account required. No telemetry. Default bind address is `127.0.0.1`.

## Why SQLite Alongside WikiLLM

Wiki-style knowledge is excellent for durable procedures, research notes, and long-form reasoning. But agents also need very fast operational memory: facts, paths, preferences, commands, failures, decisions, artifacts, and skill state.

`memento-multiagent` uses both:

| Layer | Best for | Write policy | Recall speed |
|---|---|---|---|
| **SQLite fact store** | quick facts, paths, config, preferences, decisions, artifacts, skill state | agents can auto-save concise facts | milliseconds |
| **Wiki / WikiLLM layer** | procedures, explanations, research notes, durable knowledge | ask before creating or editing | slower but deeper |
| **Keyword bridge** | connecting fast facts to deep pages | facts carry wiki references | fast first hop, deep second hop |

The result is a faster working loop:

```text
SQLite recall first
  -> use the answer immediately if the fact is enough
  -> follow wiki keywords only when deeper context is needed
```

This is not "SQLite instead of WikiLLM." It is **SQLite for fast agent memory plus wiki/WikiLLM for durable knowledge**, wired together for multi-agent operation.

## Quick Start

```bash
pipx install memento-multiagent
memento-multiagent init
memento-multiagent agent add codex-local --type codex --memory-root ~/.memento --skill-root ~/.codex/skills --instructions ./AGENTS.md
memento-multiagent web
```

Open:

```text
http://127.0.0.1:4173/
```

To keep data in a project-local directory instead of the default home directory:

```bash
MEMENTO_MULTIAGENT_HOME=.memento-multiagent memento-multiagent status
```

Default behavior:

- binds only to `127.0.0.1`;
- uses a local data directory;
- does not sync to GitHub;
- does not expose a remote API;
- does not send telemetry;
- does not export private memory.

## Agent Instruction Block

Every agent needs an instruction block so shared memory becomes automatic.

````markdown
## Shared Agent Memory

Use the shared MEMENTO memory through `memento-multiagent`.

Before starting a non-trivial task, recall relevant shared memory:

```bash
memento-multiagent recall "<task, project, user, or tool query>" --agent <agent-id>
```

Use deep recall for prior decisions, operating procedures, project history, or wiki-backed knowledge:

```bash
memento-multiagent deep-recall "<query>" --agent <agent-id>
```

At the end of a substantial task, save concise facts only:

```bash
memento-multiagent remember "<fact>" --agent <agent-id> --category <category> --keywords "<keywords>"
```

Record decisions with rationale:

```bash
memento-multiagent decide "<topic>" "<decision>" --agent <agent-id> --rationale "<why>"
```

Ask the user before creating or editing wiki pages, exporting memory, syncing to GitHub, changing another agent's instruction file, enabling a skill for all agents, or deleting/quarantining memory.

Never store API keys, OAuth tokens, cookies, SSH private keys, passwords, private records, raw `.env` files, or full chat transcripts unless explicitly requested.
````

## CLI

```bash
memento-multiagent init
memento-multiagent web
memento-multiagent status

memento-multiagent agent add <id> --type <type>
memento-multiagent agent list
memento-multiagent agent doctor <id>

memento-multiagent recall "<query>" --agent <id>
memento-multiagent deep-recall "<query>" --agent <id>
memento-multiagent remember "<fact>" --agent <id> --category <category> --keywords "<keywords>"
memento-multiagent decide "<topic>" "<decision>" --agent <id> --rationale "<why>"
memento-multiagent instructions print --agent <id>
```

## Security Model

Default stance: **nothing leaves the machine unless the user turns it on.**

- Web bind address: `127.0.0.1`
- Remote API: off
- GitHub sync: off
- Telemetry: none
- Public export: off
- Wiki write: human approval
- Memory delete: human approval or quarantine first
- Secrets: blocked by review policy

## Status

This repository starts as a dependency-light MVP:

- local config;
- agent registry;
- MEMENTO CLI wrapper;
- instruction generator;
- local web dashboard;
- stdlib-only smoke tests.

The goal is simple:

> Install it anywhere, add your agents, paste the generated instruction block into each agent's instruction file, and get a working shared multi-agent memory system.
