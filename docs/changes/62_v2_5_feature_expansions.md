# Dokumentasi Perubahan Arsitektur v2.5.0

Siklus pengembangan v2.5.0 berfokus pada pengerasan keamanan semantik elemen media dan data, integrasi penanganan istilah akademik serta tanggal formal Indonesia, perluasan evaluasi SEO dan aksesibilitas WCAG, komponen Elementor publikasi jurnal dan kelompok belajar, serta penambahan perintah CLI dan pengujian unit komprehensif.

## Rincian Fitur Utama yang Ditambahkan:
1. **Sanitasi Semantic Figure & Figcaption (`sanitizer.py`)**:
   - Penegakan kelas `.tu-figure` dan `.tu-figcaption`.
   - Pembersihan otomatis atribut berbahaya di dalam elemen sematan gambar ber-caption.
2. **Pembersihan Injeksi Atribut Kustom Data (`sanitizer.py`)**:
   - Eliminasi atribut `data-*` yang memuat muatan skrip, `javascript:`, atau evaluasi berbahaya.
3. **Penegakan Kontrol Aksesibilitas & Preload Media (`sanitizer.py`)**:
   - Penambahan atribut `controls` dan `preload="metadata"` pada tag `<video>` dan `<audio>`.
   - Penghapusan unmuted `autoplay` untuk kepatuhan WCAG.
4. **Glosarium Istilah Akademik & Tooltip Otomatis (`parser.py`)**:
   - Fungsi `wrap_glossary_terms` untuk membungkus istilah akademik di luar tag kode dengan `<dfn title="...">`.
5. **Parser Tanggal & Waktu Formal Indonesia (`parser.py`)**:
   - Fungsi `parse_indonesian_formal_date` untuk mem-parsing penanggalan formal Indonesia ke format objek terstruktur dan ISO date.
6. **Ekstraktor Kluster Riset Informatika (`parser.py`)**:
   - Fungsi `extract_research_cluster_tags` mengenali 4 kluster riset prodi Telkom Purwokerto (AI, Cyber, SE/Cloud, IoT).
7. **Normalisasi Indentasi Daftar Bertingkat Markdown (`parser.py`)**:
   - Fungsi `normalize_nested_list_indentation` memastikan nesting daftar Markdown teratur dengan kenaikan 2 spasi standar.
8. **Validator Hierarki Breadcrumb (`seo_validator.py`)**:
   - Metode `validate_breadcrumb_hierarchy` mengaudit kedalaman dan tautan beranda pada struktur breadcrumbs.
9. **Auditor Rasio Kontras CSS Inline (`seo_validator.py`)**:
   - Metode `audit_css_color_contrast` mendeteksi kombinasi warna teks dan latar belakang yang tidak terbaca.
10. **Validator Gambar Open Graph (`seo_validator.py`)**:
    - Metode `validate_og_image_specifications` memverifikasi protokol HTTPS, ekstensi raster/vektor, dimensi, dan rasio aspek 1.91:1.
11. **Indeks Keterbacaan Coleman-Liau Indonesia (`seo_validator.py`)**:
    - Metode `calculate_indonesian_coleman_liau` mengkalkulasi tingkat pemahaman teks berdasarkan rerata huruf dan kalimat.
12. **Komponen Visual Elementor Baru (`components.py`)**:
    - `render_journal_publication_card`: kartu publikasi jurnal dengan kuartil Q1-Q4 dan tautan DOI.
    - `render_student_club_card`: kartu showcase study group & club mahasiswa.
    - `render_research_grant_banner`: banner hibah riset dan pendanaan.
    - `render_specialization_track_card`: kartu peminatan kurikulum dan prospek karir.
    - `render_data_center_facility_card`: kartu spesifikasi server & data center.
13. **Formatter Notifikasi Telegram Baru (`formatters.py`)**:
    - `format_conference_call_card`: kartu peringatan CFP konferensi ilmiah.
    - `format_compact_seo_summary`: ringkasan metrik audit SEO untuk bot editorial.
14. **Ekspansi Storage Engine (`storage.py`)**:
    - `get_category_analytics`: agregasi statistik pembaca per kategori.
    - `add_bookmark`, `list_bookmarks`, `remove_bookmark`: manajemen bookmark artikel dan reading list pengguna.
    - `record_migration`, `get_applied_migrations`: pelacak versi skema migrasi database SQLite.
15. **Ekspansi Klien WordPress (`wordpress_client.py`)**:
    - `set_post_visibility`: pengelolaan status sticky dan kata sandi pos.
    - `delete_media`: penghapusan lampiran media secara permanen via REST API.
16. **Generator Skema & Nuxt Markdown (`exporter.py`)**:
    - `generate_research_project_json_ld`: Schema.org/ResearchProject dan Grant rich snippet.
    - `to_nuxt_markdown`: ekspor frontmatter YAML kompatibel Nuxt Content v2 / Gatsby.
17. **Subcommand Baru CLI (`cli.py`)**:
    - `bookmark`: kelola bookmark dan reading list.
    - `cat-stats`: statistik performa artikel per kategori.
    - `nuxt`: ekspor artikel ke Nuxt Content v2.
18. **Skrip Audit Aksesibilitas WCAG (`scripts/check_accessibility.py`)**:
    - Audit otomatis hirarki heading, alt text, tag table semantik, dan media controls.
19. **Unit Testing Terpadu**:
    - 235 unit tests lulus 100% tanpa regresi.
