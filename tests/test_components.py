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

    def test_render_key_takeaways(self):
        card = EditorialComponents.render_key_takeaways(
            items=["Kinerja tinggi", "Sandbox aman", "Hemat energi"],
            heading="Poin Inti Wasm"
        )
        self.assertIn("tu-takeaways-card", card)
        self.assertIn("Poin Inti Wasm", card)
        self.assertIn("Sandbox aman", card)

    def test_render_author_card(self):
        author = EditorialComponents.render_author_card(
            author_name="Dr. Budi Santoso",
            author_role="Dosen Riset IoT",
            bio_text="Fokus riset smart sensor."
        )
        self.assertIn("tu-author-card", author)
        self.assertIn("Dr. Budi Santoso", author)
        self.assertIn("Dosen Riset IoT", author)
        self.assertIn("Fokus riset smart sensor.", author)

    def test_render_faq_accordion(self):
        items = [
            ("Apa itu WebAssembly?", "WebAssembly adalah format instruksi biner."),
            ("Apakah aman?", "Sangat aman berkat model memori terisolasi.")
        ]
        faq = EditorialComponents.render_faq_accordion(items, section_title="Pertanyaan Populer")
        self.assertIn("tu-faq-wrap", faq)
        self.assertIn("Pertanyaan Populer", faq)
        self.assertIn("<summary class=\"tu-faq-question\">Apa itu WebAssembly?</summary>", faq)
        self.assertIn("<div class=\"tu-faq-answer\">WebAssembly adalah format instruksi biner.</div>", faq)
        self.assertIn("<details class=\"tu-faq-item\">", faq)

    def test_render_stat_grid(self):
        stats = [
            {"value": "95%", "label": "Efisiensi Memori"},
            {"value": "10x", "label": "Kecepatan Cold Start"}
        ]
        grid = EditorialComponents.render_stat_grid(stats)
        self.assertIn("tu-stat-grid", grid)
        self.assertIn("tu-stat-card", grid)
        self.assertIn("95%", grid)
        self.assertIn("Efisiensi Memori", grid)
        self.assertIn("10x", grid)
        self.assertIn("Kecepatan Cold Start", grid)

if __name__ == "__main__":
    unittest.main()

