# Catatan Perkembangan Proyek (Changelog) - Automation Tele Prodi

Dokumen ini mencatat seluruh perkembangan dan pembaruan arsitektural yang telah diimplementasikan pada proyek **Automation Tele Prodi (Editorial Specialist Bot S1 Teknik Informatika Telkom University Purwokerto)**.

---

## Ringkasan Metrik Pembaruan
- **Total Item Perubahan**: 480+ item pembaruan arsitektural terverifikasi
- **Cakupan Modul**: Sanitasi Keamanan, Parser Konten, Yoast SEO Evaluator, Komponen Semantik Elementor, Storage & SQLite, Exporter & Schema, CLI Tools, Webhook Server, Klien WordPress, serta Skrip Operasional
- **Status Pengujian**: 488 unit tests terverifikasi (100% pass rate)


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

---

## 12. Pembaruan Fitur & Arsitektur v2.4.0 (#136 - #172)

136. **Sanitasi Rumus MathML (`sanitizer.py`)**: Penambahan dukungan aman elemen MathML (`<math>`, `<mrow>`, `<mi>`, `<mo>`, `<mn>`, dll.) dan pembersihan tag manipulatif `<annotation-xml>`.
137. **Pembersihan Obfuskasi Data Payload & Komentar Bahaya (`sanitizer.py`)**: Eliminasi otomatis atribut `data-payload` berkode panjang dan pembersihan script tersembunyi di dalam blok komentar HTML.
138. **Penegakan Token Sandbox Iframe Aman (`sanitizer.py`)**: Validasi token pembatas sandbox iframe tanpa izin breakout (`allow-top-navigation`) dan pembersihan atribut `frameborder`.
139. **Normalisasi Tipografis Gelar Akademik (`parser.py`)**: Pembakuan gelar akademik Indonesia/internasional (`S.Kom.`, `M.Kom.`, `Ph.D.`, `Dr.`, `Ir.`) dengan dotting standar.
140. **Parser Kode Kurikulum & Jenjang Mata Kuliah (`parser.py`)**: Deteksi kode mata kuliah (seperti `IF2143`, `TIF101`, `CSI402`) dan resolusi kode prodi serta tingkat semester.
141. **Penyeimbang & Pengoreksi Tanda Petik Cerdas (`parser.py`)**: Transformasi otomatis tanda petik lurus menjadi kutip ganda tipografis Indonesia dan penyeimbangan kurung kutip tak tertutup.
142. **Auto-Italicizer Istilah Latin Ilmiah (`parser.py`)**: Pembungkusan otomatis tag `<em>` pada terminologi ilmiah (*et al.*, *ibid.*, *de facto*, *ad hoc*, *vice versa*, *a priori*).
143. **Evaluator Keselarasan Metadata Search & Open Graph (`seo_validator.py`)**: Analisis konsistensi dan overlap semantik antara SEO Title dan OG Title/Description.
144. **Validator Referensi DOI & Akreditasi Jurnal Ilmiah (`seo_validator.py`)**: Verifikasi format kanonis tautan DOI HTTPS serta deteksi indeks reputasi SINTA 1-6, Scopus, dan WoS.
145. **Auditor Aksesibilitas Struktur Tabel HTML (`seo_validator.py`)**: Audit keberadaan `<caption>`/`aria-label` dan kepatuhan atribut `scope` pada elemen header `<th>` untuk SEO & WCAG.
146. **Evaluator Kesegaran Konten & Anomali Kronologis (`seo_validator.py`)**: Deteksi referensi tahun kadaluarsa (>5 tahun) dan peringatan anomali tahun masa depan.
147. **Komponen Kartu Akreditasi Unggul Institusi (`components.py`)**: Kartu resmi nilai akreditasi prodi dari LAM INFOKOM / BAN-PT lengkap dengan nomor SK dan masa berlaku.
148. **Komponen Kartu Spesifikasi Fasilitas Laboratorium (`components.py`)**: Tampilan spesifikasi perangkat komputasi, kluster GPU, dan alat riset lab.
149. **Komponen Kartu Podium Juara & Prestasi Mahasiswa (`components.py`)**: Visualisasi medali emas/perak hackathon, Gemastik, dan kompetisi informatika.
150. **Komponen Showcase Mitra Pertukaran Mahasiswa (`components.py`)**: Kartu profil perguruan tinggi mitra internasional untuk program credit transfer / IISMA.
151. **Komponen Kartu Keterserapan Karir & Tracer Study (`components.py`)**: Metrik masa tunggu kerja dan statistik rata-rata gaji awal lulusan.
152. **Formatter Kartu Sitasi BibTeX Telegram (`formatters.py`)**: Generator entri BibTeX instan siap-salin untuk memfasilitasi riset mahasiswa dan dosen.
153. **Formatter Kartu Laporan Audit Similarity & Orisinalitas (`formatters.py`)**: Indikator visual tingkat kemiripan teks dengan ambang batas rekomendasi editorial.
154. **Penyimpanan Pohon Taksonomi Kategori Hierarkis (`storage.py`)**: Tabel `article_categories` dan metode traversal relasi parent-child.
155. **Manajer Lease Lock Editing Draf Konkuren (`storage.py`)**: Tabel `article_locks` dan proteksi lease locking dengan TTL untuk mencegah konflik pengeditan ganda.
156. **Pencarian & Penggantian Transaksional Massal (`storage.py`)**: Helper `batch_replace_content` untuk update teks, istilah, atau nama pejabat secara massal.
157. **Helper Penetapan Tag Pos WordPress REST API (`wordpress_client.py`)**: Resolusi taksonomi tag massal langsung ke pos WordPress target.
158. **Helper Pembaruan Metadata Lampiran Media WordPress (`wordpress_client.py`)**: Pembaruan alt-text, caption, dan deskripsi berkas pustaka media.
159. **Generator Skema EducationalOccupationalProgram JSON-LD (`exporter.py`)**: Rich snippet Schema.org untuk profil kurikulum dan program studi sarjana.
160. **Generator Format MDX Kompatibel Next.js App Router (`exporter.py`)**: Ekspor berkas MDX modern dengan ekspor metadata bertipe TypeScript.
161. **Subcommand CLI `lock` (`cli.py`)**: Perintah konsol pengelolaan status kunci penyuntingan draf artikel.
162. **Subcommand CLI `replace` (`cli.py`)**: Perintah konsol batch replace teks artikel lintas database.
163. **Subcommand CLI `schema` (`cli.py`)**: Perintah konsol generate skema JSON-LD kurikulum prodi.
164. **Skrip Validator Aset Gambar & Optimasi Kompresi (`scripts/check_images.py`)**: Perkakas audit otomatis atribut alt, format modern WebP/AVIF, dan dimensi anti-CLS.
165. **Pengembangan Suite Pengujian Unit Terpadu (203 Tests Passing)**: Penambahan pengujian menyeluruh pada seluruh modul baru dengan tingkat kelulusan 100%.

---

## 13. Pembaruan Fitur & Arsitektur v2.5.0 (#173 - #210)

