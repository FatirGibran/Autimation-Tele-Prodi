import unittest
import json
from pathlib import Path
from seo_validator import YoastSEOValidator

class TestYoastSEOValidator(unittest.TestCase):
    def setUp(self):
        self.article_dir = Path(__file__).parent.parent / "articles"
        self.html_file = self.article_dir / "2026-09-28-webassembly-edge-computing-iot.html"
        self.meta_file = self.article_dir / "2026-09-28-webassembly-edge-computing-iot-metadata.json"

        self.html_content = self.html_file.read_text(encoding="utf-8")
        with open(self.meta_file, encoding="utf-8") as f:
            data = json.load(f)
            self.metadata = data["yoast_seo"]

    def test_sample_article_is_all_green(self):
        report = YoastSEOValidator.evaluate(self.metadata, self.html_content)
        self.assertTrue(report["is_all_green"], f"Errors found: {report['errors']}")
        self.assertEqual(report["score"], 100)

    def test_meta_description_length_boundary(self):
        invalid_meta = self.metadata.copy()
        invalid_meta["meta_description"] = "Terlalu pendek."
        report = YoastSEOValidator.evaluate(invalid_meta, self.html_content)
        self.assertFalse(report["checks"]["meta_description_length"]["passed"])
        self.assertFalse(report["is_all_green"])

    def test_missing_outbound_link_triggers_error(self):
        html_without_outbound = self.html_content.replace("https://bytecodealliance.org/", "https://bif-pwt.telkomuniversity.ac.id/fakultas")
        report = YoastSEOValidator.evaluate(self.metadata, html_without_outbound)
        self.assertFalse(report["checks"]["outbound_link"]["passed"])

    def test_keyphrase_in_title_start(self):
        invalid_meta = self.metadata.copy()
        invalid_meta["seo_title"] = "Solusi Cerdas: WebAssembly Edge Computing IoT"
        report = YoastSEOValidator.evaluate(invalid_meta, self.html_content)
        self.assertFalse(report["checks"]["keyphrase_in_title_start"]["passed"])

    def test_title_length_validation(self):
        # Too short (< 30)
        short_meta = self.metadata.copy()
        short_meta["seo_title"] = "WebAssembly IoT"
        report = YoastSEOValidator.evaluate(short_meta, self.html_content)
        self.assertFalse(report["checks"]["seo_title_length"]["passed"])

    def test_readability_analysis(self):
        report = YoastSEOValidator.evaluate(self.metadata, self.html_content)
        self.assertIn("readability", report)
        self.assertGreater(report["readability"]["total_sentences"], 0)
        self.assertIn("avg_words_per_sentence", report["readability"])

    def test_consecutive_sentence_starts_detection(self):
        repetitive_text = "Namun ini adalah kalimat satu. Namun ini adalah kalimat kedua. Namun ini adalah kalimat ketiga."
        readability = YoastSEOValidator.analyze_readability(repetitive_text)
        self.assertTrue(readability["has_consecutive_duplicates"])
        self.assertFalse(readability["is_readable"])

        clean_text = "Pertama kita mulai. Kemudian langkah selanjutnya. Terakhir kita evaluasi."
        readability_clean = YoastSEOValidator.analyze_readability(clean_text)
        self.assertFalse(readability_clean["has_consecutive_duplicates"])
        self.assertTrue(readability_clean["is_readable"])

    def test_transition_words_evaluation(self):
        text = "Sistem komputasi edge berkembang pesat. Selain itu, latensi jaringan berkurang drastis. Oleh karena itu, efisiensi meningkat."
        readability = YoastSEOValidator.analyze_readability(text)
        self.assertIn("transition_words", readability)
        self.assertEqual(readability["transition_words"]["count"], 2)
        self.assertTrue(readability["transition_words"]["is_optimal"])
        self.assertGreaterEqual(readability["transition_words"]["percentage"], 20.0)

    def test_passive_voice_detection(self):
        passive_text = "Riset ini dilakukan oleh dosen. Modul dijalankan di server lokal. Pengujian diselesaikan kemarin."
        readability_passive = YoastSEOValidator.analyze_readability(passive_text)
        self.assertIn("passive_voice", readability_passive)
        self.assertEqual(readability_passive["passive_voice"]["count"], 3)
        self.assertFalse(readability_passive["passive_voice"]["is_acceptable"])

        active_text = "Dosen memimpin riset komputasi awan. Tim merancang arsitektur baru. Mahasiswa menguji kinerja modul."
        readability_active = YoastSEOValidator.analyze_readability(active_text)
        self.assertEqual(readability_active["passive_voice"]["count"], 0)
        self.assertTrue(readability_active["passive_voice"]["is_acceptable"])

    def test_syllable_count_and_reading_ease(self):
        self.assertEqual(YoastSEOValidator.count_syllables_indonesian("komputasi"), 4)
        self.assertEqual(YoastSEOValidator.count_syllables_indonesian("data"), 2)
        self.assertEqual(YoastSEOValidator.count_syllables_indonesian("ai"), 2)

        sample = "Teknologi kecerdasan buatan berkembang dengan cepat di Indonesia."
        readability = YoastSEOValidator.analyze_readability(sample)
        self.assertIn("syllables_per_word", readability)
        self.assertIn("reading_ease_score", readability)
        self.assertGreater(readability["reading_ease_score"], 0)

    def test_audit_anchor_texts(self):
        html_with_generic = '<p>Untuk panduan silakan <a href="https://example.com/guide">klik di sini</a> atau <a href="https://example.com/docs">dokumentasi resmi</a>.</p>'
        audit = YoastSEOValidator.audit_anchor_texts(html_with_generic)
        self.assertEqual(audit["total_links"], 2)
        self.assertEqual(audit["flagged_count"], 1)
        self.assertEqual(audit["flagged_links"][0]["anchor"], "klik di sini")
        self.assertFalse(audit["passed"])

    def test_keyword_cannibalization(self):
        existing = [
            "webassembly edge computing iot",
            "arsitektur microservices telkom",
            "optimasi query mysql"
        ]
        exact_check = YoastSEOValidator.check_keyword_cannibalization("WebAssembly Edge Computing IoT", existing)
        self.assertTrue(exact_check["cannibalized"])
        self.assertTrue(exact_check["conflicts"][0]["exact"])

        unique_check = YoastSEOValidator.check_keyword_cannibalization("keamanan siber quantum", existing)
        self.assertFalse(unique_check["cannibalized"])

    def test_evaluate_keyword_density(self):
        body = ("Edge AI merupakan inovasi penting dalam jaringan telekomunikasi dan komputasi edge modern. " * 3) + ("mahasiswa belajar dengan tekun di kampus telkom university purwokerto setiap hari. " * 15)
        result = YoastSEOValidator.evaluate_keyword_density("Edge AI", body)
        self.assertEqual(result["count"], 3)
        self.assertGreater(result["density_percentage"], 0.0)
        self.assertIn(result["status"], ["green", "orange"])

    def test_evaluate_paragraph_lengths(self):
        short_p = "<p>" + ("kata " * 50) + "</p>"
        long_p = "<p>" + ("panjang " * 160) + "</p>"
        html = f"<div>{short_p}{long_p}</div>"
        report = YoastSEOValidator.evaluate_paragraph_lengths(html, max_words=150)
        self.assertEqual(report["total_paragraphs"], 2)
        self.assertEqual(report["flagged_count"], 1)
        self.assertFalse(report["passed"])

    def test_evaluate_subheading_distribution(self):
        good_html = "<h2>Bab 1</h2><p>" + ("kata " * 100) + "</p><h2>Bab 2</h2><p>" + ("kata " * 100) + "</p>"
        good_rep = YoastSEOValidator.evaluate_subheading_distribution(good_html, max_words_per_section=300)
        self.assertTrue(good_rep["passed"])

        bad_html = "<h2>Bab 1</h2><p>" + ("kata " * 350) + "</p>"
        bad_rep = YoastSEOValidator.evaluate_subheading_distribution(bad_html, max_words_per_section=300)
        self.assertFalse(bad_rep["passed"])
        self.assertEqual(bad_rep["flagged_count"], 1)

    def test_audit_links_profile(self):
        html = '<p><a href="https://bif-pwt.telkomuniversity.ac.id/kurikulum">Kurikulum</a> dan <a href="https://ieee.org/paper" rel="noopener noreferrer">IEEE</a></p>'
        profile = YoastSEOValidator.audit_links_profile(html)
        self.assertEqual(profile["internal_count"], 1)
        self.assertEqual(profile["external_count"], 1)
        self.assertTrue(profile["passed"])

    def test_validate_h1_structure(self):
        single_h1 = '<div class="tu-editorial-container"><h1>Judul Utama</h1><p>Konten</p></div>'
        res1 = YoastSEOValidator.validate_h1_structure(single_h1)
        self.assertTrue(res1["passed"])
        self.assertEqual(res1["h1_count"], 1)

        multi_h1 = '<div class="tu-editorial-container"><h1>Judul 1</h1><p>Konten</p><h1>Judul 2</h1></div>'
        res2 = YoastSEOValidator.validate_h1_structure(multi_h1)
        self.assertFalse(res2["passed"])
        self.assertEqual(res2["h1_count"], 2)

    def test_evaluate_academic_title_style(self):
        title = "Edge Computing: Analisis Implementasi Arsitektur IoT Modern"
        res = YoastSEOValidator.evaluate_academic_title_style(title)
        self.assertTrue(res["has_subtitle"])
        self.assertIn("analisis", res["power_terms_found"])
        self.assertTrue(res["is_recommended"])

    def test_evaluate_stopword_ratio(self):
        text = "Sistem komputasi cerdas yang dirancang untuk mendukung penelitian dan pengembangan teknologi baru di kampus."
        res = YoastSEOValidator.evaluate_stopword_ratio(text)
        self.assertTrue(res["is_balanced"])
        self.assertGreater(res["ratio_pct"], 0.0)

    def test_evaluate_anchor_diversity(self):
        html = '<p><a href="https://a.com">WebAssembly</a>, <a href="https://b.com">Edge Computing</a>, <a href="https://c.com">Cloud</a></p>'
        res = YoastSEOValidator.evaluate_anchor_diversity(html)
        self.assertTrue(res["is_diverse"])
        self.assertEqual(res["unique_anchors"], 3)

        redundant_html = '<p>' + ''.join(f'<a href="https://a.com/{i}">klik di sini</a> ' for i in range(4)) + '</p>'
        red_res = YoastSEOValidator.evaluate_anchor_diversity(redundant_html)
        self.assertFalse(red_res["is_diverse"])
        self.assertEqual(len(red_res["repeated"]), 1)

if __name__ == "__main__":
    unittest.main()
