#!/usr/bin/env python3
"""Static package checks; model behavior requires external client evaluation."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
main = (SKILL / "SKILL.md").read_text(encoding="utf-8")
assert main.startswith("---\n"), "missing frontmatter"
front = main.split("---\n", 2)[1]
assert "name: zhixue-agent" in front and "description:" in front, "invalid frontmatter"
assert "V0.2.0" in main, "version mismatch"
for filename in ("teaching.md", "assessment.md", "materials.md", "progress.md", "deeptutor-engine.md"):
    assert (SKILL / "references" / filename).is_file(), "missing reference " + filename
for name, flags in (("deeptutor_bridge.py", ("--check", "--run")),
                    ("learning_store.py", ("--workspace", "init", "record", "summary"))):
    p = subprocess.run([sys.executable, str(SKILL / "scripts" / name), "--help"],
                       capture_output=True, text=True, check=True)
    assert all(x in p.stdout for x in flags), name + " CLI mismatch"
items = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
assert isinstance(items, list) and len(items) >= 10
assert len({item["id"] for item in items}) == len(items)
assert all(item.get("prompt") and item.get("expected") and item.get("forbidden") for item in items)
archive_path = ROOT / "dist" / "zhixue-agent-skill-v0.2.0.zip"
assert archive_path.is_file(), "build ZIP before validate"
with zipfile.ZipFile(archive_path) as archive:
    names = archive.namelist()
    assert "SKILL.md" in names
    assert "scripts/learning_store.py" in names
    assert "scripts/deeptutor_bridge.py" in names
    assert "references/assessment.md" in names
    assert all(not n.startswith("/") and ".." not in Path(n).parts for n in names)
    assert all("__pycache__" not in n and not n.endswith(".pyc") for n in names)
print("PASS: Skill structure, CLI help, scenario schema, ZIP layout (not model behavior)")