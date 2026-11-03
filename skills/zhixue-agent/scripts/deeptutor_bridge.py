#!/usr/bin/env python3
"""Optional, stdlib-only wrapper for an ALREADY installed DeepTutor CLI.

Does not install packages, read secrets, or invoke paid online probes.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def invoke(cmd: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, shell=False, check=False)


def check() -> int:
    executable = shutil.which("deeptutor")
    if not executable:
        print(json.dumps({"installed": False, "ready": False,
            "reason": "deeptutor CLI not found; native Skill mode still works"}, ensure_ascii=False))
        return 2
    try:
        proc = invoke([executable, "doctor", "--format", "json"], timeout=45)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(json.dumps({"installed": True, "ready": False, "reason": type(e).__name__}, ensure_ascii=False))
        return 3
    # Forward only offline diagnostic stdout. Never return provider credentials or settings.
    print(json.dumps({"installed": True, "doctor_exit_code": proc.returncode,
                      "doctor_output": proc.stdout[-30000:],
                      "model_live_tested": False}, ensure_ascii=False))
    return 0 if proc.returncode == 0 else 4


def run(capability: str, message: str, num_questions: int | None) -> int:
    exe = shutil.which("deeptutor")
    if not exe:
        print("DeepTutor CLI not installed. Native Skill mode remains available.", file=sys.stderr)
        return 2
    cmd = [exe, "run", capability, message, "--language", "zh", "--format", "json"]
    if capability == "deep_question" and num_questions is not None:
        cmd.extend(["--config", f"num_questions={num_questions}"])
    try:
        # The subprocess may invoke the user's configured provider and incur usage charges.
        proc = invoke(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        print("DeepTutor run timed out; check session status before retrying to avoid duplication.", file=sys.stderr)
        return 124
    except OSError as e:
        print(f"Unable to start DeepTutor: {type(e).__name__}", file=sys.stderr)
        return 3
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.returncode:
        print("DeepTutor returned an error; inspect local logs and CLI module status.", file=sys.stderr)
    return proc.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="Optional DeepTutor CLI integration")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Offline-only local readiness inspection")
    group.add_argument("--run", choices=["chat", "deep_solve", "deep_question"], help="Run a real provider-backed capability")
    p.add_argument("--message", help="Message or problem to send to the installed DeepTutor")
    p.add_argument("--num-questions", type=int, choices=range(1, 11), metavar="1..10")
    a = p.parse_args()
    if a.check:
        return check()
    if not a.message or not a.message.strip():
        p.error("--message is required with --run")
    return run(a.run, a.message, a.num_questions)


if __name__ == "__main__":
    raise SystemExit(main())