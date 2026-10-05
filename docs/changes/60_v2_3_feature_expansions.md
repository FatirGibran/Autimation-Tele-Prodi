# Perubahan #60: Rilis Fitur & Arsitektur v2.3.0

## Metadata Perubahan
- **ID**: #60
- **Modul**: `sanitizer.py`, `parser.py`, `seo_validator.py`, `components.py`, `formatters.py`, `storage.py`, `wordpress_client.py`, `exporter.py`, `cli.py`, `scripts/check_broken_links.py`
- **Test Suite**: `tests/` (179 Tests Passing, 100% Success Rate)

## Deskripsi Teknis
Ekspansi arsitektur editorial otomatis Telkom University Purwokerto versi 2.3.0 mencakup 37 pembaruan terstruktur:

1. **Penyaringan Keamanan & Sanitasi Media (`sanitizer.py`)**:
   - Sanitasi tabel bersarang (*nested table flattening & stripping*) untuk menjaga konsistensi render HTML Elementor.
   - Penegakan protokol sumber media aman pada tag audio dan video (`safe media source protocols`).
   - Pembersihan piksel pelacak tersembunyi berukuran 0x0 atau 1x1 serta elemen inline tersembunyi (`tracking pixel removal`).

2. **Parsing Markdown & Linguistik Akademik (`parser.py`)**:
   - Parser sitasi braket akademik dan ekstraksi kunci BibTeX (`parse_academic_citations`, `extract_bibtex_keys`).
   - Ekspander otomatis akronim dan singkatan resmi Bahasa Indonesia (`expand_indonesian_acronyms`).
   - Detektor sintaks bahasa pemrograman dan normalizer blok kode `<pre><code>` (`detect_code_language`, `normalize_code_blocks`).
   - Ekstraktor kalimat transisi antar-paragraf berbahasa Indonesia (`extract_paragraph_transitions`).

3. **Optimasi Mesin Pencari & Yoast SEO (`seo_validator.py`)**:
   - Validator rasio aspek dan dimensi intrinsik gambar konten (`validate_image_dimensions`).
   - Evaluator keseragaman distribusi kata kunci fokus sepanjang artikel (`evaluate_keyphrase_distribution`).
   - Auditor kedalaman dan otoritas tautan internal akademik (`audit_internal_academic_links`).
   - Validator keamanan dan atribut `rel` pada tautan eksternal (`validate_outbound_link_rel`).

4. **Komponen Desain UI Akademik Elementor (`components.py`)**:
   - Kartu profil dosen dan staf pengajar berstandar NIDN/Scopus (`render_faculty_profile_card`).
   - Kartu pameran tugas akhir / capstone mahasiswa unggulan (`render_student_capstone_showcase`).
   - Grid lencana sertifikasi internasional industri teknologi (`render_certification_badge_grid`).
   - Kartu tonggak linimasa kalender semester akademik (`render_semester_milestone_card`).
   - Spanduk kemitraan industri dan sponsor magang mahasiswa (`render_partnership_banner`).

5. **Format & Notifikasi Telegram Bot (`formatters.py`)**:
   - Pratinjau ringkas perbedaan editorial (*editorial diff*) teroptimasi untuk layar seluler (`format_compact_editorial_diff`).
   - Kartu pengingat publikasi terjadwal Telegram (`format_scheduled_publication_reminder`).

6. **Penyimpanan & Manajemen Siklus Hidup SQLite (`storage.py`)**:
   - Pengelola antrean publikasi terjadwal artikel (`schedule_publication`, `get_pending_schedules`, `cancel_schedule`).
   - Helper ekspor dan impor cadangan penuh database berformat JSON (`export_database_dump`, `import_database_dump`).
   - Pelacak statistik pembaca dan tingkat keterlibatan artikel (`record_article_view`, `get_article_engagement_stats`).

7. **Konektivitas WordPress REST API (`wordpress_client.py`)**:
   - Pengambil riwayat revisi pos remote dari WordPress REST API (`get_post_revisions`).
   - Helper penjadwalan penerbitan pos remote WordPress (`schedule_post`).

8. **Sindikasi & Ekspor Format Modern (`exporter.py`)**:
   - Generator format MDX kompatibel Astro dan Docusaurus dengan frontmatter dinamis (`to_mdx`).
   - Generator metadata Open Graph dan Twitter Card lanjutan dengan dimensi eksplisit dan locale Indonesia (`generate_enhanced_social_meta`).

9. **Perintah Antarmuka Baris Perintah (`cli.py`)**:
   - Subcommand `schedule`: Manajemen antrean publikasi terjadwal artikel.
   - Subcommand `dump`: Ekspor cadangan penuh database ke berkas JSON.
   - Subcommand `mdx`: Ekspor konten artikel ke format MDX modern.

10. **Perkakas Validasi Operasional (`scripts/`)**:
    - `scripts/check_broken_links.py`: Pemindaian otomatis jangkar halaman (*broken anchor tags*), tautan malformed, dan integritas referensi gambar.
