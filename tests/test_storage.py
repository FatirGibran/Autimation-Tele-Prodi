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


if __name__ == "__main__":
    unittest.main()


