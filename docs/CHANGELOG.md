# Catatan Perkembangan Proyek (Changelog) - Automation Tele Prodi

Dokumen ini mencatat seluruh perkembangan dan pembaruan arsitektural yang telah diimplementasikan pada proyek **Automation Tele Prodi (Editorial Specialist Bot S1 Teknik Informatika Telkom University Purwokerto)**.

---

## Ringkasan Metrik Pembaruan
- **Total Item Perubahan**: 35+ pembaruan terverifikasi
- **Cakupan Modul**: Sanitasi Keamanan, Parser Konten, Yoast SEO Evaluator, Komponen Semantik Elementor, Storage & SQLite, Exporter & Schema, CLI Tools, Webhook Server, Klien WordPress, serta Skrip Operasional
- **Status Pengujian**: 90 unit tests terverifikasi (100% pass rate)

---

## 1. Sanitasi & Pengerasan Keamanan (`sanitizer.py`)

1. **Sanitasi Inline SVG (Pencegahan XSS)**: Penghapusan tag rentan `<foreignObject>` dan `<script>` di dalam blok `<svg>`.
2. **Netralisasi Pseudo-Protokol JavaScript pada SVG**: Transformasi atribut `xlink:href="javascript:..."` menjadi `xlink:href="#"`.
3. **Pembersihan Atribut Inline CSS**: Filtrasi ketat properti `style` terhadap ekspresi berbahaya (`expression()`, `@import`, `-moz-binding`, `javascript:`, payload base64 `data:text/html`).
4. **Penegakan Keamanan Hyperlink Eksternal**: Penambahan otomatis `target="_blank"` dan `rel="noopener noreferrer"` pada seluruh tautan di luar domain kampus.
5. **Optimasi Performa Gambar Web**: Penegakan otomatis atribut `loading="lazy"` dan `decoding="async"` pada semua elemen `<img>`.
6. **Auto-Wrapping Kontainer Semantik**: Deteksi dan pembungkusan otomatis dengan `<div class="tu-editorial-container">` apabila luput dari payload generator.
7. **Pembersihan Event Handler Inline**: Pembersihan regex komprehensif terhadap atribut aksi seperti `onclick`, `onload`, `onerror`.
8. **Penghapusan Tag Sematan Tidak Aman**: Stripping otomatis elemen `<script>`, `<iframe>`, `<object>`, dan `<embed>`.

---

## 2. Parser Konten & Normalisasi Input (`parser.py`)

