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

    def test_render_references_block(self):
        refs = [
            "Haas, A. et al. (2017). Bringing the Web up to Speed with WebAssembly. ACM SIGPLAN.",
            "World Wide Web Consortium (W3C). WebAssembly Core Specification."
        ]
        block = EditorialComponents.render_references_block(refs, heading="Daftar Pustaka")
        self.assertIn("tu-references-box", block)
        self.assertIn("Daftar Pustaka", block)
        self.assertIn("Bringing the Web up to Speed", block)
        self.assertIn("tu-references-list", block)

    def test_render_code_block(self):
        sample_code = "fn main() {\n    println!(\"Hello <Wasm>\");\n}"
        block = EditorialComponents.render_code_block(sample_code, language="rust", filename="main.rs")
        self.assertIn("tu-code-container", block)
        self.assertIn("main.rs", block)
        self.assertIn("tu-code-badge", block)
        self.assertIn("rust", block)
        self.assertIn("&lt;Wasm&gt;", block)

    def test_render_timeline_component(self):
        events = [
            {"date": "Q1 2026", "title": "Inisiasi Riset", "description": "Eksplorasi modul WebAssembly."},
            {"date": "Q2 2026", "title": "Implementasi Edge", "description": "Uji coba runtime di gateway IoT."}
        ]
        timeline = EditorialComponents.render_timeline_component(events)
        self.assertIn("tu-timeline", timeline)
        self.assertIn("tu-timeline-item", timeline)
        self.assertIn("Inisiasi Riset", timeline)
        self.assertIn("Q1 2026", timeline)

    def test_render_alumni_quote_card(self):
        card = EditorialComponents.render_alumni_quote_card(
            name="Ahmad Fauzan",
            batch="Angkatan 2022",
            role="AI Engineer",
            company="Tech Corp",
            quote="Kurikulum prodi sangat aplikatif!",
            avatar_url="https://example.com/avatar.jpg"
        )
        self.assertIn("tu-alumni-card", card)
        self.assertIn("Ahmad Fauzan", card)
        self.assertIn("Angkatan 2022", card)
        self.assertIn("Tech Corp", card)
        self.assertIn("Kurikulum prodi sangat aplikatif!", card)
        self.assertIn("tu-alumni-avatar", card)

    def test_render_feature_matrix(self):
        cols = ["Materi", "S1 Sains Data", "Sertifikasi Singkat"]
        rows = [
            {"feature": "Fondasi Teori Matematika", "values": [True, False]},
            {"feature": "Portofolio Industri Terverifikasi", "values": [True, True]},
            {"feature": "Durasi Studi", "values": ["8 Semester", "3 Bulan"]}
        ]
        matrix = EditorialComponents.render_feature_matrix(cols, rows)
        self.assertIn("tu-feature-matrix", matrix)
        self.assertIn("<th>S1 Sains Data</th>", matrix)
        self.assertIn("tu-matrix-check", matrix)
        self.assertIn("tu-matrix-cross", matrix)
        self.assertIn("8 Semester", matrix)

    def test_render_table_of_contents(self):
        headings = [
            {"tag": "h2", "text": "Pengantar WebAssembly"},
            {"tag": "h3", "text": "Keunggulan Kinerja"}
        ]
        toc = EditorialComponents.render_table_of_contents(headings)
        self.assertIn("tu-toc-card", toc)
        self.assertIn("#pengantar-webassembly", toc)
        self.assertIn("tu-toc-sub", toc)

    def test_render_author_team(self):
        members = [
            {"name": "Dr. Ir. Budi", "role": "Dosen Pembina", "lab": "Lab IoT & Edge", "avatar_url": "https://example.com/budi.jpg"}
        ]
        grid = EditorialComponents.render_author_team(members)
        self.assertIn("tu-team-section", grid)
        self.assertIn("Dr. Ir. Budi", grid)
        self.assertIn("Lab IoT &amp; Edge", grid)

    def test_render_download_card(self):
        card = EditorialComponents.render_download_card(
            title="Silabus Mata Kuliah Edge Computing",
            description="Panduan kurikulum dan RPS semester genap.",
            file_type="PDF",
            file_size="2.4 MB",
            download_url="https://bif-pwt.telkomuniversity.ac.id/rps.pdf"
        )
        self.assertIn("tu-download-card", card)
        self.assertIn("PDF", card)
        self.assertIn("2.4 MB", card)

    def test_render_video_embed(self):
        video = EditorialComponents.render_video_embed(
            embed_url="https://www.youtube-nocookie.com/embed/demo123",
            title="Kuliah Umum Edge Computing",
            caption="Rekaman sesi kuliah umum semester genap 2026."
        )
        self.assertIn("tu-video-figure", video)
        self.assertIn("Kuliah Umum Edge Computing", video)

    def test_render_admission_cta(self):
        cta = EditorialComponents.render_admission_cta()
        self.assertIn("tu-cta-banner", cta)
        self.assertIn("Telkom University Purwokerto", cta)

    def test_render_metric_callout(self):
        metric = EditorialComponents.render_metric_callout("98%", "Tingkat Kelulusan Tepat Waktu", "Berdasarkan audit akademik 2026")
        self.assertIn("tu-metric-card", metric)
        self.assertIn("98%", metric)
        self.assertIn("Tingkat Kelulusan Tepat Waktu", metric)

if __name__ == "__main__":
    unittest.main()

