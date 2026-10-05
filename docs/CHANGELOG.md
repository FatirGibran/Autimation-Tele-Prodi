# Catatan Perkembangan Proyek (Changelog) - Automation Tele Prodi

Dokumen ini mencatat seluruh perkembangan dan pembaruan arsitektural yang telah diimplementasikan pada proyek **Automation Tele Prodi (Editorial Specialist Bot S1 Teknik Informatika Telkom University Purwokerto)**.

---

## Ringkasan Metrik Pembaruan
- **Total Item Perubahan**: 142 item pembaruan arsitektural terverifikasi
- **Cakupan Modul**: Sanitasi Keamanan, Parser Konten, Yoast SEO Evaluator, Komponen Semantik Elementor, Storage & SQLite, Exporter & Schema, CLI Tools, Webhook Server, Klien WordPress, serta Skrip Operasional
- **Status Pengujian**: 179 unit tests terverifikasi (100% pass rate)

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

---

## 10. Pembaruan Fitur & Arsitektur v2.2.0 (#79 - #105)

79. **Pembersihan Data URI / Base64 pada Gambar (`sanitizer.py`)**: Netralisasi atribut `src` gambar berformat `data:` untuk mencegah eksploitasi payload tersembunyi dan memory bloating.
80. **Sanitasi Tag Definisi Akademik `<abbr>` & `<dfn>` (`sanitizer.py`)**: Filtrasi atribut aman pada tag glosarium dan singkatan ilmiah.
81. **Pembersihan Paragraf Kosong & Normalisasi Whitespace (`sanitizer.py`)**: Stripping otomatis elemen `<p></p>` kosong dan perataan spasi berlebih.
82. **Parser Matematika LaTeX & Persamaan Ilmiah (`parser.py`)**: Konversi persamaan matematika inline (`$...$`) dan blok (`$$...$$`) ke markup standar institusional.
83. **Klasifikasi Tingkat Kemudahan Baca Bahasa Indonesia (`parser.py`)**: Kategorisasi label keterbacaan teks (Sangat Mudah hingga Sangat Sulit) berbasis metrik Flesch-Kincaid lokal.
84. **Parser Checklist & Task List Markdown (`parser.py`)**: Konversi sintaks tugas interaktif `[ ]` dan `[x]` ke elemen checkbox responsif.
85. **Generator Slug Judul Unik dengan Resolusi Tabrakan (`parser.py`)**: Pencegahan tabrakan tautan URL kanonis dengan penomoran berurutan otomatis.
86. **Validator Struktur Heading H1 Tunggal (`seo_validator.py`)**: Penegakan aturan SEO untuk mencegah lebih dari satu H1 di dalam isi artikel.
87. **Evaluator Gaya Judul Akademik & Power Keywords (`seo_validator.py`)**: Penilaian daya tarik judul artikel dan deteksi kata pemicu atensi pembaca.
88. **Evaluator Rasio Stop-Word & Kepadatan Konten (`seo_validator.py`)**: Analisis proporsi kata tugas terhadap kata substantif untuk mencegah thin content.
89. **Evaluator Keberagaman Anchor Text (`seo_validator.py`)**: Pendeteksi repetisi frasa tautan generik dan evaluasi variasi anchor text.
90. **Komponen Kutipan Akademik Pull-Quote (`components.py`)**: Template kutipan bernilai ilmiah dengan atribusi penulis dan sumber riset.
91. **Komponen Banner Afiliasi Lab Riset (`components.py`)**: Kartu identitas laboratorium komputasi dan kelompok keahlian fakultas.
92. **Komponen Pohon Prasyarat Kurikulum (`components.py`)**: Diagram alur prasyarat mata kuliah berformat visual kartu hierarkis.
93. **Komponen Pengumuman Acara & Seminar Akademik (`components.py`)**: Kartu agenda kegiatan ilmiah, webinar, dan pendaftaran peserta.
94. **Komponen Badge Dataset Riset Terbuka (`components.py`)**: Lencana resmi repositori GitHub dan repositori data penelitian terbuka prodi.
95. **Bilah Progres Visual Skor SEO & Indikator Keterbacaan (`formatters.py`)**: Representasi visual skor Yoast SEO berbasis Unicode bar dan lencana Telegram.
96. **Pembatas Laju Perintah Bot (Rate Limiter) (`formatters.py`)**: Proteksi anti-flood pengguna Telegram dengan mekanisme sliding cooldown.
97. **Keyboard Interaktif Review Editorial (`formatters.py`)**: Builder tombol inline keyboard Telegram untuk alur persetujuan dan revisi artikel.
98. **Manajemen Kategori & Filter Artikel Database (`storage.py`)**: Fungsi klasifikasi taksonomi dan penyaringan artikel aktif.
99. **Agregasi Analitik Editorial & Kecepatan Publikasi (`storage.py`)**: Kalkulasi metrik produktivitas tim editorial dan statistik penerbitan.
100. **Pembersihan & Retensi Revisi Kadaluarsa (`storage.py`)**: Mekanisme pruning revisi artikel usang dengan batas retensi fleksibel.
101. **Pemeriksaan Koneksi & Pembaruan Batch WordPress REST API (`wordpress_client.py`)**: Endpoint health-check dan helper pembaruan status pos massal.
102. **Ekstensi Format Hugo SSG & Skema Course JSON-LD (`exporter.py`)**: Ekspor Markdown kompatibel generator situs statis Hugo dan skema terstruktur mata kuliah Schema.org.
103. **Subcommand CLI Baru (`analytics`, `prune`, `hugo`) (`cli.py`)**: Perluasan antarmuka baris perintah untuk tata kelola editorial dan ekspor statis.
104. **Skrip Diagnostik Database & Pinger Mesin Pencari (`scripts/`)**: Skrip inspeksi SQLite `scripts/db_stats.py` dan notifikasi sitemap `scripts/ping_search_engines.py`.
105. **Pengembangan Suite Pengujian Komprehensif (151 Tests Passing)**: Penambahan pengujian unit penuh dengan 100% kelulusan pengujian (0 fail, 0 error).

