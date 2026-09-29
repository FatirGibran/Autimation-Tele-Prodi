import unittest
import tempfile
import sqlite3
from pathlib import Path
from scripts.backup_db import perform_backup

class TestBackupDB(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_orig.db"
        self.backup_dir = Path(self.temp_dir.name) / "backups"

        # Create dummy database with content
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("CREATE TABLE sample (id INT, name TEXT);")
            conn.execute("INSERT INTO sample VALUES (1, 'telecom');")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_perform_backup_success(self):
        target = perform_backup(self.db_path, self.backup_dir, max_backups=3, verify=True)
        self.assertTrue(target.exists())

        # Verify content copied faithfully
        with sqlite3.connect(str(target)) as conn:
            cursor = conn.execute("SELECT name FROM sample WHERE id = 1;")
            self.assertEqual(cursor.fetchone()[0], "telecom")

    def test_perform_backup_retention(self):
        # Create 4 backups with max_backups=2
        for _ in range(4):
            perform_backup(self.db_path, self.backup_dir, max_backups=2, verify=True)

        existing = list(self.backup_dir.glob("editorial_backup_*.db"))
        self.assertEqual(len(existing), 2)

if __name__ == "__main__":
    unittest.main()
