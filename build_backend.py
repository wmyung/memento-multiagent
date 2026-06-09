from __future__ import annotations

import base64
import csv
import hashlib
import io
import zipfile
from pathlib import Path


NAME = "memento-multiagent"
MODULE = "memento_multiagent"
VERSION = "0.1.0"
DIST_INFO = f"{MODULE}-{VERSION}.dist-info"


def _metadata() -> str:
    readme = Path("README.md").read_text()
    return f"""Metadata-Version: 2.3
Name: {NAME}
Version: {VERSION}
Summary: Local-first multi-agent memory and skill control plane for AI agents.
License: MIT
Requires-Python: >=3.10
Description-Content-Type: text/markdown

{readme}
"""


def _wheel() -> str:
    return """Wheel-Version: 1.0
Generator: memento-multiagent-stdlib-backend
Root-Is-Purelib: true
Tag: py3-none-any
"""


def _entry_points() -> str:
    return """[console_scripts]
memento-multiagent = memento_multiagent.cli:main
"""


def _hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def _write_wheel(wheel_directory: str) -> str:
    wheel_name = f"{MODULE}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    records: list[tuple[str, bytes]] = []

    def add(zf: zipfile.ZipFile, arcname: str, data: bytes) -> None:
        zf.writestr(arcname, data)
        records.append((arcname, data))

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted((Path("src") / MODULE).glob("*.py")):
            add(zf, f"{MODULE}/{path.name}", path.read_bytes())
        add(zf, f"{DIST_INFO}/METADATA", _metadata().encode())
        add(zf, f"{DIST_INFO}/WHEEL", _wheel().encode())
        add(zf, f"{DIST_INFO}/entry_points.txt", _entry_points().encode())

        record_path = f"{DIST_INFO}/RECORD"
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        for arcname, data in records:
            writer.writerow([arcname, _hash(data), str(len(data))])
        writer.writerow([record_path, "", ""])
        zf.writestr(record_path, buffer.getvalue().encode())

    return wheel_name


def build_wheel(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    return _write_wheel(wheel_directory)


def build_editable(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    return _write_wheel(wheel_directory)


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings=None) -> str:
    dist = Path(metadata_directory) / DIST_INFO
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "METADATA").write_text(_metadata())
    (dist / "WHEEL").write_text(_wheel())
    (dist / "entry_points.txt").write_text(_entry_points())
    return DIST_INFO

