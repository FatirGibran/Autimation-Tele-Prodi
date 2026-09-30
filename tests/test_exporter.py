import unittest
from exporter import ArticleExporter

class TestArticleExporter(unittest.TestCase):
    def test_elementor_json_structure(self):
        result = ArticleExporter.to_elementor_json(
            title="Judul Riset",
            html_content="<div class='tu-editorial-container'><p>Konten</p></div>"
        )
        self.assertEqual(result["version"], "0.4")
        self.assertEqual(result["type"], "section")
        self.assertEqual(len(result["content"]), 1)
        widget = result["content"][0]["elements"][0]["elements"][0]
        self.assertEqual(widget["widgetType"], "html")
        self.assertIn("tu-editorial-container", widget["settings"]["html"])

    def test_markdown_frontmatter_generation(self):
        meta = {
            "seo_title": "SEO Title Test",
            "focus_keyphrase": "keyphrase test",
            "slug": "slug-test",
            "meta_description": "Description test 123",
            "category": "Cloud",
            "publish_date": "2026-09-28"
        }
        md = ArticleExporter.to_markdown_with_frontmatter(meta, "<p>Hello</p>")
        self.assertTrue(md.startswith("---"))
        self.assertIn("focus_keyphrase: \"keyphrase test\"", md)
        self.assertIn("<p>Hello</p>", md)

    def test_to_html_document(self):
        meta = {
            "seo_title": "Standalone Doc Title",
            "meta_description": "Standalone meta description.",
            "slug": "standalone-slug"
        }
        doc = ArticleExporter.to_html_document(meta, "<div class='tu-editorial-container'>Body</div>")
        self.assertIn("<!DOCTYPE html>", doc)
        self.assertIn("<title>Standalone Doc Title</title>", doc)
        self.assertIn('property="og:title" content="Standalone Doc Title"', doc)
        self.assertIn("standalone-slug", doc)

    def test_export_bundle(self):
        import tempfile
        from pathlib import Path
        meta = {
            "seo_title": "Bundle Title",
            "meta_description": "Bundle description.",
            "slug": "bundle-slug"
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            paths = ArticleExporter.export_bundle(out_dir, "bundle-slug", meta, "<p>Bundle Content</p>")
            self.assertTrue(paths["html"].exists())
            self.assertTrue(paths["standalone_html"].exists())
            self.assertTrue(paths["markdown"].exists())
            self.assertTrue(paths["elementor_json"].exists())

    def test_generate_json_ld(self):
        import json
        meta = {
            "seo_title": "IoT Smart Campus Telkom",
            "meta_description": "Implementasi sensor cerdas di Purwokerto.",
            "slug": "iot-smart-campus-telkom",
            "publish_date": "2026-09-30",
            "image_url": "https://example.com/banner.jpg"
        }
        json_ld_str = ArticleExporter.generate_json_ld(meta, article_type="ScholarlyArticle")
        data = json.loads(json_ld_str)
        self.assertEqual(data["@context"], "https://schema.org")
        self.assertEqual(data["@type"], "ScholarlyArticle")
        self.assertEqual(data["headline"], "IoT Smart Campus Telkom")
        self.assertIn("https://bif-pwt.telkomuniversity.ac.id/iot-smart-campus-telkom/", data["mainEntityOfPage"]["@id"])
        self.assertEqual(data["image"], ["https://example.com/banner.jpg"])

if __name__ == "__main__":
    unittest.main()
