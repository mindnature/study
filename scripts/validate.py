#!/usr/bin/env python3
"""Validate distribution structure and deterministic local tooling, not AI behavior."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
VERSION = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
assert VERSION == "1.0.0"
main = (SKILL / "SKILL.md").read_text(encoding="utf-8")
assert main.startswith("---\n")
front = main.split("---\n", 2)[1]
assert "name: zhixue-agent" in front and "description:" in front
assert len(main) >= 600
for name in ("teaching.md", "assessment.md", "materials.md", "progress.md", "deeptutor-engine.md"):
    assert (SKILL / "references" / name).is_file(), f"Missing reference: {name}"
for name, flags in (("deeptutor_bridge.py", ("--check", "--run")),
                    ("learning_store.py", ("--workspace", "init", "record", "summary"))):
    p = subprocess.run([sys.executable, str(SKILL / "scripts" / name), "--help"],
                       capture_output=True, text=True, check=True)
    assert all(flag in p.stdout for flag in flags), name
items = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
assert len(items) >= 10 and len({item["id"] for item in items}) == len(items)
assert all(item.get("prompt") and item.get("expected") and item.get("forbidden") for item in items)
zip_path = ROOT / "dist" / f"zhixue-agent-skill-v{VERSION}.zip"
assert zip_path.is_file(), "Build ZIP before validation"
with zipfile.ZipFile(zip_path) as archive:
    assert archive.testzip() is None
    names = set(archive.namelist())
    assert {"SKILL.md", "VERSION", "scripts/learning_store.py",
            "scripts/deeptutor_bridge.py", "references/teaching.md",
            "references/assessment.md", "references/materials.md",
            "references/progress.md"} <= names
    assert not any(n.startswith("/") or ".." in Path(n).parts or
                   "__pycache__" in n or n.endswith((".pyc", ".pyo")) for n in names)
    assert archive.read("SKILL.md").decode("utf-8") == main
    assert archive.read("VERSION").decode("utf-8").strip() == VERSION
checksums = (ROOT / "dist" / "SHA256SUMS").read_text(encoding="utf-8").strip()
assert checksums == f"{hashlib.sha256(zip_path.read_bytes()).hexdigest()}  {zip_path.name}"
print(f"PASS: Skill v{VERSION}, {len(names)} packaged files, SHA-256 and scenario structure")
print("NOTE: workbuddy/codex real-client teaching behavior is NOT exercised by this validation")