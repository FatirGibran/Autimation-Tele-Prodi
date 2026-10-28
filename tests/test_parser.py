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

    def test_parse_ieee_journal_citation(self):
        from parser import parse_ieee_journal_citation
        cit = (
            'J. K. Author and A. B. Coauthor, "Distributed Edge Inference Architecture for IoT Sensors," '
            'IEEE Trans. Commun., vol. 68, no. 4, pp. 2400-2412, Apr. 2020, doi: 10.1109/TCOMM.2020.1234567.'
        )
        res = parse_ieee_journal_citation(cit)
        self.assertIsNotNone(res)
        self.assertEqual(res["title"], "Distributed Edge Inference Architecture for IoT Sensors")
        self.assertIn("J. K. Author", res["authors"])
        self.assertIn("A. B. Coauthor", res["authors"])
        self.assertEqual(res["journal"], "IEEE Trans. Commun.")
        self.assertEqual(res["volume"], "68")
        self.assertEqual(res["issue"], "4")
        self.assertEqual(res["pages"], "2400-2412")
        self.assertEqual(res["year"], 2020)
        self.assertEqual(res["doi"], "10.1109/TCOMM.2020.1234567")

    def test_parse_laboratory_sop(self):
        from parser import parse_laboratory_sop
        raw_sop = """
SOP-LAB-012: Pengujian Spektrum Frekuensi Radio
Bahaya Tinggi (High Hazard Level 3)
1. Periksa kabel catu daya dan grounding sebelum menyalakan instrumen spectrum analyzer.
2. Pasang attenuator 30 dB pada port RF. Peringatan: daya melebihi +30 dBm dapat merusak mixer input!
3. Nyalakan perangkat dan lakukan sweep frequency rentang 1 GHz - 6 GHz.
"""
        res = parse_laboratory_sop(raw_sop)
        self.assertIsNotNone(res)
        self.assertEqual(res["sop_code"], "SOP-LAB-012")
        self.assertEqual(res["hazard_level"], "Tinggi")
        self.assertEqual(res["total_steps"], 3)
        self.assertTrue(res["steps"][1]["has_safety_warning"])
        self.assertFalse(res["steps"][0]["has_safety_warning"])

    def test_parse_scholarship_eligibility(self):
        from parser import parse_scholarship_eligibility
        text = """
Persyaratan Pendaftaran Beasiswa Riset Telkom 2026:
- IPK minimal 3.50
- Terbuka untuk mahasiswa aktif semester 3 - 6
- Melampirkan KTM, Transkrip Nilai, dan Surat Rekomendasi Dosen
- Lolos seleksi berkas dan tahap wawancara
- Skema Beasiswa Penuh (Full Coverage)
"""
        res = parse_scholarship_eligibility(text)
        self.assertEqual(res["min_gpa"], 3.50)
        self.assertEqual(res["target_semesters"], [3, 4, 5, 6])
        self.assertIn("Transkrip Nilai", res["required_documents"])
        self.assertIn("Surat Rekomendasi Dosen", res["required_documents"])
        self.assertTrue(res["requires_interview"])
        self.assertTrue(res["is_full_coverage"])

    def test_calculate_sks_to_ects(self):
        from parser import calculate_sks_to_ects
        res = calculate_sks_to_ects(20, ects_ratio=1.6)
        self.assertEqual(res["sks_credits"], 20)
        self.assertEqual(res["ects_credits"], 32.0)
        self.assertGreater(res["workload_hours_per_semester"], 800)
        self.assertGreater(res["workload_hours_per_week"], 50)

    def test_parse_acm_citation(self):
        from parser import parse_acm_citation
        cit = "F. Gibran and B. Santoso. 2026. Automated Editorial Pipeline for Academic Systems. In Proceedings of the 2026 ACM Conference on Software Engineering (ICSE '26). ACM, New York, NY, USA, 101–110. https://doi.org/10.1145/1234567.8901234"
        res = parse_acm_citation(cit)
        self.assertEqual(len(res["authors"]), 2)
        self.assertEqual(res["year"], 2026)
        self.assertIn("Automated Editorial Pipeline", res["title"])
        self.assertEqual(res["pages"], "101-110")
        self.assertIn("10.1145/1234567.8901234", res["doi"])

    def test_calculate_defense_rubric_grade(self):
        from parser import calculate_defense_rubric_grade
        rubrics = [
            {"criteria": "Penguasaan Materi & Teori", "weight_pct": 30.0, "score": 85.0},
            {"criteria": "Metodologi Riset & Analisis", "weight_pct": 30.0, "score": 80.0},
            {"criteria": "Implementasi & Pengujian Sistem", "weight_pct": 25.0, "score": 90.0},
            {"criteria": "Presentasi & Tanya Jawab", "weight_pct": 15.0, "score": 80.0}
        ]
        res = calculate_defense_rubric_grade(rubrics)
        self.assertGreaterEqual(res["total_score"], 80.0)
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["grade_point"], 4.00)
        self.assertTrue(res["is_passed"])
        self.assertIn("Cumlaude", res["predicate"])

    def test_parse_internship_weekly_logbook(self):
        from parser import parse_internship_weekly_logbook
        logbook = """
### Minggu 1 (1 - 5 September 2026)
- Aktivitas: Setup lingkungan Docker dan Kubernetes cluster.
- Kompetensi: Container orchestration, Linux administration
- Status: Disetujui (Approved)

### Minggu 2 (8 - 12 September 2026)
- Aktivitas: Implementasi pipeline CI/CD GitLab.
- Kompetensi: DevOps, Bash scripting
- Status: Pending
"""
        entries = parse_internship_weekly_logbook(logbook)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["week_number"], 1)
        self.assertEqual(entries[0]["date_range"], "1 - 5 September 2026")
        self.assertIn("Docker dan Kubernetes", entries[0]["activities"])
        self.assertIn("Container orchestration", entries[0]["competencies"])
        self.assertTrue(entries[0]["is_approved"])
        self.assertFalse(entries[1]["is_approved"])

    def test_parse_lab_equipment_maintenance_log(self):
        from parser import parse_lab_equipment_maintenance_log
        log_text = """
Equipment: Spectrum Analyzer Agilent N9020A (LAB-RF-004)
Date: 10 Oktober 2026
Technician: Ir. Bambang Supeno, M.T.
Issue: Drift frekuensi LO pada pita 10 GHz melebihi batas.
Resolution: Penggantian osilator kristal TCXO dan kalibrasi ISO 17025.
Calibration Validity: 10 Oktober 2027
Status: Operasional Siap Pakai
"""
        res = parse_lab_equipment_maintenance_log(log_text)
        self.assertEqual(res["equipment_name"], "Spectrum Analyzer Agilent N9020A")
        self.assertEqual(res["equipment_id"], "LAB-RF-004")
        self.assertEqual(res["maintenance_date"], "10 Oktober 2026")
        self.assertEqual(res["technician"], "Ir. Bambang Supeno, M.T.")
        self.assertIn("Drift frekuensi", res["issue"])
        self.assertTrue(res["is_operational"])

    def test_parse_springer_citation(self):
        from parser import parse_springer_citation
        cit = (
            "Gibran, F., Pratama, A.: Autonomous Agent Pipelines in Telecommunications. "
            "In: Kurniawan, D. (ed.) Proceedings of ICCS 2026. LNCS, vol. 14500, pp. 45–58. "
            "Springer, Cham (2026). https://doi.org/10.1007/978-3-030-99999-9_4"
        )
        res = parse_springer_citation(cit)
        self.assertIsNotNone(res)
        self.assertIn("Gibran", res["authors"])
        self.assertIn("Autonomous Agent Pipelines", res["title"])
        self.assertEqual(res["series"], "LNCS")
        self.assertEqual(res["volume"], 14500)
        self.assertEqual(res["pages"], "45-58")
        self.assertEqual(res["year"], 2026)
        self.assertEqual(res["publisher"], "Springer")
        self.assertIn("10.1007/978-3-030-99999-9_4", res["doi"])

    def test_parse_proposal_defense_eligibility(self):
        from parser import parse_proposal_defense_eligibility
        chk = "KRS disetujui dosen wali, bebas lab selesai, bebas perpustakaan valid, bimbingan minimal 8 kali acc"
        res_ok = parse_proposal_defense_eligibility(chk, earned_sks=110, ipk=3.55, toefl_score=480)
        self.assertTrue(res_ok["is_eligible"])
        self.assertEqual(len(res_ok["missing_requirements"]), 0)

        chk_fail = "KRS disetujui tapi belum bebas lab"
        res_fail = parse_proposal_defense_eligibility(chk_fail, earned_sks=95, ipk=2.60, toefl_score=420)
        self.assertFalse(res_fail["is_eligible"])
        self.assertFalse(res_fail["sks_passed"])
        self.assertFalse(res_fail["ipk_passed"])
        self.assertFalse(res_fail["toefl_passed"])
        self.assertGreaterEqual(len(res_fail["missing_requirements"]), 3)

    def test_parse_community_service_log(self):
        from parser import parse_community_service_log
        log_text = """
Judul: Pelatihan Digital Marketing & Keamanan Siber untuk UMKM Desa Sumbang
Mitra: Paguyuban UMKM Mandiri Sumbang
Lokasi: Banyumas, Jawa Tengah
Sumber Dana: Hibah Internal Pengabdian LPPM Telkom University
Jumlah Penerima: 45
SDGs: SDG 9 - Industri, Inovasi, dan Infrastruktur
"""
        res = parse_community_service_log(log_text)
        self.assertIsNotNone(res)
        self.assertIn("Pelatihan Digital Marketing", res["title"])
        self.assertEqual(res["partner"], "Paguyuban UMKM Mandiri Sumbang")
        self.assertEqual(res["location"], "Banyumas, Jawa Tengah")
        self.assertEqual(res["beneficiaries_count"], 45)
        self.assertEqual(res["sdgs_theme"], "SDG 9 - Industri, Inovasi, dan Infrastruktur")

    def test_parse_lab_safety_inspection(self):
        from parser import parse_lab_safety_inspection
        audit_text = """
Lab: Laboratorium Sistem Transmisi & Optik
Inspektur: Tri Widyastuti, S.T., M.Eng.
Tanggal: 12 Oktober 2026
APAR: Siap Pakai dan tidak kedaluwarsa
P3K: Lengkap dengan perban dan antiseptik
Jalur Evakuasi: Bebas hambatan menuju tangga darurat
Instalasi Listrik: Rapi dan memenuhi standar K3
"""
        res = parse_lab_safety_inspection(audit_text)
        self.assertEqual(res["lab_name"], "Laboratorium Sistem Transmisi & Optik")
        self.assertEqual(res["inspector"], "Tri Widyastuti, S.T., M.Eng.")
        self.assertEqual(res["compliance_score"], 100.0)
        self.assertTrue(res["is_passed"])
        self.assertTrue(res["checks"]["apar_ready"])

    def test_parse_harvard_citation(self):
        from parser import parse_harvard_citation
        cit_journal = "Gibran, F. and Santoso, B. (2025) 'Zero-trust edge security in telecommunication microservices', Journal of Systems Architecture, 18(3), pp. 112-126. doi: 10.1016/j.sysarc.2025.102."
        res = parse_harvard_citation(cit_journal)
        self.assertIsNotNone(res)
        self.assertEqual(res["year"], 2025)
        self.assertIn("Gibran, F.", res["authors"])
        self.assertEqual(res["title"], "Zero-trust edge security in telecommunication microservices")
        self.assertIn("Journal of Systems Architecture", res["publication"])
        self.assertEqual(res["volume_issue"], "18(3)")
        self.assertEqual(res["pages"], "112-126")
        self.assertIn("10.1016/j.sysarc.2025.102", res["doi_or_url"])

    def test_validate_mbkm_credit_transfer(self):
        from parser import validate_mbkm_credit_transfer
        valid_data = {
            "program_name": "Bangkit Academy 2026 Cloud Computing",
            "partner_institution": "Google & GoTo",
            "student_name": "Fatir Gibran",
            "nim": "120122001",
            "semester": 6,
            "courses_mapped": [
                {"course_code": "IF3101", "course_name": "Cloud Computing Architecture", "sks": 4, "score_letter": "A"},
                {"course_code": "IF3102", "course_name": "Microservices Development", "sks": 4, "score_letter": "A"},
                {"course_code": "IF3103", "course_name": "DevOps Engineering", "sks": 4, "score_letter": "AB"},
                {"course_code": "IF3104", "course_name": "Capstone Project", "sks": 6, "score_letter": "A"}
            ]
        }
        res_ok = validate_mbkm_credit_transfer(valid_data)
        self.assertTrue(res_ok["is_approved"])
        self.assertEqual(res_ok["total_sks"], 18)
        self.assertGreater(res_ok["converted_gpa"], 3.7)

        # Over-limit test (>20 SKS)
        overflow_data = dict(valid_data)
        overflow_data["courses_mapped"] = valid_data["courses_mapped"] + [
            {"course_code": "IF3105", "course_name": "Extra Elective", "sks": 4, "score_letter": "B"}
        ]
        res_overflow = validate_mbkm_credit_transfer(overflow_data)
        self.assertFalse(res_overflow["is_approved"])
        self.assertEqual(res_overflow["total_sks"], 22)
        self.assertTrue(any("melebihi batas" in i for i in res_overflow["issues"]))

    def test_parse_lab_equipment_log(self):
        from parser import parse_lab_equipment_log
        log_text = """
ID Aset: LAB-RF-2026-088
Nama Alat: Digital Spectrum Analyzer 13.6 GHz
Lab: Laboratorium Sistem Transmisi & RF
Model: Rohde & Schwarz FPH
Tgl Kalibrasi: 2026-01-15
Due Date: 2027-01-15
Kondisi: Baik
PIC: Laboran Ahmad Firdaus, S.T.
"""
        res = parse_lab_equipment_log(log_text)
        self.assertIsNotNone(res)
        self.assertEqual(res["asset_id"], "LAB-RF-2026-088")
        self.assertEqual(res["equipment_name"], "Digital Spectrum Analyzer 13.6 GHz")
        self.assertEqual(res["lab_name"], "Laboratorium Sistem Transmisi & RF")
        self.assertEqual(res["operating_condition"], "Baik")
        self.assertEqual(res["calibration_status"], "Valid")
        self.assertEqual(res["pic"], "Laboran Ahmad Firdaus, S.T.")

    def test_validate_yudisium_clearance(self):
        from parser import validate_yudisium_clearance
        candidate_ok = {
            "student_name": "Fatir Gibran",
            "nim": "120122001",
            "earned_sks": 146,
            "ipk": 3.82,
            "sks_d": 0,
            "sks_e": 0,
            "toefl_score": 525,
            "skk_points": 55,
            "library_clearance": True,
            "lab_clearance": True,
            "tuition_clearance": True,
            "thesis_repository_uploaded": True
        }
        res_ok = validate_yudisium_clearance(candidate_ok)
        self.assertTrue(res_ok["is_eligible"])
        self.assertEqual(res_ok["graduation_predicate"], "Dengan Pujian (Cum Laude)")
        self.assertEqual(len(res_ok["issues"]), 0)

        candidate_fail = dict(candidate_ok)
        candidate_fail["earned_sks"] = 138
        candidate_fail["toefl_score"] = 410
        candidate_fail["lab_clearance"] = False
        res_fail = validate_yudisium_clearance(candidate_fail)
        self.assertFalse(res_fail["is_eligible"])
        self.assertEqual(res_fail["graduation_predicate"], "Belum Memenuhi Syarat")
        self.assertGreaterEqual(len(res_fail["issues"]), 3)

    def test_parse_vancouver_citations(self):
        from parser import parse_vancouver_citations
        cit_text = """
[1] Gibran F, Santoso B. IoT Telemetry based on LoRaWAN for Smart Healthcare. IEEE Trans Biomed Eng. 2026;73(2):112-120. doi:10.1109/TBME.2026.12345
[2] Halpern SD, Ubel PA, Caplan AL. Solid-organ transplantation in HIV-infected patients. N Engl J Med. 2002;347(4):284-7.
"""
        res = parse_vancouver_citations(cit_text)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["citation_index"], 1)
        self.assertIn("Gibran F", res[0]["authors"])
        self.assertEqual(res[0]["title"], "IoT Telemetry based on LoRaWAN for Smart Healthcare")
        self.assertEqual(res[0]["journal"], "IEEE Trans Biomed Eng")
        self.assertEqual(res[0]["year"], 2026)
        self.assertEqual(res[0]["volume"], "73")
        self.assertEqual(res[0]["issue"], "2")
        self.assertEqual(res[0]["pages"], "112-120")
        self.assertIn("10.1109/TBME.2026.12345", res[0]["doi"])

        self.assertEqual(res[1]["citation_index"], 2)
        self.assertEqual(res[1]["year"], 2002)

    def test_audit_academic_probation_status(self):
        from parser import audit_academic_probation_status
        ok_student = {
            "student_name": "Rian Pratama",
            "nim": "120122010",
            "semester": 4,
            "gpa_cumulative": 3.45,
            "gpa_semester": 3.50,
            "earned_credits": 76,
            "sp_history": 0
        }
        res_ok = audit_academic_probation_status(ok_student)
        self.assertEqual(res_ok["status"], "CLEAR")
        self.assertFalse(res_ok["counseling_required"])
        self.assertEqual(res_ok["remedial_sks_needed"], 0)

        warn_student = {
            "student_name": "Budi Santoso",
            "nim": "120122011",
            "semester": 4,
            "gpa_cumulative": 2.10,
            "gpa_semester": 1.75,
            "earned_credits": 40,
            "sp_history": 1
        }
        res_warn = audit_academic_probation_status(warn_student)
        self.assertEqual(res_warn["status"], "WARNING_2")
        self.assertTrue(res_warn["counseling_required"])
        self.assertEqual(res_warn["remedial_sks_needed"], 8)
        self.assertTrue(any("Perolehan SKS" in r for r in res_warn["reasons"]))

    def test_evaluate_faculty_bkd_workload(self):
        from parser import evaluate_faculty_bkd_workload
        faculty_ok = {
            "lecturer_name": "Dr. Eng. Ir. Suryo",
            "nidn": "0612345601",
            "academic_rank": "Lektor Kepala",
            "teaching_credits": 8.0,
            "research_credits": 3.0,
            "service_credits": 1.5,
            "supporting_credits": 1.0
        }
        res_ok = evaluate_faculty_bkd_workload(faculty_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["status"], "MEMENUHI")
        self.assertEqual(res_ok["total_sks"], 13.5)
        self.assertEqual(res_ok["core_subtotal"], 11.0)
        self.assertEqual(len(res_ok["issues"]), 0)

        faculty_under = {
            "lecturer_name": "Dosen Baru, M.T.",
            "nidn": "0612345602",
            "teaching_credits": 4.0,
            "research_credits": 1.0,
            "service_credits": 0.0,
            "supporting_credits": 0.0
        }
        res_under = evaluate_faculty_bkd_workload(faculty_under)
        self.assertFalse(res_under["is_compliant"])
        self.assertEqual(res_under["status"], "TIDAK MEMENUHI")
        self.assertEqual(res_under["total_sks"], 5.0)
        self.assertTrue(any("kurang dari batas minimum" in i for i in res_under["issues"]))

    def test_parse_kkn_village_assignment(self):
        from parser import parse_kkn_village_assignment
        table_md = """
| Kelompok | Desa | Kecamatan | Kabupaten | DPL | Mahasiswa | Tema |
|---|---|---|---|---|---|---|
| KKN-01 | Beji | Kedungbanteng | Banyumas | Dr. Ir. Budi | 12 Mhs | Smart Village & IoT Pertanian |
| KKN-02 | Karangcegak | Sumbang | Banyumas | Dra. Siti, M.T. | 10 Mhs | Digitalisasi UMKM Desa |
"""
        res_table = parse_kkn_village_assignment(table_md)
        self.assertEqual(len(res_table), 2)
        self.assertEqual(res_table[0]["group_code"], "KKN-01")
        self.assertEqual(res_table[0]["village_name"], "Beji")
        self.assertEqual(res_table[0]["district_name"], "Kedungbanteng")
        self.assertEqual(res_table[0]["regency_name"], "Banyumas")
        self.assertEqual(res_table[0]["student_count"], 12)
        self.assertIn("Smart Village", res_table[0]["thematic_focus"])

        list_md = "- Kelompok KKN-03: Desa Melung, Kec. Kedungbanteng, Kab. Banyumas | DPL: Ir. Hadi | 11 Mhs | Tema: Wisata Digital"
        res_list = parse_kkn_village_assignment(list_md)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]["village_name"], "Melung")
        self.assertEqual(res_list[0]["student_count"], 11)

    def test_normalize_ieee_doi(self):
        from parser import normalize_ieee_doi
        # Full URL
        res1 = normalize_ieee_doi("https://doi.org/10.1109/TWC.2026.1234567")
        self.assertIsNotNone(res1)
        self.assertEqual(res1["prefix"], "10.1109")
        self.assertEqual(res1["suffix"], "TWC.2026.1234567")
        self.assertEqual(res1["canonical_url"], "https://doi.org/10.1109/TWC.2026.1234567")
        self.assertTrue(res1["is_ieee"])

        # Plain DOI
        res2 = normalize_ieee_doi("doi: 10.1016/j.comnet.2026.01.002")
        self.assertIsNotNone(res2)
        self.assertEqual(res2["prefix"], "10.1016")
        self.assertFalse(res2["is_ieee"])

        # Invalid
        self.assertIsNone(normalize_ieee_doi("not_a_valid_doi"))

    def test_evaluate_bima_grant_proposal(self):
        from parser import evaluate_bima_grant_proposal
        # Eligible PDP proposal
        res_ok = evaluate_bima_grant_proposal(
            scheme_name="Penelitian Dosen Pemula (PDP)",
            requested_budget=20000000.0,
            lead_nidn="0412345601",
            sinta_score_3yr=65.0,
            team_member_count=1
        )
        self.assertTrue(res_ok["is_eligible"])
        self.assertTrue(res_ok["budget_compliant"])
        self.assertTrue(res_ok["sinta_compliant"])
        self.assertTrue(res_ok["team_compliant"])

        # Over budget & low SINTA proposal
        res_fail = evaluate_bima_grant_proposal(
            scheme_name="Penelitian Terapan",
            requested_budget=180000000.0,
            lead_nidn="0412345602",
            sinta_score_3yr=80.0,
            team_member_count=0
        )
        self.assertFalse(res_fail["is_eligible"])
        self.assertFalse(res_fail["budget_compliant"])
        self.assertFalse(res_fail["sinta_compliant"])
        self.assertFalse(res_fail["team_compliant"])

    def test_evaluate_kerja_praktik_placement(self):
        from parser import evaluate_kerja_praktik_placement
        # Approved KP
        res_ok = evaluate_kerja_praktik_placement(
            company_name="PT Telkom Indonesia",
            duration_weeks=10,
            project_title="Otomasi Monitoring Kualitas Jaringan 5G Menggunakan Cloud API"
        )
        self.assertTrue(res_ok["is_approved"])
        self.assertTrue(res_ok["duration_compliant"])
        self.assertTrue(res_ok["domain_compliant"])
        self.assertGreater(res_ok["relevance_score"], 0.5)

        # Under duration & out of domain
        res_fail = evaluate_kerja_praktik_placement(
            company_name="CV Toko Ritel",
            duration_weeks=4,
            project_title="Administrasi Keuangan Kasir Toko"
        )
        self.assertFalse(res_fail["is_approved"])
        self.assertFalse(res_fail["duration_compliant"])
        self.assertFalse(res_fail["domain_compliant"])

    def test_parse_telecom_isr_frequency_allocation(self):
        from parser import parse_telecom_isr_frequency_allocation
        table_md = """
| Laboratorium | Frekuensi Tengah | Bandwidth | Daya Pancar | Pita Frekuensi | Status |
|---|---|---|---|---|---|
| Lab RF & Antena | 3.5 GHz | 100 MHz | 23 dBm | n78 5G NR | Aktif |
| Lab Sistem Transmisi | 2.4 GHz | 40 MHz | 20 dBm | Wi-Fi 6 | Aktif |
"""
        allocations = parse_telecom_isr_frequency_allocation(table_md)
        self.assertEqual(len(allocations), 2)
        self.assertEqual(allocations[0]["lab_name"], "Lab RF & Antena")
        self.assertEqual(allocations[0]["center_freq_mhz"], 3500.0)
        self.assertEqual(allocations[0]["bandwidth_mhz"], 100.0)
        self.assertEqual(allocations[0]["max_power_dbm"], 23.0)
        self.assertEqual(allocations[0]["band_designation"], "n78 5G NR")
        self.assertEqual(allocations[1]["center_freq_mhz"], 2400.0)

        bullet_md = "- [ISR-99] Lab Komunikasi Nirkabel: 868 MHz | BW: 250 kHz | Power: 14 dBm | Band: LoRaWAN | Status: Uji Coba"
        res_bullet = parse_telecom_isr_frequency_allocation(bullet_md)
        self.assertEqual(len(res_bullet), 1)
        self.assertEqual(res_bullet[0]["lab_name"], "Lab Komunikasi Nirkabel")
        self.assertEqual(res_bullet[0]["center_freq_mhz"], 868.0)
        self.assertEqual(res_bullet[0]["bandwidth_mhz"], 0.25)
        self.assertEqual(res_bullet[0]["max_power_dbm"], 14.0)
        self.assertEqual(res_bullet[0]["band_designation"], "LoRaWAN")
        self.assertEqual(res_bullet[0]["status"], "Uji Coba")

    def test_parse_accreditation_status(self):
        from parser import parse_accreditation_status
        text = """
Program Studi: S1 Teknik Telekomunikasi
Badan Akreditasi: LAM-INFOKOM
Peringkat: Unggul
Nomor SK: 042/SK/LAM-INFOKOM/Ak/S/VIII/2024
Berlaku Hingga: 2029-08-31
"""
        res = parse_accreditation_status(text)
        self.assertIsNotNone(res)
        self.assertEqual(res["program_name"], "S1 Teknik Telekomunikasi")
        self.assertEqual(res["agency"], "LAM INFOKOM")
        self.assertEqual(res["rating"], "Unggul")
        self.assertEqual(res["sk_number"], "042/SK/LAM-INFOKOM/Ak/S/VIII/2024")
        self.assertEqual(res["expiry_date"], "2029-08-31")
        self.assertTrue(res["is_active"])

    def test_parse_scholarship_allocation(self):
        from parser import parse_scholarship_allocation
        text = """
Nama Mahasiswa: Bayu Pratama
NIM: 120120001
Jenis Beasiswa: Beasiswa Prestasi Unggulan
Penyelenggara: Yayasan Pendidikan Telkom
Nominal: Rp 7.500.000
Semester: Semester Ganjil 2026/2027
Syarat IPK: 3.50
"""
        res = parse_scholarship_allocation(text)
        self.assertIsNotNone(res)
        self.assertEqual(res["student_name"], "Bayu Pratama")
        self.assertEqual(res["nim"], "120120001")
        self.assertEqual(res["scholarship_type"], "Beasiswa Prestasi Unggulan")
        self.assertEqual(res["amount_idr"], 7500000.0)
        self.assertEqual(res["minimum_gpa"], 3.50)

    def test_calculate_optical_link_budget(self):
        from parser import calculate_optical_link_budget
        res = calculate_optical_link_budget(
            fiber_length_km=20.0,
            attenuation_db_per_km=0.25,
            num_splices=4,
            splice_loss_db=0.1,
            num_connectors=2,
            connector_loss_db=0.5,
            safety_margin_db=3.0,
            tx_power_dbm=0.0,
            rx_sensitivity_dbm=-28.0
        )
        self.assertEqual(res["total_fiber_loss_db"], 5.0)
        self.assertEqual(res["total_splice_loss_db"], 0.4)
        self.assertEqual(res["total_connector_loss_db"], 1.0)
        self.assertEqual(res["safety_margin_db"], 3.0)
        self.assertEqual(res["total_attenuation_db"], 9.4)
        self.assertEqual(res["allowed_optical_loss_db"], 28.0)
        self.assertEqual(res["power_margin_db"], 18.6)
        self.assertTrue(res["is_viable"])

    def test_parse_djki_patent_grant(self):
        from parser import parse_djki_patent_grant
        text = """
Judul Invensi: Antena Mikrostrip Array MIMO 5G Sub-6 GHz untuk Komunikasi Maritim
Nomor Paten: IDP000098765
Nomor Permohonan: P00202401234
Tanggal Penerimaan: 2024-03-15
Tanggal Pemberian: 2026-08-10
Inventor: Dr. Ir. Budi Santoso, M.T. dan Siti Rahma, S.T.
Tipe Paten: Paten Biasa
Status: Granted
"""
        res = parse_djki_patent_grant(text)
        self.assertIsNotNone(res)
        self.assertEqual(res["patent_number"], "IDP000098765")
        self.assertEqual(res["application_number"], "P00202401234")
        self.assertEqual(res["status"], "Granted")
        self.assertEqual(res["patent_type"], "Paten Biasa")
        self.assertEqual(len(res["inventors"]), 2)

    def test_evaluate_cum_laude_predicate(self):
        from parser import evaluate_cum_laude_predicate
        res1 = evaluate_cum_laude_predicate(ipk=3.92, study_duration_semesters=7)
        self.assertEqual(res1["predicate"], "Summa Cum Laude")
        self.assertTrue(res1["is_honor"])
        self.assertFalse(res1["is_disqualified"])

        res2 = evaluate_cum_laude_predicate(ipk=3.80, study_duration_semesters=8)
        self.assertEqual(res2["predicate"], "Magna Cum Laude")
        self.assertTrue(res2["is_honor"])

        res3 = evaluate_cum_laude_predicate(ipk=3.65, study_duration_semesters=8)
        self.assertEqual(res3["predicate"], "Dengan Pujian (Cum Laude)")
        self.assertTrue(res3["is_honor"])

        res4 = evaluate_cum_laude_predicate(ipk=3.75, study_duration_semesters=9)
        self.assertEqual(res4["predicate"], "Sangat Memuaskan")
        self.assertFalse(res4["is_honor"])
        self.assertTrue(res4["is_disqualified"])

    def test_calculate_friis_free_space_path_loss(self):
        from parser import calculate_friis_free_space_path_loss
        res = calculate_friis_free_space_path_loss(
            frequency_mhz=2400.0,
            distance_km=1.0,
            tx_gain_dbi=2.0,
            rx_gain_dbi=2.0
        )
        self.assertEqual(res["frequency_mhz"], 2400.0)
        self.assertEqual(res["distance_km"], 1.0)
        self.assertAlmostEqual(res["wavelength_meters"], 0.125, places=3)
        self.assertGreater(res["raw_fspl_db"], 95.0)
        self.assertLess(res["raw_fspl_db"], 105.0)
        self.assertEqual(res["net_path_loss_db"], round(res["raw_fspl_db"] - 4.0, 2))
        self.assertEqual(res["link_quality"], "Baik (Cakupan Seluler Standar)")

    def test_parse_kkn_thematic_evaluation(self):
        from parser import parse_kkn_thematic_evaluation
        res = parse_kkn_thematic_evaluation(
            village_name="Desa Karangmangu",
            student_count=12,
            program_category="Pemberdayaan Digital UMKM & IoT Desa",
            performance_score=88.5,
            community_impact_metric="Adopsi QRIS dan Marketplace Desa 92%"
        )
        self.assertEqual(res["village_name"], "Desa Karangmangu")
        self.assertEqual(res["student_count"], 12)
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["grade_point"], 4.0)
        self.assertTrue(res["is_passed"])
        self.assertIn("Sangat Berhasil", res["evaluation_status"])

    def test_parse_tridharma_internal_grant_compliance(self):
        from parser import parse_tridharma_internal_grant_compliance
        res_ok = parse_tridharma_internal_grant_compliance(
            nidn="0615088501",
            proposal_budget=35000000.0,
            publication_target="Jurnal Internasional Terindeks Scopus Q3",
            student_involvement_count=3
        )
        self.assertTrue(res_ok["is_valid_nidn"])
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["is_high_impact"])
        self.assertEqual(len(res_ok["compliance_issues"]), 0)

        res_fail = parse_tridharma_internal_grant_compliance(
            nidn="123",
            proposal_budget=75000000.0,
            publication_target="Blog Pribadi",
            student_involvement_count=0
        )
        self.assertFalse(res_fail["is_valid_nidn"])
        self.assertFalse(res_fail["is_compliant"])
        self.assertGreaterEqual(len(res_fail["compliance_issues"]), 3)

    def test_evaluate_fast_track_masters_eligibility(self):
        from parser import evaluate_fast_track_masters_eligibility
        res_ok = evaluate_fast_track_masters_eligibility(
            ipk=3.85,
            completed_sks=130,
            english_score=525
        )
        self.assertTrue(res_ok["is_eligible"])
        self.assertEqual(res_ok["eligibility_tier"], "Lolos Seleksi Utama")
        self.assertEqual(len(res_ok["deficiencies"]), 0)

        res_cond = evaluate_fast_track_masters_eligibility(
            ipk=3.65,
            completed_sks=124,
            english_score=450
        )
        self.assertFalse(res_cond["is_eligible"])
        self.assertEqual(res_cond["eligibility_tier"], "Lolos Bersyarat")
        self.assertEqual(len(res_cond["deficiencies"]), 1)

        res_fail = evaluate_fast_track_masters_eligibility(
            ipk=3.10,
            completed_sks=95,
            english_score=400
        )
        self.assertFalse(res_fail["is_eligible"])
        self.assertEqual(res_fail["eligibility_tier"], "Belum Memenuhi Syarat")
        self.assertEqual(len(res_fail["deficiencies"]), 3)

    def test_calculate_optical_snr_and_ber(self):
        from parser import calculate_optical_snr_and_ber
        res_excel = calculate_optical_snr_and_ber(
            signal_power_dbm=2.0,
            noise_power_dbm=-26.0,
            bitrate_gbps=10.0
        )
        self.assertEqual(res_excel["osnr_db"], 28.0)
        self.assertEqual(res_excel["quality_status"], "Excellent")
        self.assertLess(res_excel["estimated_ber"], 1e-8)

        res_marg = calculate_optical_snr_and_ber(
            signal_power_dbm=-5.0,
            noise_power_dbm=-20.0,
            bitrate_gbps=10.0
        )
        self.assertEqual(res_marg["osnr_db"], 15.0)
        self.assertEqual(res_marg["quality_status"], "Marginal")

    def test_parse_lab_equipment_calibration(self):
        from parser import parse_lab_equipment_calibration
        res_valid = parse_lab_equipment_calibration(
            equipment_name="Rohde & Schwarz Spectrum Analyzer 6 GHz",
            serial_number="RS-FPL-100234",
            last_calibration_date="2026-05-01",
            calibration_interval_months=12,
            reference_date="2026-10-19"
        )
        self.assertEqual(res_valid["status"], "Valid")
        self.assertTrue(res_valid["is_operational_compliant"])
        self.assertGreater(res_valid["days_remaining"], 30)

        res_exp = parse_lab_equipment_calibration(
            equipment_name="OTDR Yokogawa AQ7280",
            serial_number="YOKO-OTDR-099",
            last_calibration_date="2025-01-01",
            calibration_interval_months=12,
            reference_date="2026-10-19"
        )
        self.assertEqual(res_exp["status"], "Expired")
        self.assertFalse(res_exp["is_operational_compliant"])
        self.assertLess(res_exp["days_remaining"], 0)

        res_err = parse_lab_equipment_calibration(
            equipment_name="Test Tool",
            serial_number="TT-01",
            last_calibration_date="invalid-date"
        )
        self.assertFalse(res_err["is_operational_compliant"])
        self.assertIn("error", res_err)

    def test_parse_lecturer_hki_copyright(self):
        from parser import parse_lecturer_hki_copyright
        res_prog = parse_lecturer_hki_copyright(
            work_title="Software Analisis Propagasi MIMO 5G Purwokerto",
            creator_names=["Dr. Ir. Budi Santoso, M.T.", "Ahmad Fauzi, S.T."],
            creation_type="Program Komputer",
            application_number="EC00202619876",
            registration_number="000543210",
            registration_date="2026-08-15"
        )
        self.assertTrue(res_prog["is_valid_registration"])
        self.assertEqual(res_prog["creation_type"], "Program Komputer")
        self.assertEqual(res_prog["sinta_bkd_rubric_points"], 20.0)
        self.assertEqual(res_prog["primary_creator"], "Dr. Ir. Budi Santoso, M.T.")
        self.assertEqual(res_prog["legal_status"], "Granted")

        res_book = parse_lecturer_hki_copyright(
            work_title="Buku Ajar Jaringan Seluler 5G & 6G",
            creator_names=["Prof. Hendra Wijaya"],
            creation_type="Buku / Monograf",
            application_number="EC00202654321",
            registration_number="000987654",
            registration_date="2026-07-10"
        )
        self.assertEqual(res_book["sinta_bkd_rubric_points"], 40.0)
        self.assertTrue(res_book["is_valid_registration"])

    def test_calculate_fso_link_budget(self):
        from parser import calculate_fso_link_budget
        # Standard 1 km link with 10 dBm TX power
        res = calculate_fso_link_budget(
            tx_power_dbm=10.0,
            tx_beam_divergence_mrad=1.5,
            rx_aperture_diam_cm=20.0,
            link_distance_km=1.0,
            atmospheric_attenuation_db_km=2.5,
            optical_rx_sensitivity_dbm=-38.0
        )
        self.assertTrue(res["is_link_feasible"])
        self.assertGreater(res["link_margin_db"], 15.0)
        self.assertEqual(res["status"], "Robust")
        self.assertEqual(res["atmospheric_loss_db"], 2.5)

        # Distant link under heavy fog with high loss
        res_fog = calculate_fso_link_budget(
            tx_power_dbm=5.0,
            tx_beam_divergence_mrad=2.0,
            rx_aperture_diam_cm=10.0,
            link_distance_km=5.0,
            atmospheric_attenuation_db_km=12.0,
            optical_rx_sensitivity_dbm=-30.0
        )
        self.assertFalse(res_fog["is_link_feasible"])
        self.assertEqual(res_fog["status"], "Link Outage")

    def test_evaluate_student_msib_internship(self):
        from parser import evaluate_student_msib_internship
        res_pass = evaluate_student_msib_internship(
            student_name="Ahmad Zaki",
            nim="1101230045",
            industry_partner="PT Telkom Indonesia (Persero) Tbk",
            internship_role="Optical Transport & Cloud Network Engineer",
            mentor_grade=88.5,
            duration_months=5
        )
        self.assertTrue(res_pass["is_conversion_approved"])
        self.assertEqual(res_pass["letter_grade"], "A")
        self.assertEqual(res_pass["converted_sks"], 20)
        self.assertEqual(len(res_pass["converted_courses"]), 5)

        # 4 months duration gives partial 16 SKS
        res_part = evaluate_student_msib_internship(
            student_name="Rina Safitri",
            nim="1101230088",
            industry_partner="Huawei Technologies Indonesia",
            internship_role="Wireless RF Associate",
            mentor_grade=72.0,
            duration_months=4
        )
        self.assertTrue(res_part["is_conversion_approved"])
        self.assertEqual(res_part["letter_grade"], "B")
        self.assertEqual(res_part["converted_sks"], 16)

        # Failing grade
        res_fail = evaluate_student_msib_internship(
            student_name="Budi",
            nim="1101230099",
            industry_partner="Vendor X",
            internship_role="Tester",
            mentor_grade=45.0,
            duration_months=5
        )
        self.assertFalse(res_fail["is_conversion_approved"])
        self.assertEqual(res_fail["converted_sks"], 0)

    def test_calculate_antenna_polarization_loss(self):
        from parser import calculate_antenna_polarization_loss
        # Co-polarized linear (0 deg tilt)
        res_lin0 = calculate_antenna_polarization_loss("VERTICAL", "VERTICAL", tilt_angle_deg=0.0)
        self.assertEqual(res_lin0["polarization_loss_db"], 0.0)
        self.assertEqual(res_lin0["polarization_efficiency_pct"], 100.0)
        self.assertEqual(res_lin0["status"], "Optimal")

        # Cross-polarized linear (90 deg tilt)
        res_lin90 = calculate_antenna_polarization_loss("VERTICAL", "HORIZONTAL", tilt_angle_deg=90.0)
        self.assertGreaterEqual(res_lin90["polarization_loss_db"], 30.0)
        self.assertEqual(res_lin90["status"], "High Loss / Mismatch")

        # Circular to linear has 3.01 dB loss
        res_circ_lin = calculate_antenna_polarization_loss("RHCP", "VERTICAL")
        self.assertAlmostEqual(res_circ_lin["polarization_loss_db"], 3.01, places=1)
        self.assertEqual(res_circ_lin["polarization_efficiency_pct"], 50.0)

        # Circular co-pol vs cross-pol
        res_rhcp = calculate_antenna_polarization_loss("RHCP", "RHCP")
        self.assertEqual(res_rhcp["polarization_loss_db"], 0.0)
        res_cross = calculate_antenna_polarization_loss("RHCP", "LHCP")
        self.assertGreaterEqual(res_cross["polarization_loss_db"], 25.0)

    def test_parse_lecturer_pkm_grant(self):
        from parser import parse_lecturer_pkm_grant
        res_ok = parse_lecturer_pkm_grant(
            project_title="Pemberdayaan Digitalisasi Internet of Things untuk Petani Desa Karangmangu",
            team_leader="Dr. Ir. Budi Santoso, M.T.",
            nidn="0612058001",
            partner_name="Kelompok Tani Makmur Sejahtera",
            target_location="Desa Karangmangu, Banyumas",
            proposed_budget=15000000.0,
            fiscal_year=2026
        )
        self.assertTrue(res_ok["is_grant_approved"])
        self.assertEqual(res_ok["status"], "Approved")
        self.assertEqual(res_ok["approved_budget"], 15000000.0)
        self.assertEqual(len(res_ok["mandatory_deliverables"]), 4)

        # Exceed budget
        res_exceed = parse_lecturer_pkm_grant(
            project_title="Instalasi Panel Surya UMKM",
            team_leader="Dr. Ir. Budi Santoso, M.T.",
            nidn="0612058001",
            partner_name="Toko Mitra",
            target_location="Purwokerto",
            proposed_budget=30000000.0,
            fiscal_year=2026
        )
        self.assertFalse(res_exceed["is_grant_approved"])
        self.assertEqual(res_exceed["status"], "Budget Cap Exceeded")

        # Invalid NIDN
        res_bad_nidn = parse_lecturer_pkm_grant(
            project_title="Program Literasi",
            team_leader="Dosen A",
            nidn="123",
            partner_name="Mitra",
            target_location="Banyumas",
            proposed_budget=10000000.0,
            fiscal_year=2026
        )
        self.assertFalse(res_bad_nidn["is_grant_approved"])
        self.assertEqual(res_bad_nidn["status"], "NIDN Invalid")

    def test_calculate_satellite_link_budget(self):
        from parser import calculate_satellite_link_budget
        res = calculate_satellite_link_budget(
            downlink_freq_ghz=12.2,
            slant_range_km=38000.0,
            tx_eirp_dbw=52.0,
            rx_g_over_t_db_k=14.5,
            bandwidth_mhz=36.0,
            atmospheric_loss_db=0.8
        )
        self.assertAlmostEqual(res["downlink_freq_ghz"], 12.2)
        self.assertGreater(res["fspl_db"], 200.0)
        self.assertGreater(res["cnr_db"], 5.0)
        self.assertIn("is_viable", res)
        self.assertIn("modulation_recommendation", res)

    def test_calculate_rf_intermod_distortion(self):
        from parser import calculate_rf_intermod_distortion
        res = calculate_rf_intermod_distortion(
            input_power_dbm=-20.0,
            gain_db=15.0,
            iip3_dbm=10.0
        )
        self.assertEqual(res["fundamental_output_power_dbm"], -5.0)
        self.assertEqual(res["oip3_dbm"], 25.0)
        self.assertEqual(res["imd3_suppression_dbc"], 60.0)
        self.assertEqual(res["linearity_status"], "Excellent")
        self.assertTrue(res["is_linear"])

    def test_calculate_optical_fiber_dispersion(self):
        from parser import calculate_optical_fiber_dispersion
        res = calculate_optical_fiber_dispersion(
            fiber_length_km=50.0,
            dispersion_coeff_ps_nm_km=17.0,
            spectral_width_nm=0.02,
            pmd_coeff_ps_sqrt_km=0.1,
            bit_rate_gbps=10.0
        )
        self.assertGreater(res["cd_delay_ps"], 10.0)
        self.assertGreater(res["pmd_delay_ps"], 0.5)
        self.assertEqual(res["bit_duration_ps"], 100.0)
        self.assertTrue(res["is_viable"])
        self.assertIn("status", res)

    def test_parse_kampus_mengajar_evaluation(self):
        from parser import parse_kampus_mengajar_evaluation
        res = parse_kampus_mengajar_evaluation(
            student_name="Annisa Rahma",
            nim="1201200045",
            target_school="SMP Negeri 2 Kedungbanteng",
            school_level="SMP",
            teaching_hours=350,
            principal_grade=90.0,
            faculty_supervisor_grade=88.0,
            duration_months=4
        )
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["converted_sks"], 20)
        self.assertTrue(res["is_eligible"])
        self.assertEqual(len(res["course_equivalencies"]), 5)

    def test_calculate_radar_range_equation(self):
        from parser import calculate_radar_range_equation
        res = calculate_radar_range_equation(
            peak_power_kw=50.0,
            antenna_gain_dbi=35.0,
            radar_cross_section_m2=2.0,
            freq_ghz=9.4,
            min_detectable_signal_dbm=-100.0
        )
        self.assertTrue(res["is_valid"])
        self.assertGreater(res["max_range_km"], 10.0)
        self.assertGreater(res["round_trip_delay_us"], 10.0)
        self.assertEqual(res["peak_power_watts"], 50000.0)
        with self.assertRaises(ValueError):
            calculate_radar_range_equation(-10.0, 35.0, 2.0, 9.4, -100.0)

    def test_calculate_phase_noise_and_evm(self):
        from parser import calculate_phase_noise_and_evm
        res = calculate_phase_noise_and_evm(
            carrier_freq_mhz=2400.0,
            phase_jitter_ps=0.8
        )
        self.assertGreater(res["evm_percent"], 0.0)
        self.assertIn("modulation_support", res)
        self.assertIn("quality_rating", res)

        res_dbc = calculate_phase_noise_and_evm(
            carrier_freq_mhz=2400.0,
            integrated_phase_noise_dbc=-45.0
        )
        self.assertGreater(res_dbc["phase_noise_rad"], 0.0)
        self.assertGreater(res_dbc["phase_jitter_ps"], 0.0)
        with self.assertRaises(ValueError):
            calculate_phase_noise_and_evm(0.0, 1.0)

    def test_calculate_edfa_amplifier_gain(self):
        from parser import calculate_edfa_amplifier_gain
        res = calculate_edfa_amplifier_gain(
            input_power_dbm=-20.0,
            pump_power_mw=150.0,
            small_signal_gain_db=25.0,
            saturation_output_power_dbm=17.0
        )
        self.assertGreater(res["actual_gain_db"], 15.0)
        self.assertGreater(res["output_power_dbm"], -20.0)
        self.assertGreaterEqual(res["noise_figure_db"], 3.0)
        self.assertIn("operating_regime", res)
        with self.assertRaises(ValueError):
            calculate_edfa_amplifier_gain(-20.0, -10.0, 25.0)

    def test_parse_wirausaha_merdeka_evaluation(self):
        from parser import parse_wirausaha_merdeka_evaluation
        res = parse_wirausaha_merdeka_evaluation(
            student_name="Budi Santoso",
            nim="1201201050",
            startup_name="IoT AgroSense",
            business_sector="Smart Agriculture",
            mentor_score=88.0,
            pitch_score=92.0,
            duration_months=5
        )
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["converted_sks"], 20)
        self.assertTrue(res["is_eligible"])
        self.assertEqual(len(res["course_equivalencies"]), 5)

        # Partial scoring test
        res_partial = parse_wirausaha_merdeka_evaluation(
            student_name="Dewi Lestari",
            nim="1201201051",
            startup_name="EduTech",
            business_sector="Education",
            mentor_score=60.0,
            pitch_score=65.0,
            duration_months=5
        )
        self.assertEqual(res_partial["letter_grade"], "B")
        self.assertEqual(res_partial["converted_sks"], 16)
        self.assertEqual(len(res_partial["course_equivalencies"]), 4)

    def test_calculate_otdr_fiber_events(self):
        from parser import calculate_otdr_fiber_events
        res = calculate_otdr_fiber_events(
            fiber_length_km=50.0,
            total_loss_db=11.2,
            splice_loss_db=0.05,
            num_splices=4,
            connector_loss_db=0.5,
            num_connectors=2,
            wavelength_nm=1550
        )
        self.assertEqual(res["total_event_loss_db"], 1.2)
        self.assertEqual(res["intrinsic_loss_db"], 10.0)
        self.assertEqual(res["attenuation_db_per_km"], 0.20)
        self.assertTrue(res["is_compliant"])
        self.assertIn("ITU-T G.652", res["quality_status"])
        with self.assertRaises(ValueError):
            calculate_otdr_fiber_events(0.0, 10.0)

    def test_calculate_mimo_channel_capacity(self):
        from parser import calculate_mimo_channel_capacity
        res = calculate_mimo_channel_capacity(
            bandwidth_mhz=100.0,
            snr_db=20.0,
            num_tx_antennas=4,
            num_rx_antennas=4
        )
        self.assertEqual(res["mimo_rank"], 4)
        self.assertGreater(res["spectral_efficiency_bps_hz"], 5.0)
        self.assertGreater(res["capacity_mbps"], 500.0)
        self.assertGreater(res["capacity_gain_factor"], 1.5)
        self.assertIn("4x4 MIMO", res["spatial_multiplexing_status"])
        with self.assertRaises(ValueError):
            calculate_mimo_channel_capacity(-10.0, 20.0)

    def test_calculate_lorawan_battery_lifetime(self):
        from parser import calculate_lorawan_battery_lifetime
        res = calculate_lorawan_battery_lifetime(
            battery_capacity_mah=2400.0,
            tx_current_ma=40.0,
            rx_current_ma=12.0,
            sleep_current_ua=2.5,
            uplink_interval_min=15.0
        )
        self.assertGreater(res["nominal_lifetime_days"], 300.0)
        self.assertGreater(res["adjusted_lifetime_years"], 1.0)
        self.assertTrue(res["is_etsi_compliant"])
        self.assertGreater(res["avg_current_ma"], 0.0)
        with self.assertRaises(ValueError):
            calculate_lorawan_battery_lifetime(0.0, 40.0, 12.0, 2.5, 15.0)

    def test_parse_iisma_evaluation(self):
        from parser import parse_iisma_evaluation
        res = parse_iisma_evaluation(
            student_name="Nadia Putri",
            nim="1201201088",
            host_university="National University of Singapore",
            country="Singapore",
            gpa_host=3.85,
            credits_taken=16,
            duration_semesters=1
        )
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["converted_sks"], 20)
        self.assertTrue(res["is_eligible"])
        self.assertEqual(len(res["course_equivalencies"]), 5)

        # Partial evaluation
        res_partial = parse_iisma_evaluation(
            student_name="Farhan Rizky",
            nim="1201201089",
            host_university="University of Leeds",
            country="United Kingdom",
            gpa_host=3.15,
            credits_taken=12
        )
        self.assertEqual(res_partial["letter_grade"], "B")
        self.assertEqual(res_partial["converted_sks"], 16)
        self.assertEqual(len(res_partial["course_equivalencies"]), 4)

    def test_calculate_fspl_and_link_budget(self):
        from parser import calculate_fspl_and_link_budget
        res = calculate_fspl_and_link_budget(
            frequency_mhz=2400.0,
            distance_km=5.0,
            tx_power_dbm=20.0,
            tx_gain_dbi=14.0,
            rx_gain_dbi=14.0,
            misc_losses_db=2.0,
            rx_sensitivity_dbm=-85.0
        )
        self.assertGreater(res["fspl_db"], 100.0)
        self.assertGreater(res["fade_margin_db"], 10.0)
        self.assertTrue(res["is_viable"])
        self.assertIn("Andal", res["status"])

        # Test extreme distance causing outage
        outage = calculate_fspl_and_link_budget(
            frequency_mhz=5800.0,
            distance_km=150.0,
            tx_power_dbm=10.0,
            tx_gain_dbi=0.0,
            rx_gain_dbi=0.0,
            misc_losses_db=5.0,
            rx_sensitivity_dbm=-70.0
        )
        self.assertFalse(outage["is_viable"])
        self.assertIn("Gagal", outage["status"])

    def test_calculate_optical_chromatic_dispersion(self):
        from parser import calculate_optical_chromatic_dispersion
        res = calculate_optical_chromatic_dispersion(
            dispersion_param_ps_nm_km=17.0,
            spectral_width_nm=0.1,
            fiber_length_km=50.0,
            bit_rate_gbps=10.0
        )
        self.assertEqual(res["pulse_broadening_ps"], 85.0)
        self.assertEqual(res["bit_period_ps"], 100.0)
        self.assertEqual(res["spreading_ratio"], 0.85)
        self.assertTrue(res["requires_compensation"])
        self.assertIn("Tinggi", res["severity"])

    def test_calculate_cellular_handover_hysteresis(self):
        from parser import calculate_cellular_handover_hysteresis
        ho = calculate_cellular_handover_hysteresis(
            rsrp_serving_dbm=-95.0,
            rsrp_target_dbm=-82.0,
            hysteresis_db=3.0,
            a3_offset_db=2.0,
            time_to_trigger_ms=160
        )
        self.assertTrue(ho["is_a3_triggered"])
        self.assertEqual(ho["decision"], "TRIGGER_HANDOVER")
        self.assertIn("Rendah", ho["ping_pong_risk"])

        no_ho = calculate_cellular_handover_hysteresis(
            rsrp_serving_dbm=-85.0,
            rsrp_target_dbm=-90.0
        )
        self.assertFalse(no_ho["is_a3_triggered"])
        self.assertEqual(no_ho["decision"], "MAINTAIN_SERVING")

    def test_parse_proyek_kemanusiaan_evaluation(self):
        from parser import parse_proyek_kemanusiaan_evaluation
        res = parse_proyek_kemanusiaan_evaluation({
            "student_name": "Reza Kurniawan",
            "nim": "1201201099",
            "partner_org": "BPBD Kabupaten Banyumas",
            "location": "Banyumas",
            "field_hours": 450,
            "score_mentor": 90.0,
            "score_field": 88.0,
            "score_impact": 85.0
        })
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["converted_sks"], 20)
        self.assertTrue(res["is_eligible"])
        self.assertEqual(len(res["course_equivalencies"]), 5)

        # Ineligible test
        fail = parse_proyek_kemanusiaan_evaluation({
            "field_hours": 100,
            "score_mentor": 40.0,
            "score_field": 45.0,
            "score_impact": 40.0
        })
        self.assertEqual(fail["converted_sks"], 0)
        self.assertFalse(fail["is_eligible"])

    def test_calculate_polarization_mode_dispersion(self):
        from parser import calculate_polarization_mode_dispersion
        res = calculate_polarization_mode_dispersion(
            pmd_coeff_ps_sqrt_km=0.05,
            fiber_length_km=100.0,
            bit_rate_gbps=10.0
        )
        self.assertEqual(res["mean_dgd_ps"], 0.5)
        self.assertEqual(res["bit_period_ps"], 100.0)
        self.assertTrue(res["is_compliant"])
        self.assertIn("Sangat Rendah", res["outage_risk"])

        # High PMD test
        high_res = calculate_polarization_mode_dispersion(
            pmd_coeff_ps_sqrt_km=1.5,
            fiber_length_km=400.0,
            bit_rate_gbps=40.0
        )
        self.assertFalse(high_res["is_compliant"])
        self.assertIn("Tinggi", high_res["outage_risk"])

    def test_calculate_cost231_hata_path_loss(self):
        from parser import calculate_cost231_hata_path_loss
        res = calculate_cost231_hata_path_loss(
            frequency_mhz=1800.0,
            base_station_height_m=50.0,
            mobile_height_m=1.5,
            distance_km=5.0,
            is_metropolitan=False
        )
        self.assertGreater(res["path_loss_db"], 120.0)
        self.assertLess(res["path_loss_db"], 160.0)
        self.assertEqual(res["clutter_constant_cm"], 0.0)

        metro = calculate_cost231_hata_path_loss(
            frequency_mhz=1800.0,
            base_station_height_m=50.0,
            mobile_height_m=1.5,
            distance_km=5.0,
            is_metropolitan=True
        )
        self.assertEqual(round(metro["path_loss_db"] - res["path_loss_db"], 1), 3.0)

    def test_calculate_rain_attenuation_itu_r(self):
        from parser import calculate_rain_attenuation_itu_r
        res = calculate_rain_attenuation_itu_r(
            frequency_ghz=15.0,
            path_length_km=8.0,
            rain_rate_mm_hr=42.0,
            fade_margin_db=35.0,
            polarization="horizontal"
        )
        self.assertGreater(res["specific_attenuation_db_km"], 0.0)
        self.assertGreater(res["total_rain_attenuation_db"], 0.0)
        self.assertTrue(res["is_reliable"])
        self.assertGreater(res["excess_margin_db"], 0.0)

    def test_parse_studi_independen_evaluation(self):
        from parser import parse_studi_independen_evaluation
        res = parse_studi_independen_evaluation({
            "student_name": "Dian Sasmita",
            "nim": "1201201077",
            "partner_name": "Bangkit Academy by Google, GoTo, Traveloka",
            "track_name": "Cloud Computing",
            "score_mentor": 92.0,
            "score_project": 90.0,
            "score_defense": 88.0
        })
        self.assertEqual(res["letter_grade"], "A")
        self.assertEqual(res["converted_sks"], 20)
        self.assertTrue(res["is_eligible"])
        self.assertEqual(len(res["course_equivalencies"]), 5)

        fail = parse_studi_independen_evaluation({
            "score_mentor": 40.0,
            "score_project": 45.0,
            "score_defense": 40.0
        })
        self.assertEqual(fail["converted_sks"], 0)
        self.assertFalse(fail["is_eligible"])

    def test_calculate_optical_four_wave_mixing(self):
        from parser import calculate_optical_four_wave_mixing
        res = calculate_optical_four_wave_mixing(
            channel_spacing_ghz=100.0,
            fiber_length_km=50.0,
            chromatic_dispersion_ps_nm_km=17.0,
            channel_power_dbm=0.0
        )
        self.assertGreater(abs(res["delta_beta_rad_km"]), 0.0)
        self.assertGreater(res["effective_length_km"], 0.0)
        self.assertLessEqual(res["fwm_efficiency"], 1.0)
        self.assertTrue(res["is_compliant"])
        self.assertIn("Aman", res["fwm_risk"])

        # Test zero-dispersion high risk case
        res_zero = calculate_optical_four_wave_mixing(
            channel_spacing_ghz=25.0,
            fiber_length_km=80.0,
            chromatic_dispersion_ps_nm_km=0.01,
            channel_power_dbm=10.0
        )
        self.assertFalse(res_zero["is_compliant"])
        self.assertIn("Kritis", res_zero["fwm_risk"])

    def test_calculate_erlang_traffic_capacity(self):
        from parser import calculate_erlang_traffic_capacity
        # Standard trunking: 10 Erlangs on 15 channels
        res = calculate_erlang_traffic_capacity(
            offered_traffic_erlangs=10.0,
            num_channels=15,
            avg_holding_time_sec=120.0
        )
        self.assertGreater(res["carried_traffic_erlangs"], 0.0)
        self.assertLessEqual(res["blocking_probability_erlang_b"], 0.05)
        self.assertTrue(res["is_acceptable"])
        self.assertIn("GoS", res["grade_of_service_status"])

        # Severe congestion: 20 Erlangs on 5 channels
        overload = calculate_erlang_traffic_capacity(
            offered_traffic_erlangs=20.0,
            num_channels=5
        )
        self.assertFalse(overload["is_acceptable"])
        self.assertGreater(overload["blocking_probability_erlang_b"], 0.20)

    def test_calculate_satellite_atmospheric_attenuation_itu_r(self):
        from parser import calculate_satellite_atmospheric_attenuation_itu_r
        # Ku-band link at 14 GHz, 30 deg elevation
        res = calculate_satellite_atmospheric_attenuation_itu_r(
            frequency_ghz=14.0,
            elevation_angle_deg=30.0,
            water_vapor_density_g_m3=7.5
        )
        self.assertGreater(res["oxygen_attenuation_db_km"], 0.0)
        self.assertGreater(res["water_vapor_attenuation_db_km"], 0.0)
        self.assertGreater(res["slant_path_attenuation_db"], 0.0)
        self.assertTrue(res["is_viable"])

    def test_parse_pkm_mbkm_evaluation(self):
        from parser import parse_pkm_mbkm_evaluation
        # PIMNAS medal winner
        res_pimnas = parse_pkm_mbkm_evaluation({
            "student_name": "Arif Rahman",
            "nim": "1201201044",
            "scheme": "PKM-KC (Karsa Cipta)",
            "proposal_title": "Drone Pemantau Sinyal Maritim 4G/5G",
            "qualified_pimnas": True,
            "medal": "Medali Emas Kategori Presentasi",
            "score_proposal": 92.0,
            "score_progress": 95.0,
            "score_presentation": 96.0
        })
        self.assertEqual(res_pimnas["letter_grade"], "A")
        self.assertEqual(res_pimnas["converted_sks"], 20)
        self.assertTrue(res_pimnas["is_eligible"])
        self.assertEqual(len(res_pimnas["course_equivalencies"]), 5)

        # Non-passing
        res_fail = parse_pkm_mbkm_evaluation({
            "student_name": "Bayu",
            "score_proposal": 45.0,
            "score_progress": 40.0,
            "score_presentation": 42.0
        })
        self.assertEqual(res_fail["converted_sks"], 0)
        self.assertFalse(res_fail["is_eligible"])

    def test_calculate_optical_cross_phase_modulation(self):
        from parser import calculate_optical_cross_phase_modulation
        # Safe transmission: 5 mW pump, 1 mW probe over 40 km
        res = calculate_optical_cross_phase_modulation(
            pump_power_mw=5.0,
            probe_power_mw=1.0,
            fiber_length_km=40.0
        )
        self.assertGreater(res["effective_length_km"], 0.0)
        self.assertGreater(res["phi_xpm_rad"], 0.0)
        self.assertGreater(res["phi_spm_rad"], 0.0)
        self.assertTrue(res["is_acceptable"])

        # Severe nonlinear case: 100 mW pump over 100 km
        res_high = calculate_optical_cross_phase_modulation(
            pump_power_mw=100.0,
            probe_power_mw=20.0,
            fiber_length_km=100.0
        )
        self.assertFalse(res_high["is_acceptable"])
        self.assertIn("Tinggi", res_high["xpm_risk"])

    def test_calculate_5g_nr_numerology_timing(self):
        from parser import calculate_5g_nr_numerology_timing
        # Sub-6 GHz mid-band mu=1 (30 kHz SCS)
        res_mu1 = calculate_5g_nr_numerology_timing(numerology_mu=1, num_resource_blocks=100)
        self.assertEqual(res_mu1["subcarrier_spacing_khz"], 30)
        self.assertEqual(res_mu1["slots_per_subframe"], 2)
        self.assertEqual(res_mu1["slots_per_frame"], 20)
        self.assertEqual(res_mu1["slot_duration_ms"], 0.5)
        self.assertEqual(res_mu1["symbols_per_slot"], 14)
        self.assertEqual(res_mu1["total_symbols_per_subframe"], 28)
        self.assertIn("FR1", res_mu1["frequency_range"])

        # mmWave mu=3 (120 kHz SCS)
        res_mu3 = calculate_5g_nr_numerology_timing(numerology_mu=3, num_resource_blocks=66)
        self.assertEqual(res_mu3["subcarrier_spacing_khz"], 120)
        self.assertEqual(res_mu3["slots_per_frame"], 80)
        self.assertEqual(res_mu3["slot_duration_ms"], 0.125)
        self.assertIn("FR2", res_mu3["frequency_range"])

    def test_calculate_satellite_scintillation_itu_r(self):
        from parser import calculate_satellite_scintillation_itu_r
        # Ku-band link at 12 GHz, 20 deg elevation, 1.2m dish
        res = calculate_satellite_scintillation_itu_r(
            frequency_ghz=12.0,
            elevation_angle_deg=20.0,
            antenna_diameter_m=1.2,
            percentage_p=0.01
        )
        self.assertGreater(res["n_wet"], 0.0)
        self.assertGreater(res["sigma_db"], 0.0)
        self.assertGreater(res["scintillation_fade_depth_db"], 0.0)
        self.assertTrue(res["is_viable"])

    def test_parse_pmm_mbkm_evaluation(self):
        from parser import parse_pmm_mbkm_evaluation
        # Successful student exchange
        res_pass = parse_pmm_mbkm_evaluation({
            "student_name": "Rizky Ramadhan",
            "nim": "1201201099",
            "host_university": "Universitas Hasanuddin",
            "nusantara_module_score": 90.0,
            "academic_courses_score": 88.0,
            "host_mentor_score": 92.0
        })
        self.assertEqual(res_pass["letter_grade"], "A")
        self.assertEqual(res_pass["converted_sks"], 20)
        self.assertTrue(res_pass["is_eligible"])
        self.assertEqual(len(res_pass["course_equivalencies"]), 5)

        # Ineligible score
        res_fail = parse_pmm_mbkm_evaluation({
            "student_name": "Doni",
            "nusantara_module_score": 40.0,
            "academic_courses_score": 45.0,
            "host_mentor_score": 50.0
        })
        self.assertEqual(res_fail["converted_sks"], 0)
        self.assertFalse(res_fail["is_eligible"])

    def test_calculate_optical_srs_threshold(self):
        from parser import calculate_optical_srs_threshold
        # Low power safe transmission: 50 mW over 40 km
        res_safe = calculate_optical_srs_threshold(
            fiber_length_km=40.0,
            attenuation_db_km=0.2,
            effective_area_um2=80.0,
            input_power_mw=50.0
        )
        self.assertGreater(res_safe["threshold_power_mw"], 50.0)
        self.assertTrue(res_safe["is_safe"])
        self.assertIn("Aman", res_safe["srs_risk"])

        # High power depleted transmission: 3000 mW
        res_crit = calculate_optical_srs_threshold(
            fiber_length_km=50.0,
            input_power_mw=3000.0
        )
        self.assertFalse(res_crit["is_safe"])
        self.assertIn("Kritis", res_crit["srs_risk"])

    def test_calculate_5g_nr_eirp_psd(self):
        from parser import calculate_5g_nr_eirp_psd
        # Standard gNodeB macro transmitter: 46 dBm, 16 dBi antenna, 2 dB loss, 100 MHz BW
        res = calculate_5g_nr_eirp_psd(
            conducted_power_dbm=46.0,
            antenna_gain_dbi=16.0,
            cable_loss_db=2.0,
            bandwidth_mhz=100.0,
            is_macro_cell=True
        )
        self.assertEqual(res["eirp_dbm"], 60.0)
        self.assertEqual(res["psd_conducted_dbm_mhz"], 26.0)
        self.assertEqual(res["psd_eirp_dbm_mhz"], 40.0)
        self.assertTrue(res["is_compliant"])

    def test_calculate_satellite_faraday_rotation(self):
        from parser import calculate_satellite_faraday_rotation
        # L-band link at 1.5 GHz with 30 TECU
        res_lband = calculate_satellite_faraday_rotation(
            frequency_ghz=1.5,
            total_electron_content_tecu=30.0
        )
        self.assertGreater(res_lband["rotation_angle_deg"], 0.0)
        self.assertGreaterEqual(res_lband["polarization_loss_db"], 0.0)

        # High frequency Ka-band 20 GHz (Faraday rotation negligible)
        res_kaband = calculate_satellite_faraday_rotation(
            frequency_ghz=20.0,
            total_electron_content_tecu=30.0
        )
        self.assertLess(res_kaband["effective_angle_deg"], 1.0)
        self.assertTrue(res_kaband["is_linear_viable"])

    def test_parse_praktisi_mengajar_evaluation(self):
        from parser import parse_praktisi_mengajar_evaluation
        # High performing collaborative class
        res_pass = parse_praktisi_mengajar_evaluation({
            "course_name": "Rekayasa Jaringan Nirkabel",
            "course_code": "TT3201",
            "practitioner_name": "Ir. Hendra Wijaya",
            "industry_company": "PT Telkomsel",
            "lecturer_name": "Dr. Eng. Wahyu",
            "teaching_hours": 14,
            "case_study_score": 92.0,
            "practitioner_assessment": 90.0,
            "student_evaluation": 88.0
        })
        self.assertEqual(res_pass["letter_grade"], "A")
        self.assertEqual(res_pass["converted_sks"], 4)
        self.assertTrue(res_pass["is_eligible"])
        self.assertIn("PT Telkomsel", res_pass["status"])

        # Under threshold hours
        res_fail = parse_praktisi_mengajar_evaluation({
            "teaching_hours": 6,
            "case_study_score": 50.0,
            "practitioner_assessment": 55.0,
            "student_evaluation": 50.0
        })
        self.assertEqual(res_fail["converted_sks"], 0)
        self.assertFalse(res_fail["is_eligible"])

    def test_calculate_optical_spm_broadening(self):
        from parser import calculate_optical_spm_broadening
        # Moderate power in 80 km fiber
        res = calculate_optical_spm_broadening(
            fiber_length_km=80.0,
            peak_power_w=0.05,
            non_linear_coeff_gamma=1.3,
            attenuation_db_km=0.2,
            initial_pulse_width_ps=20.0
        )
        self.assertGreater(res["effective_length_km"], 0.0)
        self.assertGreater(res["phi_max_rad"], 0.0)
        self.assertGreater(res["broadening_factor"], 1.0)
        self.assertTrue(res["is_acceptable"])

        # High power leading to critical distortion
        res_high = calculate_optical_spm_broadening(
            fiber_length_km=100.0,
            peak_power_w=0.5,
            non_linear_coeff_gamma=1.5
        )
        self.assertGreater(res_high["b_integral"], 3.0)
        self.assertFalse(res_high["is_acceptable"])
        self.assertIn("Kritis", res_high["spm_risk"])

    def test_calculate_5g_nr_carrier_aggregation_throughput(self):
        from parser import calculate_5g_nr_carrier_aggregation_throughput
        # 2CC CA (100 MHz + 40 MHz) with 4x4 MIMO and 256-QAM
        ccs = [
            {"name": "PCC-n78", "bandwidth_mhz": 100, "mimo_layers": 4, "modulation": "256QAM"},
            {"name": "SCC1-n78", "bandwidth_mhz": 40, "mimo_layers": 4, "modulation": "256QAM"}
        ]
        res = calculate_5g_nr_carrier_aggregation_throughput(ccs)
        self.assertEqual(res["num_carriers"], 2)
        self.assertEqual(res["total_bandwidth_mhz"], 140.0)
        self.assertGreater(res["total_throughput_mbps"], 1000.0)
        self.assertGreater(res["total_throughput_gbps"], 1.0)
        self.assertEqual(len(res["carriers"]), 2)

    def test_calculate_satellite_rain_attenuation_itu_r(self):
        from parser import calculate_satellite_rain_attenuation_itu_r
        # Ku-band 12 GHz slant path in tropical region
        res = calculate_satellite_rain_attenuation_itu_r(
            frequency_ghz=12.0,
            elevation_angle_deg=45.0,
            rain_rate_001_mm_h=95.0,
            percentage_p=0.01
        )
        self.assertGreater(res["predicted_attenuation_db"], 5.0)
        self.assertGreater(res["effective_path_length_km"], 0.0)
        self.assertTrue(res["is_link_viable"])

    def test_parse_p2mw_evaluation(self):
        from parser import parse_p2mw_evaluation
        # High score growth startup
        res_growth = parse_p2mw_evaluation({
            "student_name": "Dimas Pratama",
            "nim": "1201202050",
            "business_name": "AgroTele-IoT",
            "business_stage": "Tahap Bertumbuh",
            "pitch_bmc_score": 90.0,
            "prototype_progress_score": 88.0,
            "financial_governance_score": 85.0
        })
        self.assertEqual(res_growth["letter_grade"], "A")
        self.assertEqual(res_growth["converted_sks"], 6)
        self.assertTrue(res_growth["is_funded"])

        # Early stage startup
        res_early = parse_p2mw_evaluation({
            "student_name": "Sarah Amalia",
            "nim": "1201202051",
            "business_name": "SmartAntenna-Labs",
            "business_stage": "Tahap Awal",
            "pitch_bmc_score": 75.0,
            "prototype_progress_score": 72.0,
            "financial_governance_score": 70.0
        })
        self.assertEqual(res_early["converted_sks"], 4)
        self.assertTrue(res_early["is_funded"])


if __name__ == "__main__":
    unittest.main()