9. **Pembersihan Parameter URL Tracking / UTM**: Implementasi `clean_url` untuk memangkas parameter pelacak analitik (`utm_*`, `fbclid`, `gclid`, `mc_eid`, `ref`, `igshid`) guna menjaga kebersihan tautan dan integritas kanonisasi.
10. **Kalkulator Durasi Baca Adaptif**: Fungsi `calculate_reading_time` berbasis densitas kata riil dengan laju 200 WPM khusus artikel teknis/akademis berbahasa Indonesia.
11. **Parser Callout / Admonition Format GitHub**: Transformasi otomatis sintaks `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, dan `> [!CAUTION]` menjadi kartu visual Elementor bergaya modern.
12. **Konversi Tabel Markdown ke HTML Responsif**: Fungsi `convert_markdown_table_to_html` untuk mengonversi tabel Markdown standar ke pembungkus `.tu-table-responsive` dan tabel semantik.
13. **Ekstraksi Hirarki Heading Semantik**: Fungsi `extract_headings` untuk mengekstrak dan memvalidasi hirarki `<h1>` sampai `<h6>`.
14. **Pembersihan Simbol Markdown Murni**: Fungsi `strip_markdown_formatting` untuk ekstraksi teks murni dalam evaluasi densitas kata kunci.

---

## 3. Peningkatan Yoast SEO & Keterbacaan (`seo_validator.py`)

15. **Estimator Suku Kata Bahasa Indonesia**: Metode `count_syllables_indonesian` berbasis analisis kluster vokal teks Indonesia.
16. **Indeks Skor Kemudahan Membaca (Reading Ease)**: Adaptasi formula Flesch-Kincaid untuk bahasa Indonesia berdasarkan rerata panjang kalimat dan suku kata per kata.
17. **Deteksi Rasio Kalimat Pasif**: Algoritma identifikasi awalan `di-` dengan pengecualian kata dasar non-pasif (`dimensi`, `digital`, `diploma`, dsb.) untuk memastikan batas kalimat pasif maksimal 25%.
18. **Evaluasi Kata Transisi Akademik**: Pemeriksaan persentase kata penghubung formal Indonesia (`selain itu`, `oleh karena itu`, `namun`, dsb.) dengan target minimal 20%.
19. **Deteksi Pengulangan Awal Kalimat Berurutan**: Pengecekan pencegahan 3 atau lebih kalimat berturut-turut yang diawali kata pembuka yang sama.
20. **Audit Kualitas Anchor Text**: Deteksi tautan dengan teks generik yang merugikan peringkat SEO (misal: "klik di sini", "link", "baca selengkapnya").
21. **Deteksi Kanibalisasi Kata Kunci Fokus**: Analisis kesamaan semantik menggunakan metrik Jaccard similarity (ambang batas 0.8) terhadap korpus artikel yang sudah terbit di database.
22. **Verifikasi Focus Keyphrase pada Heading H2**: Pemeriksaan wajib keberadaan kata kunci fokus pada sekurang-kurangnya satu subjudul H2.
23. **Verifikasi Focus Keyphrase pada Image Alt**: Validasi ketat atribut teks alternatif gambar untuk optimasi Google Images.
24. **Verifikasi Kata Kunci pada Paragraf Pembuka**: Penegakan keberadaan focus keyphrase di dalam paragraf pertama (`.tu-lead-paragraph`).

---

## 4. Komponen Visual Elementor Baru (`components.py`)

25. **Komponen Timeline / Roadmap Akademik**: Generator `render_timeline_component` untuk alur kurikulum atau milestone riset secara vertikal dan responsif.
26. **Komponen Kartu Kutipan & Prestasi Alumni**: Generator `render_alumni_quote_card` dengan avatar terisolasi, styling kutipan, peran, instansi, dan tahun angkatan.
27. **Komponen Matriks Komparasi Kurikulum / Fitur**: Generator `render_feature_matrix` dengan ikon checklist (`✓` / `✗`) dan layout responsif tabel horizontal.
28. **Komponen Accordion FAQ Interaktif**: Generator `render_faq_accordion` menggunakan tag native `<details>` dan `<summary>` tanpa dependensi skrip pihak ketiga.
29. **Komponen Grid Counter Metrik Riset**: Generator `render_stat_grid` untuk menampilkan angka capaian, akreditasi, dan metrik publikasi prodi.
30. **Komponen Blok Sitasi & Referensi Ilmiah**: Generator `render_references_block` untuk daftar pustaka berstandar akademik.
31. **Komponen Cuplikan Kode dengan Badge Bahasa**: Generator `render_code_block` dengan escaping karakter aman dan badge penanda sintaks.

---

## 5. Optimalisasi Database & Penyimpanan SQLite (`storage.py`)

32. **Snapshot Riwayat Versi Revisi Artikel**: Tabel `article_revisions` dan fungsi `create_revision` serta `get_revisions` untuk pencatatan draf sebelum penimpaan konten.
33. **Audit Trail Siklus Status Artikel**: Tabel `article_audit_logs` dan fungsi `update_status` untuk mencatat riwayat perubahan status editorial (`draft`, `review`, `ready`, `published`).
34. **Pencarian Multi-Kolom Full-Text**: Fungsi `search_articles` yang menelusuri topik, kata kunci fokus, meta deskripsi, dan isi HTML lengkap dengan cuplikan konteks kecocokan (`matched_snippet`).
35. **Pencegahan Duplikasi Keyphrase & Slug**: Fungsi `is_keyphrase_used` dan `is_slug_used` yang didukung indeks B-tree SQLite.
36. **Pembaruan Massal Status Artikel (`bulk_update_status`)**: Operasi pembaruan status batch secara efisien dalam satu transaksi database.
37. **Pemfilteran Berdasarkan Rentang Tanggal (`filter_by_date_range`)**: Query penyeleksian artikel berdasarkan periode penerbitan.
38. **Integritas & Pemadatan Database**: Fungsi `optimize_and_check_integrity` untuk mengeksekusi `PRAGMA integrity_check` dan perintah `VACUUM`.
39. **Sistem Taksonomi Tag Relasional**: Tabel relasional `article_tags` untuk pelabelan kategori topik sekunder artikel.

---

## 6. Generator Ekspor & Metadata Terstruktur (`exporter.py`)

40. **Skema BreadcrumbList JSON-LD**: Fungsi `generate_breadcrumb_schema` untuk rich snippet hierarki navigasi pada hasil penelusuran Google.
41. **Generator Metadata Media Sosial (OpenGraph & Twitter Card)**: Fungsi `generate_social_meta_tags` untuk menghasilkan paket kartu pratinjau media sosial dengan sanitasi escaping.
42. **Generator XML Sitemap Mesin Pencari**: Fungsi `generate_sitemap_xml` yang memproduksi sitemap terstandarisasi untuk perayap web mesin pencari.
43. **Generator RSS Feed 2.0**: Fungsi `generate_rss_feed` untuk sindikasi konten otomatis.
44. **Generator Skema NewsArticle & ScholarlyArticle**: Fungsi `generate_json_ld` dengan atribusi resmi prodi.
45. **Ekspor Bundel Multi-Format**: Fungsi `export_bundle` untuk memproduksi secara serentak berkas HTML, Standalone HTML5, Markdown dengan YAML frontmatter, dan JSON Elementor.

---

## 7. Ekstensi CLI, Webhook, & WordPress Client (`cli.py`, `webhook_server.py`, `wordpress_client.py`)

46. **CLI Subcommand `optimize`**: Perintah konsol untuk merawat basis data dan verifikasi integritas tabel.
47. **CLI Subcommand `sitemap`**: Perintah konsol untuk menghasilkan berkas sitemap XML secara instan.
48. **CLI Subcommand `validate`**: Perintah konsol untuk mengaudit berkas HTML dan metadata secara terisolasi tanpa koneksi jaringan.
49. **CLI Subcommand `search` & `stats`**: Perintah konsol untuk pencarian instan dan melihat agregasi statistik publikasi.
50. **Verifikasi Webhook HMAC SHA-256**: Fungsi `verify_hmac_sha256` menggunakan pembandingan konstan (`hmac.compare_digest`) guna menangkal celah timing attack.
51. **Endpoint Pemantauan Layanan (`/health`)**: Endpoint GET untuk pengecekan status server bot.
52. **Resolusi Taksonomi Otomatis WordPress REST API**: Fungsi `get_or_create_category` dan `get_or_create_tag` yang memetakan nama kategori/tag secara otomatis ke ID WordPress tanpa duplikasi.
53. **Mekanisme Retry Exponential Backoff**: Penanganan toleransi kegagalan jaringan saat mengirimkan draf ke WordPress REST API.

---

## 8. Skrip Pemeliharaan & Pipeline Pengujian (`scripts/`, `tests/`)

54. **Skrip Diagnostik Mandiri (`scripts/env_doctor.py`)**: Validasi otomatis konfigurasi lingkungan, keberadaan direktori, dan kesiapan database.
55. **Skrip Pencadangan Terjadwal (`scripts/backup_db.py`)**: Pencadangan SQLite otomatis dengan format timestamping ISO dan rotasi berkas.
56. **Skrip Batch Audit SEO (`scripts/bulk_audit.py`)**: Audit massal seluruh draf artikel untuk memastikan standar All-Green Yoast SEO terpenuhi sebelum rilis.
57. **Suite Pengujian Terotomasi (90 Tests Passing)**: Penambahan cakupan pengujian unit komprehensif pada folder `tests/` dengan 100% tingkat keberhasilan.

---

## 9. Pembaruan Fitur & Arsitektur v2.1.0 (#58 - #78)

58. **Normalisasi Struktur Tabel HTML & Sanitasi Presentasi**: Pembersihan atribut usang tabel dan penambahan kelas semantik `tu-table`.
59. **Filter & Whitelist Iframe Edukasi**: Perlindungan embed media pembelajaran dengan atribut `sandbox` ketat dan pembatasan domain terpercaya.
60. **Penegakan Keamanan Tautan Eksternal `rel="noopener noreferrer"`**: Normalisasi otomatis seluruh link keluar dengan target `_blank`.
61. **Ekstraktor Excerpt Otomatis**: Fungsi `generate_excerpt` untuk ringkasan artikel berbasis batas kata bersih.
62. **Normalisasi Tipografi Bahasa Indonesia**: Standarisasi tanda petik kurung, em-dash, non-breaking space, dan zero-width character pada `normalize_indonesian_typography`.
63. **Parser Catatan Kaki Akademik (Footnotes)**: Konversi sintaks footnote markdown `[^1]` menjadi markup semantik dengan backlink dua arah.
64. **Ekstraktor Frekuensi Kata Kunci & N-gram**: Fungsi `extract_keyword_frequency` dengan penyaringan stop words bahasa Indonesia dan Inggris.
65. **Validator Kerapatan Kata Kunci (Keyword Density)**: Evaluasi batasan rasio kerapatan kata kunci Yoast SEO (0.5% - 3.0%).
66. **Validator Batasan Panjang Paragraf**: Pemeriksaan keterbacaan terhadap paragraf yang melebihi batas maksimal 150 kata.
67. **Auditor Distribusi Subheading**: Pemastian pembagian struktur teks panjang di bawah H2/H3 tidak melebihi 300 kata per bagian.
68. **Auditor Profil Distribusi Tautan**: Pemeriksaan rasio keseimbangan link internal kampus dan referensi otoritatif eksternal.
69. **Komponen Editorial Interaktif Baru**: Penambahan Daftar Isi artikel (`render_table_of_contents`), Tim Penulis & Dosen (`render_author_team`), Kartu Unduhan Berkas/Silabus (`render_download_card`), Wadah Video Responsif 16:9 (`render_video_embed`), Spanduk Pendaftaran PMB (`render_admission_cta`), dan Badge Metrik KPI (`render_metric_callout`).
70. **Siklus Hidup Kotak Sampah & Pemulihan (Soft Delete)**: Dukungan pemindahan ke kotak sampah dan pemulihan artikel di SQLite.
71. **Penyimpanan Kustom Metadata Key-Value**: Tabel `article_meta` dan relasi atribut kustom artikel.
72. **Logging Audit Ekspor & Dukungan SQLite WAL Mode**: Tabel `article_exports` untuk pelacakan berkas hasil generate serta optimasi konkurensi Write-Ahead Logging (`enable_wal_mode`).
73. **Ekstensi WordPress REST API Client**: Penambahan metode pembaruan posting (`update_post`), penghapusan/trashing (`delete_post`), dan pengunggahan berkas media pustaka (`upload_media`).
74. **Sindikasi Konten Atom 1.0 & JSON Feed v1.1**: Generator feed RFC 4287 dan JSON Feed untuk distribusi konten ke agregator modern.
75. **Ekstraktor Plain Text Bersih**: Fungsi `to_plain_text` untuk indexing pencarian, voice generator, dan inferensi LLM.
76. **Subcommand CLI Baru (`trash`, `density`, `feed`, `meta`)**: Ekstensi perkakas baris perintah untuk audit dan tata kelola editorial terpadu.
77. **Perkakas Otomasi Migrasi Database & Benchmark SEO**: Skrip mandiri `scripts/migrate_db.py` dan `scripts/benchmark_seo.py` dengan throughput tinggi (>3.600 ops/sec).
78. **Pengembangan Suite Pengujian Komprehensif (120 Tests Passing)**: Penambahan pengujian unit penuh dengan 100% kelulusan pengujian (0 fail, 0 error).
