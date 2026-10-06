# Perubahan #61: Rilis Fitur & Arsitektur v2.4.0

## Metadata Perubahan
- **ID**: #61
- **Modul**: `sanitizer.py`, `parser.py`, `seo_validator.py`, `components.py`, `formatters.py`, `storage.py`, `wordpress_client.py`, `exporter.py`, `cli.py`, `scripts/check_images.py`
- **Test Suite**: `tests/` (203 Tests Passing, 100% Success Rate)

## Deskripsi Teknis
Ekspansi arsitektur editorial otomatis Telkom University Purwokerto versi 2.4.0 mencakup 37 pembaruan terstruktur:

1. **Penyaringan Keamanan & Sanitasi Media (`sanitizer.py`)**:
   - Sanitasi persamaan rumus MathML (`<math>`, `<mrow>`, `<mi>`, `<mo>`, `<mn>`, `<msup>`, dll.) dan pembersihan tag berbahaya `<annotation-xml>`.
   - Pembersihan atribut payload berentropi tinggi tersembunyi pada `data-` dan stripping script tersembunyi dalam komentar HTML.
   - Penegakan token sandbox iframe dan eliminasi atribut presentasi usang `frameborder`.

2. **Parsing Markdown & Tipografi Akademik (`parser.py`)**:
   - Normalisasi penulisan gelar akademik Indonesia dan internasional (`normalize_academic_degrees`).
   - Ekstraktor kode mata kuliah kurikulum dan jenjang semester (`parse_course_curriculum_codes`).
   - Penata dan penyeimbang tanda petik cerdas tipografis (`balance_and_clean_quotes`).
   - Format miring otomatis (*auto-italicization*) untuk terminologi Latin ilmiah (`italicize_academic_latin_terms`).

3. **Optimasi Mesin Pencari & Yoast SEO (`seo_validator.py`)**:
   - Evaluasi keselarasan Open Graph dan canonical meta description (`evaluate_meta_and_og_alignment`).
   - Validator tautan DOI jurnal akademik dan indeks SINTA/Scopus/WoS (`validate_academic_journal_references`).
   - Audit kepatuhan aksesibilitas tabel HTML (`audit_table_accessibility`).
   - Evaluator kesegaran konten dan anomali referensi tahun publikasi (`evaluate_content_freshness_discrepancy`).

4. **Komponen Desain UI Akademik Elementor (`components.py`)**:
   - Kartu akreditasi resmi program studi LAM INFOKOM / BAN-PT Unggul (`render_accreditation_badge`).
   - Kartu spesifikasi fasilitas peralatan laboratorium komputasi (`render_lab_equipment_card`).
   - Kartu podium juara kompetisi mahasiswa dan hackathon (`render_award_podium_card`).
   - Showcase universitas mitra program pertukaran pelajar internasional (`render_exchange_program_showcase`).
   - Kartu statistik keterserapan kerja dan masa tunggu lulusan tracer study (`render_career_placement_card`).

5. **Format & Notifikasi Telegram Bot (`formatters.py`)**:
   - Kartu sitasi akademik BibTeX siap-salin untuk rujukan skripsi/jurnal (`format_bibtex_telegram_card`).
   - Kartu laporan hasil audit kesamaan/plagiarisme dengan indikator ambang batas (`format_plagiarism_alert_card`).

6. **Penyimpanan & Manajemen Siklus Hidup SQLite (`storage.py`)**:
   - Tabel `article_categories` dan pohon taksonomi kategori hierarkis (`add_category`, `get_category_tree`).
   - Tabel `article_locks` dan lease manager editing draf konkuren (`acquire_article_lock`, `release_article_lock`).
   - Helper pencarian dan penggantian massal transaksi batch (`batch_replace_content`).

7. **Konektivitas WordPress REST API (`wordpress_client.py`)**:
   - Helper penetapan taksonomi tag pos massal (`assign_post_tags`).
   - Helper pembaruan metadata media attachment alt-text/caption (`update_media_metadata`).

8. **Sindikasi & Ekspor Format Modern (`exporter.py`)**:
   - Generator Schema.org `EducationalOccupationalProgram` JSON-LD (`generate_program_json_ld`).
   - Generator format MDX kompatibel Next.js Contentlayer dan App Router (`to_nextjs_mdx`).

9. **Perintah Antarmuka Baris Perintah (`cli.py`)**:
   - Subcommand `lock`: Manajemen lease lock pengeditan draf artikel.
   - Subcommand `replace`: Pencarian dan penggantian teks artikel secara batch.
   - Subcommand `schema`: Ekspor skema kurikulum program studi JSON-LD.

10. **Perkakas Validasi Operasional (`scripts/`)**:
    - `scripts/check_images.py`: Audit kepatuhan alt text gambar, format modern WebP/AVIF, dan dimensi anti-CLS.
