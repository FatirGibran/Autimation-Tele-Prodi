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

    def test_category_hierarchy_and_tree(self):
        root_id = self.storage.add_category("Ilmu Komputer", "ilmu-komputer", description="Kategori utama")
        self.assertIsNotNone(root_id)
        child_id = self.storage.add_category("Kecerdasan Buatan", "ai", parent_id=root_id)
        self.assertIsNotNone(child_id)

        tree = self.storage.get_category_tree()
        self.assertTrue(any(c["slug"] == "ilmu-komputer" for c in tree))
        root_node = next(c for c in tree if c["slug"] == "ilmu-komputer")
        self.assertEqual(len(root_node["children"]), 1)
        self.assertEqual(root_node["children"][0]["slug"], "ai")

        cat = self.storage.get_category_by_slug("ai")
        self.assertIsNotNone(cat)
        self.assertEqual(cat["name"], "Kecerdasan Buatan")

    def test_article_locks_acquire_and_release(self):
        art_id = self.storage.save_article({
            "topic": "Artikel Lock",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "artikel lock",
            "seo_title": "Artikel Lock",
            "slug": "artikel-lock",
            "meta_description": "Deskripsi lock.",
            "status": "draft"
        })
        # User 1 acquires lock
        ok1, blocker1 = self.storage.acquire_article_lock(art_id, user_id="editor_1", ttl_seconds=60)
        self.assertTrue(ok1)
        self.assertIsNone(blocker1)

        # User 2 tries to acquire -> blocked
        ok2, blocker2 = self.storage.acquire_article_lock(art_id, user_id="editor_2", ttl_seconds=60)
        self.assertFalse(ok2)
        self.assertEqual(blocker2, "editor_1")

        # User 1 refreshes lock -> ok
        ok1_refresh, _ = self.storage.acquire_article_lock(art_id, user_id="editor_1", ttl_seconds=120)
        self.assertTrue(ok1_refresh)

        # Status check
        status = self.storage.get_article_lock_status(art_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["locked_by"], "editor_1")

        # Release lock
        self.assertTrue(self.storage.release_article_lock(art_id, user_id="editor_1"))
        self.assertIsNone(self.storage.get_article_lock_status(art_id))

        # Now User 2 can acquire
        ok2_after, _ = self.storage.acquire_article_lock(art_id, user_id="editor_2", ttl_seconds=60)
        self.assertTrue(ok2_after)

    def test_batch_replace_content(self):
        art_id1 = self.storage.save_article({
            "topic": "Batch 1",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "batch test",
            "seo_title": "Judul lama v1",
            "slug": "batch-1",
            "meta_description": "Deskripsi lama.",
            "html_content": "<p>Teks lama di dalam artikel 1.</p>",
            "status": "draft"
        })
        art_id2 = self.storage.save_article({
            "topic": "Batch 2",
            "category": "Testing",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "batch test",
            "seo_title": "Judul Lain",
            "slug": "batch-2",
            "meta_description": "Deskripsi lama juga.",
            "html_content": "<p>Teks lama di dalam artikel 2.</p>",
            "status": "draft"
        })

        res = self.storage.batch_replace_content("lama", "baru", status_filter="draft")
        self.assertEqual(res["articles_updated"], 2)
        self.assertGreaterEqual(res["total_replacements"], 4)

        updated1 = self.storage.get_article_by_slug("batch-1")
        self.assertIn("Judul baru v1", updated1["seo_title"])
        self.assertIn("Deskripsi baru.", updated1["meta_description"])
        self.assertIn("Teks baru di dalam", updated1["html_content"])

    def test_get_category_analytics(self):
        self.storage.save_article({
            "topic": "Analytics 1",
            "category": "Akademik",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "analytics satu",
            "seo_title": "Analytics 1",
            "slug": "analytics-1",
            "meta_description": "Deskripsi.",
            "status": "published"
        })
        self.storage.save_article({
            "topic": "Analytics 2",
            "category": "Riset",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "analytics dua",
            "seo_title": "Analytics 2",
            "slug": "analytics-2",
            "meta_description": "Deskripsi.",
            "status": "published"
        })
        stats = self.storage.get_category_analytics()
        cats = [s["category"] for s in stats]
        self.assertIn("Akademik", cats)
        self.assertIn("Riset", cats)

    def test_article_bookmarks_crud(self):
        art_id = self.storage.save_article({
            "topic": "Bookmark Target",
            "category": "Mahasiswa",
            "publish_date": "2026-10-06",
            "focus_keyphrase": "bookmark target",
            "seo_title": "Bookmark Target",
            "slug": "bookmark-target",
            "meta_description": "Deskripsi bookmark.",
            "status": "published"
        })
        self.storage.add_bookmark(art_id, "user_alpha", notes="Penting untuk skripsi")
        bms = self.storage.list_bookmarks("user_alpha")
        self.assertEqual(len(bms), 1)
        self.assertEqual(bms[0]["article_id"], art_id)
        self.assertEqual(bms[0]["notes"], "Penting untuk skripsi")

        removed = self.storage.remove_bookmark(art_id, "user_alpha")
        self.assertTrue(removed)
        self.assertEqual(len(self.storage.list_bookmarks("user_alpha")), 0)

    def test_schema_migrations_tracking(self):
        self.storage.record_migration("v2.5.0")
        self.storage.record_migration("v2.5.1")
        applied = self.storage.get_applied_migrations()
        self.assertIn("v2.5.0", applied)
        self.assertIn("v2.5.1", applied)

    def test_article_reading_metrics(self):
        art_id = self.storage.save_article({
            "topic": "Reading Time Test",
            "category": "Akademik",
            "publish_date": "2026-10-07",
            "focus_keyphrase": "reading time",
            "seo_title": "Reading Time Test",
            "slug": "reading-time-test",
            "meta_description": "Deskripsi reading time.",
            "status": "draft"
        })
        self.storage.update_reading_metrics(art_id, word_count=850, reading_time_min=4)
        metrics = self.storage.get_reading_metrics(art_id)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics["word_count"], 850)
        self.assertEqual(metrics["reading_time_min"], 4)

        # Upsert
        self.storage.update_reading_metrics(art_id, word_count=1200, reading_time_min=6)
        updated = self.storage.get_reading_metrics(art_id)
        self.assertEqual(updated["word_count"], 1200)
        self.assertEqual(updated["reading_time_min"], 6)

    def test_editorial_subscribers_manager(self):
        # Subscribe users
        self.assertTrue(self.storage.subscribe_user("user_1", "telegram", "akademik"))
        self.assertTrue(self.storage.subscribe_user("user_2", "telegram", "all"))
        self.assertTrue(self.storage.subscribe_user("user_3", "email", "riset"))

        # Query all
        all_subs = self.storage.get_subscribers("all")
        self.assertEqual(len(all_subs), 3)

        # Query specific category
        akademik_subs = self.storage.get_subscribers("akademik")
        # Should include user_1 (akademik) and user_2 (all)
        user_ids = [s["user_id"] for s in akademik_subs]
        self.assertIn("user_1", user_ids)
        self.assertIn("user_2", user_ids)
        self.assertNotIn("user_3", user_ids)

        # Unsubscribe
        self.assertTrue(self.storage.unsubscribe_user("user_1", "akademik"))
        akademik_subs_after = self.storage.get_subscribers("akademik")
        self.assertNotIn("user_1", [s["user_id"] for s in akademik_subs_after])

    def test_compare_revisions(self):
        art_id = self.storage.save_article({
            "topic": "Diff Test",
            "category": "Akademik",
            "publish_date": "2026-10-07",
            "focus_keyphrase": "diff test",
            "seo_title": "Diff Test",
            "slug": "diff-test",
            "meta_description": "Versi awal meta.",
            "html_content": "<p>Satu dua tiga empat.</p>",
            "status": "draft"
        })
        rev1 = self.storage.create_revision(art_id)
        # Update article content and make rev 2
        with self.storage._get_connection() as conn:
            conn.execute(
                "UPDATE articles SET html_content = ?, meta_description = ? WHERE id = ?",
                ("<p>Satu dua tiga empat lima enam tujuh delapan sembilan sepuluh.</p>", "Versi kedua meta diperbarui.", art_id)
            )
        rev2 = self.storage.create_revision(art_id)

        diff = self.storage.compare_revisions(art_id, 1, 2)
        self.assertTrue(diff["found"])
        self.assertEqual(diff["rev_a"]["revision_num"], 1)
        self.assertEqual(diff["rev_b"]["revision_num"], 2)
        self.assertGreater(diff["deltas"]["word_diff"], 0)
        self.assertTrue(diff["deltas"]["meta_changed"])

        # Not found case
        not_found = self.storage.compare_revisions(art_id, 1, 99)
        self.assertFalse(not_found["found"])

    def test_record_article_view_and_time_series(self):
        art_id = self.storage.save_article({
            "topic": "View Tracking Test",
            "category": "Akademik",
            "publish_date": "2026-10-08",
            "focus_keyphrase": "view tracking",
            "seo_title": "View Tracking Test",
            "slug": "view-tracking-test",
            "meta_description": "Deskripsi view tracking.",
            "status": "published"
        })
        log_id1 = self.storage.record_article_view(art_id, referrer="https://google.com", user_agent_hash="abc123hash")
        log_id2 = self.storage.record_article_view(art_id, referrer="https://t.me", user_agent_hash="def456hash")
        self.assertGreater(log_id1, 0)
        self.assertGreater(log_id2, log_id1)

        # Verify time-series retrieval
        stats = self.storage.get_article_views_by_date(art_id, days=7)
        self.assertGreaterEqual(len(stats), 1)
        total_views = sum(s["views"] for s in stats)
        self.assertEqual(total_views, 2)

    def test_editorial_tasks_crud_and_status(self):
        art_id = self.storage.save_article({
            "topic": "Task Article",
            "category": "Riset",
            "publish_date": "2026-10-08",
            "focus_keyphrase": "task article",
            "seo_title": "Task Article",
            "slug": "task-article",
            "meta_description": "Deskripsi task.",
            "status": "draft"
        })
        task_id = self.storage.create_editorial_task(
            article_id=art_id,
            assignee="fatir",
            task_type="proofreading",
            due_date="2026-10-15"
        )
        self.assertGreater(task_id, 0)

        tasks = self.storage.list_editorial_tasks(status="pending")
        self.assertTrue(any(t["id"] == task_id for t in tasks))

        # Update status
        updated = self.storage.update_task_status(task_id, "completed")
        self.assertTrue(updated)

        pending_tasks = self.storage.list_editorial_tasks(status="pending")
        self.assertFalse(any(t["id"] == task_id for t in pending_tasks))

        all_tasks = self.storage.list_editorial_tasks(status="all")
        self.assertTrue(any(t["id"] == task_id and t["status"] == "completed" for t in all_tasks))

    def test_taxonomy_meta_crud(self):
        self.storage.set_taxonomy_meta("category", "akademik", "featured_color", "#1E88E5")
        self.storage.set_taxonomy_meta("category", "akademik", "banner_url", "https://cdn.example.com/banner.jpg")

        meta = self.storage.get_taxonomy_meta("category", "akademik")
        self.assertEqual(meta.get("featured_color"), "#1E88E5")
        self.assertEqual(meta.get("banner_url"), "https://cdn.example.com/banner.jpg")

        # Update existing
        self.storage.set_taxonomy_meta("category", "akademik", "featured_color", "#D32F2F")
        updated_meta = self.storage.get_taxonomy_meta("category", "akademik")
        self.assertEqual(updated_meta.get("featured_color"), "#D32F2F")

        # Delete key
        deleted = self.storage.delete_taxonomy_meta("category", "akademik", "featured_color")
        self.assertTrue(deleted)
        after_delete = self.storage.get_taxonomy_meta("category", "akademik")
        self.assertNotIn("featured_color", after_delete)
        self.assertIn("banner_url", after_delete)

    def test_article_editorial_notes(self):
        art_id = self.storage.save_article({
            "topic": "Collab Test",
            "category": "Riset",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "collab note",
            "seo_title": "Collab Note Test",
            "slug": "collab-note-test",
            "meta_description": "Deskripsi catatan kolaborasi.",
            "status": "draft"
        })
        n1 = self.storage.add_editorial_note(art_id, "editor_chief", "Perlu tambahkan kutipan IEEE terbaru.")
        n2 = self.storage.add_editorial_note(art_id, "peer_reviewer", "Format gambar sudah rapi dan jelas.")
        self.assertGreater(n1, 0)
        self.assertGreater(n2, 0)

        notes = self.storage.list_editorial_notes(art_id)
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["author"], "editor_chief")
        self.assertEqual(notes[1]["author"], "peer_reviewer")

        # Delete note 1
        self.assertTrue(self.storage.delete_editorial_note(n1))
        remaining = self.storage.list_editorial_notes(art_id)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], n2)

    def test_publishing_webhook_logs(self):
        log_id = self.storage.log_webhook_dispatch(
            event="article_published",
            target_url="https://webhook.telkomuniversity.ac.id/notify",
            status_code=200,
            payload_snippet='{"slug": "5g-antenna", "title": "5G Antenna"}'
        )
        self.assertGreater(log_id, 0)

        logs = self.storage.get_recent_webhook_logs(limit=5)
        self.assertTrue(any(l["id"] == log_id for l in logs))
        target_log = next(l for l in logs if l["id"] == log_id)
        self.assertEqual(target_log["event"], "article_published")
        self.assertEqual(target_log["status_code"], 200)
        self.assertIn("5g-antenna", target_log["payload_snippet"])

    def test_taxonomy_synonyms_resolution(self):
        self.assertTrue(self.storage.add_taxonomy_synonym("kecerdasan buatan", "artificial intelligence"))
        self.assertTrue(self.storage.add_taxonomy_synonym("kecerdasan buatan", "ai"))
        self.assertTrue(self.storage.add_taxonomy_synonym("jaringan nirkabel", "wireless network"))

        # Resolve known aliases
        self.assertEqual(self.storage.resolve_canonical_term("artificial intelligence"), "kecerdasan buatan")
        self.assertEqual(self.storage.resolve_canonical_term("ai"), "kecerdasan buatan")
        self.assertEqual(self.storage.resolve_canonical_term("wireless network"), "jaringan nirkabel")

        # Unregistered alias resolves to itself
        self.assertEqual(self.storage.resolve_canonical_term("cloud computing"), "cloud computing")

        # List synonyms
        synonyms = self.storage.list_taxonomy_synonyms()
        self.assertGreaterEqual(len(synonyms), 3)

    def test_article_reviewer_assignments(self):
        art_id = self.storage.save_article({
            "topic": "Reviewer Test",
            "category": "Akademik",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "rev test",
            "seo_title": "Reviewer Test",
            "slug": "reviewer-test",
            "meta_description": "Meta desc",
            "html_content": "<p>Content</p>",
            "status": "draft"
        })
        rev_id = self.storage.assign_article_reviewer(art_id, "Dr. Ir. Budi Raharjo", "budi@telkomuniversity.ac.id")
        self.assertGreater(rev_id, 0)

        reviewers = self.storage.list_article_reviewers(art_id)
        self.assertEqual(len(reviewers), 1)
        self.assertEqual(reviewers[0]["reviewer_name"], "Dr. Ir. Budi Raharjo")
        self.assertEqual(reviewers[0]["status"], "assigned")

        # Update status
        self.assertTrue(self.storage.update_reviewer_status(rev_id, "accepted"))
        updated_reviewers = self.storage.list_article_reviewers(art_id)
        self.assertEqual(updated_reviewers[0]["status"], "accepted")

    def test_article_syndication_logs(self):
        art_id = self.storage.save_article({
            "topic": "Syndication Test",
            "category": "Riset",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "synd test",
            "seo_title": "Syndication Test",
            "slug": "syndication-test",
            "meta_description": "Meta desc",
            "html_content": "<p>Content</p>",
            "status": "published"
        })
        log_id = self.storage.record_syndication_log(art_id, "Medium", "https://medium.com/@telkom/synd-test")
        self.assertGreater(log_id, 0)

        logs = self.storage.get_syndication_logs(art_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["platform"], "Medium")
        self.assertEqual(logs[0]["external_url"], "https://medium.com/@telkom/synd-test")

    def test_editorial_workflow_checklists(self):
        art_id = self.storage.save_article({
            "topic": "Checklist Test",
            "category": "Akademik",
            "publish_date": "2026-10-10",
            "focus_keyphrase": "chk test",
            "seo_title": "Checklist Test",
            "slug": "checklist-test",
            "meta_description": "Meta desc",
            "html_content": "<p>Content</p>",
            "status": "draft"
        })
        # Set items
        self.assertTrue(self.storage.set_checklist_item(art_id, "plagiarism_check", "Cek Turnitin < 15%", True, "Editor A"))
        self.assertTrue(self.storage.set_checklist_item(art_id, "fact_check", "Verifikasi Data & Referensi", False))

        status = self.storage.get_checklist_status(art_id)
        self.assertEqual(len(status), 2)
        plag_item = next(i for i in status if i["item_key"] == "plagiarism_check")
        fact_item = next(i for i in status if i["item_key"] == "fact_check")
        self.assertTrue(plag_item["is_checked"])
        self.assertEqual(plag_item["checked_by"], "Editor A")
        self.assertFalse(fact_item["is_checked"])

        # Update item
        self.assertTrue(self.storage.set_checklist_item(art_id, "fact_check", "Verifikasi Data & Referensi", True, "Editor B"))
        status2 = self.storage.get_checklist_status(art_id)
        fact_item2 = next(i for i in status2 if i["item_key"] == "fact_check")
        self.assertTrue(fact_item2["is_checked"])
        self.assertEqual(fact_item2["checked_by"], "Editor B")

    def test_article_academic_citations_tracker(self):
        art_id = self.storage.save_article({
            "topic": "Citations Test",
            "category": "Akademik",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "citations test",
            "seo_title": "Citations Test",
            "slug": "citations-test",
            "meta_description": "Meta desc",
            "status": "published"
        })
        cite_id1 = self.storage.record_article_citation(
            article_id=art_id,
            citing_paper_title="MIMO Beamforming Strategies in 6G",
            citing_authors="Alice Smith, Bob Jones",
            journal_name="IEEE Transactions on Communications",
            citation_year=2025,
            doi="10.1109/TCOMM.2025.1001"
        )
        cite_id2 = self.storage.record_article_citation(
            article_id=art_id,
            citing_paper_title="Optical Wireless Integration Survey",
            citing_authors="Carol Lee",
            journal_name="ACM Computing Surveys",
            citation_year=2026,
            doi="10.1145/3600000"
        )
        self.assertGreater(cite_id1, 0)
        self.assertGreater(cite_id2, 0)

        citations = self.storage.get_article_citations(art_id)
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0]["citation_year"], 2026)
        self.assertEqual(citations[0]["journal_name"], "ACM Computing Surveys")
        self.assertEqual(citations[1]["citation_year"], 2025)

    def test_editorial_review_comments_manager(self):
        art_id = self.storage.save_article({
            "topic": "Comments Test",
            "category": "Akademik",
            "publish_date": "2026-10-11",
            "focus_keyphrase": "comments test",
            "seo_title": "Comments Test",
            "slug": "comments-test",
            "meta_description": "Meta desc",
            "status": "draft"
        })
        c1 = self.storage.add_editorial_comment(art_id, author="Reviewer A", comment_text="Mohon perjelas metodologi", paragraph_index=2)
        c2 = self.storage.add_editorial_comment(art_id, author="Chief Editor", comment_text="Periksa format referensi IEEE", paragraph_index=None)
        self.assertGreater(c1, 0)
        self.assertGreater(c2, 0)

        all_comments = self.storage.list_editorial_comments(art_id, include_resolved=True)
        self.assertEqual(len(all_comments), 2)
        self.assertEqual(all_comments[0]["paragraph_index"], 2)
        self.assertEqual(all_comments[0]["is_resolved"], 0)

        resolved = self.storage.resolve_editorial_comment(c1)
        self.assertTrue(resolved)

        unresolved = self.storage.list_editorial_comments(art_id, include_resolved=False)
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["id"], c2)

    def test_content_snippets_library(self):
        sid1 = self.storage.save_content_snippet(
            snippet_key="callout_admission",
            snippet_title="Pendaftaran Mahasiswa Baru",
            snippet_html="<div class='callout'>Daftar segera di pmb.telkomuniversity.ac.id</div>",
            category="pmb"
        )
        self.assertGreater(sid1, 0)

        snippet = self.storage.get_content_snippet("callout_admission")
        self.assertIsNotNone(snippet)
        self.assertEqual(snippet["snippet_title"], "Pendaftaran Mahasiswa Baru")
        self.assertIn("pmb.telkomuniversity", snippet["snippet_html"])

        self.storage.save_content_snippet(
            snippet_key="callout_admission",
            snippet_title="Pendaftaran Jalur Beasiswa",
            snippet_html="<div class='callout'>Beasiswa Telkom University</div>",
            category="pmb"
        )
        updated = self.storage.get_content_snippet("callout_admission")
        self.assertEqual(updated["snippet_title"], "Pendaftaran Jalur Beasiswa")

        self.storage.save_content_snippet(
            snippet_key="disclaimer_lab",
            snippet_title="Prosedur Keselamatan Lab",
            snippet_html="<p>Wajib menggunakan jas lab.</p>",
            category="laboratorium"
        )

        all_snippets = self.storage.list_content_snippets()
        self.assertEqual(len(all_snippets), 2)

        pmb_snippets = self.storage.list_content_snippets(category="pmb")
        self.assertEqual(len(pmb_snippets), 1)
        self.assertEqual(pmb_snippets[0]["snippet_key"], "callout_admission")

    def test_competition_achievements_storage(self):
        aid1 = self.storage.record_competition_achievement(
            competition_name="Gemastik XVII",
            award_rank="Juara 1 Emas",
            team_name="Telematics-Purwokerto",
            team_members=["Fatir Gibran", "Budi Santoso"],
            supervisor="Dr. Ir. Wahyu, M.T.",
            year=2026,
            organizer="Puspresnas Kemendikbud"
        )
        aid2 = self.storage.record_competition_achievement(
            competition_name="Imagine Cup 2025",
            award_rank="Finalist",
            team_name="CloudPurwokerto",
            team_members=["Rina"],
            supervisor="Ahmad, M.Kom.",
            year=2025,
            organizer="Microsoft"
        )
        self.assertGreater(aid1, 0)
        self.assertGreater(aid2, 0)

        all_ach = self.storage.list_competition_achievements()
        self.assertEqual(len(all_ach), 2)

        ach_2026 = self.storage.list_competition_achievements(year=2026)
        self.assertEqual(len(ach_2026), 1)
        self.assertEqual(ach_2026[0]["team_name"], "Telematics-Purwokerto")
        self.assertIn("Fatir Gibran", ach_2026[0]["team_members"])

    def test_journal_indexings_storage(self):
        jid1 = self.storage.record_journal_indexing(
            journal_name="Jurnal Telematika Purwokerto",
            sinta_rank=2,
            issn="2798-1111",
            publisher="Telkom University Press",
            focus_scope="Telekomunikasi & Jaringan",
            archive_url="https://journal.telkomuniversity.ac.id/jtp"
        )
        jid2 = self.storage.record_journal_indexing(
            journal_name="Jurnal Sistem Cerdas",
            sinta_rank=4,
            issn="2655-2222",
            publisher="Fakultas Informatika",
            focus_scope="AI & Data Science"
        )
        self.assertGreater(jid1, 0)
        self.assertGreater(jid2, 0)

        all_journals = self.storage.list_journal_indexings()
        self.assertEqual(len(all_journals), 2)

        top_journals = self.storage.list_journal_indexings(min_sinta=2)
        self.assertEqual(len(top_journals), 1)
        self.assertEqual(top_journals[0]["journal_name"], "Jurnal Telematika Purwokerto")
        self.assertEqual(top_journals[0]["sinta_rank"], 2)

    def test_lab_safety_inspections_storage(self):
        sid1 = self.storage.record_safety_inspection(
            lab_name="Lab Jaringan Komputer",
            inspector="Agus Supriyanto, S.T.",
            inspection_date="2026-10-12",
            compliance_score=95.0,
            is_passed=True,
            notes="APAR dan P3K lengkap"
        )
        sid2 = self.storage.record_safety_inspection(
            lab_name="Lab Rekayasa Perangkat Lunak",
            inspector="Bambang K3",
            inspection_date="2026-10-13",
            compliance_score=60.0,
            is_passed=False,
            notes="APAR expired"
        )
        self.assertGreater(sid1, 0)
        self.assertGreater(sid2, 0)

        all_inspections = self.storage.list_safety_inspections()
        self.assertEqual(len(all_inspections), 2)

        lab_net = self.storage.list_safety_inspections(lab_name="Lab Jaringan Komputer")
        self.assertEqual(len(lab_net), 1)
        self.assertTrue(bool(lab_net[0]["is_passed"]))
        self.assertEqual(lab_net[0]["compliance_score"], 95.0)

    def test_mbkm_credit_transfers_storage(self):
        courses1 = [
            {"course_code": "IF3101", "course_name": "Cloud Computing", "sks": 4, "score_letter": "A"}
        ]
        mid1 = self.storage.record_mbkm_credit_transfer(
            program_name="Bangkit 2026",
            partner_institution="Google",
            student_name="Fatir Gibran",
            nim="120122001",
            semester=6,
            total_sks=4,
            converted_gpa=4.00,
            courses=courses1,
            sk_number="SK-001"
        )
        mid2 = self.storage.record_mbkm_credit_transfer(
            program_name="MSIB Magang Mandiri",
            partner_institution="Telkom",
            student_name="Budi Santoso",
            nim="120122002",
            semester=6,
            total_sks=20,
            converted_gpa=3.75,
            courses=[]
        )
        self.assertGreater(mid1, 0)
        self.assertGreater(mid2, 0)

        all_transfers = self.storage.list_mbkm_credit_transfers()
        self.assertEqual(len(all_transfers), 2)

        fatir_transfers = self.storage.list_mbkm_credit_transfers(nim="120122001")
        self.assertEqual(len(fatir_transfers), 1)
        self.assertEqual(fatir_transfers[0]["student_name"], "Fatir Gibran")
        self.assertEqual(fatir_transfers[0]["total_sks"], 4)
        self.assertEqual(len(fatir_transfers[0]["courses"]), 1)
        self.assertEqual(fatir_transfers[0]["courses"][0]["course_code"], "IF3101")

    def test_yudisium_clearances_storage(self):
        yid1 = self.storage.record_yudisium_clearance(
            student_name="Fatir Gibran",
            nim="120122001",
            thesis_title="Sistem Otomasi Portal Editorial",
            ipk=3.85,
            earned_sks=146,
            graduation_predicate="Dengan Pujian (Cum Laude)",
            yudisium_date="2026-10-20",
            verification_code="YUD-001"
        )
        yid2 = self.storage.record_yudisium_clearance(
            student_name="Rina Wulandari",
            nim="120122003",
            thesis_title="Optimasi Jaringan 5G",
            ipk=3.45,
            earned_sks=144,
            graduation_predicate="Sangat Memuaskan",
            yudisium_date="2026-10-20",
            verification_code="YUD-002"
        )
        self.assertGreater(yid1, 0)
        self.assertGreater(yid2, 0)

        all_yud = self.storage.list_yudisium_clearances()
        self.assertEqual(len(all_yud), 2)

        cum_laude = self.storage.list_yudisium_clearances(predicate="Dengan Pujian (Cum Laude)")
        self.assertEqual(len(cum_laude), 1)
        self.assertEqual(cum_laude[0]["student_name"], "Fatir Gibran")

        single = self.storage.get_yudisium_clearance_by_nim("120122001")
        self.assertIsNotNone(single)
        self.assertEqual(single["verification_code"], "YUD-001")
        self.assertEqual(single["ipk"], 3.85)

    def test_lab_equipment_calibrations_storage(self):
        cid1 = self.storage.record_equipment_calibration(
            asset_id="LAB-RF-001",
            equipment_name="Spectrum Analyzer",
            lab_name="Lab RF & Antena",
            calibration_date="2026-01-10",
            due_date="2027-01-10",
            calibration_status="Valid",
            operating_condition="Baik",
            technician_name="Ahmad Laboran",
            notes="Kalibrasi certified"
        )
        cid2 = self.storage.record_equipment_calibration(
            asset_id="LAB-NET-002",
            equipment_name="Cisco Switch",
            lab_name="Lab Jaringan Komputer",
            calibration_date="2024-01-10",
            due_date="2025-01-10",
            calibration_status="Expired",
            operating_condition="Baik",
            technician_name="Budi Teknisi"
        )
        self.assertGreater(cid1, 0)
        self.assertGreater(cid2, 0)

        all_cals = self.storage.list_equipment_calibrations()
        self.assertEqual(len(all_cals), 2)

        rf_cals = self.storage.list_equipment_calibrations(lab_name="Lab RF & Antena")
        self.assertEqual(len(rf_cals), 1)
        self.assertEqual(rf_cals[0]["asset_id"], "LAB-RF-001")

        valid_cals = self.storage.list_equipment_calibrations(status="Valid")
        self.assertEqual(len(valid_cals), 1)
        self.assertEqual(valid_cals[0]["calibration_status"], "Valid")

if __name__ == "__main__":
    unittest.main()