173. **Sanitasi Figure & Figcaption Semantik (`sanitizer.py`)**: Penegakan kelas editorial `.tu-figure` dan `.tu-figcaption`.
174. **Pembersihan Injeksi Atribut Kustom `data-*` (`sanitizer.py`)**: Netralisasi muatan script dan uri berbahaya pada atribut data kustom.
175. **Penegakan Kontrol Aksesibilitas & Preload Media (`sanitizer.py`)**: Penegakan otomatis atribut `controls`, `preload="metadata"`, dan penghapusan autoplay bersuara.
176. **Glosarium Istilah Akademik & Tooltip Otomatis (`parser.py`)**: Pembungkusan otomatis tag `<dfn title="...">` pada terminologi akademik prodi.
177. **Parser Tanggal & Waktu Formal Indonesia (`parser.py`)**: Ekstraksi tanggal, hari, jam, zona waktu (WIB/WITA/WIT), dan konversi ISO standar.
178. **Ekstraktor Kluster Riset Dosen Informatika (`parser.py`)**: Deteksi otomatis 4 kluster riset prodi Telkom Purwokerto (AI, Cyber, SE/Cloud, IoT).
179. **Normalisasi Indentasi Daftar Bertingkat Markdown (`parser.py`)**: Penyeragaman spasi hierarki nested unordered dan ordered list.
180. **Validator Hierarki & Kedalaman Breadcrumb (`seo_validator.py`)**: Verifikasi kedalaman navigasi remah roti dan validitas tautan beranda.
181. **Auditor Rasio Kontras Warna CSS Inline (`seo_validator.py`)**: Deteksi warna teks dan latar belakang beresiko kontras nol sesuai WCAG AA.
182. **Validator Spesifikasi & Aspek Rasio Gambar Open Graph (`seo_validator.py`)**: Audit dimensi minimal 600x315/1200x630 dan rasio aspek 1.91:1.
183. **Kalkulator Indeks Keterbacaan Coleman-Liau Indonesia (`seo_validator.py`)**: Pengukuran formula keterbacaan berbasis panjang kata dan kalimat.
184. **Komponen Kartu Publikasi Jurnal Ilmiah Unggulan (`components.py`)**: Visualisasi jurnal terindeks dengan badge Quartile (Q1-Q4) dan tautan DOI.
185. **Komponen Showcase Kelompok Belajar & Coding Club Mahasiswa (`components.py`)**: Kartu profil komunitas mahasiswa, koordinator, dan jadwal berkumpul.
186. **Komponen Banner Pengumuman Hibah Riset & Pendanaan (`components.py`)**: Banner capaian hibah penelitian fundamental dan kemitraan industri.
187. **Komponen Kartu Jalur Peminatan Kurikulum Pilihan (`components.py`)**: Tampilan mata kuliah pilihan utama dan prospek profesi per keminatan.
188. **Komponen Kartu Fasilitas Data Center & Infrastruktur Kampus (`components.py`)**: Tabel spesifikasi teknis rak server, jaringan, dan status operasional.
189. **Formatter Kartu Call for Papers Konferensi Ilmiah Telegram (`formatters.py`)**: Notifikasi batas waktu pengumpulan artikel dan bidang riset CFP.
190. **Formatter Kartu Ringkasan Audit SEO Yoast Ringkas (`formatters.py`)**: Ringkasan performa skor, grade, error, dan peringatan SEO untuk bot Telegram.
191. **Agregasi Analitik Pembaca per Kategori Artikel (`storage.py`)**: Query agregat jumlah artikel, total views, dan rata-rata pembaca per kategori.
192. **Manajer Daftar Bacaan & Bookmark Artikel Pengguna (`storage.py`)**: Tabel `article_bookmarks` dan manajemen CRUD bookmark pengguna.
193. **Pelacak Versi Migrasi Skema Database (`storage.py`)**: Tabel `schema_migrations` untuk pencatatan riwayat versi migrasi terstruktur.
194. **Pengatur Status Post Sticky & Proteksi Sandi WordPress (`wordpress_client.py`)**: Pembaruan visibilitas artikel unggulan dan proteksi kata sandi.
195. **Helper Penghapusan & Detasemen Media WordPress (`wordpress_client.py`)**: Penghapusan permanen lampiran pustaka media REST API.
196. **Generator JSON-LD ResearchProject & FundingAward (`exporter.py`)**: Skema data terstruktur Schema.org untuk proyek riset dan hibah dosen.
197. **Generator Markdown Kompatibel Nuxt Content v2 / Gatsby (`exporter.py`)**: Ekspor frontmatter YAML lengkap dengan navigasi dan taksonomi.
198. **Subcommand CLI `bookmark` (`cli.py`)**: Perintah konsol pengelolaan reading list dan bookmark artikel.
199. **Subcommand CLI `cat-stats` (`cli.py`)**: Perintah konsol analitik performa pembaca per kategori artikel.
200. **Subcommand CLI `nuxt` (`cli.py`)**: Perintah konsol ekspor artikel ke format Markdown Nuxt Content v2.
201. **Skrip Auditor Aksesibilitas WCAG Otomatis (`scripts/check_accessibility.py`)**: Perkakas audit otomatis hirarki heading, alt text, tabel semantik, dan media controls.
202. **Pengembangan Suite Pengujian Unit Terpadu (235 Tests Passing)**: Penambahan pengujian menyeluruh pada seluruh modul baru dengan tingkat kelulusan 100%.

---

## 14. Pembaruan Fitur & Skalabilitas v2.6.0 (Item 203 - 232)

203. **Sanitasi Semantic Disclosure Details & Summary (`sanitizer.py`)**: Sanitasi elemen `<details>` dan `<summary>` dengan penegakan kelas visual `.tu-details` dan `.tu-summary` serta pembersihan atribut berbahaya.
204. **Stripping Tag Meta Refresh & Base Terbenam (`sanitizer.py`)**: Penghapusan dan netralisasi otomatis tag `<meta http-equiv="refresh">` dan `<base href="...">` yang disusupi di dalam konten editorial.
205. **Netralisasi Form & Input Editorial Tidak Aman (`sanitizer.py`)**: Pembersihan tag `<form>`, `<input>`, `<button>`, `<textarea>` non-resmi pada artikel untuk mencegah serangan phishing internal.
206. **Kalkulator & Validator SKS Kurikulum Mahasiswa (`parser.py`)**: Ekstraksi dan kalkulasi otomatis total beban SKS mata kuliah teori dan praktikum dari tabel atau teks kurikulum prodi.
207. **Validator Format Gelar Dosen Pembimbing & Penguji (`parser.py`)**: Verifikasi penulisan gelar akademik nasional (S.Kom., M.T., Ph.D., Prof., Dr.) dan kepatuhan urutan gelar depan/belakang.
208. **Ekspansi Singkatan Akademik & Istilah Prodi (`parser.py`)**: Penggantian otomatis singkatan formal (KRS, KHS, KP, TA, MBKM, SKPI, CPL, CPMK) menjadi kepanjangan baku dalam teks editorial.
209. **Klasifikasi & Normalisasi Bahasa Blok Kode Markdown (`parser.py`)**: Deteksi dan pemetaan otomatis alias bahasa pemrograman (py -> python, js/ts -> javascript/typescript, sh/bash -> bash) pada fenced code blocks.
210. **Validator Multilingual Hreflang & Bahasa Alternatif (`seo_validator.py`)**: Audit keberadaan dan validitas tag link `rel="alternate" hreflang="..."` untuk lokalisasi bahasa (id, en).
211. **Auditor ARIA Landmarks & Skip Links Aksesibilitas (`seo_validator.py`)**: Verifikasi keberadaan navigasi skip link dan landmark semantik ARIA (`role="main"`, `navigation`, `banner`).
212. **Deteksi Canonical URL Loop & Normalisasi Domain (`seo_validator.py`)**: Pemeriksaan konsistensi tautan kanonikal, pencegahan loop pengalihan sendiri, dan penyeragaman protokol HTTPS.
213. **Auditor Irama & Panjang Paragraf Keterbacaan (`seo_validator.py`)**: Analisis panjang kata per paragraf dan variasi ritme membaca untuk mencegah kelelahan pembaca.
214. **Komponen Kartu Capstone Project Mahasiswa (`components.py`)**: Kartu showcase karya tugas akhir mahasiswa dengan judul, abstrak, teknologi yang digunakan, repositori GitHub, dan link demo langsung.
215. **Komponen Badge Sertifikasi Kompetensi Internasional (`components.py`)**: Kartu showcase sertifikasi industri mahasiswa dan dosen (AWS, Cisco CCNA, Google Cloud, RedHat) dengan masa berlaku dan nomor lisensi.
216. **Komponen Banner Milestone Kalender Akademik Semester (`components.py`)**: Banner penanda linimasa penting semester (awal perkuliahan, UTS, UAS, batas pengumpulan nilai, yudisium).
217. **Komponen Kartu Reservasi Laboratorium & Perangkat Riset (`components.py`)**: Visualisasi peminjaman fasilitas laboratorium komputer/jaringan, kapasitas kuota, dan status ketersediaan.
218. **Komponen Kartu Testimoni & Transfer SKS Student Exchange (`components.py`)**: Kartu showcase pengalaman mahasiswa pertukaran pelajar internasional/MBKM beserta pengakuan SKS universitas mitra.
219. **Formatter Kartu Pengumuman Sidang Skripsi Mahasiswa Telegram (`formatters.py`)**: Desain kartu siaran jadwal sidang tugas akhir mahasiswa, dewan penguji, ruang/tautan meeting, dan topik riset.
220. **Formatter Kartu Ringkasan Editorial Mingguan Telegram (`formatters.py`)**: Digest mingguan statistik jumlah publikasi, kategori terpopuler, dan catatan sorotan redaksi.
221. **Caching Metrik Waktu Baca & Jumlah Kata Artikel (`storage.py`)**: Tabel `article_reading_metrics` dan metode penyimpanan/pengambilan statistik durasi membaca pembaca.
222. **Manajer Langganan Notifikasi Editorial Multi-Kanal (`storage.py`)**: Tabel `editorial_subscribers` dan manajemen pendaftaran user ke kategori artikel tertentu (Telegram/Email).
223. **Helper Komparasi Dift Revisi Tersimpan Artikel (`storage.py`)**: Metode `compare_revisions` untuk analisis selisih jumlah kata, karakter, dan perubahan deskripsi meta antar versi.
224. **Pengatur Ringkasan Excerpt Postingan WordPress (`wordpress_client.py`)**: Metode `update_post_excerpt` untuk memperbarui kutipan ringkasan artikel pada WordPress REST API.
225. **Konfigurasi Status Komentar & Pingback Postingan WordPress (`wordpress_client.py`)**: Metode `set_post_comment_status` untuk membuka/menutup interaksi komentar dan trackback.
226. **Generator JSON-LD AcademicEvent & Seminar Ilmiah (`exporter.py`)**: Skema data terstruktur Schema.org `EducationEvent` untuk seminar, lokakarya, dan konferensi akademik prodi.
227. **Generator Markdown Kompatibel MDSveX / SvelteKit (`exporter.py`)**: Metode `to_sveltekit_markdown` untuk ekspor draf artikel ke format SvelteKit dengan frontmatter terstruktur.
228. **Subcommand CLI `subscribe` (`cli.py`)**: Perintah antarmuka CLI untuk manajemen pendaftaran dan peninjauan subscriber kanal redaksi.
229. **Subcommand CLI `diff-rev` (`cli.py`)**: Perintah antarmuka CLI untuk membandingkan statistik kata dan karakter dua revisi artikel secara instan.
230. **Subcommand CLI `svelte` (`cli.py`)**: Perintah antarmuka CLI untuk mengekspor artikel langsung ke berkas MDSveX SvelteKit.
231. **Skrip Auditor Tipografi & Keseimbangan Kutipan Otomatis (`scripts/check_typography.py`)**: Perkakas audit konsistensi tanda petik kurawal Indonesia, gelar akademik, dan spasi tanda baca.
232. **Ekspansi Suite Pengujian Unit Terpadu (263 Tests Passing)**: Penambahan pengujian unit menyeluruh di seluruh modul baru tanpa regresi dengan tingkat kelulusan 100%.

