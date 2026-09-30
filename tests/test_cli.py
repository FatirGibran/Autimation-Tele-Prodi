import unittest
import io
import tempfile
from pathlib import Path
from unittest.mock import patch
from storage import StorageManager
import cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = Path(self.temp_dir.name) / "test_cli.db"
        self.orig_storage = cli.storage
        cli.storage = StorageManager(self.test_db)

        self.articles_dir = Path(__file__).parent.parent / "articles"
        self.html_file = self.articles_dir / "2026-09-28-webassembly-edge-computing-iot.html"
        self.meta_file = self.articles_dir / "2026-09-28-webassembly-edge-computing-iot-metadata.json"

    def tearDown(self):
        cli.storage = self.orig_storage
        self.temp_dir.cleanup()

    def test_cmd_audit(self):
        class Args:
            html = str(self.html_file)
            meta = str(self.meta_file)

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_audit(Args())
            output = fake_out.getvalue()
            self.assertIn("Yoast SEO Status: ALL GREEN", output)
            self.assertIn("Score: 100/100", output)

    def test_cmd_stats(self):
        class Args:
            pass

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_stats(Args())
            output = fake_out.getvalue()
            self.assertIn("Statistik Database Editorial", output)
            self.assertIn("Total Artikel", output)

    def test_cmd_search_empty(self):
        class Args:
            query = "nonexistent-query-string-xyz"
            limit = 10

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_search(Args())
            output = fake_out.getvalue()
            self.assertIn("Tidak ditemukan artikel", output)

    def test_cmd_export(self):
        # Save a test article first
        slug = "cli-export-test-slug"
        cli.storage.save_article({
            "topic": "Test Export",
            "category": "Test",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "test export",
            "seo_title": "Test Export CLI",
            "slug": slug,
            "meta_description": "Test export CLI meta description sample text.",
            "html_content": "<div class='tu-editorial-container'><p>CLI Content</p></div>",
            "status": "ready"
        })

        with tempfile.TemporaryDirectory() as tmp_dir:
            class Args:
                pass
            args = Args()
            args.slug = slug
            args.out = tmp_dir

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_export(args)
                output = fake_out.getvalue()
                self.assertIn("Export selesai ke direktori", output)

            out_path = Path(tmp_dir)
            self.assertTrue((out_path / f"{slug}.html").exists())
            self.assertTrue((out_path / f"{slug}_elementor.json").exists())

    def test_cmd_validate_success(self):
        class Args:
            html = str(self.html_file)
            meta = str(self.meta_file)
            json_output = False

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_validate(Args())
            output = fake_out.getvalue()
            self.assertIn("Hasil Validasi: VALID (SIAP TERBIT)", output)
            self.assertIn("Skor SEO: 100/100", output)

    def test_cmd_validate_json(self):
        import json
        class Args:
            html = str(self.html_file)
            meta = str(self.meta_file)
            json_output = True

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_validate(Args())
            output = fake_out.getvalue()
            data = json.loads(output)
            self.assertTrue(data["valid"])
            self.assertEqual(data["seo_report"]["score"], 100)

if __name__ == "__main__":
    unittest.main()
