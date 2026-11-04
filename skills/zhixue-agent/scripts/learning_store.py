#!/usr/bin/env python3
"""Optional local, stdlib-only study evidence store for Agent Skill hosts.

No network calls, dependency installation, model calls or automatic scheduling.
This script is optional: conversational teaching works without Python.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

SCHEMA = "0.2.0"
ACTIVITIES = ("diagnostic", "practice", "transfer", "delayed")
RESULTS = ("correct", "incorrect", "uncertain")
VERIFICATIONS = ("checked", "teacher_review", "model_assessed", "unverified")
ERRORS = ("none", "concept", "procedure", "calculation", "interpretation", "transfer", "unknown")
TRUSTED = ("checked", "teacher_review")
SKILL_DIR = Path(__file__).resolve().parents[1]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_time(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamp must contain a UTC offset")
    return result.astimezone(timezone.utc)


def location(workspace: str) -> Path:
    root = Path(workspace).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("selected workspace must already exist")
    if root == SKILL_DIR or SKILL_DIR in root.parents:
        raise ValueError("cannot write learning records inside Skill installation")
    folder = root / ".zhixue"
    if folder.is_symlink():
        raise ValueError("refusing a symlinked .zhixue directory")
    file = folder / "learning-records.json"
    if file.is_symlink():
        raise ValueError("refusing symlinked learning-records.json")
    return file


@contextmanager
def exclusive(file: Path):
    lock = file.with_suffix(".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError("learning record is busy (.lock exists); retry after other writer finishes") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


def read(file: Path) -> dict:
    if not file.is_file():
        raise ValueError("learning records not initialized; obtain consent and run init")
    if file.is_symlink():
        raise ValueError("refusing symlinked records file")
    with file.open("r", encoding="utf-8") as stream:
        record = json.load(stream)
    if not isinstance(record, dict) or record.get("schema_version") != SCHEMA:
        raise ValueError("unsupported record format; back up and explicitly migrate, never overwrite")
    if not isinstance(record.get("attempts"), list):
        raise ValueError("invalid attempts structure")
    return record


def atomic_write(file: Path, record: dict) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=file.parent, prefix=".records-", suffix=".tmp", delete=False
        ) as temp:
            temp_path = Path(temp.name)
            os.chmod(temp_path, 0o600)
            json.dump(record, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())
        if file.exists():
            shutil.copy2(file, file.with_suffix(".json.bak"))
        os.replace(temp_path, file)
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def init(file: Path, consent: bool) -> dict:
    if not consent:
        raise ValueError("explicit user consent is required before initializing records")
    file.parent.mkdir(parents=True, exist_ok=True)
    with exclusive(file):
        if file.exists():
            read(file)
            return {"status": "already_initialized", "file": str(file)}
        record = {"schema_version": SCHEMA, "created_at": iso(now_utc()), "updated_at": iso(now_utc()), "attempts": []}
        atomic_write(file, record)
    return {"status": "initialized", "file": str(file)}


def choose_status(attempts: list[dict]) -> str:
    """Derive conservative mastery from distinct, verified learning evidence.

    A later incorrect attempt invalidates earlier mastery *for the current
    status*, without deleting any historic records. Same-question replays
    cannot count as independent transfer or delayed testing.
    """
    if not attempts:
        return "学习中"
    events = sorted(attempts, key=lambda x: x["attempted_at"])  # stable for equal timestamps
    last_wrong = max((i for i, e in enumerate(events) if e["result"] == "incorrect"), default=-1)
    if last_wrong == len(events) - 1:
        return "待复习"
    current = events[last_wrong + 1:]
    strong = [x for x in current if x["result"] == "correct" and x["hint_level"] == 0
              and x["verification"] in TRUSTED]
    base = next((x for x in strong if x["activity"] == "practice"), None)
    if base is None:
        return "待复习" if last_wrong >= 0 else "学习中"
    transfer = next(
        (x for x in strong if x["activity"] == "transfer"
         and x["question_id"] != base["question_id"]
         and parse_time(x["attempted_at"]) >= parse_time(base["attempted_at"])),
        None,
    )
    if transfer is None:
        return "本次独立完成"
    delayed = any(
        x["activity"] == "delayed"
        and x["question_id"] not in (base["question_id"], transfer["question_id"])
        and parse_time(x["attempted_at"]) - parse_time(transfer["attempted_at"]) >= timedelta(hours=24)
        for x in strong
    )
    return "较稳定掌握" if delayed else "初步迁移成功"


def summarize(record: dict) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for item in record["attempts"]:
        groups.setdefault((item["course"], item["objective"]), []).append(item)
    report = []
    for (course, objective), events in sorted(groups.items()):
        events.sort(key=lambda x: x["attempted_at"])
        last = events[-1]
        status = choose_status(events)
        days = 7 if status == "较稳定掌握" else 3 if status == "初步迁移成功" else 1
        due = parse_time(last["attempted_at"]) + timedelta(days=days)
        report.append({"course": course, "objective": objective, "status": status,
                       "attempt_count": len(events), "last_result": last["result"],
                       "last_hint_level": last["hint_level"], "suggested_review_date": due.date().isoformat(),
                       "automated_reminder_created": False})
    return report


def record_attempt(file: Path, args: argparse.Namespace) -> dict:
    for field in ("course", "objective", "question_id"):
        value = getattr(args, field)
        if not value.strip() or len(value) > 160:
            raise ValueError(field + " must contain 1–160 characters")
    attempt_id = args.attempt_id or str(uuid.uuid4())
    if not attempt_id.strip() or len(attempt_id) > 160:
        raise ValueError("invalid attempt_id")
    time = parse_time(args.timestamp) if args.timestamp else now_utc()
    if time > now_utc() + timedelta(minutes=5):
        raise ValueError("attempt timestamp cannot be in the future")
    event = {"attempt_id": attempt_id, "course": args.course, "objective": args.objective,
             "question_id": args.question_id, "activity": args.activity, "result": args.result,
             "hint_level": args.hint_level, "verification": args.verification,
             "error_type": args.error_type, "attempted_at": iso(time)}
    if not file.parent.is_dir():
        raise ValueError("records not initialized; ask for consent first")
    with exclusive(file):
        doc = read(file)
        existing = next((x for x in doc["attempts"] if x["attempt_id"] == attempt_id), None)
        if existing:
            comparable = dict(event)
            # A retry without an explicit timestamp refers to the original event.
            if args.timestamp is None:
                comparable["attempted_at"] = existing["attempted_at"]
            if existing != comparable:
                raise ValueError("attempt_id already exists with different content")
            return {"status": "duplicate_ignored", "attempt_id": attempt_id}
        doc["attempts"].append(event)
        doc["updated_at"] = iso(now_utc())
        atomic_write(file, doc)
    groups = [s for s in summarize(doc) if s["course"] == args.course and s["objective"] == args.objective]
    return {"status": "saved", "attempt_id": attempt_id, "objective_summary": groups[0]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-only evidence log for 知学 Agent (optional)")
    parser.add_argument("--workspace", required=True, help="Existing user-selected work folder; never Skill folder")
    subs = parser.add_subparsers(dest="action", required=True)
    ini = subs.add_parser("init", help="Initialize after actual user approval")
    ini.add_argument("--consent", action="store_true")
    rec = subs.add_parser("record", help="Append one independently identifiable attempt")
    for f in ("course", "objective", "question-id"):
        rec.add_argument("--" + f, required=True)
    rec.add_argument("--activity", choices=ACTIVITIES, required=True)
    rec.add_argument("--result", choices=RESULTS, required=True)
    rec.add_argument("--hint-level", type=int, choices=range(4), required=True)
    rec.add_argument("--verification", choices=VERIFICATIONS, required=True)
    rec.add_argument("--error-type", choices=ERRORS, default="unknown")
    rec.add_argument("--attempt-id", default=None)
    rec.add_argument("--timestamp", default=None, help="ISO-8601 with timezone; defaults to UTC now")
    subs.add_parser("summary", help="Read evidence and calculate learning status")
    try:
        args = parser.parse_args()
        file = location(args.workspace)
        if args.action == "init":
            value = init(file, args.consent)
        elif args.action == "record":
            value = record_attempt(file, args)
        else:
            value = {"status": "ok", "file": str(file), "objectives": summarize(read(file))}
        print(json.dumps(value, ensure_ascii=False))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