---

## 11. Pembaruan Fitur & Arsitektur v2.3.0 (#106 - #142)

106. **Sanitasi Tabel Bersarang (`sanitizer.py`)**: Perataan struktur nested table dan pembersihan tag tabel tidak valid untuk menjamin integritas tata letak Elementor.
107. **Penegakan Protokol Sumber Media Audio/Video (`sanitizer.py`)**: Pembatasan skema URL atribut `src` audio/video hanya pada protokol aman (`https:` dan jalur absolut institusi).
108. **Pembersihan Piksel Pelacak Tersembunyi (`sanitizer.py`)**: Eliminasi elemen tersembunyi berdimensi 0x0 atau 1x1 serta inline tracker mencurigakan.
109. **Parser Sitasi Braket Akademik & Kunci BibTeX (`parser.py`)**: Ekstraksi format sitasi ilmiah `[Author, Year]` dan parsing bibliografi BibTeX institusional.
110. **Ekspander Akronim & Singkatan Bahasa Indonesia (`parser.py`)**: Normalisasi dan ekspansi akronim formal (seperti `PTN`, `LLDIKTI`, `SNDIKTI`, `KRS`, `SKS`).
111. **Detektor Sintaks Kode & Normalizer Blok `<pre>` (`parser.py`)**: Identifikasi otomatis bahasa pemrograman (Python, JavaScript, Go, SQL, HTML, C++) dan pembersihan pembungkus `<pre><code>`.
112. **Ekstraktor Kalimat Transisi Paragraf Bahasa Indonesia (`parser.py`)**: Identifikasi frasa transisi formal pembuka kalimat untuk evaluasi koherensi bacaan.
113. **Validator Dimensi & Rasio Aspek Gambar (`seo_validator.py`)**: Verifikasi proporsi aspek gambar (16:9, 4:3, 1:1) dan batasan dimensi minimal/maksimal untuk pencegahan Cumulative Layout Shift (CLS).
114. **Evaluator Keseragaman Distribusi Focus Keyphrase (`seo_validator.py`)**: Analisis sebaran kemunculan kata kunci fokus secara merata di awal, tengah, dan akhir artikel.
115. **Auditor Kedalaman & Otoritas Tautan Internal Akademik (`seo_validator.py`)**: Validasi kedalaman URL internal dan bobot tautan menuju laman akademik/prodi resmi.
116. **Validator Atribut `rel` Tautan Keluar (`seo_validator.py`)**: Penegakan nilai keamanan `rel="noopener noreferrer external"` pada seluruh tautan outbound.
117. **Komponen Kartu Profil Dosen & Peneliti (`components.py`)**: Tampilan kartu profil staf pengajar lengkap dengan NIDN, jabatan fungsional, dan tautan profil riset (Google Scholar / Scopus).
118. **Komponen Showcase Tugas Akhir / Capstone Mahasiswa (`components.py`)**: Komponen pameran karya inovasi dan proyek akhir mahasiswa berprestasi.
119. **Komponen Grid Lencana Sertifikasi Internasional (`components.py`)**: Kartu matriks sertifikasi industri keahlian rekayasa perangkat lunak dan komputasi awan.
120. **Komponen Kartu Linimasa Kalender Semester (`components.py`)**: Visualisasi jadwal penting akademik, periode KRS, UTS, UAS, dan yudisium.
121. **Komponen Spanduk Kemitraan & Sponsor Magang (`components.py`)**: Banner kerja sama industri, program magang MBKM, dan rekrutmen lulusan.
122. **Pratinjau Ringkas Diff Editorial Mobile (`formatters.py`)**: Ringkasan modifikasi draft editorial yang terformat ringkas untuk notifikasi Telegram.
123. **Kartu Pengingat Jadwal Terbit Telegram (`formatters.py`)**: Notifikasi visual pengingat artikel yang siap diterbitkan pada waktu tertentu.
124. **Manajer Antrean Publikasi Terjadwal (`storage.py`)**: Tabel `article_schedules` dan operasi antrean penerbitan otomatis SQLite.
125. **Helper Ekspor & Impor Cadangan Database Penuh (`storage.py`)**: Serialisasi dan deserialisasi seluruh tabel SQLite ke format JSON portabel.
126. **Pelacak Statistik Pembaca & Interaksi Artikel (`storage.py`)**: Tabel `article_engagement` dan kalkulasi tingkat interaksi serta view counter.
127. **Pengambil Riwayat Revisi Remote WordPress REST API (`wordpress_client.py`)**: Integrasi endpoint `/wp/v2/posts/{id}/revisions` untuk riwayat pos WordPress.
128. **Helper Penjadwalan Pos WordPress REST API (`wordpress_client.py`)**: Publikasi artikel terjadwal dengan status `future` dan parameter `date_gmt`.
129. **Exporter MDX untuk Framework Modern (`exporter.py`)**: Ekspor berkas `.mdx` dengan frontmatter khusus Astro dan Docusaurus.
130. **Generator Open Graph & Twitter Card Lanjutan (`exporter.py`)**: Pembangkit metadata kartu media sosial dengan dimensi eksplisit dan locale Indonesia `id_ID`.
131. **Subcommand CLI `schedule` (`cli.py`)**: Perintah konsol pengelolaan jadwal publikasi artikel di database.
132. **Subcommand CLI `dump` (`cli.py`)**: Perintah konsol pencadangan penuh seluruh database ke berkas JSON.
133. **Subcommand CLI `mdx` (`cli.py`)**: Perintah konsol konversi artikel ke berkas MDX modern.
134. **Skrip Validator Dead Link & Broken Anchor (`scripts/check_broken_links.py`)**: Perkakas audit otomatis integritas tautan halaman dan jangkar in-page.
135. **Pengembangan Suite Pengujian Unit Terpadu (179 Tests Passing)**: Penambahan pengujian komprehensif pada seluruh modul baru dengan tingkat kelulusan 100%.


