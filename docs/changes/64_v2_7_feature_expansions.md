# Dokumentasi Perubahan Arsitektur v2.7.0

Siklus pengembangan v2.7.0 memperluas kapabilitas otomasi editorial prodi melalui:
- Sanitasi elemen dialog/modal HTML5, stripping animasi/font SVG berbahaya, dan penegakan gambar responsif `<picture>`/`<source>`.
- Parser rencana studi semester kurikulum (RPS), peringatan keselamatan lab, validasi nomor identifikasi bibliografi (ISBN/ISSN), dan rentang tanggal kalender akademik Indonesia.
- Auditor heading skip level SEO, matcher kata kunci berimbuhan morfologi Indonesia, validator aspek rasio Twitter card, dan integrasi readability score ke Yoast SEO audit result.
- Komponen semantic kartu Capaian Pembelajaran Lulusan (CPL), kartu mitra magang industri, kartu realisasi anggaran hibah riset, kartu buku teks wajib perpustakaan, dan statistik tracer study lulusan.
- Formatter Telegram pengingat registrasi CFP konferensi ilmiah dan siaran fast-breaking prestasi mahasiswa juara hackathon.
- Pencatatan time-series log tayangan artikel (`article_view_logs`), manajer penugasan tugas editorial (`editorial_tasks`), dan metadata taksonomi istilah (`taxonomy_meta`).
- Helper sticky toggle dan filter query media berdasar MIME type pada WordPress REST API client.
- Generator JSON-LD CollegeOrUniversity Schema.org dan eksportir markdown template Eleventy (11ty).
- Subcommand CLI `task`, `view-stats`, dan `eleventy`.
- Skrip audit hyperlink lokal `#fragment` dan kepatuhan protokol HTTPS internal (`scripts/check_hyperlinks.py`).
- Suite pengujian unit yang bertumbuh dari 263 tes menjadi 291 tes lulus terverifikasi (100% pass rate).

## Rincian Fitur Utama yang Ditambahkan:
1. **Sanitasi Semantic Modal & Dialog HTML5 (`sanitizer.py`)**:
   - Penegakan atribut dan kelas semantik pada elemen `<dialog>` serta netralisasi backdrop script.
2. **Stripping Tag Animasi & Font SVG Berbahaya (`sanitizer.py`)**:
   - Penghapusan elemen manipulatif `<animate>`, `<set>`, `<font-face>` pada aset grafik SVG inline.
3. **Sanitasi Art-Direction Gambar Responsif (`sanitizer.py`)**:
   - Sanitasi elemen `<picture>` dan `<source>` dengan penegakan tipe MIME dan protokol HTTPS aman.
4. **Parser Rencana Studi Semester Kurikulum (`parser.py`)**:
   - Ekstraksi dan pengelompokan mata kuliah semester ganjil/genap dari format teks dan tabel markdown.
5. **Parser Peringatan Keselamatan Laboratorium Komputasi (`parser.py`)**:
   - Konversi format panduan K3 dan regulasi keselamatan lab komputer menjadi blok admonition terstruktur.
6. **Validator Nomor Identifikasi Bibliografi ISBN & ISSN (`parser.py`)**:
   - Verifikasi format ISBN-10, ISBN-13, dan ISSN internasional dengan checksum dan pembakuan strip.
7. **Parser Rentang Tanggal Kalender Akademik Indonesia (`parser.py`)**:
   - Ekstraksi format tanggal rentang formal bahasa Indonesia (misal: "12 - 24 Oktober 2026") menjadi rentang ISO.
8. **Auditor Heading Skip Level SEO (`seo_validator.py`)**:
   - Deteksi lompatan tingkat heading yang melanggar hierarki semantik (misal: H2 langsung lompat ke H4).
9. **Matcher Kata Kunci Morfologi & Imbuhan Bahasa Indonesia (`seo_validator.py`)**:
   - Pemeriksaan variasi kata kunci dengan prefiks (me-, di-, ber-, ter-, pe-, per-) dan sufiks (-kan, -i, -an).
10. **Validator Rasio Aspek Gambar Twitter Card (`seo_validator.py`)**:
    - Validasi rasio aspek gambar pratinjau media sosial Twitter summary card (rasio 1:1 dan 2:1).
