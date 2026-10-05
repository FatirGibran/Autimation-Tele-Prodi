import unittest
from parser import parse_telegram_input, parse_llm_response, clean_url, DEFAULT_PLACEHOLDER_IMG, calculate_reading_time

class TestParser(unittest.TestCase):
    def test_clean_url_with_markdown(self):
        url = "[https://example.com/image.png](https://example.com/image.png)"
        self.assertEqual(clean_url(url), "https://example.com/image.png")

    def test_clean_url_fallback(self):
        self.assertEqual(clean_url(""), DEFAULT_PLACEHOLDER_IMG)

    def test_clean_url_strips_tracking_params(self):
        url = "https://example.com/photo.jpg?utm_source=telegram&utm_medium=social&fbclid=abc123xyz&keep=true"
        cleaned = clean_url(url)
        self.assertEqual(cleaned, "https://example.com/photo.jpg?keep=true")

    def test_parse_telegram_input_numbered_bullets(self):
        raw = """Topik: Edge AI Monitoring
Tanggal: 1 Oktober 2026
Kategori: Artificial Intelligence
Image URL: https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/sample.jpg
Poin Utama:
1. Akselerasi inferensi NPU
2. Optimasi quantization int8
3. Efisiensi daya baterai
"""
        data = parse_telegram_input(raw)
        self.assertEqual(data["topik"], "Edge AI Monitoring")
        self.assertEqual(data["tanggal"], "1 Oktober 2026")
        self.assertEqual(len(data["poin_utama"]), 3)
        self.assertEqual(data["poin_utama"][0], "Akselerasi inferensi NPU")

    def test_parse_llm_response_fenced(self):
        response = """
### 1. YOAST SEO METADATA
- Focus Keyphrase: `Edge AI microcontrollers`
- SEO Title: Edge AI Microcontrollers: Komputasi Cerdas di Perangkat IoT
- Slug: `edge-ai-microcontrollers`
- Meta Description: Temukan efisiensi implementasi Edge AI microcontrollers untuk sensor cerdas hemat energi dan latensi rendah pada arsitektur modern di sini.

### 2. KODE HTML LENGKAP
```html
<div class="tu-editorial-container">
  <p>Test content</p>
</div>
```
"""
        parsed = parse_llm_response(response)
        self.assertEqual(parsed["focus_keyphrase"], "Edge AI microcontrollers")
        self.assertEqual(parsed["slug"], "edge-ai-microcontrollers")
        self.assertTrue(parsed["html_code"].startswith('<div class="tu-editorial-container">'))

    def test_extract_headings(self):
        from parser import extract_headings
        html = """
        <div class="tu-editorial-container">
            <h1>Judul Utama</h1>
            <h2>Subheading <strong>Pertama</strong></h2>
            <p>Paragraf</p>
            <h3>Sub-sub</h3>
        </div>
        """
        headings = extract_headings(html)
        self.assertEqual(len(headings), 3)
        self.assertEqual(headings[0], {"tag": "h1", "text": "Judul Utama"})
        self.assertEqual(headings[1], {"tag": "h2", "text": "Subheading Pertama"})
        self.assertEqual(headings[2], {"tag": "h3", "text": "Sub-sub"})

    def test_strip_markdown_formatting(self):
        from parser import strip_markdown_formatting
        raw = "### **Teks Tebal** dan *miring* serta `kode` dan [tautan](https://example.com)"
        cleaned = strip_markdown_formatting(raw)
        self.assertEqual(cleaned, "Teks Tebal dan miring serta kode dan tautan")

    def test_convert_markdown_table_to_html(self):
        from parser import convert_markdown_table_to_html
        md = """| Fitur | Docker | Wasm |
|---|---|---|
| Ukuran | 100MB | 2MB |"""
        html = convert_markdown_table_to_html(md)
        self.assertIn("tu-table-responsive", html)
        self.assertIn("<table class=\"tu-table\">", html)
        self.assertIn("<th>Fitur</th>", html)
        self.assertIn("<th>Docker</th>", html)
        self.assertIn("<td>100MB</td>", html)
        self.assertIn("<td>2MB</td>", html)

    def test_calculate_reading_time(self):
        short_text = "Kata " * 50
        medium_text = "Kata " * 400
        self.assertEqual(calculate_reading_time(""), "1 Menit Baca")
        self.assertEqual(calculate_reading_time(short_text), "1 Menit Baca")
        self.assertEqual(calculate_reading_time(medium_text), "2 Menit Baca")

    def test_parse_markdown_callouts(self):
        from parser import parse_markdown_callouts
        raw = """> [!NOTE]
> Ini adalah catatan editorial penting.
> Mohon diperhatikan baik-baik.
"""
        rendered = parse_markdown_callouts(raw)
        self.assertIn("tu-callout tu-callout-note", rendered)
        self.assertIn("Catatan", rendered)
        self.assertIn("Ini adalah catatan editorial penting.", rendered)

    def test_generate_excerpt(self):
        from parser import generate_excerpt
        html = '<div class="tu-editorial-container"><h1>Judul</h1><p>Program Studi S1 Teknik Informatika Telkom University Purwokerto menyelenggarakan riset unggulan IoT.</p></div>'
        excerpt = generate_excerpt(html, max_length=50)
        self.assertTrue(excerpt.endswith("..."))
        self.assertNotIn("<h1>", excerpt)
        self.assertLessEqual(len(excerpt), 55)

    def test_normalize_indonesian_typography(self):
        from parser import normalize_indonesian_typography
        raw = "“Kecerdasan Buatan”—kata dosen ‘Informatika’…\u00a0itu benar\u200b."
        normalized = normalize_indonesian_typography(raw)
        self.assertIn('"Kecerdasan Buatan"', normalized)
        self.assertIn("'Informatika'", normalized)
        self.assertIn(" -- ", normalized)
        self.assertIn("...", normalized)
        self.assertNotIn("\u200b", normalized)

    def test_parse_markdown_footnotes(self):
        from parser import parse_markdown_footnotes
        raw = "Arsitektur cloud native[^1] membutuhkan orkestrator kubernetes[^2].\n\n[^1]: Standard IEEE 2026\n[^2]: CNCF Cloud Foundation"
        rendered = parse_markdown_footnotes(raw)
        self.assertIn('<sup class="tu-footnote-ref"><a href="#fn-1" id="fnref-1">[1]</a></sup>', rendered)
        self.assertIn('<div class="tu-footnotes">', rendered)
        self.assertIn('<li id="fn-1"><p>Standard IEEE 2026', rendered)
        self.assertIn('<a href="#fnref-1" class="tu-footnote-backref"', rendered)

    def test_extract_keyword_frequency(self):
        from parser import extract_keyword_frequency
        sample = "<p>Jaringan komputer dan keamanan komputer sangat penting dalam arsitektur komputer modern.</p>"
        unigrams = extract_keyword_frequency(sample, n_gram=1, top_n=3)
        self.assertEqual(unigrams[0][0], "komputer")
        self.assertEqual(unigrams[0][1], 3)
        bigrams = extract_keyword_frequency(sample, n_gram=2, top_n=2)
        self.assertIn("jaringan komputer", [bg[0] for bg in bigrams])

    def test_parse_math_blocks(self):
        from parser import parse_math_blocks
        raw = "Rumus kompleksitas waktu adalah $O(n \\log n)$ dan rumus energi:\n\n$$E = mc^2$$\n\nBiaya sensor adalah $50 per unit."
        rendered = parse_math_blocks(raw)
        self.assertIn('<span class="tu-math-inline"><code>O(n \\log n)</code></span>', rendered)
        self.assertIn('<div class="tu-math-block"><code>E = mc^2</code></div>', rendered)
        self.assertIn('$50', rendered)

    def test_get_indonesian_reading_level_label(self):
        from parser import get_indonesian_reading_level_label
        self.assertEqual(get_indonesian_reading_level_label(85.0), "Sangat Mudah Dipahami (Populer / Umum)")
        self.assertEqual(get_indonesian_reading_level_label(65.0), "Standar Editorial Edukasi & Blog")
        self.assertEqual(get_indonesian_reading_level_label(45.0), "Teks Teknis & Akademik Mahasiswa")
        self.assertEqual(get_indonesian_reading_level_label(25.0), "Jurnal Ilmiah & Makalah Riset Lanjutan")
        self.assertEqual(get_indonesian_reading_level_label(10.0), "Monograf Riset Khusus / Sangat Padat")

    def test_parse_markdown_task_lists(self):
        from parser import parse_markdown_task_lists
        raw = "- [x] Menginstal toolchain Rust\n- [ ] Kompilasi target wasm32-wasi"
        rendered = parse_markdown_task_lists(raw)
        self.assertIn('<ul class="tu-task-list">', rendered)
        self.assertIn('<input type="checkbox" checked disabled />', rendered)
        self.assertIn('<input type="checkbox" disabled />', rendered)

    def test_generate_unique_heading_slugs(self):
        from parser import generate_unique_heading_slugs
        headings = [
            {"tag": "h2", "text": "Pengantar"},
            {"tag": "h2", "text": "Metodologi"},
            {"tag": "h2", "text": "Pengantar"}
        ]
        result = generate_unique_heading_slugs(headings)
        self.assertEqual(result[0]["slug"], "pengantar")
        self.assertEqual(result[1]["slug"], "metodologi")
        self.assertEqual(result[2]["slug"], "pengantar-2")

    def test_parse_academic_citations(self):
        from parser import parse_academic_citations, extract_citation_keys
        text = "Menurut studi terbaru [@tanenbaum2021], sistem terdistribusi berkembang pesat [lihat @kurniawan2023, hal. 45]."
        rendered = parse_academic_citations(text)
        self.assertIn('<cite class="tu-citation" data-cite-key="tanenbaum2021">[@tanenbaum2021]</cite>', rendered)
        self.assertIn('data-cite-key="kurniawan2023"', rendered)

        keys = extract_citation_keys(text)
        self.assertEqual(keys, ["tanenbaum2021", "kurniawan2023"])

    def test_expand_indonesian_acronyms(self):
        from parser import expand_indonesian_acronyms
        raw = "Mahasiswa wajib mengisi KRS pada awal semester. KRS harus disetujui PA."
        expanded = expand_indonesian_acronyms(raw)
        self.assertIn('<abbr title="Kartu Rencana Studi">KRS</abbr>', expanded)
        self.assertIn('<abbr title="Pembimbing Akademik">PA</abbr>', expanded)
        # Second KRS should not be wrapped again
        self.assertEqual(expanded.count('<abbr title="Kartu Rencana Studi">KRS</abbr>'), 1)

    def test_normalize_markdown_code_blocks(self):
        from parser import normalize_markdown_code_blocks
        markdown = "Berikut script:\n\n```py\ndef hitung(x):\n    return x * 2\n```\n\n```\nconst val = 42;\n```"
        html = normalize_markdown_code_blocks(markdown)
        self.assertIn('<pre class="tu-code-block"><code class="language-python">def hitung(x):', html)
        self.assertIn('<code class="language-javascript">const val = 42;</code>', html)

    def test_extract_paragraph_transitions(self):
        from parser import extract_paragraph_transitions
        article = (
            "<p>Kecerdasan buatan berkembang dengan cepat di Indonesia. Berbagai inovasi terus bermunculan di kampus. Oleh karena itu, kurikulum harus beradaptasi.</p>\n\n"
            "<p>Tantangan utama adalah ketersediaan komputasi berkecepatan tinggi. Mahasiswa membutuhkan akses GPU. Dengan demikian, investasi laboratorium menjadi krusial.</p>"
        )
        transitions = extract_paragraph_transitions(article)
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["paragraph_index"], 1)
        self.assertIn("Kecerdasan buatan", transitions[0]["topic_sentence"])
        self.assertIn("kurikulum harus beradaptasi", transitions[0]["concluding_sentence"])
        self.assertEqual(transitions[0]["sentence_count"], 3)
        self.assertGreater(transitions[0]["word_count"], 10)

if __name__ == "__main__":
    unittest.main()

