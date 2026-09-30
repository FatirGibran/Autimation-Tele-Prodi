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

if __name__ == "__main__":
    unittest.main()
