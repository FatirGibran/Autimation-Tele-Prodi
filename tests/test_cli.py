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

    def test_cmd_lock(self):
        art_id = cli.storage.save_article({
            "topic": "CLI Lock Article",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "cli lock",
            "seo_title": "CLI Lock Article",
            "slug": "cli-lock-article",
            "meta_description": "Meta desc.",
            "status": "draft"
        })

        class ArgsAcquire:
            action = "acquire"
            id = art_id
            user = "editor_cli"
            ttl = 60

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_lock(ArgsAcquire())
            self.assertIn("Lock berhasil diperoleh", fake_out.getvalue())

        class ArgsStatus:
            action = "status"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_lock(ArgsStatus())
            self.assertIn("editor_cli", fake_out.getvalue())

        class ArgsRelease:
            action = "release"
            id = art_id
            user = "editor_cli"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_lock(ArgsRelease())
            self.assertIn("berhasil dilepaskan", fake_out.getvalue())

    def test_cmd_replace(self):
        cli.storage.save_article({
            "topic": "Target Replace",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "replace target",
            "seo_title": "Artikel Dengan Kata Kunci Target",
            "slug": "target-replace-slug",
            "meta_description": "Deskripsi artikel.",
            "html_content": "<p>Teks Target.</p>",
            "status": "draft"
        })

        class ArgsReplace:
            target = "Target"
            replace = "Pengganti"
            status = "draft"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_replace(ArgsReplace())
            self.assertIn("Batch replace selesai:", fake_out.getvalue())

    def test_cmd_schema(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            out_file = tf.name

        try:
            class ArgsSchema:
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_schema(ArgsSchema())
                self.assertIn("Schema EducationalOccupationalProgram berhasil dibuat", fake_out.getvalue())

            import json
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))
            self.assertEqual(data["@type"], "EducationalOccupationalProgram")
            self.assertEqual(data["provider"]["name"], "Telkom University Purwokerto")
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_bookmark(self):
        art_id = cli.storage.save_article({
            "topic": "Bookmark CLI Target",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "bookmark cli",
            "seo_title": "Bookmark CLI Target",
            "slug": "bookmark-cli-target",
            "meta_description": "Deskripsi bookmark cli.",
            "status": "published"
        })

        class ArgsAdd:
            action = "add"
            id = art_id
            user = "tester_cli"
            notes = "Catatan penting"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bookmark(ArgsAdd())
            self.assertIn("Bookmark berhasil ditambahkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            user = "tester_cli"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bookmark(ArgsList())
            self.assertIn("Bookmark Artikel untuk User", fake_out.getvalue())
            self.assertIn("Bookmark CLI Target", fake_out.getvalue())

    def test_cmd_cat_stats(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_cat_stats(None)
            self.assertIn("Analitik Artikel per Kategori", fake_out.getvalue())
            self.assertIn("TOTAL ARTIKEL", fake_out.getvalue())

    def test_cmd_nuxt(self):
        cli.storage.save_article({
            "topic": "Nuxt Export Target",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "nuxt export",
            "seo_title": "Nuxt Export Target",
            "slug": "nuxt-export-target",
            "meta_description": "Deskripsi nuxt export.",
            "html_content": "<p>Konten Nuxt CLI</p>",
            "status": "published"
        })

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
            out_file = tf.name

        try:
            class ArgsNuxt:
                slug = "nuxt-export-target"
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_nuxt(ArgsNuxt())
                self.assertIn("Export Nuxt markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn('title: "Nuxt Export Target"', content)
            self.assertIn("<p>Konten Nuxt CLI</p>", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_subscribe(self):
        class ArgsAdd:
            action = "add"
            user = "editor_sub_cli"
            channel = "telegram"
            category = "akademik"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_subscribe(ArgsAdd())
            self.assertIn("berhasil didaftarkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            category = "akademik"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_subscribe(ArgsList())
            self.assertIn("editor_sub_cli", fake_out.getvalue())
            self.assertIn("telegram", fake_out.getvalue())

        class ArgsRemove:
            action = "remove"
            user = "editor_sub_cli"
            category = "akademik"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_subscribe(ArgsRemove())
            self.assertIn("berhasil dihapus", fake_out.getvalue())

    def test_cmd_diff_rev(self):
        art_id = cli.storage.save_article({
            "topic": "CLI Diff Rev Target",
            "category": "Testing",
            "publish_date": "2026-10-07",
            "focus_keyphrase": "cli diff rev",
            "seo_title": "CLI Diff Rev Target",
            "slug": "cli-diff-rev-target",
            "meta_description": "Versi 1",
            "html_content": "<p>Satu dua tiga.</p>",
            "status": "draft"
        })
        cli.storage.create_revision(art_id)
        with cli.storage._get_connection() as conn:
            conn.execute(
                "UPDATE articles SET html_content = ?, meta_description = ? WHERE id = ?",
                ("<p>Satu dua tiga empat lima enam.</p>", "Versi 2 diperbarui", art_id)
            )
        cli.storage.create_revision(art_id)

        class ArgsDiff:
            id = art_id
            rev_a = 1
            rev_b = 2

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_diff_rev(ArgsDiff())
            out = fake_out.getvalue()
            self.assertIn("Komparasi Revisi Artikel ID", out)
            self.assertIn("Selisih Kata:", out)
            self.assertIn("Meta Description Berubah: Ya", out)

    def test_cmd_svelte(self):
        cli.storage.save_article({
            "topic": "Svelte CLI Target",
            "category": "Web Dev",
            "publish_date": "2026-10-07",
            "focus_keyphrase": "svelte cli",
            "seo_title": "Svelte CLI Target",
            "slug": "svelte-cli-target",
            "meta_description": "Deskripsi svelte cli.",
            "html_content": "<p>Konten Sveltekit CLI</p>",
            "status": "published"
        })

        with tempfile.NamedTemporaryFile(suffix=".svx", delete=False) as tf:
            out_file = tf.name

        try:
            class ArgsSvelte:
                slug = "svelte-cli-target"
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_svelte(ArgsSvelte())
                self.assertIn("Export SvelteKit markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn('title: "Svelte CLI Target"', content)
            self.assertIn("layout: article", content)
            self.assertIn("<p>Konten Sveltekit CLI</p>", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_task(self):
        art_id = cli.storage.save_article({
            "topic": "Task CLI Article",
            "category": "Testing",
            "publish_date": "2026-10-08",
            "focus_keyphrase": "task cli",
            "seo_title": "Task CLI Article",
            "slug": "task-cli-article",
            "meta_description": "Deskripsi task cli.",
            "status": "draft"
        })
        class ArgsAdd:
            action = "add"
            id = art_id
            assignee = "budi"
            type = "fact_check"
            due = "2026-10-20"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_task(ArgsAdd())
            self.assertIn("berhasil ditugaskan ke budi", fake_out.getvalue())

        class ArgsList:
            action = "list"
            status = "pending"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_task(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Daftar Tugas Editorial", out)
            self.assertIn("budi", out)
            self.assertIn("fact_check", out)

    def test_cmd_view_stats(self):
        art_id = cli.storage.save_article({
            "topic": "View Stats CLI",
            "category": "Testing",
            "publish_date": "2026-10-08",
            "focus_keyphrase": "view stats cli",
            "seo_title": "View Stats CLI",
            "slug": "view-stats-cli",
            "meta_description": "Deskripsi view stats cli.",
            "status": "published"
        })
        cli.storage.record_article_view(art_id, referrer="https://google.com")

        class ArgsViews:
            id = art_id
            days = 7

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_view_stats(ArgsViews())
            out = fake_out.getvalue()
            self.assertIn(f"Statistik Tayangan Artikel ID {art_id}", out)
            self.assertIn("TAYANGAN", out)

    def test_cmd_eleventy(self):
        cli.storage.save_article({
            "topic": "Eleventy CLI Target",
            "category": "Jamstack",
            "publish_date": "2026-10-08",
            "focus_keyphrase": "eleventy cli",
            "seo_title": "Eleventy CLI Target",
            "slug": "eleventy-cli-target",
            "meta_description": "Deskripsi eleventy cli.",
            "html_content": "<p>Konten 11ty CLI</p>",
            "status": "published"
        })

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
            out_file = tf.name

        try:
            class Args11ty:
                slug = "eleventy-cli-target"
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_eleventy(Args11ty())
                self.assertIn("Export Eleventy markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn('title: "Eleventy CLI Target"', content)
            self.assertIn("layout: layouts/post.njk", content)
            self.assertIn("<p>Konten 11ty CLI</p>", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

if __name__ == "__main__":
    unittest.main()


