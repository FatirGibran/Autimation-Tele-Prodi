# Dokumentasi Perubahan Arsitektur v3.2.0 Milestone Release

Siklus pengembangan v3.2.0 Milestone Architectural Release menghadirkan ekspansi arsitektural menyeluruh pada ekosistem otomasi editorial:
- **Sanitasi Media & Keamanan DOM Lanjutan**: Sanitasi elemen audio dan subtitle/caption HTML5 (`<audio>`, `<track>`), sanitasi elemen tipografi komputasi (`<kbd>`, `<samp>`), serta pengamanan atribut tooltip posisi kontekstual (`data-tooltip`, `data-placement`) dari injeksi markup.
- **Parser Standar Akademik & Tata Kelola Kampus**: Parser sitasi rujukan akademik format Harvard (*author-date*), validator konversi dan ekuivalensi transfer kredit program MBKM, parser log inventaris dan audit kalibrasi instrumen lab, serta validator kelayakan clearance yudisium kelulusan mahasiswa.
- **Auditor SEO & Standar Pengindeksan Web**: Auditor aksesibilitas transkrip audio/video (WCAG), detektor kuartil reputasi jurnal SCImago Journal Rank (SJR Q1-Q4), auditor tag multibahasa `hreflang`, serta auditor kedalaman dan integritas hierarki semantik breadcrumb.
- **Komponen Semantik Elementor Responsif**: Kartu pemetaan ekuivalensi konversi SKS MBKM, kartu sertifikat clearance kelulusan yudisium sarjana, kartu showcase makalah jurnal internasional terindeks Scopus, kartu jadwal kalibrasi alat lab, serta kartu profil visiting professor dan dosen tamu internasional.
- **Format Pesan Telegram**: Format siaran ucapan selamat kelulusan yudisium sarjana dan format siaran kuliah tamu internasional prodi.
- **Pengembangan Storage & Basis Data**: Tabel rekam konversi kredit MBKM (`mbkm_credit_transfers`), tabel rekam clearance kelulusan yudisium (`yudisium_clearances`), serta tabel riwayat kalibrasi peralatan lab (`lab_equipment_calibrations`).
- **Klien WordPress REST API**: Helper perolehan data media lampiran berdasarkan ID (`get_media_by_id`) dan helper perolehan informasi pengaturan situs (`get_site_settings`).
- **Generator Statis & Ekspor**: Generator Schema.org `EducationalOccupationalCredential` JSON-LD untuk ijazah dan sertifikasi kompetensi, serta eksportir markdown kompatibel generator situs dokumentasi Astro Starlight (`to_starlight_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `mbkm`, `yudisium`, dan `starlight`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 404 menjadi 433 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Audio & Track HTML5 (`sanitizer.py`)**:
   - Memvalidasi elemen `<audio>` dan `<track>` serta memblokir skema URI berbahaya (`javascript:`, `data:`) pada atribut `src`.

2. **Sanitasi Tipografi Komputasi Kbd & Samp (`sanitizer.py`)**:
   - Menjaga kebersihan elemen keyboard shortcuts (`<kbd>`) dan output terminal (`<samp>`) dari injeksi script.

3. **Sanitasi Tooltip Kontekstual Data-Tooltip (`sanitizer.py`)**:
   - Membersihkan atribut `data-tooltip`, `data-title`, dan `data-placement` dari tag HTML berbahaya atau event handler terselubung.

4. **Parser Sitasi Akademik Format Harvard (`parser.py`)**:
   - Mengurai format sitasi rujukan akademik Harvard (*author-date*) menjadi entitas terstruktur (penulis, tahun, judul artikel, jurnal, volume, edisi, dan rentang halaman).

5. **Validator Konversi Kredit Program MBKM (`parser.py`)**:
   - Memvalidasi kepatuhan mata kuliah konversi MBKM (maksimal SKS, kecocokan CPL, dan verifikasi silabus mitra).

6. **Parser Log Inventaris & Kalibrasi Alat Lab (`parser.py`)**:
   - Mengurai riwayat kalibrasi peralatan pengukuran laboratorium (nama alat, nomor seri, institusi kalibrator, tanggal kedaluwarsa sertifikat, dan deviasi toleransi).

7. **Validator Clearance Yudisium Kelulusan (`parser.py`)**:
   - Memvalidasi kelayakan administrasi mahasiswa menjelang yudisium (pemenuhan 144 SKS, IPK minimal, nilai kelulusan tugas akhir, bebas tanggungan perpustakaan, dan sertifikat TOEFL/EPR).

8. **Auditor Aksesibilitas Transkrip Media Audio/Video (`seo_validator.py`)**:
   - Memverifikasi keberadaan transkrip teks dan subtitle pendukung untuk seluruh elemen `<audio>` dan `<video>` sesuai panduan WCAG 2.1 level AA.

9. **Detektor Kuartil SCImago Journal Rank SJR (`seo_validator.py`)**:
   - Mengidentifikasi kluster reputasi jurnal internasional bereputasi (Q1, Q2, Q3, Q4) berdasarkan metrik kutipan SJR.

10. **Auditor Tag Multibahasa Hreflang (`seo_validator.py`)**:
    - Memeriksa keabsahan kode bahasa/wilayah ISO 639-1 dan format tag link rel alternate `hreflang` guna memastikan akurasi targeting internasional mesin pencari.

11. **Auditor Kedalaman Hierarki Breadcrumb (`seo_validator.py`)**:
    - Memvalidasi struktur navigasi rekam jejak semantik breadcrumb agar tidak melebihi kedalaman optimal dan bebas dari rantai loop navigasi.

12. **Komponen Pemetaan Ekuivalensi Kredit MBKM (`components.py`)**:
    - Kartu responsif konversi mata kuliah program Magang dan Studi Independen Bersertifikat (MSIB) ke kurikulum prodi.

13. **Komponen Sertifikat Clearance Yudisium (`components.py`)**:
    - Kartu verifikasi kelulusan sarjana dengan kode verifikasi ijazah digital dan predikat kelulusan (*Cumlaude*).

14. **Komponen Showcase Makalah Jurnal Scopus (`components.py`)**:
    - Kartu publikasi hasil penelitian dosen dan mahasiswa pada jurnal terindeks Scopus lengkap dengan nilai kuartil SJR dan tautan DOI.

15. **Komponen Kalibrasi Alat Laboratorium (`components.py`)**:
    - Kartu rekam status kelayakan uji ukur peralatan praktikum (Spectrum Analyzer, Optical Time-Domain Reflectometer, Vector Network Analyzer).

16. **Komponen Dosen Tamu & Visiting Professor (`components.py`)**:
    - Kartu profil narasumber akademik internasional beserta institusi asal dan topik kuliah pakar.

17. **Formatter Siaran Yudisium Kelulusan Telegram (`formatters.py`)**:
    - Penataan format pesan ucapan selamat yudisium sarjana teknik untuk kanal publikasi Telegram resmi prodi.

18. **Formatter Siaran Kuliah Tamu Internasional Telegram (`formatters.py`)**:
    - Penataan format siaran undangan kuliah pakar internasional untuk kanal Telegram prodi.

19. **Manajer Rekam Konversi MBKM (`storage.py`)**:
    - Manajemen basis data SQLite tabel `mbkm_credit_transfers` untuk pelacakan SKS dan IPK hasil rekognisi MBKM mahasiswa.

20. **Manajer Rekam Clearance Yudisium (`storage.py`)**:
    - Tabel `yudisium_clearances` dan pencatatan verifikasi status kelulusan mahasiswa sarjana.

21. **Manajer Riwayat Kalibrasi Lab (`storage.py`)**:
    - Tabel `lab_equipment_calibrations` untuk monitoring masa berlaku kalibrasi peralatan riset.

22. **Helper WordPress Get Media By ID (`wordpress_client.py`)**:
    - Perolehan detail lampiran media (URL, alt text, MIME type) berdasarkan ID media via REST API WordPress.

23. **Helper WordPress Get Site Settings (`wordpress_client.py`)**:
    - Perolehan informasi konfigurasi situs (nama situs, timezone, URL endpoint) via REST API WordPress.

24. **Generator Schema.org EducationalOccupationalCredential (`exporter.py`)**:
    - Konstruksi schema terstruktur untuk gelar sarjana, ijazah, dan sertifikasi profesi keahlian teknik.

25. **Generator Markdown Kompatibel Astro Starlight (`exporter.py`)**:
    - Ekspor artikel ke format Astro Starlight static documentation generator dengan konfigurasi hierarki sidebar otomatis.

26. **Subcommand CLI `mbkm` (`cli.py`)**:
    - Perintah konsol pencatatan dan peninjauan rekognisi konversi kredit MBKM mahasiswa (list, add).

27. **Subcommand CLI `yudisium` (`cli.py`)**:
    - Perintah konsol manajemen kelulusan yudisium dan verifikasi status kelulusan (list, add, check).

28. **Subcommand CLI `starlight` (`cli.py`)**:
    - Perintah konsol ekspor artikel ke format markdown Astro Starlight.

29. **Ekspansi Suite Pengujian Unit Terpadu (433 Tests Passing)**:
    - 433 unit tests terverifikasi dengan tingkat kelulusan 100% tanpa kegagalan regresi.
