from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(ROOT / "src")


def run(home: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MEMENTO_MULTIAGENT_HOME"] = str(home / "mma")
    env["PYTHONPATH"] = PYTHONPATH
    env["PATH"] = str(home / "bin") + os.pathsep + env.get("PATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "memento_multiagent.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def make_fake_memento(home: Path) -> None:
    bin_dir = home / "bin"
    bin_dir.mkdir()
    script = bin_dir / "memento"
    script.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

store = Path(os.environ["HOME"]) / ".memento" / "fake_store.json"
store.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(store.read_text()) if store.exists() else {"facts": [], "decisions": []}
cmd = sys.argv[1]
if cmd == "remember":
    data["facts"].append(" ".join(sys.argv[2:]))
    store.write_text(json.dumps(data))
    print("remembered")
elif cmd == "recall":
    print("\\n".join(data["facts"]) or "no matches")
elif cmd == "deep-recall":
    print("deep:" + " ".join(sys.argv[2:]))
elif cmd == "decide":
    data["decisions"].append(sys.argv[2:4])
    store.write_text(json.dumps(data))
    print("decided")
else:
    print("fake memento command", cmd)
"""
    )
    script.chmod(0o755)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        make_fake_memento(home)
        run(home, "init")
        run(home, "agent", "add", "codex-local", "--type", "codex", "--memory-root", str(home / "agent-home" / ".memento"), "--skill-root", str(home / "skills"), "--instructions", "AGENTS.md")
        status = json.loads(run(home, "status").stdout)
        assert status["agents"] == 1
        assert status["bind_host"] == "127.0.0.1"
        assert "codex-local" in run(home, "agent", "list").stdout
        assert "Shared Agent Memory" in run(home, "instructions", "print", "--agent", "codex-local").stdout
        assert run(home, "remember", "shared memory smoke fact", "--agent", "codex-local", "--category", "test", "--keywords", "smoke").returncode == 0
        assert "shared memory smoke fact" in run(home, "recall", "smoke", "--agent", "codex-local").stdout
        assert "decided" in run(home, "decide", "smoke", "works", "--agent", "codex-local", "--rationale", "test").stdout

        proc = subprocess.Popen(
            [sys.executable, "-m", "memento_multiagent.cli", "web", "--port", "4183"],
            cwd=ROOT,
            env={
                **os.environ,
                "MEMENTO_MULTIAGENT_HOME": str(home / "mma"),
                "PYTHONPATH": PYTHONPATH,
                "PATH": str(home / "bin") + os.pathsep + os.environ.get("PATH", ""),
            },
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            body = None
            for _ in range(30):
                try:
                    body = urlopen("http://127.0.0.1:4183/api/status", timeout=1).read().decode()
                    break
                except Exception:
                    time.sleep(0.1)
            if body is None:
                stdout, stderr = proc.communicate(timeout=1)
                raise AssertionError(f"web server did not become ready\nstdout={stdout}\nstderr={stderr}")
            payload = json.loads(body)
            assert payload["agents"] == 1
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    print("smoke ok")


if __name__ == "__main__":
    main()
