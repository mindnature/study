"""Deterministic local storage acceptance tests; no provider/model required."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "skills" / "zhixue-agent" / "scripts" / "learning_store.py"
UTC = timezone.utc


class LearningStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.store = self.workspace / ".zhixue" / "learning-records.json"

    def call(self, *argv, ok=True):
        cmd = [sys.executable, str(CLI), "--workspace", str(self.workspace), *argv]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        self.assertNotEqual(p.returncode, 0)
        return json.loads(p.stderr)

    def init(self):
        self.call("init", "--consent")

    def event(self, activity="practice", result="correct", hint="0",
              verification="checked", ident="e1", timestamp=None, qid=None):
        args = ["record", "--course", "经济数学", "--objective", "商法则",
                "--question-id", qid or "q-" + ident, "--activity", activity, "--result", result,
                "--hint-level", hint, "--verification", verification,
                "--error-type", "none", "--attempt-id", ident]
        if timestamp:
            args += ["--timestamp", timestamp]
        return self.call(*args)

    def status(self):
        return self.call("summary")["objectives"][0]["status"]

    def test_consent_required_no_implicit_write(self):
        self.assertIn("consent", self.call("init", ok=False)["error"])
        self.assertFalse(self.store.exists())

    def test_empty_initialized_record_and_existing_init(self):
        self.init()
        self.assertTrue(self.store.exists())
        self.assertEqual(self.call("summary")["objectives"], [])
        self.assertEqual(self.call("init", "--consent")["status"], "already_initialized")

    def test_checked_independent_and_backup(self):
        self.init()
        r = self.event()
        self.assertEqual(r["status"], "saved")
        self.assertEqual(self.status(), "本次独立完成")
        self.assertTrue(self.store.with_suffix(".json.bak").exists())

    def test_idempotent_same_attempt(self):
        self.init()
        t = "2026-11-03T09:00:00+00:00"
        self.event(timestamp=t)
        r = self.event(timestamp=t)
        self.assertEqual(r["status"], "duplicate_ignored")
        self.assertEqual(len(json.loads(self.store.read_text(encoding="utf-8"))["attempts"]), 1)

    def test_retry_without_timestamp_reuses_original_event(self):
        self.init()
        self.event(timestamp="2026-10-01T00:00:00+00:00")
        self.assertEqual(self.event()["status"], "duplicate_ignored")
        self.assertEqual(len(json.loads(self.store.read_text(encoding="utf-8"))["attempts"]), 1)

    def test_same_id_conflicting_attempt_rejected(self):
        self.init()
        self.event()
        e = self.call("record", "--course", "经济数学", "--objective", "商法则",
                      "--question-id", "q1", "--activity", "practice",
                      "--result", "incorrect", "--hint-level", "0",
                      "--verification", "checked", "--attempt-id", "e1", ok=False)
        self.assertIn("attempt_id", e["error"])

    def test_hint_or_unverified_does_not_claim_mastery(self):
        self.init()
        self.event(hint="1")
        self.assertEqual(self.status(), "学习中")

    def test_model_judgment_not_automatically_verified(self):
        self.init()
        self.event(verification="model_assessed")
        self.assertEqual(self.status(), "学习中")

    def test_transfer_then_delayed_24h(self):
        self.init()
        t0 = datetime(2026, 11, 1, 9, tzinfo=UTC)
        self.event(ident="practice",timestamp=t0.isoformat())
        self.event(activity="transfer",ident="transfer",timestamp=(t0+timedelta(hours=1)).isoformat())
        self.assertEqual(self.status(), "初步迁移成功")
        self.event(activity="delayed",ident="too-early",timestamp=(t0+timedelta(hours=23)).isoformat())
        self.assertEqual(self.status(), "初步迁移成功")
        self.event(activity="delayed",ident="late",timestamp=(t0+timedelta(hours=25)).isoformat())
        self.assertEqual(self.status(), "较稳定掌握")

    def test_latest_error_returns_to_review(self):
        self.init()
        self.event()
        self.event(ident="a-last",result="incorrect")
        self.assertEqual(self.status(), "待复习")

    def test_incompatible_old_record_is_not_overwritten(self):
        self.store.parent.mkdir()
        old = '{"schema_version":"0.1.0","attempts":[]}'
        self.store.write_text(old, encoding="utf-8")
        self.call("init", "--consent", ok=False)
        self.assertEqual(self.store.read_text(encoding="utf-8"), old)

    def test_invalid_timestamp_rejected_without_writing(self):
        self.init()
        e = self.call("record", "--course", "经济数学", "--objective", "商法则",
                      "--question-id", "q1", "--activity", "practice",
                      "--result", "correct", "--hint-level", "0",
                      "--verification", "checked", "--timestamp", "2026-11-03T09:00:00",
                      ok=False)
        self.assertIn("UTC offset", e["error"])
        self.assertEqual(len(json.loads(self.store.read_text(encoding="utf-8"))["attempts"]), 0)

    def test_repeated_question_is_not_transfer(self):
        self.init()
        t0 = datetime(2026, 11, 1, 9, tzinfo=UTC)
        self.event(ident="base", qid="q-same", timestamp=t0.isoformat())
        self.event(activity="transfer", ident="transfer", qid="q-same",
                   timestamp=(t0 + timedelta(hours=1)).isoformat())
        self.assertEqual(self.status(), "本次独立完成")

    def test_repeated_question_is_not_delayed(self):
        self.init()
        t0 = datetime(2026, 11, 1, 9, tzinfo=UTC)
        self.event(ident="base", timestamp=t0.isoformat())
        self.event(activity="transfer", ident="transfer",
                   timestamp=(t0 + timedelta(hours=1)).isoformat())
        self.event(activity="delayed", ident="delayed", qid="q-transfer",
                   timestamp=(t0 + timedelta(hours=28)).isoformat())
        self.assertEqual(self.status(), "初步迁移成功")

    def test_error_resets_prior_mastery_evidence(self):
        self.init()
        t0 = datetime(2026, 11, 1, 9, tzinfo=UTC)
        self.event(ident="base", timestamp=t0.isoformat())
        self.event(activity="transfer", ident="transfer",
                   timestamp=(t0 + timedelta(hours=1)).isoformat())
        self.event(activity="delayed", ident="delayed",
                   timestamp=(t0 + timedelta(hours=28)).isoformat())
        self.assertEqual(self.status(), "较稳定掌握")
        self.event(ident="error", result="incorrect",
                   timestamp=(t0 + timedelta(hours=29)).isoformat())
        self.assertEqual(self.status(), "待复习")
        self.event(ident="new-base", timestamp=(t0 + timedelta(hours=30)).isoformat())
        self.assertEqual(self.status(), "本次独立完成")

    def test_future_attempt_rejected(self):
        self.init()
        timestamp = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        err = self.call("record", "--course", "经济数学", "--objective", "商法则",
                        "--question-id", "q1", "--activity", "practice", "--result", "correct",
                        "--hint-level", "0", "--verification", "checked",
                        "--timestamp", timestamp, ok=False)
        self.assertIn("future", err["error"])
        self.assertFalse(json.loads(self.store.read_text(encoding="utf-8"))["attempts"])

    def test_summary_is_not_reminder(self):
        self.init()
        self.event()
        self.assertFalse(self.call("summary")["objectives"][0]["automated_reminder_created"])


if __name__ == "__main__":
    unittest.main()
