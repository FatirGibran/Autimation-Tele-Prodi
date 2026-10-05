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

    def test_cmd_optimize(self):
        class Args:
            pass

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_optimize(Args())
            output = fake_out.getvalue()
            self.assertIn("Status Integritas SQLite", output)
            self.assertIn("ok", output)
            self.assertIn("Berhasil", output)

    def test_cmd_sitemap(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
            temp_sitemap = tf.name

        try:
            class Args:
                out = temp_sitemap
                base_url = "https://bif-pwt.telkomuniversity.ac.id"

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_sitemap(Args())
                output = fake_out.getvalue()
                self.assertIn("Sitemap XML berhasil dibuat", output)

            content = Path(temp_sitemap).read_text(encoding="utf-8")
            self.assertIn("https://bif-pwt.telkomuniversity.ac.id", content)
        finally:
            if Path(temp_sitemap).exists():
                Path(temp_sitemap).unlink()

    def test_cmd_density(self):
        class Args:
            html = str(self.html_file)
            keyphrase = "WebAssembly edge computing IoT"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_density(Args())
            output = fake_out.getvalue()
            self.assertIn("Analisis Kerapatan Kata Kunci", output)
            self.assertIn("WebAssembly edge computing IoT", output)
            self.assertIn("Persentase", output)

    def test_cmd_trash_and_restore(self):
        # Save a sample article
        art_id = cli.storage.save_article({
            "topic": "Sampah CLI",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "sampah cli",
            "seo_title": "Sampah CLI",
            "slug": "sampah-cli",
            "meta_description": "Deskripsi artikel sampah cli.",
            "status": "draft"
        })
        class DelArgs:
            action = "delete"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_trash(DelArgs())
            self.assertIn("berhasil dipindahkan ke sampah", fake_out.getvalue())

        class RestoreArgs:
            action = "restore"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_trash(RestoreArgs())
            self.assertIn("berhasil dipulihkan dari sampah", fake_out.getvalue())

    def test_cmd_meta_get_set(self):
        art_id = cli.storage.save_article({
            "topic": "Meta CLI",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "meta cli",
            "seo_title": "Meta CLI",
            "slug": "meta-cli",
            "meta_description": "Deskripsi meta cli.",
            "status": "draft"
        })
        class SetArgs:
            action = "set"
            id = art_id
            key = "semester"
            value = "ganjil"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_meta(SetArgs())
            self.assertIn("Metadata berhasil disimpan", fake_out.getvalue())

        class GetArgs:
            action = "get"
            id = art_id
            key = "semester"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_meta(GetArgs())
            self.assertIn("ganjil", fake_out.getvalue())

    def test_cmd_feed(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
            feed_file = tf.name

        try:
            class Args:
                format = "atom"
                out = feed_file
                title = "Test Feed"
                base_url = "https://bif-pwt.telkomuniversity.ac.id"
                limit = 10

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_feed(Args())
                self.assertIn("berhasil diekspor", fake_out.getvalue())

            content = Path(feed_file).read_text(encoding="utf-8")
            self.assertIn("<feed", content)
        finally:
            if Path(feed_file).exists():
                Path(feed_file).unlink()

    def test_cmd_analytics(self):
        cli.storage.save_article({
            "topic": "Analytics CLI",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "analytics cli",
            "seo_title": "Analytics CLI",
            "slug": "analytics-cli",
            "meta_description": "Deskripsi analytics cli.",
            "status": "published"
        })
        class Args:
            days = 14

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_analytics(Args())
            output = fake_out.getvalue()
            self.assertIn("Analitik Editorial (14 Hari Terakhir)", output)
            self.assertIn("Total Artikel Baru", output)
            self.assertIn("Kecepatan Publikasi", output)

    def test_cmd_prune(self):
        art_id = cli.storage.save_article({
            "topic": "Prune CLI",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "prune cli",
            "seo_title": "Prune CLI",
            "slug": "prune-cli",
            "meta_description": "Deskripsi prune cli.",
            "html_content": "<p>Content</p>"
        })
        cli.storage.create_revision(art_id)
        cli.storage.create_revision(art_id)
        cli.storage.create_revision(art_id)

        class Args:
            retention_days = 0
            keep_minimum = 1

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_prune(Args())
            output = fake_out.getvalue()
            self.assertIn("Pembersihan Revisi Database", output)
            self.assertIn("Revisi usang dihapus", output)

    def test_cmd_hugo(self):
        slug = "hugo-cli-slug"
        cli.storage.save_article({
            "topic": "Hugo CLI Article",
            "category": "Web Dev",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "hugo cli",
            "seo_title": "Hugo CLI Article",
            "slug": slug,
            "meta_description": "Deskripsi hugo cli.",
            "html_content": "<p>Hugo HTML Content</p>",
            "status": "ready"
        })
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
            out_file = tf.name

        try:
            class Args:
                pass
            args = Args()
            args.slug = slug
            args.out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_hugo(args)
                self.assertIn("Export Hugo markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn('title: "Hugo CLI Article"', content)
            self.assertIn("<p>Hugo HTML Content</p>", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_schedule(self):
        art_id = cli.storage.save_article({
            "topic": "Scheduled Article",
            "category": "Testing",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "scheduled test",
            "seo_title": "Scheduled Article Title",
            "slug": "scheduled-article-test",
            "meta_description": "Meta desc for schedule test.",
            "html_content": "<p>Content</p>",
            "status": "ready"
        })

        class ArgsList:
            action = "list"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_schedule(ArgsList())
            self.assertIn("Tidak ada jadwal publikasi pending.", fake_out.getvalue())

        class ArgsAdd:
            action = "add"
            id = art_id
            time = "2026-10-15T10:00:00"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_schedule(ArgsAdd())
            self.assertIn("Jadwal publikasi berhasil dibuat", fake_out.getvalue())

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_schedule(ArgsList())
            out = fake_out.getvalue()
            self.assertIn(str(art_id), out)
            self.assertIn("2026-10-15T10:00:00", out)

        class ArgsCancel:
            action = "cancel"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_schedule(ArgsCancel())
            self.assertIn("berhasil dibatalkan", fake_out.getvalue())

    def test_cmd_dump(self):
        cli.storage.save_article({
            "topic": "Dump Article",
            "category": "Testing",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "dump test",
            "seo_title": "Dump Article Title",
            "slug": "dump-article-test",
            "meta_description": "Meta desc for dump test.",
            "html_content": "<p>Content</p>",
            "status": "ready"
        })
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            out_file = tf.name

        try:
            class Args:
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_dump(Args())
                self.assertIn("Database dump berhasil diekspor", fake_out.getvalue())

            import json
            dump = json.loads(Path(out_file).read_text(encoding="utf-8"))
            self.assertEqual(dump["schema_version"], "2.3.0")
            self.assertIn("articles", dump)
            self.assertGreater(len(dump["articles"]), 0)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_mdx(self):
        slug = "cli-mdx-test-slug"
        cli.storage.save_article({
            "topic": "MDX CLI Article",
            "category": "Frontend",
            "publish_date": "2026-10-03",
            "focus_keyphrase": "mdx cli",
            "seo_title": "MDX CLI Article",
            "slug": slug,
            "meta_description": "Deskripsi mdx cli.",
            "html_content": "<div class='tu-editorial-container'><p>MDX HTML</p></div>",
            "status": "ready"
        })
        with tempfile.NamedTemporaryFile(suffix=".mdx", delete=False) as tf:
            out_file = tf.name

        try:
            class Args:
                framework = "astro"
            args = Args()
            args.slug = slug
            args.out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_mdx(args)
                self.assertIn("Export MDX (astro) berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn('title: "MDX CLI Article"', content)
            self.assertIn("pubDate: 2026-10-03", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

if __name__ == "__main__":
    unittest.main()

