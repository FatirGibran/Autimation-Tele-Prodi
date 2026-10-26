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

    def test_validate_image_dimensions(self):
        good_img = '<p><img src="pic.jpg" width="800" height="600" alt="Grafik" /></p>'
        res1 = YoastSEOValidator.validate_image_dimensions(good_img)
        self.assertTrue(res1["is_optimal"])
        self.assertEqual(res1["missing_dimensions_count"], 0)

        bad_img = '<p><img src="pic.jpg" alt="Grafik" /></p>'
        res2 = YoastSEOValidator.validate_image_dimensions(bad_img)
        self.assertFalse(res2["is_optimal"])
        self.assertEqual(res2["missing_dimensions_count"], 1)

    def test_evaluate_keyphrase_distribution(self):
        # Evenly spread across 3 sections
        content = (
            "<p>Kecerdasan buatan merupakan fokus riset masa depan.</p>"
            "<p>Pengembangan modul kecerdasan buatan dilakukan di laboratorium.</p>"
            "<p>Kesimpulannya kecerdasan buatan sangat menjanjikan.</p>"
        )
        res = YoastSEOValidator.evaluate_keyphrase_distribution(content, "kecerdasan buatan")
        self.assertTrue(res["is_uniform"])
        self.assertGreaterEqual(res["sections_covered"], 2)

        # Clustered only in the first section
        skewed = (
            "<p>Kecerdasan buatan kecerdasan buatan kecerdasan buatan pada bagian pembuka.</p>"
            "<p>Paragraf tengah membahas topik lain secara lengkap dan mendalam tentang arsitektur jaringan komputer dan server lokal.</p>"
            "<p>Paragraf penutup membahas evaluasi kinerja sistem dan kesimpulan akhir tanpa menyebutkan topik utama sama sekali.</p>"
        )
        res_skewed = YoastSEOValidator.evaluate_keyphrase_distribution(skewed, "kecerdasan buatan")
        self.assertFalse(res_skewed["is_uniform"])
        self.assertEqual(res_skewed["sections_covered"], 1)


    def test_evaluate_internal_link_structure(self):
        good_links = '<p><a href="/kurikulum">Kurikulum</a> dan <a href="https://bif-pwt.telkomuniversity.ac.id/dosen">Dosen</a></p>'
        res = YoastSEOValidator.evaluate_internal_link_structure(good_links)
        self.assertTrue(res["has_internal_links"])
        self.assertTrue(res["is_optimal"])
        self.assertEqual(res["total_internal_links"], 2)

        bad_links = '<p><a href="/kurikulum/prodi/if/semester/1/matkul?utm_source=fb">Detail</a></p>'
        res_bad = YoastSEOValidator.evaluate_internal_link_structure(bad_links)
        self.assertFalse(res_bad["is_optimal"])
        self.assertTrue(any("parameter tracking" in w for w in res_bad["warnings"]))

    def test_audit_outbound_links_security(self):
        secure_html = '<p><a href="https://github.com/prodi" target="_blank" rel="noopener noreferrer">Repo</a></p>'
        res = YoastSEOValidator.audit_outbound_links_security(secure_html)
        self.assertTrue(res["is_secure"])
        self.assertEqual(res["compliant_count"], 1)

        insecure_html = '<p><a href="https://github.com/prodi">Repo</a></p>'
        res_insecure = YoastSEOValidator.audit_outbound_links_security(insecure_html)
        self.assertFalse(res_insecure["is_secure"])
        self.assertEqual(res_insecure["non_compliant_count"], 1)

    def test_evaluate_meta_and_og_alignment(self):
        # Aligned
        res = YoastSEOValidator.evaluate_meta_and_og_alignment(
            seo_title="Kurikulum Baru Informatika Telkom",
            og_title="Kurikulum Baru Informatika Telkom 2026",
            meta_description="Panduan kurikulum baru program studi teknik informatika.",
            og_description="Panduan lengkap kurikulum baru program studi teknik informatika."
        )
        self.assertTrue(res["is_aligned"])
        self.assertGreaterEqual(res["title_similarity"], 0.3)

        # Mismatched titles
        res_bad = YoastSEOValidator.evaluate_meta_and_og_alignment(
            seo_title="Kurikulum Baru Informatika Telkom",
            og_title="Resep Makanan Tradisional Nusantara",
            meta_description="Deskripsi",
            og_description="Deskripsi"
        )
        self.assertFalse(res_bad["is_aligned"])

    def test_validate_academic_journal_references(self):
        html = '<p>Diterbitkan pada jurnal <a href="https://doi.org/10.1109/ACCESS.2026.123456">IEEE Access</a> terindeks Scopus dan SINTA 1.</p>'
        res = YoastSEOValidator.validate_academic_journal_references(html)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["doi_count"], 1)
        self.assertIn("SINTA 1", res["sinta_tiers"])
        self.assertTrue(res["has_scopus_mention"])

        bad_html = '<p><a href="http://doi.org/10.1234/test">DOI HTTP</a></p>'
        res_bad = YoastSEOValidator.validate_academic_journal_references(bad_html)
        self.assertFalse(res_bad["is_valid"])

    def test_audit_table_accessibility(self):
        good_table = '<table><caption>Daftar Matkul</caption><thead><tr><th scope="col">Kode</th><th scope="col">Nama</th></tr></thead><tbody><tr><td>IF101</td><td>Pemrograman</td></tr></tbody></table>'
        res = YoastSEOValidator.audit_table_accessibility(good_table)
        self.assertTrue(res["is_compliant"])
        self.assertEqual(res["accessible_tables"], 1)

        bad_table = '<table><tr><th>Kode</th><th>Nama</th></tr></table>'
        res_bad = YoastSEOValidator.audit_table_accessibility(bad_table)
        self.assertFalse(res_bad["is_compliant"])
        self.assertGreaterEqual(len(res_bad["issues"]), 2)

    def test_evaluate_content_freshness_discrepancy(self):
        fresh_html = "<p>Data penerimaan mahasiswa tahun 2025 dan proyeksi 2026.</p>"
        res = YoastSEOValidator.evaluate_content_freshness_discrepancy(fresh_html, publish_year=2026)
        self.assertTrue(res["is_fresh"])

        stale_html = "<p>Berdasarkan survei tahun 2012 dan teknologi tahun 2015.</p>"
        res_stale = YoastSEOValidator.evaluate_content_freshness_discrepancy(stale_html, publish_year=2026)
        self.assertFalse(res_stale["is_fresh"])
        self.assertGreater(res_stale["stale_reference_count"], 0)

    def test_validate_breadcrumb_hierarchy(self):
        valid_trail = [
            {"name": "Beranda", "url": "/"},
            {"name": "Akademik", "url": "/akademik"},
            {"name": "Kurikulum", "url": "/akademik/kurikulum"}
        ]
        res = YoastSEOValidator.validate_breadcrumb_hierarchy(valid_trail)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["depth"], 3)

        invalid_trail = [{"name": "Artikel", "url": "/artikel"}]
        res_bad = YoastSEOValidator.validate_breadcrumb_hierarchy(invalid_trail)
        self.assertFalse(res_bad["is_valid"])

    def test_audit_css_color_contrast(self):
        good_css = '<p style="color: #ffffff; background-color: #003366;">Kontras Bagus</p>'
        res = YoastSEOValidator.audit_css_color_contrast(good_css)
        self.assertTrue(res["is_accessible"])

        bad_css = '<p style="color: #ffffff; background-color: #ffffff;">Teks Tak Terbaca</p>'
        res_bad = YoastSEOValidator.audit_css_color_contrast(bad_css)
        self.assertFalse(res_bad["is_accessible"])

    def test_validate_og_image_specifications(self):
        valid_url = "https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/banner.jpg"
        res = YoastSEOValidator.validate_og_image_specifications(valid_url, width=1200, height=630)
        self.assertTrue(res["is_valid"])

        invalid_url = "http://example.com/banner.gif"
        res_bad = YoastSEOValidator.validate_og_image_specifications(invalid_url, width=200, height=100)
        self.assertFalse(res_bad["is_valid"])
        self.assertGreaterEqual(len(res_bad["issues"]), 2)

    def test_calculate_indonesian_coleman_liau(self):
        text = "Program Studi Informatika Institut Teknologi Telkom Purwokerto terus berinovasi dalam riset kecerdasan buatan. Mahasiswa dibekali keterampilan praktis dan teoritis."
        res = YoastSEOValidator.calculate_indonesian_coleman_liau(text)
        self.assertIn("score", res)
        self.assertIn("grade_level", res)
        self.assertIn("difficulty", res)
        self.assertGreater(res["word_count"], 10)

    def test_validate_hreflang_alternates(self):
        valid_alts = [
            {"lang": "id", "href": "https://bif-pwt.telkomuniversity.ac.id/artikel/"},
            {"lang": "en", "href": "https://bif-pwt.telkomuniversity.ac.id/en/article/"},
            {"lang": "x-default", "href": "https://bif-pwt.telkomuniversity.ac.id/artikel/"}
        ]
        res = YoastSEOValidator.validate_hreflang_alternates(valid_alts)
        self.assertTrue(res["is_valid"])
        self.assertTrue(res["has_x_default"])

        invalid_alts = [
            {"lang": "xx-invalid", "href": "http://insecure.com"}
        ]
        res_bad = YoastSEOValidator.validate_hreflang_alternates(invalid_alts)
        self.assertFalse(res_bad["is_valid"])

    def test_audit_aria_landmarks(self):
        good_html = '<main><nav aria-label="Navigasi Utama"><a>Menu</a></nav><article><p>Konten</p></article></main>'
        res = YoastSEOValidator.audit_aria_landmarks(good_html)
        self.assertTrue(res["is_accessible"])
        self.assertTrue(res["has_main"])

        bad_html = '<div><nav><a>Menu</a></nav><p>Konten</p></div>'
        res_bad = YoastSEOValidator.audit_aria_landmarks(bad_html)
        self.assertFalse(res_bad["is_accessible"])

    def test_validate_canonical_url(self):
        valid = "https://bif-pwt.telkomuniversity.ac.id/webassembly-edge-computing-iot/"
        res = YoastSEOValidator.validate_canonical_url(valid, current_slug="webassembly-edge-computing-iot")
        self.assertTrue(res["is_valid"])

        invalid = "http://bif-pwt.telkomuniversity.ac.id/webassembly-edge-computing-iot?ref=fb"
        res_bad = YoastSEOValidator.validate_canonical_url(invalid, current_slug="webassembly-edge-computing-iot")
        self.assertFalse(res_bad["is_valid"])

    def test_audit_paragraph_rhythm(self):
        good_html = "<p>Paragraf pendek.</p><p>Paragraf kedua standar.</p>"
        res = YoastSEOValidator.audit_paragraph_rhythm(good_html)
        self.assertTrue(res["is_optimal"])

        dense_html = "<p>" + "kata " * 130 + "</p>"
        res_dense = YoastSEOValidator.audit_paragraph_rhythm(dense_html)
        self.assertFalse(res_dense["is_optimal"])
        self.assertEqual(len(res_dense["issues"]), 1)

    def test_audit_heading_hierarchy_skips(self):
        good_h = '<div class="tu-editorial-container"><h1>Judul</h1><h2>Sub 1</h2><h3>Detail 1</h3><h2>Sub 2</h2></div>'
        res1 = YoastSEOValidator.audit_heading_hierarchy_skips(good_h)
        self.assertTrue(res1["is_valid"])
        self.assertEqual(res1["h1_count"], 1)

        bad_h = '<div class="tu-editorial-container"><h1>Judul</h1><h2>Sub 1</h2><h4>Langsung H4</h4></div>'
        res2 = YoastSEOValidator.audit_heading_hierarchy_skips(bad_h)
        self.assertFalse(res2["is_valid"])
        self.assertTrue(any("skipped from <h2" in iss for iss in res2["issues"]))

    def test_check_indonesian_inflected_keyphrase(self):
        text = "Dosen dan mahasiswa aktif meriset kecerdasan buatan dalam berbagai penelitian unggulan."
        res = YoastSEOValidator.check_indonesian_inflected_keyphrase("riset kecerdasan buatan", text)
        self.assertTrue(res["is_present"])
        self.assertEqual(res["total_matches"], 1)
        self.assertIn("meriset kecerdasan buatan", res["found_forms"])

    def test_validate_twitter_card_meta(self):
        meta_html = (
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="Kurikulum Baru Informatika Telkom">'
            '<meta name="twitter:description" content="Informasi pembaruan silabus perkuliahan komprehensif.">'
            '<meta name="twitter:image" content="https://bif-pwt.telkomuniversity.ac.id/banner.jpg">'
        )
        res = YoastSEOValidator.validate_twitter_card_meta(meta_html)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["card"], "summary_large_image")

        bad_meta = '<meta name="twitter:card" content="invalid_card">'
        res_bad = YoastSEOValidator.validate_twitter_card_meta(bad_meta)
        self.assertFalse(res_bad["is_valid"])

    def test_yoast_audit_coleman_liau_integration(self):
        html = '<div class="tu-editorial-container"><p class="lead">Teknologi kecerdasan buatan terus berkembang pesat.</p><p>' + 'kata ' * 320 + '</p></div>'
        meta = {
            "seo_title": "Teknologi kecerdasan buatan masa depan",
            "slug": "teknologi-kecerdasan-buatan-masa-depan",
            "focus_keyphrase": "teknologi kecerdasan buatan",
            "meta_description": "Ulasan mendalam tentang teknologi kecerdasan buatan di era modern yang sangat relevan dan bermanfaat untuk masa depan digital prodi."
        }
        res = YoastSEOValidator.evaluate(meta, html)
        self.assertIn("coleman_liau", res)
        self.assertIn("grade_level", res["coleman_liau"])
        self.assertIn("difficulty", res["coleman_liau"])

    def test_check_consecutive_sentence_starts(self):
        text_repeating = "Penelitian ini mengkaji AI. Penelitian ini menguji model. Penelitian ini menyimpulkan akurasi tinggi."
        res_rep = YoastSEOValidator.check_consecutive_sentence_starts(text_repeating, threshold=3)
        self.assertTrue(res_rep["has_repetitive_starts"])
        self.assertEqual(len(res_rep["consecutive_groups"]), 1)
        self.assertEqual(res_rep["consecutive_groups"][0]["word"], "penelitian")

        text_varied = "Penelitian ini mengkaji AI. Selanjutnya kami menguji model. Hasil akhir menyimpulkan akurasi tinggi."
        res_var = YoastSEOValidator.check_consecutive_sentence_starts(text_varied, threshold=3)
        self.assertFalse(res_var["has_repetitive_starts"])

    def test_evaluate_paragraph_transition_distribution(self):
        html_good = (
            "<p>Kecerdasan buatan berkembang pesat. Oleh karena itu, kurikulum diperbarui.</p>"
            "<p>Selain itu, laboratorium komputasi juga ditingkatkan fasilitasnya.</p>"
            "<p>Mahasiswa antusias menyambut pembaruan sarana dan prasarana.</p>"
        )
        res_good = YoastSEOValidator.evaluate_paragraph_transition_distribution(html_good, min_ratio=0.3)
        self.assertEqual(res_good["total_paragraphs"], 3)
        self.assertEqual(res_good["paragraphs_with_transitions"], 2)
        self.assertTrue(res_good["is_optimal"])

        html_empty = ""
        res_empty = YoastSEOValidator.evaluate_paragraph_transition_distribution(html_empty)
        self.assertEqual(res_empty["total_paragraphs"], 0)

    def test_validate_meta_description_cta(self):
        cta_desc = "Pelajari kurikulum program studi S1 Teknik Telekomunikasi dan temukan peluang riset IoT."
        res_cta = YoastSEOValidator.validate_meta_description_cta(cta_desc)
        self.assertTrue(res_cta["has_cta"])
        self.assertIn("pelajari", res_cta["matched_ctas"])
        self.assertIn("temukan", res_cta["matched_ctas"])

        no_cta_desc = "Kurikulum program studi Teknik Telekomunikasi tahun ajaran baru."
        res_no_cta = YoastSEOValidator.validate_meta_description_cta(no_cta_desc)
        self.assertFalse(res_no_cta["has_cta"])

    def test_validate_embedded_json_ld(self):
        valid_html = (
            '<script type="application/ld+json">'
            '{"@context": "https://schema.org", "@type": "ScholarlyArticle", "name": "Deep Learning Edge"}'
            '</script>'
        )
        res_valid = YoastSEOValidator.validate_embedded_json_ld(valid_html)
        self.assertTrue(res_valid["is_valid"])
        self.assertEqual(res_valid["total_schemas"], 1)

        invalid_html = (
            '<script type="application/ld+json">'
            '{"@type": "ScholarlyArticle"}'
            '</script>'
        )
        res_invalid = YoastSEOValidator.validate_embedded_json_ld(invalid_html)
        self.assertFalse(res_invalid["is_valid"])
        self.assertGreater(len(res_invalid["issues"]), 0)

    def test_calculate_gunning_fog_index(self):
        text = (
            "Penelitian kecerdasan buatan membutuhkan metodologi komprehensif. "
            "Implementasi arsitektur komputasi terdistribusi meningkatkan efisiensi pemrosesan data."
        )
        res = YoastSEOValidator.calculate_gunning_fog_index(text)
        self.assertGreater(res["grade_level"], 0.0)
        self.assertIn("total_words", res)
        self.assertIn("difficulty", res)

    def test_audit_in_page_anchors(self):
        html_good = (
            '<div>'
            '<a href="#kurikulum">Lihat Kurikulum</a>'
            '<h2 id="kurikulum">Kurikulum S1</h2>'
            '</div>'
        )
        res_good = YoastSEOValidator.audit_in_page_anchors(html_good)
        self.assertTrue(res_good["is_valid"])
        self.assertEqual(len(res_good["valid_anchors"]), 1)

        html_bad = '<div><a href="#missing-section">Bagian Hilang</a></div>'
        res_bad = YoastSEOValidator.audit_in_page_anchors(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertIn("#missing-section", res_bad["broken_anchors"])

    def test_validate_author_academic_credentials(self):
        res1 = YoastSEOValidator.validate_author_academic_credentials(
            "Prof. Dr. Ir. Adiwijaya, M.Kom.",
            "Guru Besar Informatika. ORCID: https://orcid.org/0000-0002-1825-0097"
        )
        self.assertTrue(res1["has_credentials"])
        self.assertTrue(res1["has_orcid"])
        self.assertEqual(res1["orcid_id"], "0000-0002-1825-0097")
        self.assertTrue(res1["is_authoritative"])

        res2 = YoastSEOValidator.validate_author_academic_credentials("John Doe")
        self.assertFalse(res2["has_credentials"])
        self.assertFalse(res2["has_orcid"])

    def test_validate_academic_open_access_disclaimer(self):
        html_cc = (
            '<div class="tu-editorial-container">'
            '<p>Artikel ini dilisensikan di bawah Creative Commons Attribution (CC BY 4.0) Internasional.</p>'
            '</div>'
        )
        res = YoastSEOValidator.validate_academic_open_access_disclaimer(html_cc)
        self.assertTrue(res["has_license"])
        self.assertEqual(res["license_type"], "CC BY")
        self.assertTrue(res["is_compliant"])

        html_no_cc = '<div class="tu-editorial-container"><p>Konten berita kampus biasa.</p></div>'
        res_no = YoastSEOValidator.validate_academic_open_access_disclaimer(html_no_cc)
        self.assertFalse(res_no["has_license"])

    def test_calculate_coleman_liau_index(self):
        text = "Penelitian ini mengkaji performa algoritma routing adaptif pada arsitektur jaringan berbasis perangkat lunak dengan pendekatan pembelajaran mesin mendalam."
        res = YoastSEOValidator.calculate_coleman_liau_index(text)
        self.assertIsInstance(res["score"], float)
        self.assertIn("Tingkat", res["grade_level"])
        self.assertGreater(res["letters_per_100_words"], 0)
        self.assertGreater(res["sentences_per_100_words"], 0)

    def test_audit_heading_hierarchy_order(self):
        good_html = '<div><h1>Judul</h1><h2>Sub 1</h2><h3>Detail 1</h3><h2>Sub 2</h2></div>'
        res_good = YoastSEOValidator.audit_heading_hierarchy_order(good_html)
        self.assertTrue(res_good["is_valid"])
        self.assertEqual(res_good["heading_count"], 4)

        bad_html = '<div><h1>Judul 1</h1><h1>Judul 2</h1><h2>Sub 1</h2><h4>Langsung H4</h4></div>'
        res_bad = YoastSEOValidator.audit_heading_hierarchy_order(bad_html)
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(any("lebih dari satu tag H1" in i for i in res_bad["issues"]))
        self.assertTrue(any("Lompatan hirarki" in i for i in res_bad["issues"]))

    def test_validate_research_grant_acknowledgment(self):
        html_ack = (
            '<div class="tu-editorial-container">'
            '<p>Penelitian ini didanai oleh program Kemendikbudristek BIMA melalui skema Penelitian Fundamental nomor kontrak 045/E1/KS/2026.</p>'
            '</div>'
        )
        res = YoastSEOValidator.validate_research_grant_acknowledgment(html_ack)
        self.assertTrue(res["has_acknowledgment"])
        self.assertEqual(res["funding_agency"], "Kemendikbudristek BIMA")
        self.assertIn("045/E1/KS/2026", res["contract_numbers"])

        html_none = '<div><p>Hanya artikel santai.</p></div>'
        res_none = YoastSEOValidator.validate_research_grant_acknowledgment(html_none)
        self.assertFalse(res_none["has_acknowledgment"])

    def test_audit_image_accessibility_and_dimensions(self):
        html_good = '<div><img src="foto.jpg" alt="Foto laboratorium RF" width="800" height="600" /></div>'
        res_good = YoastSEOValidator.audit_image_accessibility_and_dimensions(html_good)
        self.assertFalse(res_good["has_issues"])
        self.assertEqual(res_good["total_images"], 1)

        html_bad = '<div><img src="banner.png" alt="gambar" /><img src="grafik.png" /></div>'
        res_bad = YoastSEOValidator.audit_image_accessibility_and_dimensions(html_bad)
        self.assertTrue(res_bad["has_issues"])
        self.assertGreaterEqual(res_bad["missing_alt_count"], 1)
        self.assertGreaterEqual(res_bad["missing_dimensions_count"], 2)

    def test_audit_duplicate_element_ids(self):
        good_html = '<div id="header"><h1 id="title">Judul</h1><p id="lead">Lead</p></div>'
        res_good = YoastSEOValidator.audit_duplicate_element_ids(good_html)
        self.assertFalse(res_good["has_duplicates"])
        self.assertEqual(res_good["total_ids"], 3)

        bad_html = '<div id="section-1"><p id="content">P1</p><div id="section-1"><p id="content">P2</p></div></div>'
        res_bad = YoastSEOValidator.audit_duplicate_element_ids(bad_html)
        self.assertTrue(res_bad["has_duplicates"])
        self.assertIn("section-1", res_bad["duplicate_ids"])
        self.assertIn("content", res_bad["duplicate_ids"])
        self.assertGreaterEqual(len(res_bad["issues"]), 2)

    def test_detect_sinta_accreditation(self):
        text_s2 = "Jurnal Rekayasa Sistem dan Teknologi Informasi telah terakreditasi SINTA 2 berdasarkan SK No. 105/E/KPT/2022."
        res = YoastSEOValidator.detect_sinta_accreditation(text_s2)
        self.assertTrue(res["has_sinta"])
        self.assertEqual(res["sinta_rank"], 2)
        self.assertIn("105/E/KPT/2022", res["sk_number"])
        self.assertEqual(res["confidence"], "high")

        text_none = "Artikel opini tanpa publikasi jurnal ilmiah."
        res_none = YoastSEOValidator.detect_sinta_accreditation(text_none)
        self.assertFalse(res_none["has_sinta"])
        self.assertIsNone(res_none["sinta_rank"])
        self.assertEqual(res_none["confidence"], "none")

    def test_audit_meta_robots_directives(self):
        meta_good = {"meta_robots": "index, follow, max-snippet:-1, max-image-preview:large"}
        res_good = YoastSEOValidator.audit_meta_robots_directives(meta_good)
        self.assertTrue(res_good["is_indexable"])
        self.assertTrue(res_good["is_followable"])
        self.assertTrue(res_good["has_snippet_controls"])
        self.assertTrue(res_good["is_optimal"])

        meta_bad = {"meta_robots": "noindex, nofollow"}
        res_bad = YoastSEOValidator.audit_meta_robots_directives(meta_bad)
        self.assertFalse(res_bad["is_indexable"])
        self.assertFalse(res_bad["is_followable"])
        self.assertFalse(res_bad["is_optimal"])
        self.assertGreaterEqual(len(res_bad["warnings"]), 2)

    def test_audit_social_meta_readiness(self):
        meta_ready = {
            "seo_title": "Panduan Riset Antena Mikrostrip 5G",
            "meta_description": "Pelajari rancang bangun antena mikrostrip patch untuk frekuensi 28 GHz di Telkom University Purwokerto.",
            "image_url": "https://telkomuniversity.ac.id/images/antena-5g.webp",
            "twitter_card": "summary_large_image"
        }
        res_ready = YoastSEOValidator.audit_social_meta_readiness(meta_ready)
        self.assertTrue(res_ready["is_ready"])
        self.assertGreaterEqual(res_ready["readiness_score"], 80)
        self.assertEqual(len(res_ready["issues"]), 0)

        meta_incomplete = {"seo_title": ""}
        res_inc = YoastSEOValidator.audit_social_meta_readiness(meta_incomplete)
        self.assertFalse(res_inc["is_ready"])
        self.assertGreaterEqual(len(res_inc["issues"]), 3)

    def test_audit_media_transcripts(self):
        html_good = (
            '<div>'
            '<video src="https://example.com/demo.mp4">'
            '<track kind="subtitles" src="/captions/demo_id.vtt" srclang="id">'
            '</video>'
            '</div>'
        )
        res_good = YoastSEOValidator.audit_media_transcripts(html_good)
        self.assertTrue(res_good["is_compliant"])
        self.assertEqual(res_good["accessible_media"], 1)

        html_bad = '<div><audio src="https://example.com/podcast.mp3"></audio></div>'
        res_bad = YoastSEOValidator.audit_media_transcripts(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["accessible_media"], 0)
        self.assertEqual(len(res_bad["issues"]), 1)

    def test_detect_scimago_sjr_ranking(self):
        text = "Publikasi terindeks Scopus Q1 dengan metrik SJR 1.82 dan h-index 54 pada jurnal IEEE Transactions on Communications."
        res = YoastSEOValidator.detect_scimago_sjr_ranking(text)
        self.assertTrue(res["has_scopus_indexing"])
        self.assertEqual(res["best_quartile"], "Q1")
        self.assertEqual(res["sjr_score"], 1.82)
        self.assertEqual(res["h_index"], 54)

        text_none = "Catatan seminar internal kampus."
        res_none = YoastSEOValidator.detect_scimago_sjr_ranking(text_none)
        self.assertFalse(res_none["has_scopus_indexing"])
        self.assertIsNone(res_none["best_quartile"])

    def test_audit_hreflang_multilingual_tags(self):
        html_good = (
            '<head>'
            '<link rel="alternate" hreflang="id" href="https://bif-pwt.telkomuniversity.ac.id/riset/">'
            '<link rel="alternate" hreflang="en" href="https://bif-pwt.telkomuniversity.ac.id/en/research/">'
            '<link rel="alternate" hreflang="x-default" href="https://bif-pwt.telkomuniversity.ac.id/riset/">'
            '</head>'
        )
        res_good = YoastSEOValidator.audit_hreflang_multilingual_tags(html_good)
        self.assertTrue(res_good["is_valid"])
        self.assertTrue(res_good["has_x_default"])
        self.assertIn("id", res_good["languages_found"])
        self.assertIn("en", res_good["languages_found"])

        html_bad = '<head><link rel="alternate" hreflang="bahasa-indo-123" href=""></head>'
        res_bad = YoastSEOValidator.audit_hreflang_multilingual_tags(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertGreaterEqual(len(res_bad["issues"]), 2)

    def test_audit_breadcrumb_hierarchy(self):
        html_good = (
            '<nav aria-label="breadcrumb">'
            '<ol class="breadcrumb">'
            '<li><a href="/">Beranda</a></li>'
            '<li><a href="/akademik/">Akademik</a></li>'
            '<li><span>Kurikulum 2026</span></li>'
            '</ol>'
            '</nav>'
        )
        res_good = YoastSEOValidator.audit_breadcrumb_hierarchy(html_good)
        self.assertTrue(res_good["is_valid"])
        self.assertEqual(res_good["depth"], 3)
        self.assertTrue(res_good["has_home_root"])
        self.assertEqual(res_good["trail"], ["Beranda", "Akademik", "Kurikulum 2026"])

        html_bad = '<nav aria-label="breadcrumb"><li><span>Kurikulum 2026</span></li></nav>'
        res_bad = YoastSEOValidator.audit_breadcrumb_hierarchy(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertEqual(res_bad["depth"], 1)

    def test_calculate_content_freshness_decay(self):
        # Fresh content (30 days old with fast velocity 365 days half-life)
        res_fresh = YoastSEOValidator.calculate_content_freshness_decay(
            publish_date="2026-09-15",
            field_velocity="fast",
            current_date_str="2026-10-15"
        )
        self.assertEqual(res_fresh["status"], "FRESH")
        self.assertFalse(res_fresh["is_stale"])
        self.assertGreaterEqual(res_fresh["freshness_score"], 90.0)

        # Stale content (800 days old)
        res_stale = YoastSEOValidator.calculate_content_freshness_decay(
            publish_date="2024-08-01",
            field_velocity="fast",
            current_date_str="2026-10-15"
        )
        self.assertTrue(res_stale["is_stale"])
        self.assertIn(res_stale["status"], ("NEEDS_UPDATE", "ARCHIVE_STALE"))
        self.assertLess(res_stale["freshness_score"], 30.0)

    def test_detect_academic_conference_tier(self):
        text_a_star = "Makalah dipresentasikan pada IEEE INFOCOM 2026 di San Francisco."
        res1 = YoastSEOValidator.detect_academic_conference_tier(text_a_star)
        self.assertTrue(res1["has_conference"])
        self.assertEqual(res1["core_tier"], "A*")
        self.assertTrue(res1["is_prestigious"])
        self.assertEqual(res1["publisher_sponsor"], "IEEE Xplore")

        text_b = "Paper diterima pada konferensi internasional IEEE Tencon 2026 di Bali."
        res2 = YoastSEOValidator.detect_academic_conference_tier(text_b)
        self.assertTrue(res2["has_conference"])
        self.assertEqual(res2["core_tier"], "B")
        self.assertTrue(res2["is_prestigious"])

        text_none = "Pertemuan rapat kerja internal program studi."
        res3 = YoastSEOValidator.detect_academic_conference_tier(text_none)
        self.assertFalse(res3["has_conference"])
        self.assertEqual(res3["core_tier"], "Unranked")

    def test_audit_table_of_contents_anchor_integrity(self):
        html_good = (
            '<div class="tu-editorial-container">'
            '<nav class="tu-toc">'
            '<a href="#latar-belakang">Latar Belakang</a>'
            '<a href="#metode">Metodologi</a>'
            '</nav>'
            '<h2 id="latar-belakang">Latar Belakang</h2>'
            '<h2 id="metode">Metodologi</h2>'
            '</div>'
        )
        res_good = YoastSEOValidator.audit_table_of_contents_anchor_integrity(html_good)
        self.assertTrue(res_good["is_valid"])
        self.assertEqual(res_good["valid_targets"], 2)
        self.assertEqual(len(res_good["broken_targets"]), 0)

        html_broken = (
            '<div class="tu-editorial-container">'
            '<nav class="tu-toc">'
            '<a href="#bab-1">Bab 1</a>'
            '<a href="#bab-2">Bab 2 (Hilang)</a>'
            '</nav>'
            '<h2 id="bab-1">Bab 1</h2>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_table_of_contents_anchor_integrity(html_broken)
        self.assertFalse(res_bad["is_valid"])
        self.assertIn("bab-2", res_bad["broken_targets"])

    def test_audit_math_latex_notation_accessibility(self):
        html_good = (
            '<div class="tu-editorial-container">'
            '<p class="tu-math" role="math" aria-label="Persamaan Einstein">'
            '$$E = mc^2$$'
            '</p>'
            '<p>Persamaan inline <span class="katex" role="math">$P = V \\times I$</span> berlaku.</p>'
            '</div>'
        )
        res_good = YoastSEOValidator.audit_math_latex_notation_accessibility(html_good)
        self.assertTrue(res_good["is_balanced"])
        self.assertTrue(res_good["has_accessible_markup"])
        self.assertEqual(res_good["display_count"], 1)
        self.assertEqual(res_good["inline_count"], 1)

        html_unbalanced = (
            '<div class="tu-editorial-container">'
            '<p>Nilai resistansi $R = 100 ohm tanpa penutup.</p>'
            '</div>'
        )
        res_unbalanced = YoastSEOValidator.audit_math_latex_notation_accessibility(html_unbalanced)
        self.assertFalse(res_unbalanced["is_balanced"])
        self.assertTrue(any("tidak berpasangan" in i for i in res_unbalanced["issues"]))

    def test_audit_sinta_author_metadata(self):
        res_ok = YoastSEOValidator.audit_sinta_author_metadata(
            author_name="Dr. Ir. Suryo",
            sinta_id="6001234",
            sinta_score_overall=450.0,
            sinta_score_3yr=180.0,
            profile_url="https://sinta.kemdikbud.go.id/authors/profile/6001234"
        )
        self.assertTrue(res_ok["is_valid"])
        self.assertEqual(res_ok["sinta_id"], "6001234")
        self.assertEqual(res_ok["sinta_score_overall"], 450.0)
        self.assertEqual(res_ok["sinta_score_3yr"], 180.0)
        self.assertEqual(len(res_ok["issues"]), 0)

        res_bad = YoastSEOValidator.audit_sinta_author_metadata(
            author_name="Penulis Baru",
            sinta_id="abc12",
            sinta_score_overall=50.0,
            sinta_score_3yr=90.0,
            profile_url="http://insecure.site.com/profile/999"
        )
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(any("Format SINTA ID" in i for i in res_bad["issues"]))
        self.assertTrue(any("lebih besar dari skor SINTA keseluruhan" in i for i in res_bad["issues"]))
        self.assertTrue(any("protokol HTTPS" in i for i in res_bad["issues"]))

    def test_audit_heading_hierarchy_skipping(self):
        good_html = (
            '<div class="tu-editorial-container">'
            '<h1>Pengantar 5G NR</h1>'
            '<h2>Arsitektur RAN</h2>'
            '<h3>Beamforming</h3>'
            '<h2>Core Network</h2>'
            '<h3>Network Slicing</h3>'
            '<h4>User Plane Function</h4>'
            '</div>'
        )
        res_good = YoastSEOValidator.audit_heading_hierarchy_skipping(good_html)
        self.assertTrue(res_good["is_valid"])
        self.assertEqual(len(res_good["skipped_transitions"]), 0)
        self.assertEqual(res_good["total_headings"], 6)

        bad_html = (
            '<div class="tu-editorial-container">'
            '<h1>Pengantar 5G NR</h1>'
            '<h2>Arsitektur RAN</h2>'
            '<h4>Direct Jump to H4</h4>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_heading_hierarchy_skipping(bad_html)
        self.assertFalse(res_bad["is_valid"])
        self.assertEqual(len(res_bad["skipped_transitions"]), 1)
        self.assertEqual(res_bad["skipped_transitions"][0]["from_level"], 2)
        self.assertEqual(res_bad["skipped_transitions"][0]["to_level"], 4)

    def test_audit_open_graph_multimedia_tags(self):
        good_tags = {
            "og:video": "https://video.telkomuniversity.ac.id/demo.mp4",
            "og:video:type": "video/mp4",
            "og:audio": "https://podcast.telkomuniversity.ac.id/episode1.mp3",
            "og:audio:type": "audio/mpeg"
        }
        res_good = YoastSEOValidator.audit_open_graph_multimedia_tags(good_tags)
        self.assertTrue(res_good["is_valid"])
        self.assertTrue(res_good["has_video"])
        self.assertTrue(res_good["has_audio"])
        self.assertEqual(len(res_good["issues"]), 0)

        bad_tags = {
            "og:video": "http://insecure.com/video.flv",
            "og:video:type": "video/unknown-codec",
            "og:audio": "http://insecure.com/audio.raw"
        }
        res_bad = YoastSEOValidator.audit_open_graph_multimedia_tags(bad_tags)
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(any("tidak menggunakan HTTPS" in i for i in res_bad["issues"]))
        self.assertTrue(any("tidak didukung Open Graph" in i for i in res_bad["issues"]))
        self.assertTrue(any("tanpa og:audio:type" in i for i in res_bad["issues"]))

    def test_audit_table_summary_and_caption_accessibility(self):
        accessible_html = (
            '<div class="tu-editorial-container">'
            '<table>'
            '<caption>Alokasi Spektrum 5G Kampus</caption>'
            '<tr><th scope="col">Band</th><th scope="col">Frekuensi</th></tr>'
            '<tr><td>n78</td><td>3.5 GHz</td></tr>'
            '</table>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_table_summary_and_caption_accessibility(accessible_html)
        self.assertTrue(res_ok["is_accessible"])
        self.assertEqual(res_ok["total_tables"], 1)
        self.assertEqual(res_ok["accessible_tables"], 1)

        inaccessible_html = (
            '<div class="tu-editorial-container">'
            '<table>'
            '<tr><td>Hanya sel data</td><td>Tanpa TH atau Caption</td></tr>'
            '</table>'
            '</div>'
        )
        res_fail = YoastSEOValidator.audit_table_summary_and_caption_accessibility(inaccessible_html)
        self.assertFalse(res_fail["is_accessible"])
        self.assertEqual(res_fail["accessible_tables"], 0)
        self.assertTrue(any("caption" in i or "aria-label" in i for i in res_fail["issues"]))
        self.assertTrue(any("<th>" in i for i in res_fail["issues"]))

    def test_audit_duplicate_meta(self):
        records = [
            {"id": 1, "slug": "iot-lora-maritim", "seo_title": "IoT LoRa Maritim untuk Nelayan", "meta_description": "Panduan implementasi jaringan sensor LoRa untuk pemantauan maritim terpadu."},
            {"id": 2, "slug": "5g-slicing-kampus", "seo_title": "Arsitektur Network Slicing 5G", "meta_description": "Ulasan komprehensif mengenai teknik slicing radio access network pada kampus cerdas."}
        ]
        # Duplicate title
        res_dup_title = YoastSEOValidator.audit_duplicate_meta("IoT LoRa Maritim untuk Nelayan", "Deskripsi baru yang unik dan tidak terduplikasi sama sekali.", records)
        self.assertFalse(res_dup_title["is_clean"])
        self.assertTrue(res_dup_title["has_title_conflict"])
        self.assertFalse(res_dup_title["has_desc_conflict"])

        # Duplicate description
        res_dup_desc = YoastSEOValidator.audit_duplicate_meta("Judul Unik 2026", "Panduan implementasi jaringan sensor LoRa untuk pemantauan maritim terpadu.", records)
        self.assertFalse(res_dup_desc["is_clean"])
        self.assertTrue(res_dup_desc["has_desc_conflict"])

        # Clean meta
        res_clean = YoastSEOValidator.audit_duplicate_meta("Inovasi Transmisi Satelit LEO", "Deskripsi baru satelit orbit rendah tanpa kemiripan.", records)
        self.assertTrue(res_clean["is_clean"])
        self.assertFalse(res_clean["has_title_conflict"])
        self.assertFalse(res_clean["has_desc_conflict"])

    def test_audit_robots_meta_directives(self):
        html_good = (
            '<html><head>'
            '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">'
            '</head><body><p>Konten</p></body></html>'
        )
        res_good = YoastSEOValidator.audit_robots_meta_directives(html_good)
        self.assertTrue(res_good["has_robots_meta"])
        self.assertTrue(res_good["is_indexable"])
        self.assertTrue(res_good["is_followable"])
        self.assertTrue(res_good["has_snippet_control"])
        self.assertEqual(len(res_good["blocking_reasons"]), 0)

        html_blocked = (
            '<html><head>'
            '<meta name="robots" content="noindex, nofollow">'
            '</head><body><p>Rahasia</p></body></html>'
        )
        res_blocked = YoastSEOValidator.audit_robots_meta_directives(html_blocked)
        self.assertFalse(res_blocked["is_indexable"])
        self.assertFalse(res_blocked["is_followable"])
        self.assertGreaterEqual(len(res_blocked["blocking_reasons"]), 2)

    def test_audit_video_accessibility(self):
        html_accessible = (
            '<div class="tu-editorial-container">'
            '<video controls title="Tutorial Praktikum Serat Optik">'
            '<source src="fiber.mp4" type="video/mp4">'
            '<track src="captions.vtt" kind="captions" srclang="id" label="Bahasa Indonesia">'
            '<p>Browser Anda tidak mendukung tag video. Unduh di <a href="fiber.mp4">sini</a>.</p>'
            '</video>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_video_accessibility(html_accessible)
        self.assertTrue(res_ok["is_accessible"])
        self.assertEqual(res_ok["accessible_videos"], 1)

        html_inaccessible = (
            '<div class="tu-editorial-container">'
            '<video src="insecure.mp4"></video>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_video_accessibility(html_inaccessible)
        self.assertFalse(res_bad["is_accessible"])
        self.assertEqual(res_bad["accessible_videos"], 0)
        self.assertTrue(any("captions" in i for i in res_bad["issues"]))
        self.assertTrue(any("accessible label" in i for i in res_bad["issues"]))

    def test_calculate_text_to_code_ratio(self):
        # Optimal content
        article_text = "<p>" + ("Teknologi telekomunikasi terus berkembang pesat menuju era 6G. " * 20) + "</p>"
        res_optimal = YoastSEOValidator.calculate_text_to_code_ratio(article_text)
        self.assertTrue(res_optimal["is_optimal"])
        self.assertEqual(res_optimal["status"], "optimal")
        self.assertGreater(res_optimal["ratio_percent"], 15.0)

        # Bloated markup with very little content
        bloated_html = "<div class='a'><div class='b'><div class='c'><span style='padding:0'>Hai</span></div></div></div>" * 5
        res_bloat = YoastSEOValidator.calculate_text_to_code_ratio(bloated_html)
        self.assertFalse(res_bloat["is_optimal"])
        self.assertEqual(res_bloat["status"], "low_content")

    def test_audit_audio_accessibility(self):
        html_ok = (
            '<div class="tu-editorial-container">'
            '<div>'
            '<audio controls title="Podcast Telekomunikasi Episode 1" aria-label="Podcast Episode 1">'
            '<source src="podcast.mp3" type="audio/mpeg">'
            '</audio>'
            '<p class="transcript">Transkrip lengkap podcast membahas jaringan 5G...</p>'
            '</div>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_audio_accessibility(html_ok)
        self.assertTrue(res_ok["is_accessible"])
        self.assertEqual(res_ok["accessible_audios"], 1)

        html_bad = '<audio src="bad.mp3"></audio>'
        res_bad = YoastSEOValidator.audit_audio_accessibility(html_bad)
        self.assertFalse(res_bad["is_accessible"])
        self.assertEqual(res_bad["accessible_audios"], 0)
        self.assertTrue(any("controls" in i for i in res_bad["issues"]))

    def test_audit_hreflang_tags(self):
        html_ok = (
            '<html><head>'
            '<link rel="alternate" hreflang="id" href="https://bif-pwt.telkomuniversity.ac.id/artikel-5g/">'
            '<link rel="alternate" hreflang="en" href="https://bif-pwt.telkomuniversity.ac.id/en/artikel-5g/">'
            '<link rel="alternate" hreflang="x-default" href="https://bif-pwt.telkomuniversity.ac.id/artikel-5g/">'
            '</head><body><p>Konten</p></body></html>'
        )
        res_ok = YoastSEOValidator.audit_hreflang_tags(html_ok, current_url="https://bif-pwt.telkomuniversity.ac.id/artikel-5g/")
        self.assertTrue(res_ok["is_valid"])
        self.assertEqual(res_ok["total_tags"], 3)
        self.assertTrue(res_ok["has_x_default"])

        html_bad = (
            '<html><head>'
            '<link rel="alternate" hreflang="bad_lang_code" href="/relative-path">'
            '</head><body><p>Konten</p></body></html>'
        )
        res_bad = YoastSEOValidator.audit_hreflang_tags(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(any("invalid language code" in i for i in res_bad["issues"]))
        self.assertTrue(any("absolute URL" in i for i in res_bad["issues"]))

    def test_audit_iframe_performance(self):
        html_ok = (
            '<div class="tu-editorial-container">'
            '<iframe src="https://maps.google.com/embed" loading="lazy" title="Peta Kampus Telkom Purwokerto"></iframe>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_iframe_performance(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["optimized_iframes"], 1)

        html_bad = '<iframe src="http://insecure.com/video"></iframe>'
        res_bad = YoastSEOValidator.audit_iframe_performance(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("loading='lazy'" in i for i in res_bad["issues"]))
        self.assertTrue(any("title" in i for i in res_bad["issues"]))
        self.assertTrue(any("HTTPS" in i for i in res_bad["issues"]))

    def test_audit_figure_figcaption_structure(self):
        html_ok = (
            '<div class="tu-editorial-container">'
            '<figure>'
            '<img src="diagram.png" alt="Diagram Topologi">'
            '<figcaption>Gambar 1: Topologi Jaringan Sensor LoRaWAN</figcaption>'
            '</figure>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_figure_figcaption_structure(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["valid_figures"], 1)

        html_bad = (
            '<div class="tu-editorial-container">'
            '<figure>'
            '<figcaption>Caption 1</figcaption>'
            '<p>Teks biasa tanpa media</p>'
            '<figcaption>Caption 2</figcaption>'
            '</figure>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_figure_figcaption_structure(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("multiple" in i for i in res_bad["issues"]))
        self.assertTrue(any("standard visual media" in i for i in res_bad["issues"]))

    def test_audit_table_accessibility(self):
        html_ok = (
            '<div class="tu-editorial-container">'
            '<table>'
            '<caption>Tabel 1: Perbandingan Metrik Modulasi</caption>'
            '<thead><tr><th scope="col">Modulasi</th><th scope="col">Spektrum</th></tr></thead>'
            '<tbody><tr><td>QPSK</td><td>2 bps/Hz</td></tr></tbody>'
            '</table>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_table_accessibility(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["accessible_tables"], 1)

        html_bad = '<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>'
        res_bad = YoastSEOValidator.audit_table_accessibility(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("lacks an accessible description" in i for i in res_bad["issues"]))
        self.assertTrue(any("scope attribute" in i for i in res_bad["issues"]))

    def test_audit_form_labels_and_autocomplete(self):
        html_ok = (
            '<form>'
            '<label for="u_email">Email:</label>'
            '<input type="email" id="u_email" autocomplete="email">'
            '<label><input type="checkbox"> Setuju</label>'
            '</form>'
        )
        res_ok = YoastSEOValidator.audit_form_labels_and_autocomplete(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["labeled_controls"], 2)

        html_bad = '<form><input type="email" id="bad_email"></form>'
        res_bad = YoastSEOValidator.audit_form_labels_and_autocomplete(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("associated <label>" in i for i in res_bad["issues"]))
        self.assertTrue(any("autocomplete" in i for i in res_bad["issues"]))

    def test_audit_content_language_and_direction(self):
        html_ok = '<div class="tu-editorial-container" lang="id-ID" dir="ltr"><p>Konten Bahasa Indonesia</p></div>'
        res_ok = YoastSEOValidator.audit_content_language_and_direction(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["declared_lang"], "id-ID")
        self.assertEqual(res_ok["declared_dir"], "ltr")

        html_bad = '<div class="tu-editorial-container" dir="diagonal"><p>Teks</p></div>'
        res_bad = YoastSEOValidator.audit_content_language_and_direction(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("lacks a declared 'lang'" in i for i in res_bad["issues"]))
        self.assertTrue(any("directionality" in i for i in res_bad["issues"]))

    def test_audit_svg_accessibility(self):
        html_ok = (
            '<div>'
            '<svg aria-hidden="true"><circle cx="5" cy="5" r="5"/></svg>'
            '<svg role="img" aria-label="Grafik Antena"><rect width="10" height="10"/></svg>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_svg_accessibility(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["accessible_svgs"], 2)

        html_bad = '<svg><path d="M0 0"/></svg>'
        res_bad = YoastSEOValidator.audit_svg_accessibility(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("lacks accessible labeling" in i for i in res_bad["issues"]))

    def test_audit_breadcrumb_accessibility(self):
        html_ok = (
            '<nav aria-label="breadcrumb">'
            '<ol class="breadcrumb">'
            '<li><a href="/">Beranda</a></li>'
            '<li><a href="/kurikulum">Kurikulum</a></li>'
            '<li aria-current="page">S1 Teknik Telekomunikasi</li>'
            '</ol>'
            '</nav>'
        )
        res_ok = YoastSEOValidator.audit_breadcrumb_accessibility(html_ok)
        self.assertTrue(res_ok["has_breadcrumb"])
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["total_crumbs"], 3)

        html_bad = (
            '<nav class="breadcrumb">'
            '<a href="/">Home</a> > <span>Kurikulum</span>'
            '</nav>'
        )
        res_bad = YoastSEOValidator.audit_breadcrumb_accessibility(html_bad)
        self.assertTrue(res_bad["has_breadcrumb"])
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("daftar semantik" in i for i in res_bad["issues"]))
        self.assertTrue(any("aria-current='page'" in i for i in res_bad["issues"]))

    def test_audit_video_media_accessibility(self):
        html_ok = (
            '<div class="tu-editorial-container">'
            '<video controls poster="https://example.com/poster.jpg">'
            '<source src="video.mp4" type="video/mp4">'
            '<track kind="captions" src="sub.vtt" srclang="id" label="Indonesia">'
            '<p>Browser Anda tidak mendukung HTML5 video.</p>'
            '</video>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_video_media_accessibility(html_ok)
        self.assertTrue(res_ok["has_videos"])
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["compliant_videos"], 1)

        html_bad = '<video src="stream.mp4"></video>'
        res_bad = YoastSEOValidator.audit_video_media_accessibility(html_bad)
        self.assertTrue(res_bad["has_videos"])
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("controls" in i for i in res_bad["issues"]))
        self.assertTrue(any("poster" in i for i in res_bad["issues"]))
        self.assertTrue(any("track" in i for i in res_bad["issues"]))

    def test_audit_external_links_security(self):
        html_ok = (
            '<p>'
            '<a href="https://telkomuniversity.ac.id/profil" target="_blank">Internal</a> '
            '<a href="https://ieee.org/papers" target="_blank" rel="noopener noreferrer">IEEE Portal</a>'
            '</p>'
        )
        res_ok = YoastSEOValidator.audit_external_links_security(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["external_links"], 1)
        self.assertEqual(res_ok["secure_links"], 1)

        html_bad = (
            '<p><a href="https://external-hacker.com/exploit" target="_blank">Insecure Link</a></p>'
        )
        res_bad = YoastSEOValidator.audit_external_links_security(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("rel='noopener'" in i for i in res_bad["issues"]))

    def test_audit_blockquote_citations(self):
        html_ok = (
            '<blockquote cite="https://itu.int/standards">'
            '<p>Standarisasi 5G New Radio menetapkan latensi ultra-rendah.</p>'
            '<cite>ITU-R Recommendation M.2083</cite>'
            '</blockquote>'
        )
        res_ok = YoastSEOValidator.audit_blockquote_citations(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["attributed_quotes"], 1)

        html_bad = '<blockquote><p>Kutipan tanpa atribusi apa pun.</p></blockquote>'
        res_bad = YoastSEOValidator.audit_blockquote_citations(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("sumber atribusi" in i for i in res_bad["issues"]))

    def test_audit_audio_accessibility_controls(self):
        html_ok = (
            '<div>'
            '<audio controls><source src="podcast.mp3" type="audio/mpeg"></audio>'
            '<p><a href="/transkrip/podcast.txt">Baca transkrip teks rekaman</a></p>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_audio_accessibility_controls(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["accessible_audio"], 1)

        html_bad = '<audio autoplay src="audio.mp3"></audio>'
        res_bad = YoastSEOValidator.audit_audio_accessibility_controls(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("controls" in i for i in res_bad["issues"]))
        self.assertTrue(any("autoplay" in i for i in res_bad["issues"]))

    def test_audit_semantic_definition_lists(self):
        html_ok = (
            '<dl>'
            '<dt>EIRP</dt><dd>Effective Isotropic Radiated Power</dd>'
            '<dt>FSPL</dt><dd>Free Space Path Loss</dd>'
            '</dl>'
        )
        res_ok = YoastSEOValidator.audit_semantic_definition_lists(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["valid_dl"], 1)

        html_bad = '<dl><dt>Orphaned Term</dt></dl>'
        res_bad = YoastSEOValidator.audit_semantic_definition_lists(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("tidak memiliki penjelasan <dd>" in i for i in res_bad["issues"]))

    def test_audit_image_cls_dimensions(self):
        html_ok = '<img src="/img/diagram.png" width="800" height="600" alt="Topology">'
        res_ok = YoastSEOValidator.audit_image_cls_dimensions(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["sized_images"], 1)

        html_bad = '<img src="/img/no-size.png" alt="No size">'
        res_bad = YoastSEOValidator.audit_image_cls_dimensions(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("tidak memiliki atribut eksplisit" in i for i in res_bad["issues"]))

    def test_audit_mathml_accessibility(self):
        html_ok = (
            '<math display="block" alttext="E = m c^2">'
            '<mrow><mi>E</mi><mo>=</mo><mi>m</mi><msup><mi>c</mi><mn>2</mn></msup></mrow>'
            '</math>'
        )
        res_ok = YoastSEOValidator.audit_mathml_accessibility(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["accessible_math"], 1)

        html_bad = '<math display="random"><mi>x</mi></math>'
        res_bad = YoastSEOValidator.audit_mathml_accessibility(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("tidak standar" in i for i in res_bad["issues"]))
        self.assertTrue(any("anotasi teks aksesibel" in i for i in res_bad["issues"]))

    def test_audit_inp_script_accessibility(self):
        html_ok = (
            '<div>'
            '<script src="https://cdn.example.com/app.js" defer></script>'
            '<script src="https://cdn.example.com/analytics.js" async></script>'
            '<button class="btn">Klik</button>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_inp_script_accessibility(html_ok)
        self.assertTrue(res_ok["is_inp_optimized"])
        self.assertEqual(res_ok["render_blocking_scripts"], 0)
        self.assertEqual(res_ok["async_or_deferred_scripts"], 2)

        html_bad = (
            '<div>'
            '<script src="https://cdn.example.com/blocking.js"></script>'
            '<button onclick="doSomething()">Klik</button>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_inp_script_accessibility(html_bad)
        self.assertFalse(res_bad["is_inp_optimized"])
        self.assertEqual(res_bad["render_blocking_scripts"], 1)
        self.assertEqual(res_bad["inline_event_handlers"], 1)

    def test_audit_rich_media_opengraph(self):
        html_ok = (
            '<head>'
            '<meta property="og:video" content="https://example.com/video.mp4">'
            '<meta property="og:video:secure_url" content="https://example.com/video.mp4">'
            '<meta property="og:video:type" content="video/mp4">'
            '<meta property="og:video:width" content="1280">'
            '<meta property="og:video:height" content="720">'
            '<meta property="og:audio" content="https://example.com/podcast.mp3">'
            '<meta property="og:audio:type" content="audio/mpeg">'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_rich_media_opengraph(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["has_video_og"])
        self.assertTrue(res_ok["has_audio_og"])

        html_bad = (
            '<head>'
            '<meta property="og:video" content="http://insecure.example.com/video.mp4">'
            '<meta property="og:audio" content="http://insecure.example.com/audio.mp3">'
            '</head>'
        )
        res_bad = YoastSEOValidator.audit_rich_media_opengraph(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("HTTPS" in i for i in res_bad["issues"]))
        self.assertTrue(any("og:video:type" in i for i in res_bad["issues"]))

    def test_audit_picture_source_fallbacks(self):
        html_ok = (
            '<picture>'
            '<source srcset="/img/opt.avif" type="image/avif">'
            '<source srcset="/img/opt.webp" type="image/webp">'
            '<img src="/img/opt.jpg" alt="Optimal diagram">'
            '</picture>'
        )
        res_ok = YoastSEOValidator.audit_picture_source_fallbacks(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["valid_pictures"], 1)

        html_bad = '<picture><source srcset="/img/opt.webp"></picture>'
        res_bad = YoastSEOValidator.audit_picture_source_fallbacks(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["missing_fallback_img"], 1)

    def test_audit_semantic_landmark_regions(self):
        html_ok = (
            '<html>'
            '<header>Banner</header>'
            '<nav aria-label="Navigasi Utama">Menu</nav>'
            '<main><p>Konten Utama</p></main>'
            '<footer>Hak Cipta</footer>'
            '</html>'
        )
        res_ok = YoastSEOValidator.audit_semantic_landmark_regions(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["has_main"])
        self.assertEqual(res_ok["main_count"], 1)

        html_bad = (
            '<html>'
            '<main>Main 1</main>'
            '<main>Main 2</main>'
            '<nav>Nav 1</nav>'
            '<nav>Nav 2</nav>'
            '</html>'
        )
        res_bad = YoastSEOValidator.audit_semantic_landmark_regions(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("elemen <main>" in i for i in res_bad["issues"]))
        self.assertTrue(any("tanpa atribut 'aria-label'" in i for i in res_bad["issues"]))

    def test_audit_font_display_and_preload(self):
        html_ok = (
            '<head>'
            '<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>'
            '<style>@font-face { font-family: Inter; src: url(/fonts/inter.woff2); font-display: swap; }</style>'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_font_display_and_preload(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["font_preloads_count"], 1)
        self.assertTrue(res_ok["font_display_optimized"])

        html_bad = (
            '<head>'
            '<link rel="preload" href="/fonts/bad.woff2" as="font">'
            '<style>@font-face { font-family: Bad; src: url(/fonts/bad.woff2); }</style>'
            '</head>'
        )
        res_bad = YoastSEOValidator.audit_font_display_and_preload(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["missing_crossorigin_count"], 1)
        self.assertFalse(res_bad["font_display_optimized"])

    def test_audit_opengraph_article_metadata(self):
        html_ok = (
            '<head>'
            '<meta property="og:type" content="article">'
            '<meta property="article:published_time" content="2026-10-23T08:00:00Z">'
            '<meta property="article:author" content="Dr. Ir. Hendra">'
            '<meta property="article:section" content="Telekomunikasi">'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_opengraph_article_metadata(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["has_article_og"])
        self.assertEqual(res_ok["author"], "Dr. Ir. Hendra")

        html_bad = (
            '<head>'
            '<meta property="og:type" content="website">'
            '<meta property="article:published_time" content="invalid-date">'
            '</head>'
        )
        res_bad = YoastSEOValidator.audit_opengraph_article_metadata(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertTrue(any("og:type" in i for i in res_bad["issues"]))
        self.assertTrue(any("ISO 8601" in i for i in res_bad["issues"]))

    def test_audit_details_summary_accessibility(self):
        html_ok = (
            '<details>'
            '<summary>Pertanyaan Umum Seputar SKS</summary>'
            '<p>Penjelasan lengkap konversi SKS.</p>'
            '</details>'
        )
        res_ok = YoastSEOValidator.audit_details_summary_accessibility(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["valid_details"], 1)

        html_bad = (
            '<details>'
            '<summary><a href="#">Link di dalam summary</a></summary>'
            '<p>Konten</p>'
            '</details>'
        )
        res_bad = YoastSEOValidator.audit_details_summary_accessibility(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["nested_interactive_count"], 1)

    def test_audit_touch_target_accessibility(self):
        html_ok = (
            '<div>'
            '<button aria-label="Kirim Formulir" style="padding: 12px 24px;">Kirim</button>'
            '<a href="/detail" style="display:inline-block; padding: 10px;">Lihat Detail</a>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_touch_target_accessibility(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["accessible_targets"], 2)

        html_bad = (
            '<div>'
            '<a href="/empty"></a>'
            '<button style="font-size: 8px;">Kecil</button>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_touch_target_accessibility(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["unlabeled_targets"], 1)
        self.assertEqual(res_bad["cramped_targets"], 1)

    def test_audit_av_transcripts_and_captions(self):
        html_ok = (
            '<div>'
            '<video><track kind="captions" src="/sub.vtt" srclang="id"></video>'
            '<div class="tu-media-transcript"><p>Teks rekaman webinar.</p></div>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_av_transcripts_and_captions(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["captioned_videos"], 1)

        html_bad = '<div><video><source src="clip.mp4"></video></div>'
        res_bad = YoastSEOValidator.audit_av_transcripts_and_captions(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["captioned_videos"], 0)

    def test_audit_rel_canonical_urls(self):
        html_ok = '<head><link rel="canonical" href="https://ittelkom-pwt.ac.id/riset-telekomunikasi"></head>'
        res_ok = YoastSEOValidator.audit_rel_canonical_urls(html_ok)
        self.assertTrue(res_ok["is_valid"])
        self.assertTrue(res_ok["is_https"])
        self.assertFalse(res_ok["has_tracking_params"])

        html_bad = '<head><link rel="canonical" href="http://ittelkom-pwt.ac.id/riset?utm_source=news"></head>'
        res_bad = YoastSEOValidator.audit_rel_canonical_urls(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(res_bad["has_tracking_params"])

    def test_audit_breadcrumb_navigation_schema(self):
        html_ok = (
            '<nav aria-label="breadcrumb">'
            '<ol itemscope itemtype="https://schema.org/BreadcrumbList">'
            '<li itemprop="itemListElement"><a href="/">Beranda</a></li>'
            '<li itemprop="itemListElement" aria-current="page">Akademik</li>'
            '</ol>'
            '</nav>'
        )
        res_ok = YoastSEOValidator.audit_breadcrumb_navigation_schema(html_ok)
        self.assertTrue(res_ok["is_valid"])
        self.assertTrue(res_ok["has_schema_markup"])
        self.assertTrue(res_ok["has_aria_current"])

        html_bad = '<nav><ol><li>Hanya Satu</li></ol></nav>'
        res_bad = YoastSEOValidator.audit_breadcrumb_navigation_schema(html_bad)
        self.assertFalse(res_bad["is_valid"])

    def test_audit_cls_media_aspect_ratios(self):
        html_ok = (
            '<div>'
            '<img src="/foto.jpg" width="600" height="400">'
            '<canvas width="300" height="200"></canvas>'
            '<iframe src="/embed" style="aspect-ratio: 16/9;"></iframe>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_cls_media_aspect_ratios(html_ok)
        self.assertTrue(res_ok["is_cls_safe"])
        self.assertEqual(res_ok["dimensioned_elements"], 3)

        html_bad = '<div><img src="/shift.jpg"></div>'
        res_bad = YoastSEOValidator.audit_cls_media_aspect_ratios(html_bad)
        self.assertFalse(res_bad["is_cls_safe"])
        self.assertEqual(res_bad["missing_dimensions_count"], 1)

    def test_audit_hreflang_localization_tags(self):
        html_ok = (
            '<head>'
            '<link rel="alternate" hreflang="id" href="https://ittelkom-pwt.ac.id/riset">'
            '<link rel="alternate" hreflang="en" href="https://ittelkom-pwt.ac.id/en/research">'
            '<link rel="alternate" hreflang="x-default" href="https://ittelkom-pwt.ac.id/riset">'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_hreflang_localization_tags(html_ok, current_lang="id")
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["has_self_ref"])
        self.assertTrue(res_ok["has_x_default"])

        html_bad = '<head><link rel="alternate" hreflang="invalid_code" href="http://unencrypted.com"></head>'
        res_bad = YoastSEOValidator.audit_hreflang_localization_tags(html_bad, current_lang="id")
        self.assertFalse(res_bad["is_compliant"])

    def test_audit_robots_meta_directives(self):
        html_ok = '<head><meta name="robots" content="index, follow, max-image-preview:large"></head>'
        res_ok = YoastSEOValidator.audit_robots_meta_directives(html_ok, is_production=True)
        self.assertTrue(res_ok["is_compliant"])
        self.assertTrue(res_ok["is_indexable"])

        html_bad = '<head><meta name="robots" content="noindex, follow"></head>'
        res_bad = YoastSEOValidator.audit_robots_meta_directives(html_bad, is_production=True)
        self.assertFalse(res_bad["is_compliant"])
        self.assertFalse(res_bad["is_indexable"])

    def test_audit_faqpage_schema_markup(self):
        html_ok = (
            '<div>'
            '<script type="application/ld+json">'
            '{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "Berapa SKS?"}]}'
            '</script>'
            '<details><summary>Berapa SKS?</summary><p>20 SKS.</p></details>'
            '<details><summary>Syarat IPK?</summary><p>Min 3.00.</p></details>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_faqpage_schema_markup(html_ok)
        self.assertTrue(res_ok["has_faqpage_schema"])
        self.assertTrue(res_ok["is_compliant"])

        html_bad = (
            '<div>'
            '<details><summary>Tanya 1</summary><p>Jawab 1</p></details>'
            '<details><summary>Tanya 2</summary><p>Jawab 2</p></details>'
            '</div>'
        )
        res_bad = YoastSEOValidator.audit_faqpage_schema_markup(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertFalse(res_bad["has_faqpage_schema"])

    def test_audit_table_caption_and_headers(self):
        html_ok = (
            '<table>'
            '<caption>Tabel Distribusi Spektrum Frekuensi</caption>'
            '<tr><th scope="col">Kanal</th><th scope="col">Frekuensi</th></tr>'
            '<tr><td>CH 1</td><td>2412 MHz</td></tr>'
            '</table>'
        )
        res_ok = YoastSEOValidator.audit_table_caption_and_headers(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["captioned_tables"], 1)
        self.assertEqual(res_ok["scoped_headers"], 2)

        html_bad = '<table><tr><th>Kanal</th></tr></table>'
        res_bad = YoastSEOValidator.audit_table_caption_and_headers(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["captioned_tables"], 0)

    def test_audit_web_app_manifest_and_pwa(self):
        html_ok = (
            '<head>'
            '<link rel="manifest" href="/manifest.webmanifest">'
            '<meta name="theme-color" content="#0284c7">'
            '<link rel="apple-touch-icon" href="/icons/apple-icon-180.png">'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_web_app_manifest_and_pwa(html_ok)
        self.assertTrue(res_ok["has_manifest"])
        self.assertTrue(res_ok["has_theme_color"])
        self.assertTrue(res_ok["has_apple_touch_icon"])
        self.assertTrue(res_ok["is_pwa_ready"])

        html_bad = '<head><title>No PWA</title></head>'
        res_bad = YoastSEOValidator.audit_web_app_manifest_and_pwa(html_bad)
        self.assertFalse(res_bad["is_pwa_ready"])
        self.assertFalse(res_bad["has_manifest"])

    def test_audit_pagination_rel_links(self):
        html_ok = (
            '<head>'
            '<link rel="prev" href="https://example.com/page/1/">'
            '<link rel="next" href="https://example.com/page/3/">'
            '</head>'
        )
        res_ok = YoastSEOValidator.audit_pagination_rel_links(html_ok, current_url="https://example.com/page/2/")
        self.assertTrue(res_ok["has_pagination"])
        self.assertTrue(res_ok["has_prev"])
        self.assertTrue(res_ok["has_next"])
        self.assertTrue(res_ok["is_valid"])

        # Identical URLs error
        html_bad = (
            '<head>'
            '<link rel="prev" href="https://example.com/loop/">'
            '<link rel="next" href="https://example.com/loop/">'
            '</head>'
        )
        res_bad = YoastSEOValidator.audit_pagination_rel_links(html_bad)
        self.assertFalse(res_bad["is_valid"])
        self.assertTrue(any("identik" in i for i in res_bad["issues"]))

    def test_audit_howto_schema_markup(self):
        html_ok = (
            '<div>'
            '<script type="application/ld+json">'
            '{"@context": "https://schema.org", "@type": "HowTo", "name": "Cara Splicing Fiber Optic", "step": [{"@type": "HowToStep", "name": "Kupas jaket", "text": "Gunakan stripper"}]}'
            '</script>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_howto_schema_markup(html_ok)
        self.assertTrue(res_ok["has_howto_schema"])
        self.assertTrue(res_ok["has_name"])
        self.assertEqual(res_ok["step_count"], 1)
        self.assertTrue(res_ok["is_compliant"])

        html_bad = '<div><p>Tanpa HowTo Schema</p></div>'
        res_bad = YoastSEOValidator.audit_howto_schema_markup(html_bad)
        self.assertFalse(res_bad["has_howto_schema"])
        self.assertFalse(res_bad["is_compliant"])

    def test_audit_multimedia_audio_descriptions(self):
        html_ok = (
            '<div>'
            '<video src="lecture.mp4">'
            '<track kind="descriptions" src="desc.vtt" srclang="id" label="Audio Deskripsi">'
            '</video>'
            '</div>'
        )
        res_ok = YoastSEOValidator.audit_multimedia_audio_descriptions(html_ok)
        self.assertTrue(res_ok["is_compliant"])
        self.assertEqual(res_ok["total_videos"], 1)
        self.assertEqual(res_ok["described_videos"], 1)

        html_bad = '<video src="undescribed.mp4"></video>'
        res_bad = YoastSEOValidator.audit_multimedia_audio_descriptions(html_bad)
        self.assertFalse(res_bad["is_compliant"])
        self.assertEqual(res_bad["described_videos"], 0)


if __name__ == "__main__":
    unittest.main()





