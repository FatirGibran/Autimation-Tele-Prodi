import unittest
import tempfile
from pathlib import Path
from storage import StorageManager

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_editorial.db"
        self.storage = StorageManager(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_get_article(self):
        sample = {
            "topic": "IoT Edge Computing",
            "category": "Teknologi",
            "publish_date": "2026-09-29",
            "image_url": "https://example.com/img.jpg",
            "focus_keyphrase": "iot edge computing",
            "seo_title": "IoT Edge Computing: Panduan Lengkap",
            "slug": "iot-edge-computing",
            "meta_description": "Ulasan mendalam mengenai implementasi iot edge computing di lingkungan kampus.",
            "html_content": "<div class=\"tu-editorial-container\"><p>Konten</p></div>",
            "status": "ready"
        }
        art_id = self.storage.save_article(sample)
        self.assertGreater(art_id, 0)

        # Retrieve by slug
        by_slug = self.storage.get_article_by_slug("iot-edge-computing")
        self.assertIsNotNone(by_slug)
        self.assertEqual(by_slug["seo_title"], sample["seo_title"])

        # Retrieve by ID
        by_id = self.storage.get_article_by_id(art_id)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id["slug"], "iot-edge-computing")

    def test_is_keyphrase_and_slug_used(self):
        sample = {
            "topic": "WebAssembly Performance",
            "category": "Riset",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "webassembly performance",
            "seo_title": "WebAssembly Performance 2026",
            "slug": "webassembly-performance-2026",
            "meta_description": "Meta description test sample for keyphrase uniqueness check.",
            "status": "ready"
        }
        self.storage.save_article(sample)

        self.assertTrue(self.storage.is_keyphrase_used("WebAssembly Performance"))
        self.assertTrue(self.storage.is_keyphrase_used("webassembly performance"))
        self.assertFalse(self.storage.is_keyphrase_used("cloud native"))

        self.assertTrue(self.storage.is_slug_used("webassembly-performance-2026"))
        self.assertFalse(self.storage.is_slug_used("unknown-slug"))

    def test_search_and_statistics(self):
        self.storage.save_article({
            "topic": "Kecerdasan Buatan Terapan",
            "category": "AI",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "ai terapan",
            "seo_title": "AI Terapan untuk Smart Campus",
            "slug": "ai-terapan-smart-campus",
            "meta_description": "Analisis penerapan kecerdasan buatan di kampus.",
            "status": "ready"
        })
        self.storage.save_article({
            "topic": "Keamanan Siber Jaringan",
            "category": "Cybersecurity",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "keamanan siber",
            "seo_title": "Keamanan Siber Jaringan Institusi",
            "slug": "keamanan-siber-jaringan",
            "meta_description": "Strategi pertahanan keamanan siber institusi.",
            "status": "needs_review"
        })

        search_results = self.storage.search_articles("cerdas")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["slug"], "ai-terapan-smart-campus")

        stats = self.storage.get_statistics()
        self.assertEqual(stats["total_articles"], 2)
        self.assertEqual(stats["ready_count"], 1)
        self.assertEqual(stats["needs_review_count"], 1)

    def test_delete_article(self):
        art_id = self.storage.save_article({
            "topic": "Hapus Artikel",
            "category": "General",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "hapus artikel",
            "seo_title": "Hapus Artikel Uji",
            "slug": "hapus-artikel-uji",
            "meta_description": "Artikel yang akan dihapus.",
            "status": "draft"
        })
        self.assertTrue(self.storage.delete_article(art_id))
        self.assertIsNone(self.storage.get_article_by_id(art_id))
        self.assertFalse(self.storage.delete_article(99999))

    def test_article_tagging(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Bertag",
            "category": "IoT",
            "publish_date": "2026-09-30",
            "focus_keyphrase": "artikel bertag",
            "seo_title": "Artikel Bertag untuk Uji",
            "slug": "artikel-bertag-untuk-uji",
            "meta_description": "Deskripsi meta untuk artikel bertag dalam unit test.",
            "status": "draft"
        })
        self.storage.add_tags(art_id, ["Wasm", "Edge-Computing", "IoT", "wasm"])
        tags = self.storage.get_article_tags(art_id)
        self.assertEqual(tags, ["edge-computing", "iot", "wasm"])

        by_tag = self.storage.get_articles_by_tag("wasm")
        self.assertEqual(len(by_tag), 1)
        self.assertEqual(by_tag[0]["id"], art_id)

    def test_status_transitions_and_audit_logs(self):
        art_id = self.storage.save_article({
            "topic": "Status Test",
            "category": "System",
            "publish_date": "2026-09-30",
            "focus_keyphrase": "status test",
            "seo_title": "Status Test Article",
            "slug": "status-test-article",
            "meta_description": "Meta description test for status transitions.",
            "status": "draft"
        })

        success = self.storage.update_status(art_id, "ready", note="Lolos audit Yoast SEO")
        self.assertTrue(success)
        self.assertFalse(self.storage.update_status(99999, "ready"))

        art = self.storage.get_article_by_id(art_id)
        self.assertEqual(art["status"], "ready")

        self.storage.update_status(art_id, "published", note="Dipublikasikan ke WP")
        logs = self.storage.get_audit_logs(art_id)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["old_status"], "draft")
        self.assertEqual(logs[0]["new_status"], "ready")
        self.assertEqual(logs[0]["note"], "Lolos audit Yoast SEO")
        self.assertEqual(logs[1]["old_status"], "ready")
        self.assertEqual(logs[1]["new_status"], "published")

    def test_bulk_update_and_date_filtering(self):
        id1 = self.storage.save_article({
            "topic": "Artikel 1",
            "category": "Tech",
            "publish_date": "2026-09-01",
            "focus_keyphrase": "artikel satu",
            "seo_title": "Artikel Satu",
            "slug": "artikel-satu",
            "meta_description": "Deskripsi satu untuk pengujian.",
            "status": "draft"
        })
        id2 = self.storage.save_article({
            "topic": "Artikel 2",
            "category": "Tech",
            "publish_date": "2026-09-15",
            "focus_keyphrase": "artikel dua",
            "seo_title": "Artikel Dua",
            "slug": "artikel-dua",
            "meta_description": "Deskripsi dua untuk pengujian.",
            "status": "draft"
        })

        # Bulk update
        updated = self.storage.bulk_update_status([id1, id2], "ready")
        self.assertEqual(updated, 2)
        self.assertEqual(self.storage.get_article_by_id(id1)["status"], "ready")
        self.assertEqual(self.storage.get_article_by_id(id2)["status"], "ready")

        # Date range filtering
        filtered = self.storage.filter_by_date_range("2026-09-10", "2026-09-20")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["slug"], "artikel-dua")

    def test_search_articles(self):
        self.storage.save_article({
            "topic": "Edge AI Security Protocol",
            "category": "Keamanan",
            "publish_date": "2026-10-01",
            "focus_keyphrase": "edge ai security",
            "seo_title": "Edge AI Security",
            "slug": "edge-ai-sec",
            "meta_description": "Enkripsi end to end pada sensor IoT edge.",
            "status": "published"
        })
        results = self.storage.search_articles("sensor IoT")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["slug"], "edge-ai-sec")
        self.assertIn("Enkripsi", results[0]["matched_snippet"])

    def test_optimize_and_check_integrity(self):
        res = self.storage.optimize_and_check_integrity()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["integrity_check"], "ok")
        self.assertTrue(res["vacuumed"])

    def test_create_and_get_revisions(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Versi Awal",
            "category": "Riset",
            "publish_date": "2026-10-01",
            "focus_keyphrase": "artikel revisi",
            "seo_title": "Artikel Revisi",
            "slug": "artikel-revisi",
            "meta_description": "Deskripsi versi awal.",
            "html_content": "<p>Versi 1</p>"
        })
        rev_id = self.storage.create_revision(art_id)
        self.assertIsNotNone(rev_id)

        revisions = self.storage.get_revisions(art_id)
        self.assertEqual(len(revisions), 1)
        self.assertEqual(revisions[0]["revision_num"], 1)
        self.assertIn("Versi 1", revisions[0]["html_content"])

    def test_soft_delete_and_restore_trash(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Sampah",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "artikel sampah",
            "seo_title": "Artikel Sampah",
            "slug": "artikel-sampah",
            "meta_description": "Deskripsi artikel sampah.",
            "status": "draft"
        })
        self.assertTrue(self.storage.soft_delete_article(art_id))
        trash = self.storage.list_trash()
        self.assertTrue(any(a["id"] == art_id for a in trash))
        active = self.storage.list_articles()
        self.assertFalse(any(a["id"] == art_id for a in active))

        self.assertTrue(self.storage.restore_article(art_id))
        active_after = self.storage.list_articles()
        self.assertTrue(any(a["id"] == art_id for a in active_after))

    def test_custom_article_metadata(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Meta",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "artikel meta",
            "seo_title": "Artikel Meta",
            "slug": "artikel-meta",
            "meta_description": "Deskripsi artikel meta.",
            "status": "draft"
        })
        self.storage.set_article_meta(art_id, "curriculum_code", "IF-2026-B")
        self.assertEqual(self.storage.get_article_meta(art_id, "curriculum_code"), "IF-2026-B")

        all_meta = self.storage.get_article_meta(art_id)
        self.assertIn("curriculum_code", all_meta)
        self.assertTrue(self.storage.delete_article_meta(art_id, "curriculum_code"))
        self.assertIsNone(self.storage.get_article_meta(art_id, "curriculum_code"))

    def test_export_event_logging(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Export Log",
            "category": "Testing",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "artikel export",
            "seo_title": "Artikel Export",
            "slug": "artikel-export",
            "meta_description": "Deskripsi artikel export.",
            "status": "draft"
        })
        export_id = self.storage.log_export_event(art_id, "elementor_json", "output/article.json")
        self.assertIsNotNone(export_id)
        history = self.storage.get_export_history(art_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["export_type"], "elementor_json")

    def test_enable_wal_mode(self):
        mode = self.storage.enable_wal_mode()
        self.assertIn(mode, ["WAL", "MEMORY", "DELETE"])

    def test_list_categories_and_filter(self):
        self.storage.save_article({
            "topic": "Telecom AI",
            "category": "Kecerdasan Buatan",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "telecom ai",
            "seo_title": "Telecom AI",
            "slug": "telecom-ai",
            "meta_description": "Deskripsi telecom ai.",
            "status": "ready"
        })
        self.storage.save_article({
            "topic": "Telecom 5G",
            "category": "Jaringan",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "telecom 5g",
            "seo_title": "Telecom 5G",
            "slug": "telecom-5g",
            "meta_description": "Deskripsi telecom 5g.",
            "status": "published"
        })
        cats = self.storage.list_categories()
        cat_names = [c["category"] for c in cats]
        self.assertIn("Kecerdasan Buatan", cat_names)
        self.assertIn("Jaringan", cat_names)

        filtered = self.storage.get_articles_by_category("Kecerdasan Buatan")
        self.assertTrue(any(a["slug"] == "telecom-ai" for a in filtered))
        self.assertFalse(any(a["slug"] == "telecom-5g" for a in filtered))

    def test_get_editorial_analytics(self):
        self.storage.save_article({
            "topic": "Analitik 1",
            "category": "Riset",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "analitik satu",
            "seo_title": "Analitik Satu",
            "slug": "analitik-satu",
            "meta_description": "Deskripsi analitik satu.",
            "status": "published"
        })
        analytics = self.storage.get_editorial_analytics(days=7)
        self.assertEqual(analytics["window_days"], 7)
        self.assertGreaterEqual(analytics["total_articles"], 1)
        self.assertGreaterEqual(analytics["published_count"], 1)
        self.assertIn("published", analytics["status_breakdown"])

    def test_prune_revisions(self):
        art_id = self.storage.save_article({
            "topic": "Revisi Prune",
            "category": "Riset",
            "publish_date": "2026-10-02",
            "focus_keyphrase": "revisi prune",
            "seo_title": "Revisi Prune",
            "slug": "revisi-prune",
            "meta_description": "Deskripsi prune.",
            "html_content": "<p>Content</p>"
        })
        self.storage.create_revision(art_id)
        self.storage.create_revision(art_id)
        self.storage.create_revision(art_id)
        revs = self.storage.get_revisions(art_id)
        self.assertEqual(len(revs), 3)

        deleted = self.storage.prune_revisions(retention_days=0, keep_minimum=2)
        revs_after = self.storage.get_revisions(art_id)
        self.assertEqual(len(revs_after), 2)
        self.assertEqual(deleted, 1)

    def test_schedule_publication_and_cancel(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Terjadwal",
            "category": "Riset",
            "publish_date": "2026-10-05",
            "focus_keyphrase": "artikel terjadwal",
            "seo_title": "Artikel Terjadwal",
            "slug": "artikel-terjadwal-1",
            "meta_description": "Deskripsi artikel terjadwal.",
            "status": "ready"
        })
        sched_id = self.storage.schedule_publication(art_id, "2026-10-10T08:00:00")
        self.assertIsNotNone(sched_id)

        pending = self.storage.get_pending_schedules()
        self.assertTrue(any(s["article_id"] == art_id for s in pending))

        cancelled = self.storage.cancel_schedule(art_id)
        self.assertTrue(cancelled)

        pending_after = self.storage.get_pending_schedules()
        self.assertFalse(any(s["article_id"] == art_id for s in pending_after))

    def test_export_and_import_database_dump(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Dump",
            "category": "Testing",
            "publish_date": "2026-10-05",
            "focus_keyphrase": "artikel dump",
            "seo_title": "Artikel Dump",
            "slug": "artikel-dump-unique",
            "meta_description": "Deskripsi dump.",
            "status": "published"
        })
        self.storage.add_tags(art_id, ["dump-test-tag"])
        dump = self.storage.export_database_dump()

        self.assertEqual(dump["schema_version"], "2.3.0")
        self.assertTrue(any(a["slug"] == "artikel-dump-unique" for a in dump["articles"]))

        # Import into an empty temporary storage
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp_dir:
            from storage import StorageManager
            other_storage = StorageManager(Path(tmp_dir) / "imported.db")
            res = other_storage.import_database_dump(dump)
            self.assertGreaterEqual(res["articles_imported"], 1)
            imported_art = other_storage.get_article_by_slug("artikel-dump-unique")
            self.assertIsNotNone(imported_art)
            self.assertEqual(imported_art["topic"], "Artikel Dump")

    def test_record_engagement_and_top_articles(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Populer",
            "category": "Trending",
            "publish_date": "2026-10-05",
            "focus_keyphrase": "artikel populer",
            "seo_title": "Artikel Populer",
            "slug": "artikel-populer",
            "meta_description": "Deskripsi populer.",
            "status": "published"
        })
        eng = self.storage.record_engagement(art_id, views_increment=50, shares_increment=10)
        self.assertEqual(eng["view_count"], 50)
        self.assertEqual(eng["share_count"], 10)

        # Increment again
        eng2 = self.storage.record_engagement(art_id, views_increment=25, shares_increment=5)
        self.assertEqual(eng2["view_count"], 75)
        self.assertEqual(eng2["share_count"], 15)

        top = self.storage.get_top_engaged_articles(limit=5)
        self.assertTrue(any(a["article_id"] == art_id for a in top))

if __name__ == "__main__":
    unittest.main()