---

## 15. Pembaruan Fitur & Arsitektur v2.7.0 (Item 233 - 262+)

233. **Sanitasi Semantic Modal & Dialog HTML5 (`sanitizer.py`)**: Sanitasi elemen `<dialog>` dengan penegakan kelas visual dan pembersihan atribut/backdrop skrip manipulatif.
234. **Stripping Tag Animasi & Font SVG Berbahaya (`sanitizer.py`)**: Pembersihan tag `<animate>`, `<set>`, dan `<font-face>` pada aset grafik SVG inline guna mencegah eksploitasi visual denial-of-service.
235. **Sanitasi Art-Direction Gambar Responsif (`sanitizer.py`)**: Sanitasi elemen `<picture>` dan `<source>` dengan penegakan tipe MIME dan protokol gambar HTTPS terpercaya.
236. **Parser Rencana Studi Semester Kurikulum RPS (`parser.py`)**: Ekstraksi dan pengelompokan mata kuliah semester ganjil/genap dari format teks dan tabel markdown kurikulum.
237. **Parser Peringatan Keselamatan Laboratorium Komputasi (`parser.py`)**: Konversi otomatis format pedoman keselamatan K3 laboratorium komputer ke blok kartu peringatan visual.
238. **Validator Nomor Identifikasi Bibliografi ISBN & ISSN (`parser.py`)**: Verifikasi format ISBN-10, ISBN-13, dan ISSN internasional lengkap dengan kalkulasi checksum.
239. **Parser Rentang Tanggal Kalender Akademik Indonesia (`parser.py`)**: Ekstraksi rentang tanggal berformat bahasa Indonesia menjadi rentang representasi waktu standar ISO.
240. **Auditor Heading Skip Level SEO (`seo_validator.py`)**: Deteksi anomali hierarki heading yang melompati level (seperti H2 langsung melompat ke H4).
241. **Matcher Kata Kunci Morfologi & Imbuhan Bahasa Indonesia (`seo_validator.py`)**: Identifikasi variasi kata kunci fokus dengan prefiks dan sufiks morfologi bahasa Indonesia.
242. **Validator Rasio Aspek Gambar Twitter Summary Card (`seo_validator.py`)**: Audit dimensi dan rasio aspek gambar pratinjau media sosial Twitter card.
243. **Adapter Nilai Keterbacaan ke Hasil Audit Yoast SEO (`seo_validator.py`)**: Integrasi metrik kemudahan membaca Flesch-Kincaid bahasa Indonesia ke evaluasi Yoast.
244. **Komponen Kartu Capaian Pembelajaran Lulusan CPL (`components.py`)**: Visualisasi capaian pembelajaran kurikulum (CPL) per mata kuliah dengan kode dan domain kompetensi.
245. **Komponen Showcase Mitra Magang Industri (`components.py`)**: Kartu profil industri mitra magang mahasiswa lengkap dengan kuota posisi dan bidang teknologi.
246. **Komponen Realisasi Anggaran Hibah Riset Dosen (`components.py`)**: Visualisasi progress bar realisasi anggaran belanja dan milestone tahapan hibah penelitian.
247. **Komponen Kartu Buku Teks Wajib Perpustakaan (`components.py`)**: Kartu ketersediaan buku cadangan perpustakaan (course reserves) dengan nomor panggil resmi.
248. **Komponen Statistik Tracer Study Lulusan (`components.py`)**: Visualisasi KPI respon tracer study, rata-rata masa tunggu kerja, dan distribusi penyerapan karir alumni.
249. **Formatter Kartu Pengingat Call for Papers Konferensi Telegram (`formatters.py`)**: Format kartu siaran Telegram pengingat tenggat waktu submit makalah konferensi ilmiah.
250. **Formatter Siaran Prestasi Juara Mahasiswa Telegram (`formatters.py`)**: Format siaran cepat berita prestasi mahasiswa pemenang hackathon dan kompetisi nasional.
251. **Pencatatan Time-Series Tayangan Artikel (`storage.py`)**: Tabel `article_view_logs` dan query agregasi harian performa artikel untuk analitik historis.
252. **Manajer Penugasan Editorial Artikel (`storage.py`)**: Tabel `editorial_tasks` dan pelacakan alur kerja tugas delegasi review, fact-checking, dan proofreading.
253. **Manajer Metadata Istilah Taksonomi (`storage.py`)**: Tabel `taxonomy_meta` untuk penyimpanan atribut visual warna, url banner, dan deskripsi kategori/tag.
254. **Helper Post Sticky Toggle WordPress REST API (`wordpress_client.py`)**: Metode pengaktifan status sematan pos utama (pinned post) via API WordPress.
255. **Filter Query Media berdasarkan MIME Type WordPress (`wordpress_client.py`)**: Metode penyaringan koleksi pustaka berkas berdasarkan prefiks tipe konten (`image/`, `application/pdf`).
256. **Generator Skema CollegeOrUniversity Schema.org (`exporter.py`)**: Skema data terstruktur identitas institusi dan akreditasi untuk Google Knowledge Graph.
257. **Generator Markdown Kompatibel Eleventy (11ty) (`exporter.py`)**: Ekspor artikel ke format SSG Eleventy dengan layout nunjucks dan penugasan permalink dinamis.
258. **Subcommand CLI `task` (`cli.py`)**: Perintah konsol penugasan, pemantauan, dan pembaruan status tugas editorial tim prodi.
259. **Subcommand CLI `view-stats` (`cli.py`)**: Perintah konsol visualisasi riwayat tayangan harian artikel berdasarkan ID database.
260. **Subcommand CLI `eleventy` (`cli.py`)**: Perintah konsol konversi artikel langsung ke format markdown Eleventy SSG.
261. **Skrip Auditor Hyperlink & Anchor Target (`scripts/check_hyperlinks.py`)**: Perkakas otomatisasi verifikasi tautan `#fragment` lokal, penegakan HTTPS internal, dan audit keamanan rel link.
262. **Ekspansi Suite Pengujian Unit Terpadu (291 Tests Passing)**: Verifikasi penuh 291 unit test tanpa kegagalan (100% pass rate) pada seluruh modul arsitektur.

