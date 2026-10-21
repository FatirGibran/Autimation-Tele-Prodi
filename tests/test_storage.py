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

    def test_kkn_village_projects_crud(self):
        pid1 = self.storage.record_kkn_project(
            group_code="KKN-TM-01",
            village_name="Cibodas",
            district_name="Pasirjambu",
            regency_name="Bandung",
            supervisor_dpl="Dr. Ir. Ahmad",
            student_count=12,
            thematic_focus="Desa Cerdas",
            flagship_program="IoT Pertanian"
        )
        pid2 = self.storage.record_kkn_project(
            group_code="KKN-TM-02",
            village_name="Lembang",
            district_name="Lembang",
            regency_name="Bandung Barat",
            supervisor_dpl="Dr. Siti",
            student_count=10,
            thematic_focus="Pemberdayaan UMKM",
            flagship_program="Marketplace Desa"
        )
        self.assertGreater(pid1, 0)
        self.assertGreater(pid2, 0)

        all_projects = self.storage.list_kkn_projects()
        self.assertEqual(len(all_projects), 2)

        bandung_projects = self.storage.list_kkn_projects(regency_name="Bandung")
        self.assertEqual(len(bandung_projects), 1)
        self.assertEqual(bandung_projects[0]["group_code"], "KKN-TM-01")

        project = self.storage.get_kkn_project_by_id(pid1)
        self.assertIsNotNone(project)
        self.assertEqual(project["village_name"], "Cibodas")
        self.assertEqual(project["student_count"], 12)

    def test_faculty_bkd_records_crud(self):
        bid1 = self.storage.record_faculty_bkd(
            lecturer_name="Dr. Ir. Hendra",
            nidn="0412345601",
            academic_rank="Lektor Kepala",
            semester="2025/2026 Ganjil",
            teaching_credits=6.0,
            research_credits=4.0,
            service_credits=2.0,
            supporting_credits=1.0,
            total_sks=13.0,
            is_compliant=True
        )
        bid2 = self.storage.record_faculty_bkd(
            lecturer_name="Dr. Ir. Hendra",
            nidn="0412345601",
            academic_rank="Lektor Kepala",
            semester="2025/2026 Genap",
            teaching_credits=4.0,
            research_credits=3.0,
            service_credits=1.0,
            supporting_credits=0.5,
            total_sks=8.5,
            is_compliant=False
        )
        self.assertGreater(bid1, 0)
        self.assertGreater(bid2, 0)

        ganjil_records = self.storage.list_faculty_bkd_records(semester="2025/2026 Ganjil")
        self.assertEqual(len(ganjil_records), 1)
        self.assertTrue(ganjil_records[0]["is_compliant"])

        hendra_records = self.storage.get_faculty_bkd_by_nidn("0412345601")
        self.assertEqual(len(hendra_records), 2)

    def test_conference_presentations_crud(self):
        cid1 = self.storage.record_conference_presentation(
            paper_title="Deep Learning for 6G Telemetry",
            authors="Fatir Gibran, Bayu Pratama",
            conference_name="IEEE International Conference on Communications",
            acronym="ICC 2026",
            core_tier="A",
            publisher="IEEE Xplore",
            year=2026,
            city="Montreal, Canada",
            paper_url="https://doi.org/10.1109/ICC.2026.1"
        )
        cid2 = self.storage.record_conference_presentation(
            paper_title="IoT Protocol Optimization in Campus Network",
            authors="Siti Rahma, Dr. Ahmad",
            conference_name="International Conference on Networking and Services",
            acronym="ICNS 2025",
            core_tier="B",
            publisher="Springer",
            year=2025,
            city="Berlin, Germany"
        )
        self.assertGreater(cid1, 0)
        self.assertGreater(cid2, 0)

        all_confs = self.storage.list_conference_presentations()
        self.assertEqual(len(all_confs), 2)

        tier_a = self.storage.list_conference_presentations(core_tier="A")
        self.assertEqual(len(tier_a), 1)
        self.assertEqual(tier_a[0]["acronym"], "ICC 2026")

        conf_2025 = self.storage.list_conference_presentations(year=2025)
        self.assertEqual(len(conf_2025), 1)
        self.assertEqual(conf_2025[0]["city"], "Berlin, Germany")

    def test_bima_grant_proposals_storage(self):
        gid1 = self.storage.record_bima_grant(
            project_title="Optimasi Jaringan 5G untuk IoT Maritim",
            lead_researcher="Dr. Ir. Budi Santoso, M.T.",
            lead_nidn="0012057801",
            scheme_name="Penelitian Terapan Unggulan Perguruan Tinggi",
            requested_budget=150000000.0,
            approved_budget=125000000.0,
            fiscal_year=2026,
            proposal_status="approved",
            contract_number="124/E5/PG.02.00.PT/2026"
        )
        gid2 = self.storage.record_bima_grant(
            project_title="Machine Learning untuk Deteksi Anomali Jaringan Kampus",
            lead_researcher="Siti Rahma, S.T., M.Kom.",
            lead_nidn="0023088502",
            scheme_name="Penelitian Dosen Pemula",
            requested_budget=25000000.0,
            approved_budget=20000000.0,
            fiscal_year=2025,
            proposal_status="completed"
        )
        self.assertGreater(gid1, 0)
        self.assertGreater(gid2, 0)

        all_grants = self.storage.list_bima_grants()
        self.assertEqual(len(all_grants), 2)

        grants_2026 = self.storage.list_bima_grants(fiscal_year=2026)
        self.assertEqual(len(grants_2026), 1)
        self.assertEqual(grants_2026[0]["lead_nidn"], "0012057801")

        approved_grants = self.storage.list_bima_grants(status="approved")
        self.assertEqual(len(approved_grants), 1)
        self.assertEqual(approved_grants[0]["id"], gid1)

        single = self.storage.get_bima_grant_by_id(gid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["contract_number"], "124/E5/PG.02.00.PT/2026")

        none_grant = self.storage.get_bima_grant_by_id(999999)
        self.assertIsNone(none_grant)

    def test_kerja_praktik_placements_storage(self):
        kpid1 = self.storage.record_kp_placement(
            student_name="Bayu Pratama",
            nim="120120001",
            company_name="PT Telkom Indonesia",
            industry_sector="Telekomunikasi Seluler & Fiber",
            duration_weeks=8,
            project_title="Monitoring Core Network OLT GPON",
            company_mentor="Ir. Hendra Wijaya",
            placement_status="active"
        )
        kpid2 = self.storage.record_kp_placement(
            student_name="Bayu Pratama",
            nim="120120001",
            company_name="Huawei Tech Investment",
            industry_sector="Vendor Telekomunikasi",
            duration_weeks=12,
            project_title="Deployment RAN 5G Sub-6",
            placement_status="completed"
        )
        self.assertGreater(kpid1, 0)
        self.assertGreater(kpid2, 0)

        all_kp = self.storage.list_kp_placements()
        self.assertEqual(len(all_kp), 2)

        active_kp = self.storage.list_kp_placements(placement_status="active")
        self.assertEqual(len(active_kp), 1)
        self.assertEqual(active_kp[0]["company_name"], "PT Telkom Indonesia")

        telkom_kp = self.storage.list_kp_placements(company_name="PT Telkom Indonesia")
        self.assertEqual(len(telkom_kp), 1)

        by_nim = self.storage.get_kp_placement_by_nim("120120001")
        self.assertEqual(len(by_nim), 2)

        empty_nim = self.storage.get_kp_placement_by_nim("99999999")
        self.assertEqual(len(empty_nim), 0)

    def test_lab_spectrum_allocations_storage(self):
        aid1 = self.storage.record_spectrum_allocation(
            lab_name="Lab Transmisi Frekuensi Radio",
            center_frequency_mhz=2450.0,
            bandwidth_mhz=20.0,
            transmit_power_dbm=20.0,
            band_designation="S-Band ISM",
            license_number="ISR-2026-RF-0091",
            valid_until="2027-12-31",
            is_active=True
        )
        aid2 = self.storage.record_spectrum_allocation(
            lab_name="Lab Jaringan Nirkabel",
            center_frequency_mhz=5800.0,
            bandwidth_mhz=40.0,
            transmit_power_dbm=23.0,
            band_designation="C-Band ISM",
            is_active=False
        )
        self.assertGreater(aid1, 0)
        self.assertGreater(aid2, 0)

        all_allocs = self.storage.list_spectrum_allocations()
        self.assertEqual(len(all_allocs), 2)

        active_allocs = self.storage.list_spectrum_allocations(is_active=True)
        self.assertEqual(len(active_allocs), 1)
        self.assertEqual(active_allocs[0]["center_frequency_mhz"], 2450.0)

        inactive_allocs = self.storage.list_spectrum_allocations(is_active=False)
        self.assertEqual(len(inactive_allocs), 1)

        rf_allocs = self.storage.list_spectrum_allocations(lab_name="Lab Transmisi Frekuensi Radio")
        self.assertEqual(len(rf_allocs), 1)

        single = self.storage.get_spectrum_allocation_by_id(aid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["license_number"], "ISR-2026-RF-0091")

        none_alloc = self.storage.get_spectrum_allocation_by_id(999999)
        self.assertIsNone(none_alloc)

    def test_study_program_accreditations_storage(self):
        aid1 = self.storage.record_accreditation(
            program_name="S1 Teknik Telekomunikasi",
            agency="LAM INFOKOM",
            rating="Unggul",
            sk_number="042/SK/LAM-INFOKOM/Ak/S/XII/2025",
            expiry_date="2030-12-01",
            issued_date="2025-12-01",
            is_active=True
        )
        aid2 = self.storage.record_accreditation(
            program_name="D3 Teknik Telekomunikasi",
            agency="BAN-PT",
            rating="Baik Sekali",
            sk_number="101/SK/BAN-PT/Ak/D3/2021",
            expiry_date="2026-01-01",
            issued_date="2021-01-01",
            is_active=False
        )
        self.assertGreater(aid1, 0)
        self.assertGreater(aid2, 0)

        all_acc = self.storage.list_accreditations()
        self.assertEqual(len(all_acc), 2)

        lam_acc = self.storage.list_accreditations(agency="LAM INFOKOM")
        self.assertEqual(len(lam_acc), 1)
        self.assertEqual(lam_acc[0]["rating"], "Unggul")

        active_acc = self.storage.list_accreditations(is_active=True)
        self.assertEqual(len(active_acc), 1)
        self.assertEqual(active_acc[0]["id"], aid1)

        single = self.storage.get_accreditation_by_id(aid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["sk_number"], "042/SK/LAM-INFOKOM/Ak/S/XII/2025")
        self.assertIsNone(self.storage.get_accreditation_by_id(999999))

    def test_student_scholarships_storage(self):
        sid1 = self.storage.record_scholarship(
            student_name="Ahmad Hidayat",
            nim="1101220001",
            scholarship_type="pemerintah",
            sponsor_name="Beasiswa KIP Kuliah Merdeka",
            amount=6000000.0,
            semester="Ganjil",
            academic_year="2026/2027",
            status="active"
        )
        sid2 = self.storage.record_scholarship(
            student_name="Ahmad Hidayat",
            nim="1101220001",
            scholarship_type="alumni",
            sponsor_name="Bantuan UKT Ikatan Alumni",
            amount=2500000.0,
            semester="Genap",
            academic_year="2026/2027",
            status="nominated"
        )
        sid3 = self.storage.record_scholarship(
            student_name="Dewi Sartika",
            nim="1101220002",
            scholarship_type="industri",
            sponsor_name="Beasiswa Industri Telco",
            amount=10000000.0,
            semester="Ganjil",
            academic_year="2026/2027",
            status="active"
        )
        self.assertGreater(sid1, 0)
        self.assertGreater(sid2, 0)
        self.assertGreater(sid3, 0)

        all_schol = self.storage.list_scholarships()
        self.assertEqual(len(all_schol), 3)

        awarded = self.storage.list_scholarships(status="active")
        self.assertEqual(len(awarded), 2)

        industri = self.storage.list_scholarships(scholarship_type="industri")
        self.assertEqual(len(industri), 1)
        self.assertEqual(industri[0]["student_name"], "Dewi Sartika")

        ahmad_schols = self.storage.get_scholarships_by_nim("1101220001")
        self.assertEqual(len(ahmad_schols), 2)

    def test_bnsp_certifications_storage(self):
        cid1 = self.storage.record_bnsp_certification(
            student_name="Budi Pratama",
            nim="1101220045",
            scheme_name="Teknisi Madya Fiber Optik",
            assessor_name="Ir. Joko Susanto, M.T.",
            cert_number="BNSP-TEL-2026-00451",
            issue_date="2026-06-15",
            valid_until="2029-06-15",
            is_competent=True
        )
        cid2 = self.storage.record_bnsp_certification(
            student_name="Siti Rahma",
            nim="1101220078",
            scheme_name="Perancang Jaringan Nirkabel",
            assessor_name="Dr. Hendra Gunawan, S.T.",
            cert_number="BNSP-TEL-2026-00452",
            issue_date="2026-06-15",
            valid_until="2029-06-15",
            is_competent=False
        )
        self.assertGreater(cid1, 0)
        self.assertGreater(cid2, 0)

        all_certs = self.storage.list_bnsp_certifications()
        self.assertEqual(len(all_certs), 2)

        competent = self.storage.list_bnsp_certifications(is_competent=True)
        self.assertEqual(len(competent), 1)
        self.assertEqual(competent[0]["student_name"], "Budi Pratama")

        fo_certs = self.storage.list_bnsp_certifications(scheme_name="Teknisi Madya Fiber Optik")
        self.assertEqual(len(fo_certs), 1)

        budi_certs = self.storage.get_bnsp_certification_by_nim("1101220045")
        self.assertEqual(len(budi_certs), 1)
        self.assertEqual(budi_certs[0]["cert_number"], "BNSP-TEL-2026-00451")

    def test_student_graduation_honors_storage(self):
        data1 = {
            "student_name": "Dewi Sartika",
            "nim": "120120005",
            "ipk": 3.92,
            "honor_predicate": "Dengan Pujian (Cum Laude)",
            "thesis_title": "Optimasi MIMO Beamforming 5G",
            "study_duration_semesters": 8,
            "graduation_year": 2026
        }
        data2 = {
            "student_name": "Bambang Pamungkas",
            "nim": "120120006",
            "ipk": 3.75,
            "honor_predicate": "Sangat Memuaskan",
            "thesis_title": "Analisis Quality of Service LoRaWAN",
            "study_duration_semesters": 8,
            "graduation_year": 2025
        }
        hid1 = self.storage.record_graduation_honor(data1)
        hid2 = self.storage.record_graduation_honor(data2)
        self.assertGreater(hid1, 0)
        self.assertGreater(hid2, 0)

        all_honors = self.storage.list_graduation_honors()
        self.assertEqual(len(all_honors), 2)

        honors_2026 = self.storage.list_graduation_honors(graduation_year=2026)
        self.assertEqual(len(honors_2026), 1)
        self.assertEqual(honors_2026[0]["student_name"], "Dewi Sartika")

        cum_laude = self.storage.list_graduation_honors(predicate_keyword="Cum Laude")
        self.assertEqual(len(cum_laude), 1)
        self.assertEqual(cum_laude[0]["nim"], "120120005")

        dewi = self.storage.get_graduation_honor_by_nim("120120005")
        self.assertIsNotNone(dewi)
        self.assertEqual(dewi["honor_predicate"], "Dengan Pujian (Cum Laude)")

    def test_tridharma_grants_storage(self):
        grant1 = {
            "lecturer_name": "Dr. Ir. Budi Santoso, M.T.",
            "nidn": "0612058001",
            "project_title": "Rancang Bangun Sensor Akustik Kelautan",
            "grant_amount": 25000000.0,
            "fiscal_year": 2026,
            "publication_target": "Jurnal SINTA 2",
            "status": "active"
        }
        grant2 = {
            "lecturer_name": "Dr. Ir. Budi Santoso, M.T.",
            "nidn": "0612058001",
            "project_title": "Antena Mikrostrip Patch Array 28 GHz",
            "grant_amount": 30000000.0,
            "fiscal_year": 2025,
            "publication_target": "IEEE Access",
            "status": "completed"
        }
        gid1 = self.storage.record_tridharma_grant(grant1)
        gid2 = self.storage.record_tridharma_grant(grant2)
        self.assertGreater(gid1, 0)
        self.assertGreater(gid2, 0)

        all_grants = self.storage.list_tridharma_grants()
        self.assertEqual(len(all_grants), 2)

        grants_2026 = self.storage.list_tridharma_grants(fiscal_year=2026)
        self.assertEqual(len(grants_2026), 1)
        self.assertEqual(grants_2026[0]["project_title"], "Rancang Bangun Sensor Akustik Kelautan")

        completed_grants = self.storage.list_tridharma_grants(status="completed")
        self.assertEqual(len(completed_grants), 1)

        budi_grants = self.storage.get_tridharma_grants_by_nidn("0612058001")
        self.assertEqual(len(budi_grants), 2)

    def test_iot_sensor_telemetry_storage(self):
        feed1 = {
            "node_id": "NODE-01",
            "sensor_type": "Temperature",
            "reading_value": 24.5,
            "unit": "°C",
            "battery_level": 95.0
        }
        feed2 = {
            "node_id": "NODE-01",
            "sensor_type": "Humidity",
            "reading_value": 60.2,
            "unit": "%",
            "battery_level": 94.8
        }
        feed3 = {
            "node_id": "NODE-02",
            "sensor_type": "CO2",
            "reading_value": 450.0,
            "unit": "ppm",
            "battery_level": 98.0
        }
        fid1 = self.storage.record_sensor_telemetry(feed1)
        fid2 = self.storage.record_sensor_telemetry(feed2)
        fid3 = self.storage.record_sensor_telemetry(feed3)
        self.assertGreater(fid1, 0)
        self.assertGreater(fid2, 0)
        self.assertGreater(fid3, 0)

        latest = self.storage.list_latest_sensor_telemetry(limit=2)
        self.assertEqual(len(latest), 2)

        node1_feeds = self.storage.get_sensor_telemetry_by_node("NODE-01")
        self.assertEqual(len(node1_feeds), 2)
        node2_feeds = self.storage.get_sensor_telemetry_by_node("NODE-02")
        self.assertEqual(len(node2_feeds), 1)
        self.assertEqual(node2_feeds[0]["sensor_type"], "CO2")

    def test_fast_track_students_storage(self):
        sid1 = self.storage.record_fast_track_student(
            student_name="Ahmad Zaki",
            nim="1101230045",
            ipk=3.85,
            completed_sks=124,
            toefl_score=530,
            masters_specialization="Telecommunications & IoT",
            status="Eligible"
        )
        sid2 = self.storage.record_fast_track_student(
            student_name="Rina Safitri",
            nim="1101230088",
            ipk=3.55,
            completed_sks=118,
            toefl_score=480,
            masters_specialization="Wireless Systems",
            status="Provisionally Eligible"
        )
        self.assertGreater(sid1, 0)
        self.assertGreater(sid2, 0)

        all_students = self.storage.list_fast_track_students()
        self.assertEqual(len(all_students), 2)
        self.assertEqual(all_students[0]["nim"], "1101230045")

        eligible_only = self.storage.list_fast_track_students(status="Eligible")
        self.assertEqual(len(eligible_only), 1)

        single = self.storage.get_fast_track_student_by_nim("1101230045")
        self.assertIsNotNone(single)
        self.assertEqual(single["student_name"], "Ahmad Zaki")
        self.assertAlmostEqual(single["ipk"], 3.85)

        missing = self.storage.get_fast_track_student_by_nim("9999999999")
        self.assertIsNone(missing)

    def test_lab_calibration_compliance_storage(self):
        cid1 = self.storage.record_lab_calibration_compliance(
            equipment_name="Rohde & Schwarz FSW Spectrum Analyzer",
            serial_number="RS-FSW-84920",
            lab_room="Lab Frekuensi Radio LT.3",
            last_calibration_date="2025-11-15",
            next_due_date="2026-11-15",
            calibration_status="Valid",
            cert_number="CAL/RS/2025/1109"
        )
        cid2 = self.storage.record_lab_calibration_compliance(
            equipment_name="Anritsu Site Master S331E",
            serial_number="ANR-S331E-1002",
            lab_room="Lab Antena & Propagasi",
            last_calibration_date="2024-05-10",
            next_due_date="2025-05-10",
            calibration_status="Expired",
            cert_number="CAL/ANR/2024/052"
        )
        self.assertGreater(cid1, 0)
        self.assertGreater(cid2, 0)

        all_cals = self.storage.list_lab_calibration_compliance()
        self.assertEqual(len(all_cals), 2)

        valid_cals = self.storage.list_lab_calibration_compliance(status="Valid")
        self.assertEqual(len(valid_cals), 1)
        self.assertEqual(valid_cals[0]["serial_number"], "RS-FSW-84920")

        single = self.storage.get_lab_calibration_by_serial("RS-FSW-84920")
        self.assertIsNotNone(single)
        self.assertEqual(single["equipment_name"], "Rohde & Schwarz FSW Spectrum Analyzer")

        missing = self.storage.get_lab_calibration_by_serial("UNKNOWN-SN")
        self.assertIsNone(missing)

    def test_lecturer_hki_records_storage(self):
        hid1 = self.storage.record_lecturer_hki(
            work_title="Perangkat Lunak Simulasi Propagasi Gelombang Mikro 5G",
            creators=["Dr. Ir. Budi Santoso, M.T.", "Ahmad Zaki"],
            creation_type="Program Komputer",
            application_number="EC002026104829",
            registration_number="000492819",
            registration_date="2026-10-14",
            rubric_points=20.0
        )
        hid2 = self.storage.record_lecturer_hki(
            work_title="Monograf Desain Antena MIMO Berbasis Metamaterial",
            creators=["Dr. Siti Rahmawati, M.T."],
            creation_type="Buku / Monograf",
            application_number="EC002026104830",
            registration_number="000492820",
            registration_date="2026-10-15",
            rubric_points=40.0
        )
        self.assertGreater(hid1, 0)
        self.assertGreater(hid2, 0)

        all_hki = self.storage.list_lecturer_hki_records()
        self.assertEqual(len(all_hki), 2)

        software_hki = self.storage.list_lecturer_hki_records(creation_type="Program Komputer")
        self.assertEqual(len(software_hki), 1)
        self.assertEqual(software_hki[0]["registration_number"], "000492819")

        single = self.storage.get_lecturer_hki_by_reg_number("000492819")
        self.assertIsNotNone(single)
        self.assertEqual(single["work_title"], "Perangkat Lunak Simulasi Propagasi Gelombang Mikro 5G")
        self.assertEqual(single["creators"], ["Dr. Ir. Budi Santoso, M.T.", "Ahmad Zaki"])

        missing = self.storage.get_lecturer_hki_by_reg_number("99999999")
        self.assertIsNone(missing)

    def test_student_msib_internships_storage(self):
        mid1 = self.storage.record_msib_internship(
            student_name="Ahmad Zaki",
            nim="1101230045",
            industry_partner="PT Telkom Indonesia",
            internship_role="Cloud & Network Engineer",
            mentor_grade=88.5,
            letter_grade="A",
            converted_sks=20,
            duration_months=5
        )
        mid2 = self.storage.record_msib_internship(
            student_name="Rina Safitri",
            nim="1101230088",
            industry_partner="PT Indosat Ooredoo Hutchison",
            internship_role="RF Optimization Associate",
            mentor_grade=76.0,
            letter_grade="AB",
            converted_sks=20,
            duration_months=5
        )
        self.assertGreater(mid1, 0)
        self.assertGreater(mid2, 0)

        all_msib = self.storage.list_msib_internships()
        self.assertEqual(len(all_msib), 2)

        telkom_msib = self.storage.list_msib_internships(partner="Telkom")
        self.assertEqual(len(telkom_msib), 1)
        self.assertEqual(telkom_msib[0]["nim"], "1101230045")

        single = self.storage.get_msib_by_nim("1101230045")
        self.assertIsNotNone(single)
        self.assertEqual(single["student_name"], "Ahmad Zaki")
        self.assertEqual(single["converted_sks"], 20)

        none_res = self.storage.get_msib_by_nim("0000000000")
        self.assertIsNone(none_res)

    def test_lecturer_pkm_grants_storage(self):
        gid1 = self.storage.record_pkm_grant(
            project_title="Pemberdayaan IoT Petani Karangmangu",
            team_leader="Dr. Ir. Budi Santoso, M.T.",
            nidn="0612058001",
            partner_name="Kelompok Tani Makmur",
            target_location="Desa Karangmangu",
            proposed_budget=15000000.0,
            approved_budget=15000000.0,
            fiscal_year=2026,
            focus_area="Pemberdayaan Teknologi Digital"
        )
        gid2 = self.storage.record_pkm_grant(
            project_title="Pelatihan Jaringan Komputer SMK",
            team_leader="Dr. Siti Rahmawati",
            nidn="0612058002",
            partner_name="SMK Telkom",
            target_location="Purwokerto",
            proposed_budget=12000000.0,
            approved_budget=12000000.0,
            fiscal_year=2025,
            focus_area="Pelatihan Vokasi"
        )
        self.assertGreater(gid1, 0)
        self.assertGreater(gid2, 0)

        all_grants = self.storage.list_pkm_grants()
        self.assertEqual(len(all_grants), 2)

        grants_2026 = self.storage.list_pkm_grants(fiscal_year=2026)
        self.assertEqual(len(grants_2026), 1)
        self.assertEqual(grants_2026[0]["id"], gid1)

        single = self.storage.get_pkm_grant_by_id(gid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["team_leader"], "Dr. Ir. Budi Santoso, M.T.")

        none_g = self.storage.get_pkm_grant_by_id(999999)
        self.assertIsNone(none_g)

    def test_fso_link_budget_records_storage(self):
        fid1 = self.storage.record_fso_link_budget(
            link_name="FSO Kampus 1 - Kampus 2",
            link_distance_km=1.2,
            tx_power_dbm=10.0,
            rx_power_dbm=-18.0,
            geometric_loss_db=25.0,
            atmospheric_loss_db=3.0,
            link_margin_db=20.0,
            status="Robust"
        )
        self.assertGreater(fid1, 0)

        all_fso = self.storage.list_fso_link_budgets()
        self.assertEqual(len(all_fso), 1)
        self.assertEqual(all_fso[0]["link_name"], "FSO Kampus 1 - Kampus 2")

        single = self.storage.get_fso_link_budget_by_id(fid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["status"], "Robust")

        none_f = self.storage.get_fso_link_budget_by_id(999999)
        self.assertIsNone(none_f)

    def test_satellite_link_budgets_storage(self):
        bid1 = self.storage.record_satellite_link_budget(
            satellite_name="Telkom-4 (Merah Putih)",
            downlink_freq_ghz=12.2,
            slant_range_km=38000.0,
            tx_eirp_dbw=53.5,
            rx_g_over_t_db_k=15.0,
            bandwidth_mhz=36.0,
            cnr_db=11.25,
            link_margin_db=4.25,
            is_viable=True,
            status="Feasible"
        )
        bid2 = self.storage.record_satellite_link_budget(
            satellite_name="BRIsat",
            downlink_freq_ghz=11.7,
            slant_range_km=39000.0,
            tx_eirp_dbw=45.0,
            rx_g_over_t_db_k=10.0,
            bandwidth_mhz=72.0,
            cnr_db=4.5,
            link_margin_db=-2.5,
            is_viable=False,
            status="Margin Deficient"
        )
        self.assertGreater(bid1, 0)
        self.assertGreater(bid2, 0)

        all_budgets = self.storage.list_satellite_link_budgets()
        self.assertEqual(len(all_budgets), 2)

        viable_budgets = self.storage.list_satellite_link_budgets(is_viable=True)
        self.assertEqual(len(viable_budgets), 1)
        self.assertEqual(viable_budgets[0]["satellite_name"], "Telkom-4 (Merah Putih)")

        single = self.storage.get_satellite_link_budget_by_id(bid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["status"], "Feasible")

    def test_kampus_mengajar_students_storage(self):
        kid1 = self.storage.record_kampus_mengajar_student(
            student_name="Annisa Rahma",
            nim="1201200045",
            target_school="SMP Negeri 2 Kedungbanteng",
            school_level="SMP",
            teaching_hours=350,
            composite_score=89.0,
            letter_grade="A",
            converted_sks=20,
            status="Completed with Full Recognition"
        )
        self.assertGreater(kid1, 0)

        all_km = self.storage.list_kampus_mengajar_students()
        self.assertEqual(len(all_km), 1)
        self.assertEqual(all_km[0]["student_name"], "Annisa Rahma")

        by_nim = self.storage.get_kampus_mengajar_by_nim("1201200045")
        self.assertIsNotNone(by_nim)
        self.assertEqual(by_nim["converted_sks"], 20)

    def test_rf_intermod_records_storage(self):
        rid1 = self.storage.record_rf_intermod_distortion(
            component_name="Mixer Downconverter Stage",
            input_power_dbm=-15.0,
            gain_db=12.0,
            iip3_dbm=8.0,
            fundamental_pout_dbm=-3.0,
            imd3_suppression_dbc=46.0,
            linearity_status="Acceptable",
            is_linear=True
        )
        self.assertGreater(rid1, 0)

        all_rf = self.storage.list_rf_intermod_records()
        self.assertEqual(len(all_rf), 1)

        linear_rf = self.storage.list_rf_intermod_records(is_linear=True)
        self.assertEqual(len(linear_rf), 1)
        self.assertEqual(linear_rf[0]["component_name"], "Mixer Downconverter Stage")

        single = self.storage.get_rf_intermod_by_id(rid1)
        self.assertIsNotNone(single)
        self.assertEqual(single["linearity_status"], "Acceptable")



if __name__ == "__main__":
    unittest.main()








