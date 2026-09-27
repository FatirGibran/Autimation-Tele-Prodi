import unittest
from components import EditorialComponents

class TestEditorialComponents(unittest.TestCase):
    def test_css_scoping(self):
        css = EditorialComponents.get_scoped_css()
        self.assertIn(".tu-editorial-container", css)
        self.assertIn("#c53030", css)
        self.assertIn("#0f172a", css)

    def test_render_hero(self):
        hero = EditorialComponents.render_hero(
            category="IoT",
            date_str="28 September 2026",
            read_time="4 Menit Baca",
            title="Judul Artikel",
            lead_html="Lead paragraf contoh."
        )
        self.assertIn('<header class="tu-hero-header">', hero)
        self.assertIn("Judul Artikel", hero)
        self.assertIn("28 September 2026", hero)

    def test_render_figure(self):
        fig = EditorialComponents.render_figure(
            img_url="https://example.com/img.jpg",
            alt_text="Alt test",
            caption="Caption test"
        )
        self.assertIn('loading="lazy"', fig)
        self.assertIn('alt="Alt test"', fig)

    def test_render_comparison_grid(self):
        grid = EditorialComponents.render_comparison_grid(
            legacy_title="Docker",
            legacy_items=["Berat", "Lambat"],
            modern_title="Wasm",
            modern_items=["Ringan", "Cepat"]
        )
        self.assertIn('<div class="tu-comparison-grid">', grid)
        self.assertIn("Docker", grid)
        self.assertIn("Wasm", grid)

if __name__ == "__main__":
    unittest.main()
