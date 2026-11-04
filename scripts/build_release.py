#!/usr/bin/env python3
"""Reproducible, root-SKILL.md ZIP and SHA-256 file; Python stdlib only."""
from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "zhixue-agent"
VERSION = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
DEST = ROOT / "dist" / ("zhixue-agent-skill-v" + VERSION + ".zip")
DEST.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(DEST, "w") as archive:
    for p in sorted(SKILL.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix in (".pyc", ".pyo"):
            continue
        relative = p.relative_to(SKILL).as_posix()
        item = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
        item.compress_type = zipfile.ZIP_DEFLATED
        item.external_attr = (0o644 & 0xFFFF) << 16
        archive.writestr(item, p.read_bytes())
digest = hashlib.sha256(DEST.read_bytes()).hexdigest()
(ROOT / "dist" / "SHA256SUMS").write_text(f"{digest}  {DEST.name}\n", encoding="utf-8")
print(f"Built: {DEST}")
print(f"SHA256: {digest}")