# Dokumentasi Perubahan Arsitektur v3.5.0 Milestone Release

Siklus pengembangan v3.5.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Telemetri**: Sanitasi elemen `<track>` subtitle dan keterangan video HTML5 dengan validasi file `.vtt`, sanitasi elemen kode `<kbd>` dan `<samp>` untuk dokumentasi teknis telemetri, serta sanitasi elemen `<data>` dengan validasi token nilai yang terbaca mesin (*machine-readable tokens*).
- **Parser Standar Akademik & Regulasi Telekomunikasi**: Parser status akreditasi program studi LAM INFOKOM dan BAN-PT, parser alokasi bantuan beasiswa mahasiswa, kalkulator link budget atenuasi loss transmisi serat optik (*optical fiber link budget*), serta parser sertifikat paten granted DJKI Kemenkumham RI.
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut**: Auditor duplikasi tag title dan meta description, auditor kepatuhan direktif meta tag `robots` dan `googlebot`, auditor aksesibilitas video HTML5 dan ketersediaan closed caption / subtitle, serta auditor rasio perbandingan teks terhadap kode HTML bloat.
- **Komponen Semantik Elementor Responsif**: Kartu status akreditasi LAM INFOKOM program studi, kartu pameran alokasi beasiswa pendidikan mahasiswa, kartu kalkulasi link budget transmisi serat optik, kartu sertifikat paten granted DJKI Kemenkumham, serta kartu sertifikasi kompetensi kejuruan BNSP telekomunikasi mahasiswa.
- **Format Pesan Telegram**: Format siaran bulletin perolehan akreditasi Unggul LAM INFOKOM dan format siaran pengumuman alokasi beasiswa mahasiswa.
- **Pengembangan Storage & Basis Data**: Tabel rekam akreditasi prodi (`study_program_accreditations`), tabel alokasi beasiswa mahasiswa (`student_scholarships`), serta tabel sertifikasi kompetensi kejuruan BNSP mahasiswa (`bnsp_certifications`).
- **Klien WordPress REST API**: Helper pencarian pustaka media berbasis kata kunci (`search_media`) dan helper pembaruan status moderasi komentar (`update_comment_status`).
- **Generator Statis & Ekspor**: Generator Schema.org `FinancialAssistance` JSON-LD untuk program bantuan biaya pendidikan dan beasiswa, serta eksportir markdown kompatibel generator blog statis Jekyll (`to_jekyll_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `accreditation`, `scholarship`, dan `jekyll`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 488 menjadi 516 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Track Subtitle (`sanitizer.py`)**:
   - Memvalidasi elemen `<track>` pada video, memastikan ekstensi aman `.vtt`, membatasi jenis trek (`subtitles`, `captions`, `descriptions`), dan membuang skrip manipulasi sumber media.

2. **Sanitasi Elemen Dokumentasi Teknis KBD & SAMP (`sanitizer.py`)**:
   - Membersihkan elemen input keyboard `<kbd>` dan sampel keluaran mesin `<samp>` dari atribut event handler berbahaya pada dokumentasi teknis lab.

3. **Sanitasi Elemen Data Token Mesin (`sanitizer.py`)**:
   - Menjaga integritas elemen `<data>` dengan memvalidasi atribut `value` numerik atau token baku untuk interoperabilitas telemetri.

4. **Parser Status Akreditasi Prodi LAM INFOKOM & BAN-PT (`parser.py`)**:
   - Mengurai peringkat akreditasi (Unggul, Baik Sekali, Baik), nomor SK penetapan, skor asesmen, dan masa berlaku legalitas program studi.

5. **Parser Alokasi Bantuan Beasiswa Mahasiswa (`parser.py`)**:
   - Mengurai penerima bantuan biaya pendidikan dari berbagai sumber (pemerintah KIP-Kuliah, industri telco, ikatan alumni, internal yayasan).

6. **Kalkulator Link Budget Atenuasi Serat Optik (`parser.py`)**:
   - Menghitung total peredaman saluran serat optik (redaman kabel dB/km, sambungan splice, konektor transmisi, serta margin pengaman sistem).

7. **Parser Sertifikat Paten Terdaftar & Granted DJKI (`parser.py`)**:
   - Mengurai sertifikat paten teknologi DJKI Kemenkumham RI, nomor permohonan, nomor paten IDS resmi, susunan inventor, dan tanggal perlindungan hukum.

8. **Auditor Duplikasi Tag Title & Meta Description (`seo_validator.py`)**:
   - Mendeteksi adanya duplikasi deklarasi tag `<title>` dan `<meta name="description">` dalam dokumen HTML tunggal.

9. **Auditor Kepatuhan Direktif Robots Meta Tag (`seo_validator.py`)**:
   - Memeriksa direktif pengindeksan mesin pencari pada tag `<meta name="robots">` (seperti `noindex`, `nofollow`, `noarchive`, `nosnippet`).

10. **Auditor Aksesibilitas Video & Closed Caption HTML5 (`seo_validator.py`)**:
    - Memverifikasi keberadaan track subtitle/closed-captioning pada pemutar video HTML5 untuk kepatuhan pedoman aksesibilitas konten web WCAG.

11. **Auditor Rasio Teks terhadap Kode HTML Bloat (`seo_validator.py`)**:
    - Menganalisis proporsi persentase teks murni terhadap ukuran kode markup HTML guna mencegah penurunan performa rendering dan pemborosan crawl budget.

12. **Komponen Akreditasi LAM INFOKOM Prodi (`components.py`)**:
    - Kartu presentasi legalitas akreditasi program studi dengan badge reputasi Unggul dan rincian SK BAN-PT/LAM INFOKOM.

13. **Komponen Pameran Alokasi Beasiswa Mahasiswa (`components.py`)**:
    - Kartu showcase mahasiswa penerima beasiswa prestasi dan bantuan biaya kuliah industri telekomunikasi.

14. **Komponen Kalkulasi Link Budget Serat Optik (`components.py`)**:
    - Kartu ringkasan kalkulasi redaman saluran optik lengkap dengan visualisasi margin daya transmisi.

15. **Komponen Sertifikat Paten Granted DJKI (`components.py`)**:
    - Kartu pameran luaran kekayaan intelektual (HKI) paten dosen dan mahasiswa dengan nomor sertifikat resmi.

16. **Komponen Sertifikasi Kompetensi BNSP Mahasiswa (`components.py`)**:
    - Kartu sertifikasi kompetensi profesi LSP BNSP bidang teknisi serat optik dan jaringan seluler.

17. **Format Pengumuman Telegram Akreditasi Prodi (`formatters.py`)**:
    - Template pesan siaran resmi Telegram pengumuman status akreditasi Unggul program studi.

18. **Format Pengumuman Telegram Beasiswa Mahasiswa (`formatters.py`)**:
    - Template pesan siaran Telegram pengumuman kelulusan seleksi dan alokasi dana beasiswa pendidikan.

19. **Manajemen Akreditasi Prodi di Penyimpanan SQLite (`storage.py`)**:
    - Skema tabel `study_program_accreditations` dan operasi CRUD untuk pengarsipan riwayat akreditasi jurusan.

20. **Manajemen Rekam Beasiswa Mahasiswa di Storage (`storage.py`)**:
    - Skema tabel `student_scholarships` untuk pencatatan riwayat distribusi bantuan beasiswa mahasiswa.

21. **Manajemen Sertifikasi BNSP Mahasiswa di Storage (`storage.py`)**:
    - Skema tabel `bnsp_certifications` untuk pendataan kompetensi profesi lulusan dan mahasiswa.

22. **Pencarian Pustaka Media WordPress REST API (`wordpress_client.py`)**:
    - Metode `search_media` untuk memudahkan pencarian ID berkas media gambar diagram dan sertifikat.

23. **Pembaruan Status Komentar WordPress (`wordpress_client.py`)**:
    - Metode `update_comment_status` untuk moderasi interaktif komentar publik pada portal prodi.

24. **Generator Schema.org FinancialAssistance JSON-LD (`exporter.py`)**:
    - Penyusunan metadata terstruktur Schema.org `FinancialAssistance` untuk transparansi beasiswa akademik.

25. **Eksportir Blog Statis Jekyll Markdown (`exporter.py`)**:
    - Fungsi `to_jekyll_markdown` yang menghasilkan berkas markdown siap publikasi pada static engine Jekyll.

26. **Subcommand CLI Akreditasi, Beasiswa, dan Jekyll (`cli.py`)**:
    - Perintah CLI `accreditation`, `scholarship`, dan `jekyll` terintegrasi pada alur kerja otomatisasi prodi.
