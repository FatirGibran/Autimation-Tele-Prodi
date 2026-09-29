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

if __name__ == "__main__":
    unittest.main()
