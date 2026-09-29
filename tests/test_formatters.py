import unittest
from formatters import TelegramFormatter

class TestTelegramFormatter(unittest.TestCase):
    def test_format_seo_report(self):
        meta = {
            "focus_keyphrase": "teknologi iot",
            "seo_title": "Teknologi IoT Terkini",
            "slug": "teknologi-iot-terkini",
            "meta_description": "Pelajari perkembangan teknologi iot terbaru di Telkom University Purwokerto."
        }
        res = {
            "is_all_green": True,
            "score": 100,
            "checks": {
                "word_count": {"passed": True, "value": 450},
                "keyphrase_in_meta": {"passed": True}
            },
            "warnings": ["Pastikan gambar di-upload."]
        }
        output = TelegramFormatter.format_seo_report(meta, res)
        self.assertIn("YOAST SEO METADATA", output)
        self.assertIn("teknologi-iot-terkini", output)
        self.assertIn("Word Count (450)", output)
        self.assertIn("Pastikan gambar di-upload.", output)

    def test_format_stats_report(self):
        stats = {
            "total_articles": 15,
            "published_count": 5,
            "ready_count": 7,
            "needs_review_count": 3
        }
        output = TelegramFormatter.format_stats_report(stats)
        self.assertIn("Ringkasan Statistik Editorial", output)
        self.assertIn("Total Artikel: `15`", output)
        self.assertIn("Terpublikasi / WP Draft: `5`", output)

    def test_format_article_summary_card(self):
        art = {
            "id": 42,
            "topic": "Sistem Terdistribusi",
            "seo_title": "Sistem Terdistribusi di Cloud",
            "category": "Jaringan & Cloud",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "sistem terdistribusi",
            "slug": "sistem-terdistribusi-cloud",
            "status": "ready",
            "wp_post_id": 999
        }
        output = TelegramFormatter.format_article_summary_card(art)
        self.assertIn("Detail Artikel (ID: 42)", output)
        self.assertIn("**WP Post ID:** `999`", output)
        self.assertIn("sistem-terdistribusi-cloud", output)

if __name__ == "__main__":
    unittest.main()
