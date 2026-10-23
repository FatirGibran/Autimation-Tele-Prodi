# Dokumentasi Perubahan Arsitektur v4.2.0 Milestone Release

Siklus pengembangan v4.2.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen canvas grafis dan pembatasan batas dimensi integer aman (`sanitize_html5_canvas_dimensions`), pengamanan elemen matematika MathML terhadap eksekusi script dan XML berbahaya (`sanitize_mathml_math_elements`), serta sanitasi isolasi arah teks bidi `<bdi>` dan `<bdo>` (`sanitize_html5_bdi_bdo_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator rugi propagasi ruang bebas (FSPL) dan margin link budget nirkabel (`calculate_fspl_and_link_budget`), kalkulator dispersi kromatik serat optik dan pelebaran pulsa temporal inter-symbol interference (`calculate_optical_chromatic_dispersion`), penganalisis ambang batas event A3 handover seluler LTE/5G dan mitigasi ping-pong (`calculate_cellular_handover_hysteresis`), serta evaluator rekognisi program MBKM Proyek Kemanusiaan dan kebencanaan hingga 20 SKS (`parse_proyek_kemanusiaan_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor ketersediaan takarir video dan transkrip audio alternatif (`audit_av_transcripts_and_captions`), auditor keabsahan tag kanonisasi URL kanonis HTTPS dan pembersihan tracking query (`audit_rel_canonical_urls`), auditor semantik navigasi breadcrumb dan Schema.org BreadcrumbList (`audit_breadcrumb_navigation_schema`), serta auditor pencegahan pergeseran tata letak kumulatif CLS melalui penegakan rasio aspek media visual (`audit_cls_media_aspect_ratios`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri propagasi FSPL dan link budget nirkabel (`render_fspl_link_budget_card`), kartu analisis dispersi kromatik serat optik (`render_chromatic_dispersion_card`), kartu kestabilan handover event A3 seluler (`render_cellular_handover_card`), kartu rekognisi relawan MBKM Proyek Kemanusiaan (`render_proyek_kemanusiaan_card`), serta kartu visualisasi diagram mata sinyal (eye diagram) optik responsif SVG (`render_optical_eye_diagram_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram audit link budget nirkabel FSPL (`format_fspl_link_budget_telegram`) dan format apresiasi penuntasan MBKM Proyek Kemanusiaan mahasiswa (`format_proyek_kemanusiaan_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit link budget radio (`fspl_link_budget_records`), tabel audit dispersi serat optik (`optical_dispersion_records`), serta tabel rekam mahasiswa MBKM kemanusiaan (`student_proyek_kemanusiaan`).
- **Klien WordPress REST API**: Helper perolehan daftar komentar artikel berdasarkan status moderasi (`get_post_comments`) dan helper publikasi komentar/balasan interaktif artikel (`create_post_comment`).
- **Generator Statis & Ekspor**: Generator Schema.org `Project` / `VolunteerService` JSON-LD aksi kemanusiaan (`generate_humanitarian_action_json_ld`) serta eksportir markdown Hugo Academic / Hugo Blox (`to_hugo_academic_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `fspl`, `dispersion`, dan `kemanusiaan`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 678 menjadi 706 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Dimensi Canvas HTML5 (`sanitizer.py`)**:
   - Memvalidasi elemen `<canvas>`, mensterilkan event handler inline (`onclick`, `oncontextmenu`), menghapus style inline, dan menegakkan nilai integer positif aman (1 sampai 4096 px) pada atribut width dan height.

2. **Sanitasi Elemen MathML Math (`sanitizer.py`)**:
   - Membersihkan blok MathML `<math>` dari elemen `<script>` terselubung, menetralkan elemen eksekusi XML berbahaya `<annotation-xml encoding="text/html">`, dan menyaring URI pseudo-protokol pada atribut `href` dan `xlink:href`.

3. **Sanitasi Isolasi Teks Bidi HTML5 (`sanitizer.py`)**:
   - Memvalidasi elemen `<bdi>` dan `<bdo>`, menegakkan nilai atribut `dir` hanya untuk token valid (`ltr`, `rtl`, `auto`), melucuti event handler, dan mendaftarkan tag ke daftar putih parser.

4. **Kalkulator FSPL & Link Budget Nirkabel (`parser.py`)**:
   - Menghitung Free Space Path Loss (FSPL) $32.44 + 20\log_{10}(d_{\text{km}}) + 20\log_{10}(f_{\text{MHz}})$, panjang gelombang $\lambda$, daya terima $P_{rx}$, dan fade margin kelayakan tautan nirkabel.

5. **Kalkulator Dispersi Kromatik Serat Optik (`parser.py`)**:
   - Mengalkulasi pelebaran pulsa temporal $\Delta t = |D| \times L \times \Delta\lambda$, periode bit $T_b$, rasio pelebaran pulsa, batas laju bit maksimal $B_{max}$, dan tingkat keparahan degradasi Inter-Symbol Interference (ISI).

6. **Penganalisis Handover Event A3 Seluler (`parser.py`)**:
   - Mengevaluasi syarat pemicu event A3 3GPP LTE/5G ($RSRP_{target} - RSRP_{serving} > A3_{offset} + Hysteresis$), margin diferensial, dan estimasi risiko ping-pong handover.

7. **Evaluator Rekognisi MBKM Proyek Kemanusiaan (`parser.py`)**:
   - Menghitung skor komposit aktivitas relawan kebencanaan (pembimbing, supervisor lapangan, laporan dampak), konversi nilai mutu, dan ekuivalensi hingga 20 SKS kurikulum prodi.

8. **Auditor Takarir & Transkrip Media AV (`seo_validator.py`)**:
   - Mengaudit keberadaan elemen `<track kind="captions">` atau `<track kind="subtitles">` pada video dan kontainer transkrip teks alternatif (`.tu-media-transcript`) sesuai panduan WCAG 2.1 AA.

9. **Auditor Tag Kanonisasi Rel Canonical (`seo_validator.py`)**:
   - Memvalidasi keberadaan tag `<link rel="canonical">` tunggal, penegakan protokol HTTPS absolut, kesesuaian domain resmi institusi, dan eliminasi query pelacak.

10. **Auditor Navigasi Breadcrumb & Skema Microdata (`seo_validator.py`)**:
    - Memverifikasi kontainer navigasi `<nav aria-label="breadcrumb">`, indikator aksesibel `aria-current="page"` pada item aktif terakhir, dan penanda Schema.org `BreadcrumbList`.

11. **Auditor Rasio Aspek Media CLS Core Web Vitals (`seo_validator.py`)**:
    - Memeriksa elemen media visual (`<img>`, `<video>`, `<canvas>`, `<iframe>`) untuk memastikan tersedianya dimensi eksplisit atribut `width`/`height` atau aturan CSS `aspect-ratio`.

12. **Komponen Link Budget FSPL Nirkabel (`components.py`)**:
    - Kartu Elementor parameter frekuensi gelombang, jarak jangkauan, path loss, daya terima, dan badge status margin kelayakan link.

13. **Komponen Dispersi Kromatik Serat Optik (`components.py`)**:
    - Kartu ringkasan panjang bentangan optik, parameter $D$, pelebaran pulsa picosecond, dan kapasitas throughput batas modulasi data.

14. **Komponen Handover Seluler A3 (`components.py`)**:
    - Kartu visualisasi perbandingan daya terima sinyal seluler serving vs target, delta RSRP, margin histeresis, dan keputusan stabilitas handover.

15. **Komponen Relawan MBKM Proyek Kemanusiaan (`components.py`)**:
    - Kartu pencapaian pengabdian kebencanaan mahasiswa, mitra BPBD/organisasi kemanusiaan, skor komposit, dan konversi 20 SKS kurikulum.

16. **Komponen Diagram Mata Sinyal Optik SVG (`components.py`)**:
    - Kartu visualisasi diagram mata sinyal transmisi optik berkecepatan tinggi dengan metrik eye height, eye width, jitter RMS, dan Q-factor berbasis inline SVG responsif.

17. **Formatter Telegram Audit Link Budget FSPL (`formatters.py`)**:
    - Format siaran Telegram resmi untuk hasil verifikasi audit link budget gelombang mikro dan propagasi nirkabel.

18. **Formatter Telegram Apresiasi Proyek Kemanusiaan (`formatters.py`)**:
    - Format siaran Telegram resmi apresiasi penuntasan pengabdian relawan kemanusiaan MBKM mahasiswa.

19. **Manajer Rekam Audit Link Budget FSPL (`storage.py`)**:
    - Tabel SQLite `fspl_link_budget_records` dan metode `record_fspl_link_budget`, `list_fspl_link_budgets`, `get_fspl_link_budget_by_id`.

20. **Manajer Rekam Dispersi Serat Optik (`storage.py`)**:
    - Tabel SQLite `optical_dispersion_records` dan metode `record_optical_dispersion`, `list_optical_dispersions`, `get_optical_dispersion_by_id`.

21. **Manajer Rekam Mahasiswa MBKM Kemanusiaan (`storage.py`)**:
    - Tabel SQLite `student_proyek_kemanusiaan` dan metode `record_proyek_kemanusiaan`, `list_proyek_kemanusiaan`, `get_proyek_kemanusiaan_by_nim`.

22. **Helper WordPress Get Post Comments (`wordpress_client.py`)**:
    - Metode REST API `get_post_comments` untuk mengambil daftar komentar artikel berdasarkan filter status moderasi (`approve`, `hold`).

23. **Helper WordPress Create Post Comment (`wordpress_client.py`)**:
    - Metode REST API `create_post_comment` untuk mengirimkan komentar baru atau balasan terstruktur pada postingan WordPress.

24. **Generator Schema.org Humanitarian Action JSON-LD (`exporter.py`)**:
    - Metode `generate_humanitarian_action_json_ld` menghasilkan struktur metadata standar `Project` / `VolunteerService` untuk kegiatan mitigasi bencana.

25. **Eksportir Markdown Hugo Academic Documentation (`exporter.py`)**:
    - Metode `to_hugo_academic_markdown` mengonversi artikel blog menjadi format markdown Hugo Academic / Hugo Blox dengan frontmatter YAML terstandarisasi.

26. **Subcommand CLI `fspl` (`cli.py`)**:
    - Perintah konsol `fspl` untuk menyimpan dan menampilkan riwayat audit link budget gelombang mikro nirkabel.

27. **Subcommand CLI `dispersion` (`cli.py`)**:
    - Perintah konsol `dispersion` untuk menyimpan dan menampilkan riwayat analisis dispersi kromatik serat optik.

28. **Subcommand CLI `kemanusiaan` (`cli.py`)**:
    - Perintah konsol `kemanusiaan` untuk mencatat dan menampilkan riwayat evaluasi pengakuan kredit MBKM Proyek Kemanusiaan.

29. **Ekspansi Suite Pengujian Unit Terpadu (706 Tests Passing)**:
    - Penambahan 28 unit test komprehensif pada modul sanitizer, parser, seo_validator, components, formatters, storage, wordpress_client, exporter, dan cli.