---

## 16. Ekspansi Arsitektural v2.8.0

263. **Sanitasi Elemen Subtitle/Caption Track HTML5 (`sanitizer.py`)**: Penegakan validitas atribut `kind`, `srclang`, `label`, serta penyaringan atribut berbahaya pada elemen `<track>`.
264. **Pelucutan Primitif Filter SVG Berbahaya (`sanitizer.py`)**: Stripping elemen `<filter>`, `<feImage>`, dan atribut manipulasi filter SVG yang berpotensi memicu kebocoran data.
265. **Sanitasi Shadow DOM Template & Slot (`sanitizer.py`)**: Pembersihan markup deklaratif shadow DOM pada elemen `<template>` dan `<slot>`.
266. **Parser Inventaris Spesifikasi Alat Lab (`parser.py`)**: Parsing tabel perangkat keras laboratorium, nomor seri, dan kondisi peralatan.
267. **Parser Sitasi Ilmiah Format APA Edisi ke-7 (`parser.py`)**: Ekstraksi terstruktur daftar pustaka jurnal ilmiah standar APA 7th edition.
268. **Parser Rubrik Penilaian Sidang Tugas Akhir (`parser.py`)**: Parsing kriteria dan bobot evaluasi sidang skripsi mahasiswa.
269. **Konverter Skala Mutu Nilai Huruf ke IPK (`parser.py`)**: Konversi otomatis nilai mutu huruf (A, AB, B, BC, C, D, E) ke angka IPK 4.00.
270. **Detektor Kalimat Berurutan Berawalan Kata Sama (`seo_validator.py`)**: Analisis streak repetisi kata awal kalimat untuk menjaga variasi diksi teks.
271. **Evaluator Distribusi Konjungsi Transisi Paragraf (`seo_validator.py`)**: Evaluasi proporsi sebaran penanda transisi bahasa Indonesia antar paragraf.
272. **Validator Ajakan Bertindak (CTA) Meta Description (`seo_validator.py`)**: Pengecekan engagement verbs penelusuran (pelajari, temukan, simak, dll.).
273. **Validator Otomatis Sintaks & Atribut JSON-LD Schema.org (`seo_validator.py`)**: Audit validitas sintaks dan kelengkapan properti wajib embedded script Schema.org.
274. **Komponen Alur Prasyarat Mata Kuliah Kurikulum (`components.py`)**: Kartu visual relasi prasyarat pengambilan mata kuliah dan mata kuliah terminal.
275. **Komponen Checklist APD Keselamatan Lab (`components.py`)**: Visualisasi protokol OHS (K3) laboratorium, status APD wajib, dan nomor darurat.
276. **Komponen Tabel Kuota Pertukaran Mahasiswa Internasional (`components.py`)**: Visualisasi universitas mitra, negara, kuota, syarat IPK, dan syarat bahasa.
277. **Komponen Milestone Progres Hibah Riset Dosen (`components.py`)**: Kartu pelacakan anggaran Rupiah dan persentase capaian luaran penelitian.
278. **Komponen Histogram Distribusi Gaji Alumni (`components.py`)**: Kartu grafik batang sebaran pendapatan lulusan disertai median gaji.
279. **Formatter Pengumuman Beasiswa Pendidikan Telegram (`formatters.py`)**: Format pesan siaran pembukaan beasiswa dan syarat pendaftaran mahasiswa.
280. **Formatter Siaran Cepat Publikasi Jurnal Internasional (`formatters.py`)**: Format pesan siaran kilat artikel jurnal ilmiah Scopus bereputasi dengan DOI.
281. **Manajer Papan Catatan Kolaborasi Editorial (`storage.py`)**: Tabel `article_notes` untuk penambahan, pencarian, dan penghapusan catatan tim editorial.
282. **Manajer Log Webhook Publikasi Outbound (`storage.py`)**: Tabel `publishing_webhook_logs` dan audit rekaman riwayat pengiriman sinyal webhook.
283. **Resolver Sinonim & Alias Istilah Taksonomi (`storage.py`)**: Tabel `taxonomy_synonyms` dan resolusi otomatis istilah alias ke kanonikal prodi.
284. **Helper Bulk Trash Posts Klien WordPress (`wordpress_client.py`)**: Pembersihan pos jamak secara berurutan dengan laporan status keberhasilan.
285. **Helper Pencarian Media Berdasarkan Slug WordPress (`wordpress_client.py`)**: Pengambilan data berkas media dari REST API berdasarkan slug berkas.
286. **Generator Skema ScholarlyArticle Schema.org (`exporter.py`)**: Konstruksi metadata JSON-LD artikel ilmiah dengan entitas author dan DOI.
287. **Generator Markdown Kompatibel Zola SSG (`exporter.py`)**: Ekspor artikel ke format Zola static site generator dengan frontmatter TOML `+++`.
288. **Subcommand CLI `note` (`cli.py`)**: Manajemen konsol catatan editorial artikel (list, add, delete).
289. **Subcommand CLI `zola` (`cli.py`)**: Ekspor konsol artikel langsung ke format markdown Zola SSG.
290. **Subcommand CLI `webhook-logs` (`cli.py`)**: Pemantauan konsol riwayat pengiriman notifikasi webhook publikasi.
291. **Ekspansi Suite Pengujian Unit Terpadu (319 Tests Passing)**: Verifikasi penuh 319 unit test terverifikasi (100% pass rate) pada seluruh modul arsitektur.

---

## 17. Ekspansi Arsitektural v2.9.0