11. **Adapter Readability Score ke Audit Yoast SEO (`seo_validator.py`)**:
    - Integrasi nilai skor keterbacaan Flesch-Kincaid bahasa Indonesia ke ringkasan audit Yoast.
12. **Komponen Kartu Capaian Pembelajaran Lulusan CPL (`components.py`)**:
    - Generator visualisasi kartu taksonomi CPL prodi lengkap dengan kode dan deskripsi capaian.
13. **Komponen Showcase Mitra Magang Industri (`components.py`)**:
    - Generator profil perusahaan mitra magang MBKM, lokasi kota, bidang industri, dan kuota posisi.
14. **Komponen Realisasi Anggaran Hibah Riset Dosen (`components.py`)**:
    - Visualisasi progress bar realisasi anggaran, skema pendanaan, dan milestone pengeluaran.
15. **Komponen Kartu Buku Teks Wajib Perpustakaan (`components.py`)**:
    - Kartu ketersediaan buku teks wajib mata kuliah dengan nomor panggil perpustakaan (call number).
16. **Komponen Statistik Tracer Study Lulusan (`components.py`)**:
    - Kartu ringkasan respon tracer study, rata-rata masa tunggu kerja, dan distribusi industri penyerapan kerja.
17. **Formatter Kartu Pengingat Call for Papers Konferensi Telegram (`formatters.py`)**:
    - Format pesan siaran batas akhir pengumpulan manuskrip konferensi ilmiah internasional.
18. **Formatter Siaran Prestasi Juara Mahasiswa Telegram (`formatters.py`)**:
    - Desain pesan siaran cepat (fast-breaking) keberhasilan mahasiswa memenangkan kompetisi hackathon nasional.
19. **Pencatatan Time-Series Tayangan Artikel (`storage.py`)**:
    - Tabel `article_view_logs` dan query agregasi harian performa artikel untuk analitik historis.
20. **Manajer Penugasan Editorial Artikel (`storage.py`)**:
    - Tabel `editorial_tasks` dan pelacakan alur kerja delegasi review, fact-checking, dan proofreading.
21. **Manajer Metadata Istilah Taksonomi (`storage.py`)**:
    - Tabel `taxonomy_meta` untuk penyimpanan atribut warna lencana, url banner, dan deskripsi kategori/tag.
22. **Helper Post Sticky Toggle WordPress REST API (`wordpress_client.py`)**:
    - Metode pengaktifan status sematan pos utama (pinned post) via API WordPress.
23. **Filter Query Media berdasarkan MIME Type WordPress (`wordpress_client.py`)**:
    - Metode penyaringan koleksi pustaka berkas berdasarkan prefiks tipe konten (`image/`, `application/pdf`).
24. **Generator Skema CollegeOrUniversity Schema.org (`exporter.py`)**:
    - Skema data terstruktur identitas institusi dan akreditasi untuk Google Knowledge Graph.
25. **Generator Markdown Kompatibel Eleventy (11ty) (`exporter.py`)**:
    - Ekspor artikel ke format SSG Eleventy dengan layout nunjucks dan penugasan permalink dinamis.
26. **Subcommand CLI `task` (`cli.py`)**:
    - Perintah konsol penugasan, pemantauan, dan pembaruan status tugas editorial tim prodi.
27. **Subcommand CLI `view-stats` (`cli.py`)**:
    - Perintah konsol visualisasi riwayat tayangan harian artikel berdasarkan ID database.
28. **Subcommand CLI `eleventy` (`cli.py`)**:
    - Perintah konsol konversi artikel langsung ke format markdown Eleventy SSG.
29. **Skrip Auditor Hyperlink & Anchor Target (`scripts/check_hyperlinks.py`)**:
    - Perkakas otomatisasi verifikasi tautan `#fragment` lokal, penegakan HTTPS internal, dan audit keamanan rel link.
30. **Ekspansi Suite Pengujian Unit Terpadu (291 Tests Passing)**:
    - Verifikasi penuh 291 unit test tanpa kegagalan (100% pass rate) pada seluruh modul arsitektur.
