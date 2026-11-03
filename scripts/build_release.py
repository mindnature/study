#!/usr/bin/env python3
"""Build import-ready ZIP with SKILL.md at archive root."""
from __future__ import annotations

from pathlib import Path
import zipfile

VERSION = "0.2.0"
ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
DEST = ROOT / "dist" / ("zhixue-agent-skill-v" + VERSION + ".zip")
DEST.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(DEST, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(SKILL.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo"):
            relative = p.relative_to(SKILL).as_posix()
            archive.write(p, relative)
print(DEST)