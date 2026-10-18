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

    def test_cmd_note(self):
        art_id = cli.storage.save_article({
            "topic": "Note CLI Test",
            "category": "Akademik",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "note cli",
            "seo_title": "Note CLI Test",
            "slug": "note-cli-test",
            "meta_description": "Deskripsi catatan cli.",
            "status": "draft"
        })

        class ArgsAdd:
            action = "add"
            id = art_id
            note_id = None
            author = "editor_bima"
            text = "Tinjau bab metodologi"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_note(ArgsAdd())
            self.assertIn("Catatan editorial berhasil ditambahkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            id = art_id
            note_id = None

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_note(ArgsList())
            self.assertIn("editor_bima", fake_out.getvalue())
            self.assertIn("Tinjau bab metodologi", fake_out.getvalue())

    def test_cmd_zola(self):
        cli.storage.save_article({
            "topic": "Zola CLI Target",
            "category": "Akademik",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "zola cli",
            "seo_title": "Zola CLI Target",
            "slug": "zola-cli-target",
            "meta_description": "Deskripsi zola cli.",
            "html_content": "<p>Konten Zola CLI</p>",
            "status": "published"
        })

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
            out_file = tf.name

        try:
            class ArgsZola:
                slug = "zola-cli-target"
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_zola(ArgsZola())
                self.assertIn("Export Zola markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("+++"))
            self.assertIn('title = "Zola CLI Target"', content)
            self.assertIn('<p>Konten Zola CLI</p>', content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_webhook_logs(self):
        cli.storage.log_webhook_dispatch(
            event="test_dispatch",
            target_url="https://api.telkomuniversity.ac.id/hook",
            status_code=200,
            payload_snippet="payload test snippet"
        )

        class ArgsLogs:
            limit = 5

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_webhook_logs(ArgsLogs())
            out = fake_out.getvalue()
            self.assertIn("EVENT", out)
            self.assertIn("test_dispatch", out)

    def test_cmd_reviewer(self):
        art_id = cli.storage.save_article({
            "topic": "Reviewer CLI Topic",
            "category": "Akademik",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "rev cli",
            "seo_title": "Reviewer CLI Article",
            "slug": "reviewer-cli-article",
            "meta_description": "Meta reviewer cli",
            "status": "draft"
        })

        class ArgsAssign:
            action = "assign"
            id = art_id
            name = "Prof. Dr. Ir. Sri Wahyuni"
            email = "sri@telkomuniversity.ac.id"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_reviewer(ArgsAssign())
            self.assertIn("Reviewer 'Prof. Dr. Ir. Sri Wahyuni' berhasil ditugaskan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_reviewer(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Daftar Reviewer Artikel", out)
            self.assertIn("Prof. Dr. Ir. Sri Wahyuni", out)

        # Update status
        reviewers = cli.storage.list_article_reviewers(art_id)
        rev_id = reviewers[0]["id"]

        class ArgsStatus:
            action = "status"
            review_id = rev_id
            status = "accepted"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_reviewer(ArgsStatus())
            self.assertIn("berhasil diubah menjadi 'accepted'", fake_out.getvalue())

    def test_cmd_pelican(self):
        slug = "pelican-cli-target"
        cli.storage.save_article({
            "topic": "Pelican CLI Article",
            "category": "Teknologi",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "pelican cli",
            "seo_title": "Pelican CLI Target",
            "slug": slug,
            "meta_description": "Deskripsi pelican cli.",
            "html_content": "<p>Konten Pelican CLI</p>",
            "status": "published"
        })

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
            out_file = tf.name

        try:
            class ArgsPelican:
                slug = "pelican-cli-target"
                out = out_file

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_pelican(ArgsPelican())
                self.assertIn("Export Pelican markdown berhasil", fake_out.getvalue())

            content = Path(out_file).read_text(encoding="utf-8")
            self.assertIn("Title: Pelican CLI Target", content)
            self.assertIn("Date: 2026-10-11", content)
            self.assertIn("<p>Konten Pelican CLI</p>", content)
        finally:
            if Path(out_file).exists():
                Path(out_file).unlink()

    def test_cmd_checklist(self):
        art_id = cli.storage.save_article({
            "topic": "Checklist CLI Topic",
            "category": "Akademik",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "chk cli",
            "seo_title": "Checklist CLI Article",
            "slug": "checklist-cli-article",
            "meta_description": "Meta checklist cli",
            "status": "draft"
        })

        class ArgsSet:
            action = "set"
            id = art_id
            key = "proofread"
            label = "Proofread Tata Bahasa Indonesia"
            checked = True
            by = "Fatir Gibran"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_checklist(ArgsSet())
            self.assertIn("diatur ke [SELESAI (V)]", fake_out.getvalue())

        class ArgsList:
            action = "list"
            id = art_id

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_checklist(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Status Checklist Editorial", out)
            self.assertIn("[V] proofread: Proofread Tata Bahasa Indonesia (oleh: Fatir Gibran)", out)

    def test_cmd_snippet(self):
        class ArgsSave:
            action = "save"
            key = "telkom_cta"
            title = "Call To Action PMB"
            html = "<div>Daftar sekarang di Telkom Purwokerto!</div>"
            category = "marketing"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_snippet(ArgsSave())
            self.assertIn("Snippet 'telkom_cta' berhasil disimpan", fake_out.getvalue())

        class ArgsGet:
            action = "get"
            key = "telkom_cta"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_snippet(ArgsGet())
            out = fake_out.getvalue()
            self.assertIn("Call To Action PMB", out)
            self.assertIn("marketing", out)

        class ArgsList:
            action = "list"
            category = None

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_snippet(ArgsList())
            self.assertIn("telkom_cta", fake_out.getvalue())

    def test_cmd_docusaurus(self):
        slug = "docusaurus-cli-target"
        cli.storage.save_article({
            "topic": "Docusaurus Topic",
            "category": "Dokumentasi",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "docu target",
            "seo_title": "Docusaurus CLI Target",
            "slug": slug,
            "meta_description": "Meta docusaurus cli",
            "html_content": "<p>Konten Docusaurus CLI</p>",
            "status": "published"
        })
        out_file = Path(self.temp_dir.name) / "test_docu.md"
        try:
            class ArgsDocu:
                pass
            args = ArgsDocu()
            args.slug = slug
            args.out = str(out_file)
            args.label = "Docu Sidebar"
            args.position = 2

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_docusaurus(args)
                self.assertIn("Export Docusaurus markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "Docusaurus CLI Target"', content)
            self.assertIn('sidebar_label: "Docu Sidebar"', content)
            self.assertIn("sidebar_position: 2", content)
            self.assertIn("<p>Konten Docusaurus CLI</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_comment(self):
        art_id = cli.storage.save_article({
            "topic": "Comment Article",
            "category": "Akademik",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "comment target",
            "seo_title": "Comment Article Target",
            "slug": "comment-article-target",
            "meta_description": "Meta comment",
            "status": "draft"
        })

        class ArgsAdd:
            action = "add"
            id = art_id
            author = "Reviewer B"
            text = "Mohon tambahkan sitasi IEEE"
            paragraph = 3

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_comment(ArgsAdd())
            self.assertIn("Komentar editorial berhasil ditambahkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            id = art_id
            unresolved_only = False

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_comment(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Komentar Editorial Artikel", out)
            self.assertIn("Reviewer B (Paragraf 3): Mohon tambahkan sitasi IEEE", out)

        class ArgsResolve:
            action = "resolve"
            comment_id = 1

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_comment(ArgsResolve())
            self.assertIn("Komentar #1 berhasil diselesaikan", fake_out.getvalue())

    def test_cmd_achievement(self):
        class ArgsAdd:
            action = "add"
            name = "Gemastik XVII"
            rank = "Juara 1 Emas"
            team = "Telematics-PWT"
            members = "Fatir Gibran, Budi Santoso"
            supervisor = "Dr. Wahyu"
            year = 2026
            organizer = "Puspresnas"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_achievement(ArgsAdd())
            self.assertIn("Prestasi kompetisi berhasil dicatat", fake_out.getvalue())

        class ArgsList:
            action = "list"
            year = 2026

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_achievement(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Prestasi Kompetisi Mahasiswa", out)
            self.assertIn("Gemastik XVII", out)
            self.assertIn("Juara 1 Emas", out)

    def test_cmd_mkdocs(self):
        slug = "mkdocs-cli-test-article"
        cli.storage.save_article({
            "topic": "MkDocs Panduan",
            "category": "Dokumentasi",
            "publish_date": "2026-10-12",
            "focus_keyphrase": "mkdocs panduan",
            "seo_title": "MkDocs CLI Target",
            "slug": slug,
            "meta_description": "Meta mkdocs",
            "html_content": "<p>Konten MkDocs CLI</p>",
            "tags": ["mkdocs", "cli"],
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsMkdocs:
                pass
            args = ArgsMkdocs()
            args.slug = slug
            args.out = str(out_file)

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_mkdocs(args)
                self.assertIn("Export MkDocs markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "MkDocs CLI Target"', content)
            self.assertIn('# MkDocs CLI Target', content)
            self.assertIn("<p>Konten MkDocs CLI</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_safety_log(self):
        class ArgsAdd:
            action = "add"
            lab = "Lab Jaringan Komputer"
            inspector = "Agus K3"
            score = 92.5
            passed = True
            date = "2026-10-12"
            notes = "Kondisi APAR dan P3K lengkap"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_safety_log(ArgsAdd())
            self.assertIn("Log inspeksi K3 lab berhasil dicatat", fake_out.getvalue())

        class ArgsList:
            action = "list"
            lab = "Lab Jaringan Komputer"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_safety_log(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Log Inspeksi Keselamatan Kerja & K3 Lab", out)
            self.assertIn("Lab Jaringan Komputer", out)
            self.assertIn("LULUS", out)

    def test_cmd_mbkm(self):
        class ArgsAdd:
            action = "add"
            program = "Magang Bersertifikat Kampus Merdeka"
            partner = "PT Telkom Indonesia Tbk"
            name = "Rizky Ramadhan"
            nim = "1201234050"
            semester = 6
            sks = 20
            gpa = 3.90
            sk = "SK/MBKM/2026/042"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_mbkm(ArgsAdd())
            self.assertIn("Konversi kredit MBKM berhasil dicatat", fake_out.getvalue())
            self.assertIn("Rizky Ramadhan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            nim = "1201234050"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_mbkm(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Konversi Kredit MBKM", out)
            self.assertIn("PT Telkom Indonesia Tbk", out)
            self.assertIn("20 SKS", out)

    def test_cmd_yudisium(self):
        class ArgsAdd:
            action = "add"
            name = "Ayu Lestari"
            nim = "1201234099"
            thesis = "Optimasi Jaringan 5G Millimeter-Wave Purwokerto"
            ipk = 3.88
            sks = 144
            predicate = "Dengan Pujian (Cumlaude)"
            date = "2026-10-14"
            code = "YUD-2026-099"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_yudisium(ArgsAdd())
            self.assertIn("Kelulusan yudisium berhasil dicatat", fake_out.getvalue())
            self.assertIn("Ayu Lestari", fake_out.getvalue())

        class ArgsCheck:
            action = "check"
            nim = "1201234099"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_yudisium(ArgsCheck())
            out = fake_out.getvalue()
            self.assertIn("Status Yudisium Ayu Lestari (1201234099): LULUS / CLEARED", out)
            self.assertIn("3.88", out)
            self.assertIn("YUD-2026-099", out)

        class ArgsList:
            action = "list"
            predicate = "Dengan Pujian (Cumlaude)"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_yudisium(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Kelulusan Yudisium Mahasiswa", out)
            self.assertIn("Ayu Lestari", out)

    def test_cmd_starlight(self):
        slug = "starlight-cli-test-article"
        cli.storage.save_article({
            "topic": "Starlight Modul Panduan",
            "category": "Dokumentasi",
            "publish_date": "2026-10-14",
            "focus_keyphrase": "starlight panduan",
            "seo_title": "Starlight CLI Target",
            "slug": slug,
            "meta_description": "Meta starlight doc",
            "html_content": "<p>Konten Starlight CLI</p>",
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsStarlight:
                pass
            args = ArgsStarlight()
            args.slug = slug
            args.out = str(out_file)
            args.label = "Modul Starlight"
            args.order = 3

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_starlight(args)
                self.assertIn("Export Astro Starlight markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "Starlight CLI Target"', content)
            self.assertIn("sidebar:", content)
            self.assertIn('  label: "Modul Starlight"', content)
            self.assertIn("  order: 3", content)
            self.assertIn("<p>Konten Starlight CLI</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_kkn(self):
        class ArgsAdd:
            action = "add"
            group = "KKN-TM-CLI-01"
            village = "Pageraji"
            district = "Cilongok"
            regency = "Banyumas"
            supervisor = "Dr. Eng. Irfan"
            students = 11
            theme = "Smart Village IoT"
            flagship = "Telemetri Irigasi Sawah"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_kkn(ArgsAdd())
            out = fake_out.getvalue()
            self.assertIn("Penempatan KKN tematik berhasil dicatat", out)
            self.assertIn("KKN-TM-CLI-01", out)
            self.assertIn("Desa Pageraji", out)

        class ArgsList:
            action = "list"
            regency = "Banyumas"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_kkn(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Program KKN Tematik Mahasiswa", out)
            self.assertIn("KKN-TM-CLI-01", out)
            self.assertIn("Pageraji", out)

    def test_cmd_bkd(self):
        class ArgsAdd:
            action = "add"
            name = "Dr. Budi Santoso"
            nidn = "0401018501"
            rank = "Lektor"
            semester = "2025/2026 Genap"
            teaching = 6.0
            research = 4.0
            service = 2.0
            supporting = 1.0
            total = 13.0
            compliant = True

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bkd(ArgsAdd())
            out = fake_out.getvalue()
            self.assertIn("Beban kerja dosen (BKD) berhasil dicatat", out)
            self.assertIn("Dr. Budi Santoso", out)
            self.assertIn("[MEMENUHI]", out)

        class ArgsList:
            action = "list"
            semester = "2025/2026 Genap"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bkd(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Kepatuhan Beban Kerja Dosen (BKD)", out)
            self.assertIn("Dr. Budi Santoso", out)
            self.assertIn("13.0 SKS", out)

    def test_cmd_hexo(self):
        slug = "hexo-cli-test-article"
        cli.storage.save_article({
            "topic": "Hexo Blog Target",
            "category": "Jaringan Komputer",
            "publish_date": "2026-10-15 11:00:00",
            "focus_keyphrase": "hexo blog",
            "seo_title": "Hexo CLI Target",
            "slug": slug,
            "meta_description": "Meta hexo blog",
            "html_content": "<p>Konten Hexo Blog CLI</p>",
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsHexo:
                pass
            args = ArgsHexo()
            args.slug = slug
            args.out = str(out_file)

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_hexo(args)
                self.assertIn("Export Hexo markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "Hexo CLI Target"', content)
            self.assertIn("categories:", content)
            self.assertIn('  - "Jaringan Komputer"', content)
            self.assertIn("<p>Konten Hexo Blog CLI</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_bima(self):
        class ArgsAdd:
            action = "add"
            title = "Pengembangan Sistem Radar Maritim C-Band"
            name = "Dr. Ir. Budi Santoso, M.T."
            nidn = "0012057801"
            scheme = "Penelitian Terapan Unggulan"
            requested = 150000000.0
            approved = 120000000.0
            year = 2026
            status = "approved"
            contract = "124/BIMA/2026"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bima(ArgsAdd())
            out = fake_out.getvalue()
            self.assertIn("Usulan hibah BIMA berhasil dicatat", out)
            self.assertIn("Pengembangan Sistem Radar Maritim C-Band", out)

        class ArgsList:
            action = "list"
            year = 2026
            status = "approved"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_bima(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Usulan Hibah Penelitian BIMA Kemdikbud", out)
            self.assertIn("Dr. Ir. Budi Santoso, M.T.", out)

    def test_cmd_kp(self):
        class ArgsAdd:
            action = "add"
            name = "Bayu Pratama"
            nim = "120120001"
            company = "PT Telkom Indonesia"
            sector = "Telekomunikasi Seluler & Fiber"
            weeks = 8
            project = "Monitoring Core Network OLT GPON"
            mentor = "Ir. Hendra Wijaya"
            status = "active"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_kp(ArgsAdd())
            out = fake_out.getvalue()
            self.assertIn("Penempatan kerja praktik berhasil dicatat", out)
            self.assertIn("Bayu Pratama", out)
            self.assertIn("PT Telkom Indonesia", out)

        class ArgsList:
            action = "list"
            status = "active"
            company = None

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_kp(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Penempatan Kerja Praktik (KP) Mahasiswa", out)
            self.assertIn("120120001", out)

    def test_cmd_vitepress(self):
        slug = "vitepress-cli-test-article"
        cli.storage.save_article({
            "topic": "VitePress Docs",
            "category": "Dokumentasi",
            "publish_date": "2026-10-15",
            "focus_keyphrase": "vitepress docs",
            "seo_title": "Panduan VitePress CLI",
            "slug": slug,
            "meta_description": "Dokumentasi vitepress cli prodi",
            "html_content": "<p>Isi panduan VitePress</p>",
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsVP:
                pass
            args = ArgsVP()
            args.slug = slug
            args.out = str(out_file)

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_vitepress(args)
                self.assertIn("Export VitePress markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "Panduan VitePress CLI"', content)
            self.assertIn("outline: [2, 3]", content)
            self.assertIn("<p>Isi panduan VitePress</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_accreditation(self):
        class ArgsAdd:
            action = "add"
            program = "S1 Teknik Telekomunikasi"
            agency = "LAM INFOKOM"
            rating = "Unggul"
            sk = "042/SK/LAM-INFOKOM/Ak/S/XII/2025"
            expiry = "2030-12-01"
            issued = "2025-12-01"
            active = True

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_accreditation(ArgsAdd())
            self.assertIn("Catatan akreditasi prodi berhasil disimpan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            agency = "LAM INFOKOM"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_accreditation(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Akreditasi Program Studi", out)
            self.assertIn("S1 Teknik Telekomunikasi", out)
            self.assertIn("Unggul", out)

    def test_cmd_scholarship(self):
        class ArgsAdd:
            action = "add"
            name = "Ahmad Hidayat"
            nim = "1101220001"
            type = "pemerintah"
            sponsor = "KIP Kuliah Merdeka"
            amount = 6000000.0
            semester = "Ganjil"
            year = "2026/2027"
            status = "active"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_scholarship(ArgsAdd())
            self.assertIn("Alokasi beasiswa mahasiswa berhasil dicatat", fake_out.getvalue())

        class ArgsList:
            action = "list"
            type = "pemerintah"
            status = "active"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_scholarship(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("Rekam Jejak Alokasi Beasiswa Mahasiswa", out)
            self.assertIn("Ahmad Hidayat", out)
            self.assertIn("KIP Kuliah Merdeka", out)

    def test_cmd_jekyll(self):
        slug = "jekyll-cli-test-article"
        cli.storage.save_article({
            "topic": "Jekyll Tutorial",
            "category": "Tutorial",
            "publish_date": "2026-10-16 12:00:00",
            "focus_keyphrase": "jekyll tutorial",
            "seo_title": "Panduan Jekyll Static Site",
            "slug": slug,
            "meta_description": "Dokumentasi jekyll cli prodi",
            "html_content": "<p>Isi panduan Jekyll</p>",
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsJekyll:
                pass
            args = ArgsJekyll()
            args.slug = slug
            args.out = str(out_file)
            args.layout = "post"

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_jekyll(args)
                self.assertIn("Export Jekyll markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn("layout: post", content)
            self.assertIn('title: "Panduan Jekyll Static Site"', content)
            self.assertIn("<p>Isi panduan Jekyll</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()

    def test_cmd_honors(self):
        class ArgsAdd:
            action = "add"
            name = "Dewi Sartika"
            nim = "120120005"
            ipk = 3.92
            predicate = "Dengan Pujian (Cum Laude)"
            thesis = "Optimasi MIMO Beamforming 5G"
            duration = 8
            year = 2026

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_honors(ArgsAdd())
            self.assertIn("Catatan yudisium berhasil ditambahkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            year = 2026
            predicate = "Cum Laude"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_honors(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("120120005", out)
            self.assertIn("Dewi Sartika", out)
            self.assertIn("Cum Laude", out)

    def test_cmd_tridharma(self):
        class ArgsAdd:
            action = "add"
            lecturer = "Dr. Ir. Budi Santoso, M.T."
            nidn = "0612058001"
            title = "Rancang Bangun Sensor Akustik Kelautan"
            amount = 25000000.0
            year = 2026
            target = "Jurnal SINTA 2"
            status = "active"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_tridharma(ArgsAdd())
            self.assertIn("Catatan hibah riset tridharma berhasil ditambahkan", fake_out.getvalue())

        class ArgsList:
            action = "list"
            year = 2026
            status = "active"

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            cli.cmd_tridharma(ArgsList())
            out = fake_out.getvalue()
            self.assertIn("0612058001", out)
            self.assertIn("25,000,000", out)
            self.assertIn("2026", out)

    def test_cmd_quartz(self):
        slug = "quartz-cli-test-article"
        cli.storage.save_article({
            "topic": "Quartz Tutorial",
            "category": "Catatan",
            "publish_date": "2026-10-18",
            "focus_keyphrase": "quartz digital garden",
            "seo_title": "Membangun Digital Garden Quartz",
            "slug": slug,
            "meta_description": "Dokumentasi quartz digital garden prodi",
            "html_content": "<p>Isi panduan Quartz</p>",
            "status": "ready"
        })

        out_file = Path(self.temp_dir.name) / f"{slug}.md"
        try:
            class ArgsQuartz:
                pass
            args = ArgsQuartz()
            args.slug = slug
            args.out = str(out_file)

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                cli.cmd_quartz(args)
                self.assertIn("Export Quartz markdown berhasil", fake_out.getvalue())

            content = out_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"))
            self.assertIn('title: "Membangun Digital Garden Quartz"', content)
            self.assertIn('description: "Catatan note"', content)
            self.assertIn("<p>Isi panduan Quartz</p>", content)
        finally:
            if out_file.exists():
                out_file.unlink()


if __name__ == "__main__":
    unittest.main()