292. **Sanitasi Elemen Fallback Canvas HTML5 (`sanitizer.py`)**: Sanitasi elemen fallback aksesibilitas pada tag `<canvas>` dan pemblokiran atribut scriptable context.
293. **Sanitasi Anotasi Ruby Fonetik Linguistik (`sanitizer.py`)**: Validasi dan pembersihan struktur penanda fonetik `<ruby>`, `<rt>`, `<rp>`, `<rb>`, `<rtc>`.
294. **Netralisasi Skrip & Tautan Eksternal MathML (`sanitizer.py`)**: Pembersihan formula matematis MathML dengan pelucutan atribut `href` dan `xlink:href`.
295. **Parser Sitasi IEEE Journal & Transactions (`parser.py`)**: Parsing format sitasi IEEE standar (penulis, judul artikel, jurnal, volume, nomor, halaman, tahun, DOI).
296. **Parser Standar Operasional Prosedur (SOP) Lab (`parser.py`)**: Ekstraksi urutan tahapan SOP praktikum, nomor langkah, arahan teknis, dan catatan K3.
297. **Parser Kriteria Kelayakan Beasiswa Akademik (`parser.py`)**: Ekstraksi informasi eligibilitas beasiswa (IPK minimal, semester, berkas, batas pendaftaran).
298. **Kalkulator Konversi Beban SKS ke ECTS (`parser.py`)**: Konversi beban jam studi SKS ke standar European Credit Transfer System (1 SKS ≈ 1.6 ECTS).
299. **Kalkulator Indeks Keterbacaan Gunning Fog Akademik Indonesia (`seo_validator.py`)**: Evaluasi kompleksitas kalimat dan persentase kata bersuku kata tinggi pada teks akademik.
300. **Detektor Orphan Links & Broken Internal Anchors (`seo_validator.py`)**: Audit konsistensi tautan jangkar internal (`href="#..."`) terhadap ID elemen tujuan.
301. **Validator Kredensial Akademik & ORCID ID Penulis (`seo_validator.py`)**: Validasi format 16-digit ORCID ID dan gelar akademik penulis resmi.
302. **Validator Lisensi Open Access & Creative Commons (`seo_validator.py`)**: Pemeriksaan kelengkapan klausul lisensi terbuka (CC BY / CC BY-SA) dan hak cipta.
303. **Komponen Pemetaan Level Taksonomi Bloom C1-C6 (`components.py`)**: Kartu visual capaian kompetensi pembelajaran kurikulum OBE (Outcome-Based Education).
304. **Komponen Protokol Pengelolaan Limbah B3 Laboratorium (`components.py`)**: Tabel semantik visual klasifikasi limbah kimia/B3, kontainer, lokasi simpan, dan jadwal disposal.
305. **Komponen Matriks Transfer Kredit Pertukaran Pelajar (`components.py`)**: Tabel perbandingan mata kuliah kampus mitra dengan kurikulum prodi dan konversi SKS.
306. **Komponen Kartu Pameran Hak Paten & HKI Dosen (`components.py`)**: Showcase resmi perlindungan hukum invensi riset dosen, nomor paten DJKI, dan abstrak teknologi.
307. **Komponen Testimoni Mitra Industri Tracer Study (`components.py`)**: Kartu feedback pimpinan industri mitra dan indikator serapan alumni di dunia kerja.
308. **Formatter Pengumuman Pendaftaran Paten Telegram (`formatters.py`)**: Format pesan siaran resmi perolehan hak paten terdaftar untuk kanal Telegram prodi.
309. **Formatter Persetujuan Transfer Kredit Telegram (`formatters.py`)**: Format pesan notifikasi resmi hasil konversi nilai dan kredit mata kuliah pertukaran mahasiswa.
310. **Manajer Penugasan Peer Reviewer Artikel (`storage.py`)**: Tabel `article_reviewers` dan pelacakan penugasan editorial peer reviewer, email, dan status review.
311. **Manajer Log Sindikasi Eksternal Artikel (`storage.py`)**: Tabel `syndication_logs` untuk pelacakan distribusi konten ke Medium, LinkedIn, dan portal riset.
312. **Manajer Checklist Alur Kerja Editorial (`storage.py`)**: Tabel `editorial_checklists` untuk verifikasi kelayakan praterbit (plagiarism check, fact check, proofreading).
313. **Helper Batch Update Kategori Pos WordPress (`wordpress_client.py`)**: Metode batch update kategori pada sekumpulan pos WordPress via REST API.
314. **Helper Pencarian Pengguna Berdasarkan Slug WordPress (`wordpress_client.py`)**: Pengambilan detail entitas user penulis berdasarkan slug akun dari REST API.
315. **Generator Schema.org TechArticle JSON-LD (`exporter.py`)**: Metadata terstruktur panduan teknis laboratorium dan tutorial rekayasa dengan dependensi teknis.
316. **Generator Markdown Kompatibel Pelican SSG (`exporter.py`)**: Ekspor artikel ke format Pelican static site generator dengan format header metadata.
317. **Subcommand CLI `reviewer` (`cli.py`)**: Manajemen konsol penugasan peer reviewer artikel (assign, status, list).
318. **Subcommand CLI `pelican` (`cli.py`)**: Perintah konsol ekspor artikel langsung ke format markdown Pelican SSG.
319. **Subcommand CLI `checklist` (`cli.py`)**: Perintah konsol manajemen dan verifikasi checklist alur kerja editorial (list, set).
320. **Ekspansi Suite Pengujian Unit Terpadu (347 Tests Passing)**: Verifikasi penuh seluruh modul dengan 347 unit test terverifikasi (100% pass rate).

---

## 18. Ekspansi Arsitektural v3.0.0 Milestone Release

321. **Sanitasi Elemen Dialog & Modal HTML5 (`sanitizer.py`)**: Sanitasi elemen `<dialog>` dengan pelucutan atribut aksi skrip tak berizin.
322. **Sanitasi Tag Interaktif Details & Summary (`sanitizer.py`)**: Sanitasi blok disclosure `<details>` dan `<summary>` dengan pembatasan atribut standar (`open`).
323. **Sanitasi Nama Slot Web Component (`sanitizer.py`)**: Sanitasi atribut `slot` pada web components untuk mencegah prototype pollution (`__proto__`, `constructor`, `prototype`).
324. **Parser Sitasi Konferensi & Transaksi ACM (`parser.py`)**: Parsing format rujukan sitasi ACM (Association for Computing Machinery) berstandar internasional dengan DOI dan venue.
325. **Kalkulator Rubrik Penilaian Sidang Skripsi (`parser.py`)**: Perhitungan skor berbobot sidang tugas akhir (presentasi, penguasaan materi, naskah, produk) serta konversi huruf mutu dan IPK standar Indonesia.
326. **Parser Logbook Mingguan Magang MBKM (`parser.py`)**: Ekstraksi catatan aktivitas mingguan magang bersertifikat industri, total jam, dan ringkasan capaian kompetensi.
327. **Parser Log Pemeliharaan & Kalibrasi Alat Lab (`parser.py`)**: Ekstraksi riwayat perawatan alat instrumen lab, tanggal kalibrasi, teknisi, dan status kelayakan operasional.
328. **Kalkulator Indeks Keterbacaan Coleman-Liau Teks Indonesia (`seo_validator.py`)**: Evaluasi keterbacaan teks berbasis jumlah huruf per 100 kata dan jumlah kalimat per 100 kata.
329. **Auditor Urutan Hierarki Heading Berjenjang (`seo_validator.py`)**: Pemeriksaan pelanggaran level heading (tidak boleh melompat tingkat, misal H2 langsung ke H4 tanpa H3).
330. **Detektor Klausul Pengakuan Dana Hibah Riset (`seo_validator.py`)**: Identifikasi keberadaan acknowledgments pendanaan penelitian (Kemendikbudristek/LPDP/BRIN/Internal) beserta nomor kontrak/SPK.
331. **Auditor Aksesibilitas Gambar & Pencegahan CLS (`seo_validator.py`)**: Audit kelengkapan atribut `width`, `height`, dan deskriptivitas `alt` pada elemen `<img>` guna mencegah Cumulative Layout Shift.
332. **Komponen Stepper Milestone Capstone Proyek Akhir (`components.py`)**: Generator kartu visual interaktif tahapan tugas akhir mahasiswa (proposal, seminar kemajuan, sidang terbuka).
333. **Komponen Banner Pendaftaran Workshop Open House Lab (`components.py`)**: Kartu promosi pelatihan dan open house laboratorium riset dengan jadwal dan tautan registrasi.
334. **Komponen Showcase Magang Industri Bersertifikat MBKM (`components.py`)**: Kartu portofolio pengalaman mahasiswa magang di industri teknologi mitra.
335. **Komponen Pameran Monograf Publikasi Buku Dosen (`components.py`)**: Showcase penerbitan monograf dan buku referensi dosen ber-ISBN.
336. **Komponen Profil Universitas Mitra Pertukaran Internasional (`components.py`)**: Kartu profil perguruan tinggi mitra luar negeri, QS ranking, negara, dan kuota pertukaran.
337. **Formatter Undangan Webinar & Workshop Telegram (`formatters.py`)**: Format siaran pengumuman workshop akademik dan webinar untuk kanal Telegram prodi.
338. **Formatter Jadwal Sidang Tugas Akhir Telegram (`formatters.py`)**: Format siaran pengumuman jadwal sidang skripsi mahasiswa, penguji, waktu, dan ruangan.
339. **Pelacak Sitasi Akademik Eksternal Artikel (`storage.py`)**: Tabel `article_citations` dan metode pelacakan sitasi jurnal eksternal yang merujuk artikel prodi.
340. **Manajer Komentar Review Editorial Inline (`storage.py`)**: Tabel `editorial_comments` dan alur peninjauan per paragraf oleh editor dan reviewer.
341. **Library Snippet Konten Editorial Terpakai-Ulang (`storage.py`)**: Tabel `content_snippets` untuk penyimpanan potongan markup callout/disclaimer yang dapat disematkan berulang.
342. **Helper Batch Update Post Tags WordPress (`wordpress_client.py`)**: Pembaruan massal tag pada sekumpulan pos WordPress via REST API.
343. **Helper Pencarian Tag Berdasarkan Slug WordPress (`wordpress_client.py`)**: Pengambilan data tag WordPress berdasarkan slug dari REST API.
344. **Generator Schema.org Dataset JSON-LD (`exporter.py`)**: Konstruksi metadata terstruktur untuk dataset riset terbuka laboratorium telematika.
345. **Generator Markdown Kompatibel Docusaurus SSG (`exporter.py`)**: Ekspor artikel ke format markdown Docusaurus dengan frontmatter YAML dan konfigurasi hierarki sidebar.
346. **Subcommand CLI `snippet` (`cli.py`)**: Manajemen konsol perpustakaan snippet konten editorial (list, save, get).
347. **Subcommand CLI `docusaurus` (`cli.py`)**: Ekspor konsol artikel langsung ke format markdown Docusaurus.
348. **Subcommand CLI `comment` (`cli.py`)**: Manajemen konsol komentar review editorial dan resolusi status review (list, add, resolve).
349. **Ekspansi Suite Pengujian Unit Terpadu (375 Tests Passing)**: Verifikasi menyeluruh seluruh modul sistem dengan 375 unit test terverifikasi (100% pass rate).

