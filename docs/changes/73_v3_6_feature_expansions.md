# Dokumentasi Perubahan Arsitektur v3.6.0 Milestone Release

Siklus pengembangan v3.6.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Telemetri**: Sanitasi elemen gauge `<meter>` HTML5 dengan validasi atribut telemetri numerik, sanitasi elemen `<progress>` HTML5 dengan penegakan rentang rasio ternormalisasi, serta sanitasi elemen `<time>` dengan atribut `datetime` bertoken durasi ISO 8601 (`PnDTnHnMnS`).
- **Parser Standar Akademik & Regulasi Telekomunikasi**: Evaluator predikat kelulusan kehormatan yudisium mahasiswa (Cum Laude, Magna Cum Laude, Summa Cum Laude), kalkulator redaman propagasi radio Friis Free Space Path Loss (FSPL) BTS seluler, parser evaluasi program KKN Tematik perdesaan mahasiswa, serta parser kepatuhan pendanaan hibah riset internal Tridharma dosen LPPM.
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut**: Auditor aksesibilitas elemen pemutar audio/podcast dan ketersediaan tautan transkrip, auditor penandaan multi-bahasa rel alternate `hreflang` regional dan fallback `x-default`, auditor performa loading lambat (*lazy loading*) sematan iframe & peta digital, serta auditor hubungan struktur semantik elemen `<figure>` dan `<figcaption>`.
- **Komponen Semantik Elementor Responsif**: Kartu apresiasi yudisium kelulusan Cum Laude mahasiswa, kartu kalkulasi redaman Friis Path Loss transmisi gelombang mikro, kartu pameran pengabdian masyarakat KKN Tematik mahasiswa, kartu penetapan penerima hibah riset Tridharma dosen, serta kartu pengukur telemetri sensor IoT laboratorium dengan elemen semantik meter.
- **Format Pesan Telegram**: Format buletin Telegram apresiasi kelulusan yudisium Cum Laude dan format buletin pengumuman penetapan hibah riset internal LPPM.
- **Pengembangan Storage & Basis Data**: Tabel rekam yudisium berpredikat kehormatan (`student_graduation_honors`), tabel rekam hibah riset Tridharma dosen (`tridharma_research_grants`), serta tabel feed pembacaan telemetri sensor IoT lab (`iot_sensor_telemetry_feeds`).
- **Klien WordPress REST API**: Helper perolehan taksonomi kategori beserta metrik jumlah artikel terpublikasi (`get_categories_with_counts`) dan helper filter pengguna WordPress berdasarkan peran (*user roles*, `get_users_by_role`).
- **Generator Statis & Ekspor**: Generator Schema.org `Thesis` / `ScholarlyArticle` JSON-LD untuk naskah tugas akhir/disertasi sarjana, serta eksportir markdown digital garden kompatibel Quartz 4.0 (`to_quartz_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `honors`, `tridharma`, dan `quartz`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 516 menjadi 544 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Meter Telemetri (`sanitizer.py`)**:
   - Memvalidasi elemen `<meter>` HTML5, membersihkan atribut berbahaya, dan memvalidasi batas nilai numerik (`min`, `max`, `value`, `low`, `high`, `optimum`).

2. **Sanitasi Elemen HTML5 Progress Gauge (`sanitizer.py`)**:
   - Membersihkan elemen `<progress>` HTML5 dengan penegakan rentang rasio gauge ternormalisasi non-negatif.

3. **Sanitasi Elemen Waktu Durasi ISO 8601 (`sanitizer.py`)**:
   - Memvalidasi token durasi standar ISO 8601 (`PnDTnHnMnS`) pada atribut `datetime` elemen semantik `<time>`.

4. **Evaluator Predikat Yudisium Cum Laude Mahasiswa (`parser.py`)**:
   - Mengevaluasi syarat IPK, masa studi maksimal, nilai mata kuliah, dan menetapkan predikat kelulusan kehormatan akademik.

5. **Kalkulator Friis Free Space Path Loss Transmisi Gelombang Radio (`parser.py`)**:
   - Menghitung atenuasi redaman sinyal gelombang radio ruang bebas (FSPL) berdasarkan frekuensi transmisi dan jarak jangkauan antena BTS seluler.

6. **Parser Evaluasi KKN Tematik Mahasiswa (`parser.py`)**:
   - Mengurai rekam pelaksanaan program kuliah kerja nyata tematik perdesaan, susunan kelompok, dosen pembimbing lapangan, dan dampak keberlanjutan.

7. **Parser Kepatuhan Hibah Riset Tridharma Dosen (`parser.py`)**:
   - Mengurai proposal hibah penelitian internal LPPM, pagu anggaran, tahun anggaran, target luaran publikasi terindeks SINTA/Scopus, dan status evaluasi.

8. **Auditor Aksesibilitas Audio & Transkrip Podcast (`seo_validator.py`)**:
   - Memverifikasi keberadaan atribut kontrol pada elemen `<audio>` dan ketersediaan tautan transkrip teks pendamping guna memenuhi standar WCAG.

9. **Auditor Multilingual Rel Alternate Hreflang Tag (`seo_validator.py`)**:
   - Memvalidasi pasangan tag `<link rel="alternate" hreflang="...">`, format kode bahasa ISO (e.g. `id-ID`, `en-US`), tag self-referencing, dan fallback `x-default`.

10. **Auditor Lazy Loading Iframe & Embedded Map Performance (`seo_validator.py`)**:
    - Mendeteksi elemen sematan `<iframe>` eksternal dan peta digital yang belum menerapkan optimasi `loading="lazy"`.

11. **Auditor Struktur Hubungan Semantik Figure & Figcaption (`seo_validator.py`)**:
    - Memverifikasi posisi valid `<figcaption>` sebagai anak langsung pertama atau terakhir dari elemen `<figure>`, serta mencegah duplikasi tag keterangan.

12. **Komponen Yudisium Kelulusan Cum Laude (`components.py`)**:
    - Kartu penghargaan wisudawan berprestasi akademik tinggi dengan badge kehormatan Cum Laude dan detail tugas akhir.

13. **Komponen Kalkulasi Redaman Friis Path Loss BTS Seluler (`components.py`)**:
    - Kartu kalkulasi redaman propagasi sinyal RF lengkap dengan parameter frekuensi, jarak, daya pemancar, dan daya terima sinyal.

14. **Komponen Pameran Program KKN Tematik (`components.py`)**:
    - Kartu presentasi program unggulan KKN tematik perdesaan mahasiswa beserta metrik dampak sosial kemasyarakatan.

15. **Komponen Penetapan Hibah Riset Internal LPPM Dosen (`components.py`)**:
    - Kartu penetapan pemenang hibah riset internal perguruan tinggi dengan pagu dana dan komitmen target luaran ilmiah.

16. **Komponen Gauge Telemetri Sensor IoT Laboratorium (`components.py`)**:
    - Kartu visualisasi status pembacaan sensor laboratorium nirkabel menggunakan elemen pengukur semantik `<meter>`.

17. **Formatter Telegram Apresiasi Yudisium Cum Laude (`formatters.py`)**:
    - Template pesan siaran resmi Telegram untuk merayakan kelulusan mahasiswa berpredikat Dengan Pujian.

18. **Formatter Telegram Pengumuman Hibah Riset Tridharma (`formatters.py`)**:
    - Template pengumuman Telegram daftar penerima pendanaan hibah riset internal LPPM bagi para dosen.

19. **Manajer Rekam Yudisium Kehormatan (`storage.py`)**:
    - Tabel SQLite `student_graduation_honors` dan operasi CRUD pengarsipan rekam prestasi yudisium sarjana.

20. **Manajer Rekam Hibah Riset Tridharma Dosen (`storage.py`)**:
    - Skema tabel basis data `tridharma_research_grants` untuk pemantauan alokasi dan status hibah penelitian institusi.

21. **Manajer Rekam Telemetri Sensor IoT Laboratorium (`storage.py`)**:
    - Skema tabel `iot_sensor_telemetry_feeds` untuk penyimpanan deret waktu log pembacaan sensor nirkabel lab.

22. **Helper WordPress Get Categories With Counts (`wordpress_client.py`)**:
    - Pengambilan daftar taksonomi kategori WordPress lengkap dengan metrik jumlah post terbitan via REST API.

23. **Helper WordPress Get Users By Role (`wordpress_client.py`)**:
    - Penyaringan akun pengguna WordPress berdasarkan peran otorisasi spesifik (administrator, editor, author, dsb).

24. **Generator Schema.org Thesis ScholarlyArticle JSON-LD (`exporter.py`)**:
    - Pembuatan metadata terstruktur Schema.org `Thesis` untuk naskah skripsi sarjana teknik telekomunikasi.

25. **Eksportir Markdown Quartz Digital Garden (`exporter.py`)**:
    - Ekspor artikel database ke berkas markdown berkategori catatan digital garden Quartz 4.0.

26. **Subcommand CLI `honors` (`cli.py`)**:
    - Perintah konsol manajemen catatan yudisium kelulusan kehormatan mahasiswa (list, add).

27. **Subcommand CLI `tridharma` (`cli.py`)**:
    - Perintah konsol manajemen catatan hibah riset Tridharma dosen LPPM (list, add).

28. **Subcommand CLI `quartz` (`cli.py`)**:
    - Perintah konsol ekspor artikel ke format markdown digital garden Quartz.

29. **Pengujian Unit Terpadu Seluruh Modul (`tests/`)**:
    - Penambahan kasus uji unit komprehensif pada sanitizer, parser, seo validator, components, formatters, storage, wp client, exporter, dan cli.

30. **Dokumentasi Rilis & Catatan Perubahan (`docs/`)**:
    - Pembaruan dokumen ringkasan arsitektur, release changelog, dan sinkronisasi rincian rilis v3.6.0.

31. **Ekspansi Suite Pengujian Unit Terpadu (544 Tests Passing)**:
    - Verifikasi menyeluruh seluruh modul sistem dengan 544 unit test terverifikasi (100% pass rate).
