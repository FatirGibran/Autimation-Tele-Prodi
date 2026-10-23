# Dokumentasi Perubahan Arsitektur v4.1.0 Milestone Release

Siklus pengembangan v4.1.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi gambar responsif `<picture>` dan validasi MIME type format modern (`sanitize_html5_picture_elements`), pengamanan dialog modal HTML5 dan penanganan `formmethod="dialog"` serta autofocus (`sanitize_html5_dialog_elements`), dan sanitasi pemutar audio HTML5 dengan penegakan pembatasan unduhan dan pencegahan preload agresif (`sanitize_html5_audio_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator parameter reflektansi dan redaman serat optik OTDR sesuai standar ITU-T G.652 (`calculate_otdr_fiber_events`), kalkulator kapasitas kanal nirkabel dan efisiensi spektral Shannon antena MIMO array (`calculate_mimo_channel_capacity`), estimator profil konsumsi energi harian dan masa pakai baterai node sensor LoRaWAN (`calculate_lorawan_node_battery_lifetime`), serta evaluator pengakuan kredit beasiswa mobilitas internasional mahasiswa IISMA MBKM hingga 20 SKS (`parse_iisma_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor pemuatan font web modern (`font-display: swap` dan preload font eksternal) untuk optimasi CLS dan LCP (`audit_font_display_and_preload`), auditor metadata artikel OpenGraph (`article:published_time`, `article:author`, dsb.) untuk Google Discover dan media sosial (`audit_opengraph_article_metadata`), auditor aksesibilitas widget pengungkapan informasi `<details>` dan `<summary>` (`audit_details_summary_accessibility`), serta auditor kecukupan ukuran target sentuh interaktif mobile sesuai pedoman WCAG 2.5.5 (`audit_touch_target_sizes`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri pengujian kabel serat optik OTDR (`render_otdr_fiber_card`), kartu kapasitas kanal dan efisiensi spektral MIMO (`render_mimo_capacity_card`), kartu profil energi dan masa pakai baterai node LoRaWAN (`render_lorawan_battery_card`), kartu rekognisi program beasiswa IISMA mahasiswa (`render_iisma_scholarship_card`), serta kartu visualisasi pola radiasi beamforming antena phased-array berbasis vektor SVG responsif (`render_beamforming_pattern_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram telemetri redaman link kabel serat optik OTDR (`format_otdr_telemetry_telegram`) dan format buletin apresiasi kelulusan program pertukaran pelajar internasional IISMA (`format_iisma_exchange_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit kabel serat optik OTDR (`otdr_fiber_records`), tabel rekam audit kapasitas MIMO (`mimo_capacity_records`), serta tabel rekam penghargaan mobilitas mahasiswa IISMA (`student_iisma_exchange`).
- **Klien WordPress REST API**: Helper perolehan daftar pengguna WordPress berdasarkan peran (`get_users_by_role`) dan helper pembaruan penugasan ID penulis postingan (`assign_post_author`).
- **Generator Statis & Ekspor**: Generator Schema.org `EducationalOccupationalProgram` JSON-LD beasiswa mobilitas (`generate_academic_exchange_program_json_ld`) serta eksportir markdown VitePress dokumentasi teknis (`to_vitepress_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `otdr`, `mimo`, dan `iisma`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 652 menjadi 678 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Picture & MIME Type (`sanitizer.py`)**:
   - Memvalidasi elemen `<picture>` dan `<source>`, membersihkan nilai atribut `type` terhadap potensi eksekusi MIME scripting berbahaya (`application/x-javascript`, `text/html`), serta memastikan keberadaan fallback `<img>`.

2. **Sanitasi Elemen HTML5 Dialog & Autofocus (`sanitizer.py`)**:
   - Mensterilkan atribut `<dialog formmethod="dialog">`, mengamankan penggunaan atribut `autofocus` agar tidak mengganggu navigasi pembaca layar, dan menetralkan injeksi script handler.

3. **Sanitasi Elemen HTML5 Audio (`sanitizer.py`)**:
   - Memvalidasi elemen `<audio>` dan `<source>`, menegakkan atribut `controlslist="nodownload"`, menonaktifkan preloading bandwidth intensif (`preload="none"` atau `metadata`), serta menyaring skema URI berbahaya.

4. **Kalkulator Reflektansi & Redaman OTDR Serat Optik (`parser.py`)**:
   - Menghitung koefisien redaman serat optik $\alpha$ (dB/km), total insertion loss kabel, loss splice sambungan, connector loss, dan memverifikasi batas redaman ITU-T G.652 pada panjang gelombang 1310 nm dan 1550 nm.

5. **Kalkulator Kapasitas & Efisiensi Spektral MIMO (`parser.py`)**:
   - Mengalkulasi kapasitas kanal nirkabel multi-antena $N_T \times N_R$, efisiensi spektral Shannon teoritis, rasio signal-to-noise linier, dan estimasi throughput kanal transmisi data.

6. **Estimator Konsumsi Energi & Masa Pakai Baterai LoRaWAN (`parser.py`)**:
   - Menghitung konsumsi energi harian (mWh) pada mode sleep dan transmit, arus beban, kapasitas baterai terpakai, dan estimasi usia pakai operasional node IoT dalam satuan tahun.

7. **Evaluator Rekognisi Beasiswa Mahasiswa IISMA (`parser.py`)**:
   - Mengonversi kredit mata kuliah perguruan tinggi luar negeri mitra IISMA, kalkulasi bobot IPK luar negeri, dan ekuivalensi hingga 20 SKS kurikulum prodi.

8. **Auditor Optimasi Webfont & Preload (`seo_validator.py`)**:
   - Mengaudit kepatuhan deklarasi stylesheet `@font-face` terhadap atribut `font-display: swap` serta keberadaan `<link rel="preload" as="font">` untuk mencegah Flash of Invisible Text (FOIT).

9. **Auditor Metadata Artikel OpenGraph (`seo_validator.py`)**:
   - Memverifikasi tag `article:published_time`, `article:modified_time`, `article:author`, dan `article:section` dalam format ISO 8601 untuk optimalisasi crawling Google Discover.

10. **Auditor Aksesibilitas Accordion Details & Summary (`seo_validator.py`)**:
    - Memverifikasi elemen `<details>` memiliki anak langsung `<summary>`, teks ringkasan tidak kosong, dan struktur semantik memenuhi pedoman WCAG 2.1.

11. **Auditor Ukuran Target Sentuh Interaktif Mobile (`seo_validator.py`)**:
    - Memeriksa dimensi interaktif tombol dan tautan pada tampilan mobile agar berukuran sekurang-kurangnya $48 \times 48\text{ px}$ dengan margin spasi yang cukup sesuai standar Google Lighthouse.

12. **Komponen Telemetri Kabel Serat Optik OTDR (`components.py`)**:
    - Kartu Elementor ringkasan parameter panjang bentangan kabel, loss kabel, jumlah sambungan splice, dan status kelulusan standar redaman ITU-T G.652.

13. **Komponen Kapasitas Antena MIMO Array (`components.py`)**:
    - Kartu visualisasi konfigurasi $N_T \times N_R$, bandwidth saluran, SNR operasional, efisiensi spektral, dan throughput maksimum.

14. **Komponen Profil Baterai Node LoRaWAN (`components.py`)**:
    - Kartu ringkasan metrik konsumsi energi harian, duty cycle transmit, kapasitas baterai, dan estimasi masa pakai perangkat dalam tahun.

15. **Komponen Penghargaan Mobilitas Mahasiswa IISMA (`components.py`)**:
    - Kartu pencapaian prestasi mahasiswa penerima beasiswa IISMA, universitas tujuan luar negeri, IPK konversi, dan ekuivalensi 20 SKS.

16. **Komponen Pola Radiasi Beamforming Responsif SVG (`components.py`)**:
    - Kartu visualisasi diagram kutub radiasi antena terarah phased-array dengan main lobe, sidelobes, dan beam steering angle berbasis vektor SVG terisolasi.

17. **Formatter Telegram Audit OTDR (`formatters.py`)**:
    - Format siaran Telegram resmi untuk hasil pengukuran kabel optik dan audit redaman transmisi optik.

18. **Formatter Telegram Apresiasi Beasiswa IISMA (`formatters.py`)**:
    - Format siaran Telegram resmi ucapan selamat dan pengumuman kelulusan program beasiswa pertukaran pelajar internasional IISMA mahasiswa.

19. **Manajer Rekam Audit Serat Optik OTDR (`storage.py`)**:
    - Tabel SQLite `otdr_fiber_records` dan fungsi `record_otdr_fiber`, `list_otdr_fibers`, dan `get_otdr_fiber_by_id`.

20. **Manajer Rekam Kapasitas Antena MIMO (`storage.py`)**:
    - Tabel SQLite `mimo_capacity_records` dan fungsi `record_mimo_capacity`, `list_mimo_capacities`, dan `get_mimo_capacity_by_id`.

21. **Manajer Rekam Beasiswa Mahasiswa IISMA (`storage.py`)**:
    - Tabel SQLite `student_iisma_exchange` dan fungsi `record_iisma_exchange`, `list_iisma_exchanges`, dan `get_iisma_exchange_by_nim`.

22. **Helper WordPress Get Users by Role (`wordpress_client.py`)**:
    - Metode REST API `get_users_by_role` untuk menyaring pengguna WordPress berdasarkan peran (author, editor, administrator).

23. **Helper WordPress Assign Post Author (`wordpress_client.py`)**:
    - Metode REST API `assign_post_author` untuk menetapkan atribusi ID author pada artikel.

24. **Generator Schema.org Academic Exchange Program JSON-LD (`exporter.py`)**:
    - Metode `generate_academic_exchange_program_json_ld` menghasilkan structured data standar `EducationalOccupationalProgram` untuk program mobilitas mahasiswa internasional.

25. **Eksportir Markdown VitePress Documentation (`exporter.py`)**:
    - Metode `to_vitepress_markdown` mengonversi artikel blog menjadi format dokumentasi statis VitePress dengan frontmatter YAML terstruktur.

26. **Subcommand CLI `otdr` (`cli.py`)**:
    - Perintah konsol `otdr` untuk menyimpan dan menampilkan riwayat pengukuran kabel serat optik OTDR.

27. **Subcommand CLI `mimo` (`cli.py`)**:
    - Perintah konsol `mimo` untuk menyimpan dan menampilkan riwayat analisis kapasitas antena MIMO array.

28. **Subcommand CLI `iisma` (`cli.py`)**:
    - Perintah konsol `iisma` untuk mencatat dan menampilkan daftar mahasiswa penerima penghargaan mobilitas IISMA.

29. **Ekspansi Suite Pengujian Unit Terpadu (678 Tests Passing)**:
    - Penambahan 26 unit test komprehensif pada modul sanitizer, parser, seo_validator, components, formatters, storage, wordpress_client, exporter, dan cli.