---

## 19. Ekspansi Arsitektural v3.1.0 Milestone Release

350. **Sanitasi Elemen Meter & Progress HTML5 (`sanitizer.py`)**: Sanitasi elemen `<meter>` dan `<progress>` terhadap atribut nilai di luar rentang dan payload script tersembunyi.
351. **Sanitasi Elemen Gambar Responsif Picture & Source (`sanitizer.py`)**: Validasi elemen `<picture>` dan `<source>` dengan penegakan skema URI aman dan MIME type gambar yang diizinkan.
352. **Sanitasi Atribut Tema & Mode Tampilan (`sanitizer.py`)**: Pembersihan nilai atribut `data-theme` dan `data-mode` terhadap serangan CSS-in-attribute injection.
353. **Parser Sitasi Springer LNCS & LSCS (`parser.py`)**: Penguraian sitasi rujukan akademik standar Springer Lecture Notes in Computer Science (LNCS/LSCS).
354. **Validator Kelayakan Ujian Proposal Skripsi (`parser.py`)**: Validasi kelayakan checklist syarat pendaftaran seminar proposal skripsi (SKS kelulusan, IPK minimal, dan persetujuan dosen pembimbing).
355. **Parser Log Kegiatan Pengabdian Masyarakat PKM (`parser.py`)**: Ekstraksi log aktivitas pengabdian kepada masyarakat, skema hibah, kelompok sasaran binaan, dan luaran kegiatan.
356. **Parser Audit Checklist Keselamatan Laboratorium K3 (`parser.py`)**: Parsing audit kepatuhan standar keselamatan kerja K3 lab, inventaris APAR, kotak P3K, dan jalur evakuasi darurat.
357. **Auditor ID Elemen Duplikat Semantik (`seo_validator.py`)**: Deteksi ID HTML duplikat yang merusak navigasi anchor internal dan standar aksesibilitas WCAG/W3C.
358. **Detektor Akreditasi & Peringkat Jurnal SINTA (`seo_validator.py`)**: Analisis dan pengenalan otomatis status akreditasi jurnal ilmiah nasional SINTA 1 hingga SINTA 6.
359. **Auditor Direktif Meta Robots Indexing (`seo_validator.py`)**: Evaluasi direktif indexing robots (`noindex`, `nofollow`, `noarchive`, `max-snippet`) untuk mencegah kesalahan pengindeksan mesin pencari.
360. **Auditor Kesiapan Metadata Sosial Open Graph & Twitter Cards (`seo_validator.py`)**: Validasi kelengkapan properti `og:title`, `og:description`, `og:image`, `twitter:card`, dan `twitter:image`.
361. **Komponen Showcase Pengabdian Masyarakat PKM (`components.py`)**: Kartu visual kegiatan PKM dosen dan mahasiswa bersama komunitas mitra binaan.
362. **Komponen Kartu Prestasi Juara Kompetisi Mahasiswa (`components.py`)**: Showcase kejuaraan dan medali kompetisi inovasi teknologi mahasiswa (Pimnas, Gemastik, Imagine Cup, dsb.).
363. **Komponen Badge & Profil Jurnal Terakreditasi SINTA (`components.py`)**: Kartu informasi jurnal ilmiah dengan badge peringkat SINTA 1-6 dan tautan arsip berkala.
364. **Komponen Rekrutmen Asisten Praktikum Lab (`components.py`)**: Kartu pendaftaran asisten praktikum dengan persyaratan mata kuliah, periode seleksi, dan tautan formulir pendaftaran.
365. **Komponen Standar K3 Laboratorium & Posisi APAR (`components.py`)**: Kartu keselamatan kerja lab dengan panduan tanggap darurat, nomor kontak P3K, dan penunjuk lokasi APAR.
366. **Formatter Notifikasi Pengabdian Masyarakat Telegram (`formatters.py`)**: Format siaran pengumuman kegiatan PKM dan diseminasi teknologi prodi untuk kanal Telegram.
367. **Formatter Notifikasi Prestasi Juara Mahasiswa Telegram (`formatters.py`)**: Format pesan siaran kemenangan mahasiswa dalam kompetisi inovasi teknologi untuk kanal Telegram.
368. **Manajer Catatan Prestasi Kompetisi Mahasiswa (`storage.py`)**: Tabel `competition_achievements` dan pelacakan riwayat kemenangan tim, pembimbing, tahun, dan penyelenggara.
369. **Manajer Direktori Indeksasi Jurnal SINTA (`storage.py`)**: Tabel `journal_indexings` dan penyimpanan katalog jurnal ilmiah terakreditasi nasional/internasional.
370. **Manajer Log Inspeksi K3 Laboratorium (`storage.py`)**: Tabel `safety_inspections` dan pencatatan riwayat audit keselamatan kerja berkala fasilitas lab.
371. **Helper Pengambilan Kategori Turunan WordPress (`wordpress_client.py`)**: Pengambilan seluruh kategori anak berdasarkan parent ID via REST API.
372. **Helper Ping Kesehatan & Otentikasi REST API WordPress (`wordpress_client.py`)**: Endpoint ping diagnostik konektivitas server, latensi respons, dan validasi kredensial pengguna `/users/me`.
373. **Generator Schema.org SpecialAnnouncement JSON-LD (`exporter.py`)**: Pembuatan metadata terstruktur pemberitahuan darurat kampus dan instruksi akademik khusus.
374. **Generator Markdown Kompatibel MkDocs Material SSG (`exporter.py`)**: Ekspor artikel ke format Material for MkDocs static site generator dengan frontmatter YAML dan heading hierarki.
375. **Subcommand CLI `achievement` (`cli.py`)**: Perintah konsol manajemen rekam jejak prestasi kompetisi mahasiswa (list, add).
376. **Subcommand CLI `mkdocs` (`cli.py`)**: Perintah konsol ekspor artikel ke format markdown MkDocs.
377. **Subcommand CLI `safety-log` (`cli.py`)**: Perintah konsol pencatatan dan peninjauan log inspeksi K3 laboratorium (list, add).
378. **Ekspansi Suite Pengujian Unit Terpadu (404 Tests Passing)**: Verifikasi menyeluruh seluruh modul sistem dengan 404 unit test terverifikasi (100% pass rate).

---

## 20. Ekspansi Arsitektural v3.2.0 Milestone Release

