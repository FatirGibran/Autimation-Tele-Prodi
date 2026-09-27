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

if __name__ == "__main__":
    unittest.main()
