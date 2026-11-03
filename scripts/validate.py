#!/usr/bin/env python3
"""Static skill checks; does not invoke any external models or install packages."""
from __future__ import annotations

import pathlib
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
assert text.startswith("---\n"), "missing frontmatter"
front = text.split("---\n", 2)[1]
assert "name: zhixue-agent" in front and "description:" in front, "missing frontmatter keys"
assert len(text) > 1000, "instruction body too short"
assert (SKILL / "references" / "deeptutor-engine.md").is_file()
assert (SKILL / "references" / "progress.md").is_file()
p = subprocess.run([sys.executable, str(SKILL / "scripts" / "deeptutor_bridge.py"), "--help"],
                   capture_output=True, text=True, check=True)
assert "--check" in p.stdout and "--run" in p.stdout
archive = ROOT / "dist" / "zhixue-agent-skill-v0.1.0.zip"
if archive.exists():
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert "SKILL.md" in names, "Skill ZIP must have root SKILL.md"
        assert all(not n.startswith("../") and not n.startswith("/") for n in names)
        assert "references/progress.md" in names
        assert "scripts/deeptutor_bridge.py" in names
print("PASS: frontmatter, references, optional bridge, ZIP layout")