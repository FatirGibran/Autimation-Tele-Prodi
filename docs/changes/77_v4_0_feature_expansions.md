# Dokumentasi Perubahan Arsitektur v4.0.0 Milestone Release

Siklus pengembangan v4.0.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi pemutar media `<video>` dan `<source>` dengan scrubbing codec berbahaya (`sanitize_html5_video_elements`), sanitasi elemen terminologi `<abbr>` dan `<dfn>` (`sanitize_html5_abbr_dfn_elements`), serta sanitasi atribut grouping `name` pada `<details>` HTML5.2 untuk accordion eksklusif (`sanitize_html5_accordion_grouping`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator persamaan jangkauan radar monostatik $R_{max}$ dan delay round-trip (`calculate_radar_range_equation`), konverter derau fasa sudut $(\phi_{rad}, \phi_{deg})$ dan estimasi degradasi Error Vector Magnitude (EVM) konstelasi (`calculate_phase_noise_and_evm`), simulasi saturasi penguatan dan noise figure penguat optik EDFA C-band (`calculate_edfa_amplifier_gain`), serta evaluator rekognisi program MBKM Wirausaha Merdeka (WMK) hingga 20 SKS (`parse_wirausaha_merdeka_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor eliminasi skrip sinkronus pemblokir render dan optimasi Interaction to Next Paint (INP) (`audit_inp_script_accessibility`), auditor metadata OpenGraph media kaya video dan audio (`audit_rich_media_opengraph`), auditor kepatuhan format gambar responsif `<picture>` dan fallback `<img>` (`audit_picture_source_fallbacks`), serta auditor integritas landmark semantik `<main>` dan pelabelan unik `<nav>` (`audit_semantic_landmark_regions`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri jangkauan radar monostatik (`render_radar_detection_card`), kartu analisis derau fasa dan EVM modulasi digital (`render_phase_noise_evm_card`), kartu saturasi penguat optik EDFA (`render_edfa_amplifier_card`), kartu inkubasi startup Wirausaha Merdeka (`render_wirausaha_merdeka_card`), serta kartu visualisasi diagram konstelasi I/Q SVG responsif (`render_iq_constellation_diagram_card`).
- **Format Pesan Telegram**: Format buletin Telegram audit telemetri radar (`format_radar_telemetry_announcement_telegram`) dan format buletin apresiasi kelulusan program Wirausaha Merdeka (`format_wirausaha_merdeka_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit kalkulasi radar (`radar_detection_records`), tabel rekam mahasiswa dan startup Wirausaha Merdeka (`student_wirausaha_merdeka`), serta tabel rekaman penguat optik EDFA (`edfa_amplifier_records`).
- **Klien WordPress REST API**: Helper pengambilan daftar snapshot revisi postingan WordPress (`get_post_revisions`) dan helper pemulihan konten dari riwayat revisi (`restore_post_revision`).
- **Generator Statis & Ekspor**: Generator Schema.org `Project` startup inkubasi mahasiswa (`generate_startup_incubation_project_json_ld`) serta eksportir markdown Remix / React Router v7 MDX (`to_remix_route_mdx`).
- **Antarmuka Konsol CLI**: Subcommand baru `radar`, `wmk`, dan `edfa`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 625 menjadi 652 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Video & Codec (`sanitizer.py`)**:
   - Memvalidasi elemen `<video>` dan `<source>`, membersihkan `src` dari protokol `javascript:`, melucuti event handler inline, serta menegakkan ketersediaan kontrol pemutar.

2. **Sanitasi Elemen HTML5 Abbr & Dfn (`sanitizer.py`)**:
   - Membersihkan tag singkatan `<abbr>` dan definisi istilah `<dfn>` dari script injection dan atribut berbahaya.

3. **Sanitasi Pengelompokan Eksklusif Accordion Details (`sanitizer.py`)**:
   - Mengamankan atribut `name` pada elemen `<details>` HTML5.2 dan menetralkan event handler `ontoggle`.

4. **Kalkulator Persamaan Jangkauan Radar Monostatik (`parser.py`)**:
   - Menghitung jangkauan deteksi maksimum $R_{max}$, panjang gelombang $\lambda$, gain linier antena, daya sinyal minimum $S_{min}$, dan waktu tunda pantulan pulsa.

5. **Kalkulator Derau Fasa & Estimasi EVM (`parser.py`)**:
   - Mengonversi jitter fasa RMS dan integrated phase noise dBc ke derau fasa sudut serta mengestimasi persentase Error Vector Magnitude (EVM) untuk modulasi digital.

6. **Kalkulator Penguat Optik EDFA C-Band (`parser.py`)**:
   - Menghitung saturasi penguatan optik terhadap daya pompa laser 980/1480 nm, daya keluaran tersaturasi, dan estimasi nilai Noise Figure (NF).

7. **Evaluator Rekognisi MBKM Wirausaha Merdeka (`parser.py`)**:
   - Mengakumulasikan nilai mentor dan presentasi pitching menjadi skor komposit, konversi nilai mutu, dan ekuivalensi hingga 20 SKS kurikulum prodi.

8. **Auditor Interaksi ke Cat Berikutnya (INP) (`seo_validator.py`)**:
   - Mengaudit skrip eksternal render-blocking dan event handler inline yang berpotensi menimbulkan long task pada main thread browser.

9. **Auditor OpenGraph Video & Audio (`seo_validator.py`)**:
   - Memvalidasi tag kaya OpenGraph `og:video` dan `og:audio` terhadap kepatuhan enkripsi HTTPS dan format MIME.

10. **Auditor Kontainer Gambar Responsif Picture (`seo_validator.py`)**:
    - Memverifikasi keberadaan elemen fallback `<img>` lengkap dengan atribut `alt` serta struktur tag `<source>`.

11. **Auditor Wilayah Landmark Semantik Aksesibilitas (`seo_validator.py`)**:
    - Memastikan dokumen memiliki tepat satu landmark `<main>` aktif dan setiap navigasi `<nav>` memiliki identitas aksesibel unik.

12. **Komponen Telemetri Jangkauan Radar (`components.py`)**:
    - Kartu ringkasan Elementor parameter transmit radar, RCS target, jangkauan deteksi maksimum, dan waktu tempuh sinyal.

13. **Komponen Derau Fasa & EVM Modulasi (`components.py`)**:
    - Kartu visualisasi integritas konstelasi sinyal digital dengan metrik jitter fasa, phase error, dan persentase degradasi EVM.

14. **Komponen Penguat Optik EDFA (`components.py`)**:
    - Kartu visualisasi parameter penguatan serat optik, daya pompa laser, net gain, dan estimasi derau spontan ASE.

15. **Komponen Startup Wirausaha Merdeka (`components.py`)**:
    - Kartu pencapaian kewirausahaan mahasiswa dengan skor komposit dan konversi kurikulum akademik.

16. **Komponen Diagram Konstelasi I/Q Responsif (`components.py`)**:
    - Kartu visualisasi simbol konstelasi bidang I/Q dengan grid crosshair dan titik-titik simbol berbasis SVG inline.

17. **Formatter Telegram Audit Radar (`formatters.py`)**:
    - Template pesan siaran resmi Telegram untuk hasil verifikasi persamaan jangkauan deteksi radar.

18. **Formatter Telegram Wirausaha Merdeka (`formatters.py`)**:
    - Template siaran Telegram pengumuman kelulusan dan apresiasi rekognisi SKS program startup WMK.

19. **Manajer Storage Radar Monostatik (`storage.py`)**:
    - Tabel SQLite `radar_detection_records` dan API manajemen data telemetri radar.

20. **Manajer Storage Wirausaha Merdeka (`storage.py`)**:
    - Tabel SQLite `student_wirausaha_merdeka` dan API manajemen rekaman startup mahasiswa.

21. **Manajer Storage Penguat EDFA (`storage.py`)**:
    - Tabel SQLite `edfa_amplifier_records` dan API manajemen rekaman penguat optik.

22. **Helper WordPress Get Post Revisions (`wordpress_client.py`)**:
    - Pengambilan daftar histori snapshot revisi artikel via WordPress REST API.

23. **Helper WordPress Restore Post Revision (`wordpress_client.py`)**:
    - Pemulihan artikel ke versi revisi tertentu melalui API.

24. **Generator Schema.org Startup Project JSON-LD (`exporter.py`)**:
    - Pembuatan metadata Schema.org Project untuk program inkubasi startup teknologi mahasiswa.

25. **Eksportir Remix Route MDX (`exporter.py`)**:
    - Ekspor artikel dengan frontmatter route meta dan breadcrumb handle format Remix / React Router v7.

26. **Subcommand CLI `radar`, `wmk`, `edfa` (`cli.py`)**:
    - Perintah CLI untuk pencatatan dan peninjauan data radar, startup WMK, dan penguat EDFA.

27. **Suite Pengujian Unit Komprehensif (652 Tests Passing)**:
    - 652 pengujian unit terverifikasi 100% lulus tanpa kegagalan (`Ran 652 tests in 5.953s, OK`).
