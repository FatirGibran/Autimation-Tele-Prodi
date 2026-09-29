import unittest
import tempfile
import json
from pathlib import Path
from scripts.bulk_audit import audit_directory

class TestBulkAudit(unittest.TestCase):
    def test_audit_directory_with_sample(self):
        articles_dir = Path(__file__).parent.parent / "articles"
        summary = audit_directory(articles_dir)
        self.assertGreaterEqual(summary["scanned_files"], 1)
        self.assertTrue(summary["all_passed"])
        self.assertEqual(summary["results"][0]["score"], 100)

    def test_audit_directory_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = audit_directory(Path(tmp_dir))
            self.assertEqual(summary["scanned_files"], 0)
            self.assertTrue(summary["all_passed"])

    def test_audit_directory_nonexistent(self):
        with self.assertRaises(FileNotFoundError):
            audit_directory(Path("/nonexistent/path/dir"))

if __name__ == "__main__":
    unittest.main()
