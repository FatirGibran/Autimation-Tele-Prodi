# Dokumentasi Perubahan Arsitektur v3.7.0 Milestone Release

Siklus pengembangan v3.7.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Template HTML5**: Sanitasi elemen modal `<dialog>` dengan penegakan atribut aksesibilitas, sanitasi elemen pengungkapan interaktif `<details>` dan `<summary>`, serta pembersihan aman elemen `<template>` dan pencegahan declarative shadow DOM script injection.
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Evaluator seleksi program magister akselerasi fast-track S1 + S2 (`parse_fast_track_eligibility`), kalkulator Optical Signal-to-Noise Ratio (OSNR) dan Bit Error Rate (BER) transmisi serat optik DWDM (`calculate_optical_snr_and_ber`), evaluator kepatuhan kalibrasi peralatan lab ISO/IEC 17025 (`parse_lab_equipment_calibration`), serta parser sertifikat Hak Cipta / HKI DJKI Kemenkumham RI (`parse_lecturer_hki_copyright`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1)**: Auditor aksesibilitas tabel data (`audit_table_accessibility`), auditor asosiasi label dan atribut autocomplete formulir identitas (`audit_form_labels_and_autocomplete`), auditor deklarasi bahasa dan arah pembacaan konten (`audit_content_language_and_direction`), serta auditor aksesibilitas inline SVG title/desc (`audit_svg_inline_accessibility`).
- **Komponen Semantik Elementor Responsif**: Kartu showcase mahasiswa fast-track magister (`render_fast_track_program_card`), kartu kalkulasi OSNR dan BER serat optik DWDM (`render_optical_osnr_ber_card`), kartu sertifikat kalibrasi instrumen lab RF (`render_lab_equipment_calibration_card`), kartu pameran sertifikat hak cipta HKI dosen (`render_hki_copyright_certificate_card`), serta kartu interaktif pengungkapan informasi akademik aksesibel (`render_accessible_disclosure_card`).
- **Format Pesan Telegram**: Format buletin Telegram pengumuman kelolosan seleksi fast-track (`format_fast_track_announcement_telegram`) dan format buletin pengumuman pencatatan HKI Kemenkumham (`format_hki_copyright_announcement_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel rekam mahasiswa fast-track magister (`fast_track_students`), tabel kepatuhan kalibrasi lab (`lab_calibration_compliance`), serta tabel pencatatan HKI kekayaan intelektual dosen (`lecturer_hki_records`).
- **Klien WordPress REST API**: Helper pemindahan massal postingan ke tempat sampah (`bulk_trash_posts`) dan helper perolehan pengaturan global situs WordPress (`get_site_settings`).
- **Generator Statis & Ekspor**: Generator Schema.org `EducationalOccupationalCredential` JSON-LD (`generate_educational_credential_json_ld`) serta eksportir markdown Astro Starlight dengan frontmatter sidebar order dan badge (`to_astro_starlight_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `fast-track`, `calibration`, dan `hki`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 544 menjadi 570 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Dialog & Aksesibilitas Modal (`sanitizer.py`)**:
   - Memvalidasi elemen `<dialog>` HTML5, mengizinkan atribut `open`, `aria-modal`, dan membersihkan atribut injeksi event handler.

2. **Sanitasi Elemen HTML5 Details Summary Disclosure (`sanitizer.py`)**:
   - Membersihkan elemen interaktif `<details>` dan `<summary>` dengan mencegah eksploitasi atribut inline.

3. **Sanitasi Elemen HTML5 Template (`sanitizer.py`)**:
   - Membersihkan isi elemen `<template>` sembari menetralisasi skrip berbahaya dan declarative shadow DOM injection.

4. **Evaluator Seleksi Mahasiswa Program Magister Fast-Track (`parser.py`)**:
   - Memvalidasi prasyarat IPK (>= 3.50), jumlah SKS lulus (>= 120 SKS), dan skor TOEFL (>= 475) untuk program akselerasi S1 + S2.

5. **Kalkulator OSNR & Bit Error Rate Serat Optik DWDM (`parser.py`)**:
   - Menghitung Optical Signal-to-Noise Ratio (OSNR) dalam skala dB, faktor kualitas Q, dan estimasi BER komplementer.

6. **Parser Kepatuhan Kalibrasi Instrumen Laboratorium ISO/IEC 17025 (`parser.py`)**:
   - Mengurai masa berlaku kalibrasi peralatan telekomunikasi, sisa hari aktif, status (Valid/Due Soon/Expired), dan rekomendasi tindak lanjut.

7. **Parser Pendaftaran Hak Cipta / HKI Dosen Kemenkumham RI (`parser.py`)**:
   - Mengurai nomor pencatatan, jenis ciptaan, pencipta, validitas format DJKI, serta mengalkulasi poin rubrik BKD/SINTA.

8. **Auditor Aksesibilitas Tabel Data WCAG 2.1 (`seo_validator.py`)**:
   - Memeriksa keberadaan `<caption>` atau `aria-label`/`aria-labelledby` serta penegakan atribut `scope="col"` atau `scope="row"` pada tag `<th>`.

9. **Auditor Asosiasi Label & Autocomplete Formulir (`seo_validator.py`)**:
   - Memverifikasi keterkaitan eksplisit elemen `<label for="...">` dengan input ID dan keberadaan atribut `autocomplete` pada input identitas pengguna.

10. **Auditor Deklarasi Bahasa & Arah Teks Konten (`seo_validator.py`)**:
    - Memverifikasi deklarasi kode bahasa `lang` (ISO 639-1) dan arah pembacaan `dir` (`ltr` atau `rtl`).

11. **Auditor Aksesibilitas Inline SVG Title & Desc (`seo_validator.py`)**:
    - Memeriksa elemen `<title>` pendamping atau atribut `aria-label` serta peranan `role="img"` pada elemen grafis `<svg>` inline.

12. **Komponen Pengakuan Mahasiswa Fast-Track Magister (`components.py`)**:
    - Kartu visual Elementor mahasiswa berprestasi terpilih program akselerasi S1 + S2.

13. **Komponen Kalkulasi OSNR & Bit Error Rate Serat Optik (`components.py`)**:
    - Kartu kalkulasi teknis tautan serat optik berkecepatan tinggi dengan parameter sinyal, derau, laju data, dan BER.

14. **Komponen Sertifikat Kalibrasi Alat Lab RF (`components.py`)**:
    - Kartu pemenuhan standar mutu dan kalibrasi alat ukur lab telekomunikasi terakreditasi ISO/IEC 17025.

15. **Komponen Showcase Sertifikat Hak Cipta Dosen (`components.py`)**:
    - Kartu showcase sertifikat pencatatan Hak Cipta resmi DJKI Kemenkumham RI.

16. **Komponen Kartu Pengungkapan Interaktif Aksesibel (`components.py`)**:
    - Kartu FAQ dan pedoman akademik berbasis elemen interaktif `<details>` dan `<summary>` dengan styling modern terisolasi.

17. **Formatter Telegram Seleksi Fast-Track (`formatters.py`)**:
    - Template buletin resmi Telegram ucapan selamat dan informasi kelolosan seleksi fast-track magister.

18. **Formatter Telegram Hak Cipta HKI Kemenkumham (`formatters.py`)**:
    - Template pengumuman resmi Telegram penerbitan sertifikat Hak Cipta Kemenkumham.

19. **Manajer Rekam Mahasiswa Fast-Track Magister (`storage.py`)**:
    - Skema tabel `fast_track_students` dan metode `record_fast_track_student`, `list_fast_track_students`, `get_fast_track_student_by_nim`.

20. **Manajer Rekam Kepatuhan Kalibrasi Laboratorium (`storage.py`)**:
    - Skema tabel `lab_calibration_compliance` dan metode `record_lab_calibration_compliance`, `list_lab_calibration_compliance`, `get_lab_calibration_by_serial`.

21. **Manajer Rekam Hak Cipta / HKI Dosen (`storage.py`)**:
    - Skema tabel `lecturer_hki_records` dan metode `record_lecturer_hki`, `list_lecturer_hki_records`, `get_lecturer_hki_by_reg_number`.

22. **Helper WordPress Bulk Trash Posts (`wordpress_client.py`)**:
    - Metode `bulk_trash_posts` untuk memindahkan banyak postingan ke tempat sampah secara terprogram.

23. **Helper WordPress Get Site Settings (`wordpress_client.py`)**:
    - Metode `get_site_settings` untuk membaca konfigurasi judul, deskripsi, timezone, dan URL situs WordPress.

24. **Generator Schema.org EducationalOccupationalCredential JSON-LD (`exporter.py`)**:
    - Metode `generate_educational_credential_json_ld` untuk standarisasi sertifikasi kompetensi dan kredensial akademik.

25. **Eksportir Markdown Astro Starlight SSG (`exporter.py`)**:
    - Metode `to_astro_starlight_markdown` untuk transformasi artikel ke format dokumentasi Astro Starlight dengan konfigurasi frontmatter sidebar.

26. **Subcommand CLI `fast-track` (`cli.py`)**:
    - Perintah konsol `fast-track` untuk mencatat dan menampilkan daftar kandidat program magister fast-track.

27. **Subcommand CLI `calibration` (`cli.py`)**:
    - Perintah konsol `calibration` untuk mencatat dan memantau jatuh tempo kalibrasi alat lab telekomunikasi.

28. **Subcommand CLI `hki` (`cli.py`)**:
    - Perintah konsol `hki` untuk mencatat dan menginventarisasi sertifikat hak cipta dosen.

29. **Peningkatan Suite Pengujian Unit (570 Tests Passing)**:
    - Seluruh modul teruji dengan 570 unit test tanpa error dan tanpa kegagalan (100% pass rate).