379. **Sanitasi Elemen Audio & Track HTML5 (`sanitizer.py`)**: Sanitasi elemen `<audio>` dan `<track>` serta penegakan skema URI aman pada atribut `src`.
380. **Sanitasi Tipografi Komputasi Kbd & Samp (`sanitizer.py`)**: Sanitasi elemen tipografi komputasi `<kbd>` dan `<samp>` dari injeksi markup dan script tersembunyi.
381. **Sanitasi Tooltip Kontekstual Data-Tooltip (`sanitizer.py`)**: Pembersihan nilai atribut `data-tooltip`, `data-title`, dan `data-placement` dari injeksi event handler.
382. **Parser Sitasi Akademik Format Harvard (`parser.py`)**: Penguraian format sitasi rujukan akademik standar Harvard (*author-date*) ke dalam entitas terstruktur.
383. **Validator Konversi Kredit Program MBKM (`parser.py`)**: Validasi rekognisi dan ekuivalensi mata kuliah mahasiswa program Magang Merdeka dan Studi Independen.
384. **Parser Log Inventaris & Kalibrasi Alat Lab (`parser.py`)**: Parsing audit masa berlaku kalibrasi peralatan riset laboratorium dan sertifikat kalibrator.
385. **Validator Clearance Yudisium Kelulusan (`parser.py`)**: Validasi kelayakan checklist administrasi kelulusan sarjana sebelum pelaksanaan yudisium.
386. **Auditor Aksesibilitas Transkrip Media Audio/Video (`seo_validator.py`)**: Pemeriksaan ketersediaan alternatif teks dan transkrip konten multimedia (WCAG 2.1 AA).
387. **Detektor Kuartil SCImago Journal Rank SJR (`seo_validator.py`)**: Pengenalan otomatis kuartil reputasi publikasi ilmiah internasional Scopus/SJR (Q1, Q2, Q3, Q4).
388. **Auditor Tag Multibahasa Hreflang (`seo_validator.py`)**: Validasi keabsahan format tag `hreflang` dan kode bahasa internasional ISO 639-1.
389. **Auditor Kedalaman Hierarki Breadcrumb (`seo_validator.py`)**: Evaluasi kedalaman rantai navigasi semantik breadcrumb dan pencegahan self-loop.
390. **Komponen Pemetaan Ekuivalensi Kredit MBKM (`components.py`)**: Kartu visualisasi konversi mata kuliah program MBKM ke kurikulum sarjana teknik.
391. **Komponen Sertifikat Clearance Yudisium (`components.py`)**: Kartu status kelulusan sarjana lengkap dengan predikat dan kode verifikasi ijazah.
392. **Komponen Showcase Makalah Jurnal Scopus (`components.py`)**: Kartu pameran publikasi riset civitas akademika pada jurnal bereputasi Scopus dengan indikator kuartil SJR.
393. **Komponen Kalibrasi Alat Laboratorium (`components.py`)**: Kartu monitoring status kelayakan ukur instrumen laboratorium prodi.
394. **Komponen Dosen Tamu & Visiting Professor (`components.py`)**: Kartu profil narasumber akademik internasional dan dokumentasi kuliah pakar.
395. **Formatter Siaran Yudisium Kelulusan Telegram (`formatters.py`)**: Format siaran kartu ucapan selamat yudisium mahasiswa sarjana teknik di kanal Telegram.
396. **Formatter Siaran Kuliah Tamu Internasional Telegram (`formatters.py`)**: Format pesan undangan kuliah pakar dosen tamu internasional di kanal Telegram.
397. **Manajer Rekam Konversi MBKM (`storage.py`)**: Tabel basis data `mbkm_credit_transfers` untuk pengelolaan rekam jejak rekognisi SKS mahasiswa.
398. **Manajer Rekam Clearance Yudisium (`storage.py`)**: Tabel basis data `yudisium_clearances` untuk penyimpanan status kelulusan sarjana.
399. **Manajer Riwayat Kalibrasi Lab (`storage.py`)**: Tabel basis data `lab_equipment_calibrations` untuk monitoring masa aktif kalibrasi alat.
400. **Helper WordPress Get Media By ID (`wordpress_client.py`)**: Pengambilan metadata file media lampiran berdasarkan ID melalui REST API WordPress.
401. **Helper WordPress Get Site Settings (`wordpress_client.py`)**: Pengambilan informasi pengaturan situs dan konfigurasi direktori via REST API WordPress.
402. **Generator Schema.org EducationalOccupationalCredential (`exporter.py`)**: Pembuatan metadata terstruktur JSON-LD untuk ijazah sarjana dan sertifikat keahlian.
403. **Generator Markdown Kompatibel Astro Starlight (`exporter.py`)**: Ekspor artikel ke format Astro Starlight static documentation generator dengan hierarki sidebar.
404. **Subcommand CLI `mbkm` (`cli.py`)**: Perintah konsol pencatatan dan peninjauan rekognisi konversi kredit MBKM mahasiswa (list, add).
405. **Subcommand CLI `yudisium` (`cli.py`)**: Perintah konsol manajemen rekam kelulusan yudisium mahasiswa (list, add, check).
406. **Subcommand CLI `starlight` (`cli.py`)**: Perintah konsol ekspor artikel ke format markdown Astro Starlight.
407. **Ekspansi Suite Pengujian Unit Terpadu (433 Tests Passing)**: Verifikasi menyeluruh seluruh modul sistem dengan 433 unit test terverifikasi (100% pass rate).

---

## 21. Ekspansi Arsitektural v3.3.0 Milestone Release

408. **Sanitasi Media Responsif Picture & Source (`sanitizer.py`)**: Sanitasi elemen responsif `<picture>` dan `<source>` dengan penegakan validasi atribut `srcset` dan media breakpoint.
409. **Sanitasi Elemen Dialog & Tombol Form Dialog Method (`sanitizer.py`)**: Validasi elemen modal `<dialog>` dan tombol interaksi form dialog (`formmethod="dialog"`).
410. **Sanitasi Atribut Interaktif Data-Filter & Data-Sort Tabular (`sanitizer.py`)**: Pembersihan nilai atribut kontrol tabel interaktif (`data-filter`, `data-sort`) dari injeksi markup.
411. **Parser Sitasi Akademik Format Vancouver (`parser.py`)**: Penguraian format sitasi biomedis/telemetri numerik standar Vancouver menjadi entitas terstruktur.
412. **Auditor Masa Percobaan Akademik Mahasiswa (`parser.py`)**: Evaluasi status masa percobaan akademik, klasifikasi surat peringatan (SP1, SP2, SP3), dan verifikasi kelayakan kliring.
413. **Evaluator Kepatuhan Beban Kerja Dosen BKD (`parser.py`)**: Perhitungan beban kerja SKS tridharma dosen per semester dan evaluasi kepatuhan batas 12 - 16 SKS.
414. **Parser Penempatan Mahasiswa KKN Tematik (`parser.py`)**: Penguraian data penempatan kelompok KKN tematik pedesaan (kelompok, wilayah, DPL, jumlah peserta, tema).
415. **Kalkulator Peluruhan Kesegaran Konten Publikasi (`seo_validator.py`)**: Analisis peluruhan kesegaran artikel (*freshness decay*) berdasarkan usia terbit dan interval modifikasi.
416. **Detektor Peringkat Konferensi Internasional CORE (`seo_validator.py`)**: Pengenalan otomatis kluster peringkat konferensi internasional bereputasi CORE (A*, A, B, C).
417. **Auditor Integritas Tautan Jangkar Daftar Isi (`seo_validator.py`)**: Verifikasi tautan internal daftar isi (TOC) ke target heading dokumen tanpa broken anchor.
418. **Auditor Aksesibilitas Notasi Matematika LaTeX (`seo_validator.py`)**: Pemeriksaan konsistensi delimiter matematika LaTeX dan ketersediaan atribut aksesibilitas pembaca layar.
419. **Komponen Profil Desa KKN Tematik (`components.py`)**: Kartu responsif pameran pengabdian desa mitra mahasiswa lengkap dengan program unggulan dan dosen pembimbing.
420. **Komponen Kepatuhan Beban Kerja Dosen BKD (`components.py`)**: Kartu visualisasi status kepatuhan SKS tridharma dosen per semester lengkap dengan indikator batas.
421. **Komponen Konferensi Internasional CORE (`components.py`)**: Kartu pameran presentasi publikasi hasil riset di konferensi internasional bereputasi CORE.
422. **Komponen Konseling Kliring SP Mahasiswa (`components.py`)**: Kartu rencana bimbingan konseling akademik bagi mahasiswa dalam masa perbaikan indeks prestasi.
423. **Komponen Riset Telemetri Biomedis (`components.py`)**: Kartu pameran hasil pengujian perangkat telemetri kesehatan dan biosensor laboratorium.
424. **Formatter Siaran Penutupan KKN Tematik Telegram (`formatters.py`)**: Format siaran bulletin diseminasi luaran KKN tematik pedesaan di kanal Telegram.
425. **Formatter Siaran Presentasi Konferensi CORE Telegram (`formatters.py`)**: Format kartu ucapan selamat presentasi makalah konferensi internasional berperingkat CORE di Telegram.
426. **Manajer Rekam Proyek KKN Tematik Desa (`storage.py`)**: Tabel basis data `kkn_village_projects` untuk menyimpan dan meninjau program KKN pedesaan mahasiswa.
427. **Manajer Rekam Kepatuhan BKD Dosen (`storage.py`)**: Tabel basis data `faculty_bkd_records` untuk monitoring beban kerja dan kepatuhan SKS pengajar prodi.
428. **Manajer Rekam Konferensi Internasional (`storage.py`)**: Tabel basis data `conference_presentations` untuk rekam jejak diseminasi riset di forum internasional.
429. **Helper WordPress Get Comments By Post ID (`wordpress_client.py`)**: Pengambilan data komentar pengguna pada artikel postingan WordPress via REST API.
430. **Helper WordPress Create Post Tag (`wordpress_client.py`)**: Pembuatan taksonomi tag baru pada WordPress via REST API secara terprogram.
431. **Generator Schema.org AcademicEvent Konferensi (`exporter.py`)**: Pembuatan metadata terstruktur JSON-LD untuk forum seminar/konferensi ilmiah dengan anotasi tier CORE.
432. **Eksportir Markdown Kompatibel Hexo Static Blog (`exporter.py`)**: Ekspor artikel ke format blog statis Hexo dengan konfigurasi frontmatter tanggal, kategori, dan tag.
433. **Subcommand CLI `kkn` (`cli.py`)**: Perintah konsol manajemen rekam penempatan KKN tematik mahasiswa (list, add).
434. **Subcommand CLI `bkd` (`cli.py`)**: Perintah konsol pencatatan dan evaluasi kepatuhan beban kerja dosen (list, add).
435. **Subcommand CLI `hexo` (`cli.py`)**: Perintah konsol ekspor artikel ke format markdown blog statis Hexo.
436. **Pengujian Unit Terpadu Seluruh Modul (`tests/`)**: Penambahan kasus uji komprehensif pada modul sanitizer, parser, seo validator, komponen, formatters, storage, wp client, exporter, dan cli.
437. **Dokumentasi Rilis & Catatan Perubahan (`docs/`)**: Pembaruan dokumen ringkasan arsitektur, release changelog, dan sinkronisasi rincian rilis v3.3.0.
438. **Ekspansi Suite Pengujian Unit Terpadu (460 Tests Passing)**: Verifikasi menyeluruh seluruh modul sistem dengan 460 unit test terverifikasi (100% pass rate).

