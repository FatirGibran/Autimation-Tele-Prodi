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

    def test_normalize_academic_degrees(self):
        from parser import normalize_academic_degrees
        raw = "Dosen pembimbing adalah Budi S Kom M Kom dan Dr Ir Hendra Ph D."
        norm = normalize_academic_degrees(raw)
        self.assertIn("S.Kom.", norm)
        self.assertIn("M.Kom.", norm)
        self.assertIn("Dr.", norm)
        self.assertIn("Ir.", norm)
        self.assertIn("Ph.D.", norm)

    def test_parse_course_curriculum_codes(self):
        from parser import parse_course_curriculum_codes
        text = "Mata kuliah wajib IF2143 Struktur Data dan TIF101 Pemrograman Dasar serta pilihan CSI402."
        codes = parse_course_curriculum_codes(text)
        self.assertEqual(len(codes), 3)
        codes_dict = {c["code"]: c for c in codes}
        self.assertIn("IF2143", codes_dict)
        self.assertEqual(codes_dict["IF2143"]["department_prefix"], "IF")
        self.assertEqual(codes_dict["IF2143"]["level"], 2)
        self.assertEqual(codes_dict["TIF101"]["department_prefix"], "TIF")
        self.assertEqual(codes_dict["TIF101"]["level"], 1)

    def test_balance_and_clean_quotes(self):
        from parser import balance_and_clean_quotes
        balanced = balance_and_clean_quotes('Direktur menyatakan, "Kurikulum baru siap diimplementasikan.')
        self.assertTrue(balanced.startswith('Direktur menyatakan, “Kurikulum baru'))
        self.assertTrue(balanced.endswith('”'))
        self.assertEqual(balanced.count('“'), balanced.count('”'))

    def test_italicize_academic_latin_terms(self):
        from parser import italicize_academic_latin_terms
        raw = "<p>Menurut Smith et al. metode ini ad hoc dan de facto berlaku.</p><pre><code>print('et al.')</code></pre>"
        res = italicize_academic_latin_terms(raw)
        self.assertIn("<em>et al.</em>", res)
        self.assertIn("<em>ad hoc</em>", res)
        self.assertIn("<em>de facto</em>", res)
        self.assertIn("<code>print('et al.')</code>", res)

    def test_wrap_glossary_terms(self):
        from parser import wrap_glossary_terms
        glossary = {
            "IoT": "Internet of Things",
            "Machine Learning": "Cabang AI berfokus pada pembelajaran dari data",
        }
        text = "<p>Penerapan Machine Learning dan IoT sangat vital.</p><code>IoT</code>"
        res = wrap_glossary_terms(text, glossary)
        self.assertIn('<dfn title="Cabang AI berfokus pada pembelajaran dari data">Machine Learning</dfn>', res)
        self.assertIn('<dfn title="Internet of Things">IoT</dfn>', res)
        self.assertIn('<code>IoT</code>', res)

    def test_parse_indonesian_formal_date(self):
        from parser import parse_indonesian_formal_date
        parsed = parse_indonesian_formal_date("Senin, 14 Oktober 2024 15:30 WIB")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["day"], 14)
        self.assertEqual(parsed["month"], 10)
        self.assertEqual(parsed["year"], 2024)
        self.assertEqual(parsed["timezone"], "WIB")
        self.assertEqual(parsed["iso_date"], "2024-10-14T15:30:00")

    def test_extract_research_cluster_tags(self):
        from parser import extract_research_cluster_tags
        text = "Penelitian ini mengembangkan arsitektur deep learning dan sistem sensor iot untuk smart campus."
        tags = extract_research_cluster_tags(text)
        self.assertIn("Artificial Intelligence & Data Science", tags)
        self.assertIn("Internet of Things & Embedded Systems", tags)

    def test_normalize_nested_list_indentation(self):
        from parser import normalize_nested_list_indentation
        raw = "- Level 1\n   - Level 2 misaligned\n     - Level 3"
        norm = normalize_nested_list_indentation(raw)
        lines = norm.splitlines()
        self.assertEqual(lines[0], "- Level 1")
        self.assertEqual(lines[1], "  - Level 2 misaligned")
        self.assertEqual(lines[2], "    - Level 3")

    def test_calculate_total_sks_credits(self):
        from parser import calculate_total_sks_credits
        text = "Mata kuliah terdiri dari 3 SKS Teori dan 1 SKS Praktikum di Lab Informatika."
        credits = calculate_total_sks_credits(text)
        self.assertEqual(credits["total_sks"], 4)
        self.assertEqual(credits["theory_sks"], 3)
        self.assertEqual(credits["practical_sks"], 1)
        self.assertEqual(credits["mentions_count"], 2)

    def test_validate_academic_advisor_credentials(self):
        from parser import validate_academic_advisor_credentials
        text = "Pembimbing 1: Dr. Ir. Budi Santoso, S.Kom., M.Kom.\nPenguji 1: Prof. Dr. Hendra, Ph.D."
        advisors = validate_academic_advisor_credentials(text)
        self.assertEqual(len(advisors), 2)
        self.assertTrue(advisors[0]["has_doctorate"])
        self.assertTrue(advisors[0]["is_qualified_for_defense"])
        self.assertEqual(advisors[1]["role"], "Penguji 1")

    def test_expand_academic_acronyms(self):
        from parser import expand_academic_acronyms
        text = "<p>Mahasiswa wajib mengikuti program MBKM dan mengisi KRS semester ganjil.</p><code>KRS</code>"
        expanded = expand_academic_acronyms(text)
        self.assertIn('<abbr title="Merdeka Belajar Kampus Merdeka">MBKM</abbr>', expanded)
        self.assertIn('<abbr title="Kartu Rencana Studi">KRS</abbr>', expanded)
        self.assertIn('<code>KRS</code>', expanded)

    def test_normalize_code_block_language_tags(self):
        from parser import normalize_code_block_language_tags
        md = "Contoh kode:\n```py\nprint('hello')\n```\nDan skrip bash:\n```sh\necho hi\n```"
        norm = normalize_code_block_language_tags(md)
        self.assertIn("```python", norm)
        self.assertIn("```bash", norm)

    def test_parse_curriculum_semester_plan(self):
        from parser import parse_curriculum_semester_plan
        md = (
            "### Semester 1\n"
            "- CS101 Pengantar Pemrograman (3 SKS) [Wajib]\n"
            "- MA101 Kalkulus 1 (4 SKS)\n\n"
            "### Semester 2\n"
            "- IF201 Struktur Data (3 SKS)\n"
            "- IF202 Bahasa Inggris Teknis (2 SKS) [Pilihan]\n"
        )
        plan = parse_curriculum_semester_plan(md)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0]["semester"], 1)
        self.assertEqual(plan[0]["total_credits"], 7)
        self.assertFalse(plan[0]["courses"][0]["is_elective"])
        self.assertEqual(plan[1]["semester"], 2)
        self.assertEqual(plan[1]["total_credits"], 5)
        self.assertTrue(plan[1]["courses"][1]["is_elective"])

    def test_parse_lab_safety_guidelines(self):
        from parser import parse_lab_safety_guidelines
        text = (
            "**Aturan APD Laboratorium**:\n"
            "- Wajib memakai jas laboratorium berwarna putih\n"
            "- Gunakan kacamata pelindung saat menyolder\n\n"
            "**Tanggap Darurat**:\n"
            "- Segera tekan tombol darurat bila terjadi korsleting\n"
        )
        rules = parse_lab_safety_guidelines(text)
        self.assertEqual(len(rules), 3)
        self.assertEqual(rules[0]["category"], "Alat Pelindung Diri (APD)")
        self.assertIn("jas laboratorium", rules[0]["rule"])
        self.assertEqual(rules[2]["category"], "Tanggap Darurat")

    def test_validate_and_format_bibliographic_ids(self):
        from parser import validate_and_format_bibliographic_ids
        text = "Referensi buku: ISBN 9786022620128 dan versi lama ISBN 0131103628 serta jurnal dengan ISSN 2088-3285."
        res = validate_and_format_bibliographic_ids(text)
        self.assertIn("978-60-22620-12-8", res["isbn"])
        self.assertIn("01-3110-362-8", res["isbn"])
        self.assertIn("2088-3285", res["issn"])

    def test_parse_academic_calendar_range(self):
        from parser import parse_academic_calendar_range
        res1 = parse_academic_calendar_range("12 - 24 Agustus 2026")
        self.assertIsNotNone(res1)
        self.assertEqual(res1["start_iso"], "2026-08-12")
        self.assertEqual(res1["end_iso"], "2026-08-24")
        self.assertEqual(res1["days_span"], 13)

        res2 = parse_academic_calendar_range("28 Juli - 15 Agustus 2026")
        self.assertIsNotNone(res2)
        self.assertEqual(res2["start_iso"], "2026-07-28")
        self.assertEqual(res2["end_iso"], "2026-08-15")
        self.assertEqual(res2["days_span"], 19)

    def test_parse_lab_inventory_specs_table_and_list(self):
        from parser import parse_lab_inventory_specs
        # Table format
        table_md = """
| Nama Alat | Kategori | Jumlah | Kondisi | Spesifikasi |
|---|---|---|---|---|
| NVIDIA DGX Station | Server AI | 2 unit | Siap Pakai | 4x A100 GPU 320GB |
| Switch Cisco 2960 | Jaringan | 6 unit | Berfungsi Baik | 24-Port Gigabit |
"""
        res_table = parse_lab_inventory_specs(table_md)
        self.assertEqual(len(res_table), 2)
        self.assertEqual(res_table[0]["name"], "NVIDIA DGX Station")
        self.assertEqual(res_table[0]["quantity"], 2)
        self.assertEqual(res_table[1]["category"], "Jaringan")

        # List format
        list_md = "- Workstation Dell Precision: 8 unit [Kondisi: Baik] (Intel Xeon, 64GB RAM)"
        res_list = parse_lab_inventory_specs(list_md)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]["name"], "Workstation Dell Precision")
        self.assertEqual(res_list[0]["quantity"], 8)
        self.assertEqual(res_list[0]["condition"], "Baik")

    def test_parse_apa_journal_citations(self):
        from parser import parse_apa_journal_citations
        cite_text = "Santoso, B., & Rahma, S. (2024). Deep learning optimization on edge devices. IEEE Internet of Things Journal, 11(2), 1234-1245. https://doi.org/10.1109/JIOT.2024.123456"
        res = parse_apa_journal_citations(cite_text)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["year"], 2024)
        self.assertEqual(res[0]["journal"], "IEEE Internet of Things Journal")
        self.assertEqual(res[0]["volume"], "11")
        self.assertEqual(res[0]["issue"], "2")
        self.assertEqual(res[0]["pages"], "1234-1245")
        self.assertEqual(res[0]["doi"], "https://doi.org/10.1109/JIOT.2024.123456")

    def test_parse_defense_rubric_criteria(self):
        from parser import parse_defense_rubric_criteria
        rubric_md = """
- Metodologi Riset & Analisis Kebutuhan (30%) [CPL-02]: Ketepatan metode perancangan perangkat lunak
- Penguasaan Teori & Argumentasi (40%) [CPL-01]: Penguasaan substansi komputasi
- Kualitas Prototipe Aplikasi (30%) [CPL-03]: Fungsionalitas produk
"""
        res = parse_defense_rubric_criteria(rubric_md)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]["criteria"], "Metodologi Riset & Analisis Kebutuhan")
        self.assertEqual(res[0]["weight_percentage"], 30)
        self.assertEqual(res[0]["cpl_target"], "CPL-02")

    def test_convert_indonesian_grade_letter_and_gpa(self):
        from parser import convert_indonesian_grade_letter, calculate_weighted_semester_gpa
        g_a = convert_indonesian_grade_letter("A")
        self.assertEqual(g_a["gpa_point"], 4.0)
        self.assertTrue(g_a["is_passing"])

        g_ab = convert_indonesian_grade_letter("AB")
        self.assertEqual(g_ab["gpa_point"], 3.5)

        g_e = convert_indonesian_grade_letter("E")
        self.assertEqual(g_e["gpa_point"], 0.0)
        self.assertFalse(g_e["is_passing"])

        # Semester GPA calculation
        courses = [
            {"code": "IF2143", "credits": 4, "grade": "A"},   # 4 * 4.0 = 16.0
            {"code": "IF2144", "credits": 3, "grade": "AB"},  # 3 * 3.5 = 10.5
            {"code": "IF2145", "credits": 3, "grade": "B"},   # 3 * 3.0 = 9.0
        ]
        # Total SKS = 10, total points = 35.5, GPA = 3.55
        calc = calculate_weighted_semester_gpa(courses)
        self.assertEqual(calc["total_credits"], 10)
        self.assertEqual(calc["gpa"], 3.55)
        self.assertEqual(calc["academic_standing"], "Dengan Pujian (Cum Laude)")

if __name__ == "__main__":
    unittest.main()


