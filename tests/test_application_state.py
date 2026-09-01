import csv
import tempfile
import unittest
from pathlib import Path

from tools.application_state import ApplicationInput, archive_path, canonical_url, ensure_application


class ApplicationStateTests(unittest.TestCase):
    def test_canonical_url_removes_tracking_and_fragment(self):
        self.assertEqual(
            canonical_url("HTTPS://Example.COM/job/?b=2&utm_source=test&a=1#section"),
            "https://example.com/job?a=1&b=2",
        )

    def test_ensure_is_idempotent_and_persists_deadline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = ensure_application(
                root,
                ApplicationInput(
                    company="Acme / Robotics",
                    role="Mechanical Engineer",
                    location="Vancouver, BC",
                    source="https://example.com/jobs/1?utm_source=portal",
                    deadline="2026-09-15",
                    status="ready",
                    cv_file="cv/main_acme.tex",
                    cover_letter_file="cover_letters/cover_acme.tex",
                    posting_text="# Posting\n",
                ),
            )
            second = ensure_application(
                root,
                ApplicationInput(
                    company="Acme / Robotics",
                    role="Mechanical Engineer",
                    source="https://example.com/jobs/1",
                    deadline="2026-09-15",
                    posting_text="# New text must not overwrite\n",
                ),
            )
            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            with (root / "job_search_tracker.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["deadline"], "2026-09-15")
            self.assertEqual(rows[0]["source"], "https://example.com/jobs/1")
            self.assertEqual(rows[0]["status"], "ready")
            self.assertEqual(rows[0]["cv_file"], "cv/main_acme.tex")
            posting = root / "documents/applications/acme_robotics_mechanical_engineer/job_posting.md"
            self.assertEqual(posting.read_text(encoding="utf-8"), "# Posting\n")

    def test_archive_path_cannot_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = archive_path(Path(tmp), "../../Acme", "../Engineer")
            self.assertEqual(target.parent, (Path(tmp) / "documents/applications").resolve())

    def test_artifact_path_cannot_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "escaped"):
                ensure_application(
                    Path(tmp),
                    ApplicationInput(company="Acme", role="Engineer", cv_file="../outside.tex"),
                )
