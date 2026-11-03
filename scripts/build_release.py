#!/usr/bin/env python3
"""Build a ZIP with SKILL.md at archive root for direct Skill import."""
from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
DEST = ROOT / "dist" / "zhixue-agent-skill-v0.1.0.zip"
DEST.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(DEST, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(SKILL.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            relative = str(p.relative_to(SKILL)).replace("\\", "/")
            archive.write(p, relative)
print(DEST)