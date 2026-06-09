from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .config import Config


def _html(config: Config) -> str:
    agent_rows = "\n".join(
        f"<tr><td>{a.id}</td><td>{a.type}</td><td>{a.transport}</td><td>{a.memory_root}</td><td>{len(a.skill_roots)}</td></tr>"
        for a in config.agents.values()
    )
    if not agent_rows:
        agent_rows = '<tr><td colspan="5">No agents registered yet.</td></tr>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>memento-multiagent</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #f6f7f9; color: #15171a; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dde3; padding: 20px 28px; }}
    main {{ padding: 24px 28px; max-width: 1120px; }}
    h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 10px; font-size: 18px; letter-spacing: 0; }}
    p {{ margin: 0; color: #4b5563; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: #ffffff; border: 1px solid #d9dde3; border-radius: 8px; padding: 14px; }}
    .metric strong {{ display: block; font-size: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9dde3; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e8ebef; text-align: left; font-size: 14px; }}
    th {{ background: #eef2f6; font-weight: 650; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>memento-multiagent</h1>
    <p>Local-first control plane for shared agent memory, skills, cleanup, and privacy review.</p>
  </header>
  <main>
    <section class="grid">
      <div class="metric"><strong>{len(config.agents)}</strong><span>Registered agents</span></div>
      <div class="metric"><strong>{config.bind_host}</strong><span>Bind host</span></div>
      <div class="metric"><strong>{config.bind_port}</strong><span>Port</span></div>
    </section>
    <h2>Agents</h2>
    <table>
      <thead><tr><th>ID</th><th>Type</th><th>Transport</th><th>Memory root</th><th>Skill roots</th></tr></thead>
      <tbody>{agent_rows}</tbody>
    </table>
    <h2>Security defaults</h2>
    <p>Remote API, telemetry, public export, and GitHub sync are off by default. Use <code>127.0.0.1</code> unless you explicitly need another bind host.</p>
  </main>
</body>
</html>"""


def serve(config: Config, host: str | None = None, port: int | None = None) -> None:
    bind_host = host or config.bind_host
    bind_port = int(port or config.bind_port)

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/api/status":
                self._send_json({"agents": len(config.agents), "bind_host": bind_host, "bind_port": bind_port})
                return
            if self.path == "/api/agents":
                self._send_json({"agents": [agent.__dict__ for agent in config.agents.values()]})
                return
            body = _html(config).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((bind_host, bind_port), Handler)
    print(f"memento-multiagent web listening on http://{bind_host}:{bind_port}/")
    server.serve_forever()