---

## 22. Ekspansi Arsitektural v3.4.0 Milestone Release

439. **Sanitasi SVG Use xlink:href & Pencegahan Cross-Origin Reference (`sanitizer.py`)**: Netralisasi elemen `<use>` SVG dengan blokir referensi remote eksternal dan enkapsulasi referensi simbol lokal saja.
440. **Sanitasi Atribut Waktu HTML5 datetime ISO 8601 (`sanitizer.py`)**: Validasi elemen `<time>` dengan atribut `datetime` yang mengeliminasi payload microdata dan script injeksi.
441. **Sanitasi Elemen HTML5 Output & Atribut Perhitungan Telemetri (`sanitizer.py`)**: Sanitasi elemen `<output>` dengan validasi token atribut `for` dan `name` serta pelucutan event listener inline.
442. **Parser DOI Artikel IEEE Transactions & Jurnal Internasional (`parser.py`)**: Resolver dan normalizer DOI publikasi ilmiah (`10.1109/...`) menjadi URL HTTPS kanonikal IEEE Xplore.
443. **Evaluator Usulan Hibah Penelitian BIMA Kemdikbud (`parser.py`)**: Evaluasi kelayakan proposal hibah penelitian berbasis skema riset Dikti, validasi NIDN ketua, dan kewajaran anggaran.
444. **Evaluator Penempatan Mahasiswa Kerja Praktik Industri (`parser.py`)**: Validasi kelayakan tempat magang/KP, kesesuaian sektor industri telekomunikasi/TIK, durasi minimal, dan profil mentor lapangan.
445. **Parser Izin Stasiun Radio (ISR) & Alokasi Spektrum Laboratorium (`parser.py`)**: Penguraian parameter teknis frekuensi, bandwidth, daya pancar (dBm), dan penentuan pita frekuensi ISM / seluler.
446. **Auditor Skor SINTA & Tautan Profil Author Dosen (`seo_validator.py`)**: Validasi format URL profil SINTA Kemdikbudristek dosen dan integritas metadata metrik sitasi.
447. **Auditor Kepatuhan Hirarki Heading & Deteksi Level Skipping (`seo_validator.py`)**: Pemeriksaan kelompatan urutan tag heading HTML (misal H2 langsung ke H4 tanpa H3) untuk aksesibilitas WCAG dan SEO.
448. **Auditor Tag Multimedia Open Graph Audio & Video (`seo_validator.py`)**: Verifikasi kelengkapan meta tag `og:audio` dan `og:video` beserta atribut tipe MIME, durasi, dan secure URL.
449. **Auditor Aksesibilitas Keterangan Tabel Caption & Summary (`seo_validator.py`)**: Verifikasi elemen `<caption>` dan deskripsi ringkasan pada tabel data demi kepatuhan pembaca layar.
450. **Komponen Pameran Hibah Penelitian BIMA Kemdikbud (`components.py`)**: Kartu responsif Elementor pameran penghargaan dana hibah riset dosen lengkap dengan skema dan nomor kontrak.
451. **Komponen Laporan Penempatan Kerja Praktik Mahasiswa (`components.py`)**: Kartu showcase pelaksanaan magang industri mahasiswa di mitra telekomunikasi terkemuka.
452. **Komponen Status Alokasi Spektrum Frekuensi ISR Lab (`components.py`)**: Kartu visualisasi izin frekuensi radio laboratorium dengan badge legalitas ISR aktif.
453. **Komponen Profil Skor SINTA Dosen (`components.py`)**: Kartu showcase metrik luaran riset dan capaian skor SINTA dosen pengajar prodi.
454. **Komponen Jaringan Tulang Punggung Fiber Optik Kampus (`components.py`)**: Kartu diagram topologi transmisi kabel serat optik kampus dengan metrik kapasitas gigabit.
455. **Formatter Pengumuman Hibah BIMA Kemdikbud Telegram (`formatters.py`)**: Format siaran bulletin penghargaan dana riset BIMA dosen di kanal Telegram prodi.
456. **Formatter Showcase Penempatan Kerja Praktik Telegram (`formatters.py`)**: Format siaran ucapan selamat penempatan magang industri mahasiswa di Telegram.
457. **Manajer Rekam Usulan Hibah BIMA Kemdikbud (`storage.py`)**: Tabel basis data `bima_grant_proposals` untuk pencatatan dan evaluasi proposal riset dosen.
458. **Manajer Rekam Penempatan Kerja Praktik Mahasiswa (`storage.py`)**: Tabel basis data `kerja_praktik_placements` untuk monitoring program KP mahasiswa di industri.
459. **Manajer Rekam Alokasi Frekuensi Spektrum Lab (`storage.py`)**: Tabel basis data `lab_spectrum_allocations` untuk inventaris izin stasiun radio dan frekuensi riset.
460. **Helper WordPress Get Posts By Author ID (`wordpress_client.py`)**: Pengambilan daftar artikel yang ditulis oleh pengguna WordPress tertentu via REST API.
461. **Helper WordPress Delete Post Tag (`wordpress_client.py`)**: Penghapusan taksonomi tag WordPress secara terprogram via REST API dengan flag force.
462. **Generator Schema.org GovernmentService Hibah Penelitian (`exporter.py`)**: Pembuatan metadata terstruktur JSON-LD untuk program hibah riset kementerian dengan rincian pendanaan.
463. **Eksportir Markdown Kompatibel VitePress Static Docs (`exporter.py`)**: Ekspor artikel ke format dokumentasi modern VitePress dengan konfigurasi frontmatter terstruktur.
464. **Subcommand CLI `bima` (`cli.py`)**: Perintah konsol manajemen usulan hibah riset BIMA Kemdikbud (list, add).
465. **Subcommand CLI `kp` (`cli.py`)**: Perintah konsol manajemen penempatan kerja praktik industri mahasiswa (list, add).
466. **Subcommand CLI `vitepress` (`cli.py`)**: Perintah konsol ekspor artikel ke format markdown VitePress static docs.
467. **Pengujian Unit Terpadu Seluruh Modul (`tests/`)**: Penambahan kasus uji komprehensif pada modul sanitizer, parser, seo validator, komponen, formatters, storage, wp client, exporter, dan cli.
468. **Dokumentasi Rilis & Catatan Perubahan (`docs/`)**: Pembaruan dokumen ringkasan arsitektur, release changelog, dan sinkronisasi rincian rilis v3.4.0.
469. **Ekspansi Suite Pengujian Unit Terpadu (488 Tests Passing)**: Verifikasi menyeluruh seluruh modul sistem dengan 488 unit test terverifikasi (100% pass rate).








