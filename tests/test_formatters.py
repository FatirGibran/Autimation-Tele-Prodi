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

    def test_format_score_progress_bar(self):
        bar_high = TelegramFormatter.format_score_progress_bar(95)
        self.assertIn("100/100" if 100 in [95] else "95/100", bar_high)
        self.assertIn("Sempurna", bar_high)
        self.assertIn("█", bar_high)

        bar_low = TelegramFormatter.format_score_progress_bar(40)
        self.assertIn("40/100", bar_low)
        self.assertIn("Kritis", bar_low)

    def test_format_readability_badge(self):
        badge_good = TelegramFormatter.format_readability_badge(72.5)
        self.assertIn("🟢", badge_good)
        self.assertIn("72.5", badge_good)

        badge_poor = TelegramFormatter.format_readability_badge(30.0, label="Sulit Dibaca")
        self.assertIn("🔴", badge_poor)
        self.assertIn("Sulit Dibaca", badge_poor)

    def test_build_review_management_keyboard(self):
        keyboard = TelegramFormatter.build_review_management_keyboard(123, "test-slug")
        self.assertIn("inline_keyboard", keyboard)
        buttons = [btn["text"] for row in keyboard["inline_keyboard"] for btn in row]
        self.assertTrue(any("Setujui" in t for t in buttons))
        self.assertTrue(any("Revisi" in t for t in buttons))
        self.assertTrue(any(btn["callback_data"] == "approve:123" for row in keyboard["inline_keyboard"] for btn in row))

    def test_format_editorial_diff_preview(self):
        old_data = {
            "id": 10,
            "seo_title": "Judul Lama",
            "focus_keyphrase": "keyphrase lama",
            "status": "draft",
            "html_content": "<p>Satu dua tiga empat lima.</p>"
        }
        new_data = {
            "id": 10,
            "seo_title": "Judul Baru yang Diperbarui",
            "focus_keyphrase": "keyphrase baru",
            "status": "ready",
            "html_content": "<p>Satu dua tiga empat lima enam tujuh delapan.</p>"
        }
        diff_text = TelegramFormatter.format_editorial_diff_preview(old_data, new_data)
        self.assertIn("Perbandingan Revisi Editorial", diff_text)
        self.assertIn("Judul Lama", diff_text)
        self.assertIn("Judul Baru yang Diperbarui", diff_text)
        self.assertIn("keyphrase baru", diff_text)
        self.assertIn("ready", diff_text)
        self.assertIn("kata", diff_text)

    def test_format_scheduled_reminder_card(self):
        article = {
            "seo_title": "Peluncuran Lab Baru",
            "category": "Infrastruktur",
            "slug": "peluncuran-lab-baru"
        }
        card = TelegramFormatter.format_scheduled_reminder_card(article, "2026-10-10 10:00 WIB")
        self.assertIn("Pengingat Jadwal Terbit Artikel", card)
        self.assertIn("Peluncuran Lab Baru", card)
        self.assertIn("Infrastruktur", card)
        self.assertIn("2026-10-10 10:00 WIB", card)
        self.assertIn("peluncuran-lab-baru", card)



class TestCommandRateLimiter(unittest.TestCase):
    def test_rate_limiter_allows_and_blocks(self):
        from formatters import CommandRateLimiter
        import time

        limiter = CommandRateLimiter(default_cooldown=0.2)
        allowed, remaining = limiter.is_allowed(1001)
        self.assertTrue(allowed)
        self.assertEqual(remaining, 0.0)

        # Immediate repeat should be blocked
        allowed2, remaining2 = limiter.is_allowed(1001)
        self.assertFalse(allowed2)
        self.assertGreater(remaining2, 0.0)

        # Different user is not blocked
        allowed_other, _ = limiter.is_allowed(1002)
        self.assertTrue(allowed_other)

        # Reset user
        limiter.reset(1001)
        allowed_reset, _ = limiter.is_allowed(1001)
        self.assertTrue(allowed_reset)


if __name__ == "__main__":
    unittest.main()

