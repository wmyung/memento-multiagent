from __future__ import annotations


def instruction_block(agent_id: str) -> str:
    return f"""## Shared Agent Memory

Use the shared MEMENTO memory through `memento-multiagent`.

- Before non-trivial work, run `memento-multiagent recall "<query>" --agent {agent_id}`.
- Use `memento-multiagent deep-recall "<query>" --agent {agent_id}` for prior decisions, operating procedures, and project history.
- Before ending substantial work, save concise facts, decisions, paths, commands, and follow-ups.
- Use `memento-multiagent remember "<fact>" --agent {agent_id} --category <category> --keywords "<keywords>"` for compact facts.
- Use `memento-multiagent decide "<topic>" "<decision>" --agent {agent_id} --rationale "<why>"` for decisions.
- Ask before wiki edits, public sync, global skill changes, memory deletion, or changes to another agent's instruction file.
- Never store API keys, OAuth tokens, cookies, SSH private keys, passwords, raw `.env` contents, private records, or full chat transcripts unless explicitly requested.
- Treat memory cleanup as maintenance: mark stale, duplicate, conflicting, or risky entries for review.
"""

