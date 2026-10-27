# Dokumentasi Perubahan Arsitektur v4.5.0 Milestone Release

Siklus pengembangan v4.5.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen nilai data terstruktur `<data>` dengan validasi token semantik dan pembersihan payload (`sanitize_html5_data_value_attributes`), pengamanan elemen Web Component `<slot>` dengan validasi token identifikasi aman (`sanitize_html5_slot_name_attributes`), serta sanitasi tipografi fonetik `<ruby>`, `<rt>`, `<rp>`, `<rb>`, `<rtc>` (`sanitize_html5_ruby_annotation_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator Cross-Phase Modulation (XPM) serat optik DWDM menurut kaidah optika nonlinier Agrawal (`calculate_optical_cross_phase_modulation`), kalkulator numerologi dan slot timing fisik 5G NR menurut spesifikasi 3GPP TS 38.211 (`calculate_5g_nr_numerology_timing`), kalkulator redaman dan variansi amplitudo sintilasi troposfer satelit bumi-angkasa menurut rekomendasi ITU-R P.618 (`calculate_satellite_scintillation_itu_r`), serta evaluator rekognisi kurikulum program Pertukaran Mahasiswa Merdeka (PMM) Kemendikbudristek hingga 20 SKS MBKM (`parse_pmm_mbkm_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor penanda data terstruktur Schema.org Course (`audit_course_schema_markup`), auditor autodiscovery link feed RSS 2.0 dan Atom (`audit_rss_atom_autodiscovery_links`), auditor kebijakan keamanan konten Content-Security-Policy (CSP) meta directives (`audit_csp_meta_directive`), serta auditor optimasi resource hints preconnect dan dns-prefetch (`audit_resource_hints_prefetch_preconnect`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri pergeseran fase nonlinier XPM serat optik (`render_optical_xpm_card`), kartu analisis numerologi dan alokasi slot timing 5G NR (`render_5g_nr_numerology_card`), kartu sintilasi troposfer satelit ITU-R P.618 (`render_satellite_scintillation_card`), kartu pencapaian dan rekognisi SKS mahasiswa PMM MBKM (`render_pmm_mbkm_card`), serta kartu visualisasi diagram struktur 10 subframe (10 ms) radio frame 5G NR berbasis inline SVG responsif (`render_5g_nr_frame_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan telemetri sintilasi troposfer satelit ITU-R P.618 (`format_satellite_scintillation_telegram`) dan format apresiasi penuntasan program Pertukaran Mahasiswa Merdeka mahasiswa (`format_pmm_mbkm_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit XPM serat optik (`optical_xpm_records`), tabel audit konfigurasi numerologi 5G NR (`nr_numerology_records`), serta tabel rekam mahasiswa PMM MBKM (`student_pmm_records`).
- **Klien WordPress REST API**: Helper perolehan objek halaman statis WordPress berdasarkan slug URL (`get_page_by_slug`) dan helper perolehan objek halaman berdasarkan ID numerik (`get_page_by_id`).
- **Generator Statis & Ekspor**: Generator Schema.org `LearningResource` JSON-LD standar modul laboratorium dan panduan praktikum (`generate_learning_resource_json_ld`) serta eksportir dokumentasi modern Next.js App Router MDX Fumadocs (`to_fumadocs_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `xpm`, `numerology`, dan `pmm`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 763 menjadi 791 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Data Machine-Readable (`sanitizer.py`)**:
   - Memvalidasi elemen `<data value="...">`, membersihkan nilai atribut dari skema pseudo-protokol JavaScript, data URIs, serta karakter berbahaya, dan menghapus event handler inline.

2. **Sanitasi Elemen Slot Web Component (`sanitizer.py`)**:
   - Mengamankan elemen `<slot name="...">`, menegakkan token identifikasi aman (`^[a-zA-Z0-9_\-]+$`), dan membuang style inline serta event listeners.

3. **Sanitasi Tipografi Anotasi Fonetik Ruby (`sanitizer.py`)**:
   - Mensterilkan hierarki elemen `<ruby>`, `<rt>`, `<rp>`, `<rb>`, `<rtc>`, membuang skrip dan iframe bersarang, serta membersihkan event handler inline.

4. **Kalkulator Cross-Phase Modulation (XPM) Serat Optik DWDM (`parser.py`)**:
   - Menghitung koefisien nonlinier $\gamma$, panjang efektif serat $L_{\text{eff}}$, pergeseran fase Self-Phase Modulation $\Phi_{\text{SPM}}$ dan Cross-Phase Modulation $\Phi_{\text{XPM}} = 2\gamma P_{\text{pump}} L_{\text{eff}}$ dalam radian dan derajat, serta evaluasi risiko transmisi.

5. **Kalkulator Numerologi & Timing 5G NR 3GPP TS 38.211 (`parser.py`)**:
   - Mengalkulasi subcarrier spacing $\Delta f = 15 \times 2^\mu\text{ kHz}$ ($\mu = 0, 1, 2, 3, 4$), durasi slot $T_{\text{slot}} = 1/2^\mu\text{ ms}$, jumlah slot per radio frame, durasi simbol OFDM dan cyclic prefix, serta bandwidth terokupasi Resource Block.

6. **Kalkulator Sintilasi Troposfer Satelit ITU-R P.618 (`parser.py`)**:
   - Mengalkulasi tekanan uap air jenuh, radio refractivity wet term $N_{\text{wet}}$, simpangan baku acuan $\sigma_{\text{ref}}$, panjang lintasan turbulen efektif, faktor aperture averaging $g(x)$, dan fade depth $A(p)$ untuk persentil waktu outage tertentu.

7. **Evaluator Rekognisi MBKM Pertukaran Mahasiswa Merdeka (`parser.py`)**:
   - Mengevaluasi skor komposit Modul Nusantara (30%), mata kuliah akademik host (50%), dan mentor host (20%), konversi nilai mutu, serta pemetaan hingga 20 SKS mata kuliah prodi.

8. **Auditor Skema Course Schema.org (`seo_validator.py`)**:
   - Memvalidasi struktur data terstruktur Schema.org Course (JSON-LD atau Microdata), kelengkapan nama modul mata kuliah, deskripsi silabus, dan institusi penyelenggara.

9. **Auditor Autodiscovery Feed RSS 2.0 & Atom (`seo_validator.py`)**:
   - Memeriksa konsistensi tag `<link rel="alternate" type="application/rss+xml">` dan `<link rel="alternate" type="application/atom+xml">`, validitas URL href, dan ketersediaan judul feed.

10. **Auditor Direktif Content-Security-Policy (CSP) Meta (`seo_validator.py`)**:
    - Memverifikasi keberadaan tag `<meta http-equiv="Content-Security-Policy">`, kepatuhan terhadap default-src/script-src, pencegahan unsafe-inline tanpa nonce, dan pengamanan object-src.

11. **Auditor Resource Hints Preconnect & DNS-Prefetch (`seo_validator.py`)**:
    - Memvalidasi link resource hints `<link rel="preconnect">` dan `<link rel="dns-prefetch">`, memeriksa validitas URL eksternal, dan penegakan atribut crossorigin pada Google Fonts.

12. **Komponen Visualisasi Radio Frame 5G NR Inline SVG (`components.py`)**:
    - Kartu visualisasi diagram alokasi 10 subframe (10 ms) radio frame 5G NR berbasis inline SVG responsif.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Tabel baru `optical_xpm_records`, `nr_numerology_records`, dan `student_pmm_records` dilengkapi metode CRUD dan indeks terindeksasi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper query `get_page_by_slug` dan `get_page_by_id` untuk pengambilan metadata halaman statis WordPress secara presisi.

15. **Generator LearningResource JSON-LD & Eksportir Fumadocs MDX (`exporter.py`)**:
    - Generator Schema.org `LearningResource` JSON-LD standar modul laboratorium dan eksportir format dokumentasi Next.js App Router Fumadocs MDX.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `xpm`, `numerology`, dan `pmm` untuk operasionalisasi langsung dari terminal.
