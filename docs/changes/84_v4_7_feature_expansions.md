# Dokumentasi Perubahan Arsitektur v4.7.0 Milestone Release

Siklus pengembangan v4.7.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen tabel HTML5 `<col>` dan `<colgroup>` dengan validasi atribut numerik `span` dan properti `width` (`sanitize_html5_col_colgroup_attributes`), sanitasi kutipan teks `<cite>` dan `<q>` dengan penegakan validasi skema aman atribut URI `cite` (`sanitize_html5_cite_q_elements`), serta sanitasi atribut kontrol formulir multi-baris `<textarea>` (`sanitize_html5_textarea_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator pelebaran spektral nonlinier Self-Phase Modulation (SPM) serat optik DWDM menurut kaidah optika nonlinier Agrawal (`calculate_optical_spm_broadening`), kalkulator aggregate throughput multi-carrier 5G NR Carrier Aggregation (CA) menurut spesifikasi 3GPP TS 38.306 (`calculate_5g_nr_carrier_aggregation_throughput`), kalkulator redaman hujan propagasi lintasan miring satelit bumi-angkasa menurut rekomendasi ITU-R P.618-13 (`calculate_satellite_rain_attenuation_itu_r_p618`), serta evaluator rekognisi kurikulum program Program Pembinaan Mahasiswa Wirausaha (P2MW) Kemendikbudristek (`parse_p2mw_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor penanda data terstruktur Schema.org EducationalOccupationalCredential untuk program mikrokredensial dan sertifikasi prodi (`audit_educational_credential_schema`), auditor kelengkapan Web App Manifest dan meta theme-color untuk mobile indexing dan PWA (`audit_manifest_and_theme_color`), auditor penanda aksesibilitas ARIA Landmarks dan struktur hirarki heading WCAG 2.1 SC 1.3.1 (`audit_aria_landmarks_and_headings`), serta auditor kepatuhan CORS pada atribut preload font web guna mencegah double-fetch aset render-blocking (`audit_font_preload_cors`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri pergeseran fase nonlinier SPM dan B-integral serat optik (`render_optical_spm_card`), kartu telemetri aggregate throughput 5G NR Carrier Aggregation (`render_5g_nr_carrier_aggregation_card`), kartu evaluasi link margin redaman hujan satelit ITU-R P.618 (`render_satellite_rain_attenuation_card`), kartu rekognisi startup mahasiswa program P2MW (`render_p2mw_startup_card`), serta kartu visualisasi diagram alokasi spektrum frekuensi multi-carrier 5G NR Carrier Aggregation berbasis inline SVG responsif (`render_5g_nr_ca_spectrum_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan telemetri redaman hujan propagasi satelit ITU-R P.618 (`format_satellite_rain_attenuation_telegram`) dan format pengumuman rekognisi SKS program wirausaha mahasiswa P2MW (`format_p2mw_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit pergeseran fase SPM serat optik (`optical_spm_records`), tabel rekam konfigurasi throughput 5G NR CA (`nr_ca_records`), serta tabel rekam evaluasi & rekognisi wirausaha P2MW (`p2mw_startup_records`).
- **Klien WordPress REST API**: Helper pembaca konfigurasi situs WordPress (`get_site_settings`) dan helper pembaruan pengaturan situs WordPress (`update_site_settings`) via endpoint `/wp/v2/settings`.
- **Generator Statis & Ekspor**: Generator Schema.org `EducationalOccupationalCredential` JSON-LD (`generate_credential_json_ld`) serta eksportir dokumentasi framework modern Qwik City MDX (`to_qwik_city_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `spm`, `ca`, dan `p2mw`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 817 menjadi 845 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Kolom Tabel `<col>` dan `<colgroup>` (`sanitizer.py`)**:
   - Memvalidasi elemen kolom tabel `<col>` dan `<colgroup>`, mensterilkan atribut `span` bernilai integer positif, membatasi format lebar `width` (persentase, piksel, atau nilai relatif), serta mengeliminasi atribut event handler inline.

2. **Sanitasi Elemen Kutipan `<cite>` dan `<q>` (`sanitizer.py`)**:
   - Memvalidasi elemen kutipan teks, memastikan atribut sumber `cite` menggunakan skema protokol aman (`http`, `https`, atau jalur relatif), menolak skema pseudo-protokol JavaScript, serta membersihkan event handler.

3. **Sanitasi Atribut Form Kontrol `<textarea>` (`sanitizer.py`)**:
   - Mensterilkan atribut form control `<textarea>`, membatasi nilai dimensi baris dan kolom (`rows`, `cols`), panjang masukan (`maxlength`, `minlength`), placeholder teks, serta mode pembungkusan teks (`wrap="soft|hard"`).

4. **Kalkulator Pelebaran Spektral Self-Phase Modulation (SPM) Serat Optik DWDM (`parser.py`)**:
   - Menghitung panjang efektif serat $L_{\text{eff}} = \frac{1 - e^{-\alpha L}}{\alpha}$, pergeseran fase nonlinier maksimum $\phi_{\max} = \gamma P_0 L_{\text{eff}}$, B-integral, estimasi rasio pelebaran spektral pulsa optik $\frac{\sigma}{\sigma_0} = \sqrt{1 + \frac{4}{3\sqrt{3}} \phi_{\max}^2}$, dan evaluasi tingkat risiko SPM transmisi DWDM berkecepatan tinggi.

5. **Kalkulator Throughput 5G NR Carrier Aggregation (CA) 3GPP TS 38.306 (`parser.py`)**:
   - Menghitung akumulasi kapasitas data throughput multi-carrier (PCC dan beberapa SCC) dengan mempertimbangkan alokasi bandwidth MHz, jumlah lapisan MIMO spatial multiplexing, dan efisiensi modulasi (QPSK, 16QAM, 64QAM, 256QAM), serta efisiensi spektral agregat (bps/Hz).

6. **Kalkulator Redaman Hujan Propagasi Satelit ITU-R P.618-13 (`parser.py`)**:
   - Menghitung panjang lintasan miring efektif satelit bumi-angkasa $L_s$, tinggi hujan $h_R$, koefisien redaman spesifik $\gamma_R = k R^\alpha$ menurut rekomendasi ITU-R P.838, faktor penyesuaian horizontal & vertikal, estimasi redaman hujan persentase terlampaui $A_{0.01}$, dan evaluasi link margin ketersediaan layanan satelit pita Ku/Ka.

7. **Evaluator Rekognisi MBKM Wirausaha Mahasiswa P2MW (`parser.py`)**:
   - Mengevaluasi performa startup mahasiswa peserta program P2MW berdasarkan Business Model Canvas & Pitching (35%), kemajuan prototipe dan traksi pasar (40%), tata kelola dan akuntabilitas keuangan (25%), konversi nilai mutu, dan pengakuan hingga 6 SKS kurikulum prodi.

8. **Auditor Skema EducationalOccupationalCredential Schema.org (`seo_validator.py`)**:
   - Memvalidasi keberadaan struktur data Schema.org `EducationalOccupationalCredential` (JSON-LD atau Microdata) untuk publikasi sertifikat kompetensi keahlian telekomunikasi dan modul mikrokredensial.

9. **Auditor Web App Manifest & Theme Color (`seo_validator.py`)**:
   - Memeriksa keterhubungan file `manifest.json` atau `site.webmanifest` beserta penanda `<meta name="theme-color">` pada header HTML untuk optimalisasi pengalaman peramban seluler dan Progressive Web App.

10. **Auditor Aksesibilitas ARIA Landmarks & Heading Semantik WCAG 2.1 (`seo_validator.py`)**:
    - Mengaudit kelengkapan penanda struktur peran ARIA (`banner`, `main`, `navigation`, `contentinfo`) serta konsistensi hirarki heading semantik guna menjamin pemenuhan standar aksesibilitas layar pembaca tunanetra WCAG 2.1 SC 1.3.1.

11. **Auditor Kepatuhan CORS Preload Font Web (`seo_validator.py`)**:
    - Mengaudit deklarasi `<link rel="preload" as="font">` terhadap keharusan pencantuman atribut `crossorigin="anonymous"` demi mencegah terjadinya double-fetch resource font yang menurunkan skor Largest Contentful Paint (LCP).

12. **Komponen Visualisasi Spektrum Frekuensi 5G NR Carrier Aggregation Inline SVG (`components.py`)**:
    - Kartu visualisasi representasi grafis alokasi pita spektrum komponen carrier PCC dan SCC multi-carrier 5G NR berbasis inline SVG responsif lengkap dengan penanda lebar pita MHz, frekuensi tengah, dan akumulasi total bandwidth.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Skema tabel database `optical_spm_records`, `nr_ca_records`, dan `p2mw_startup_records` dilengkapi metode CRUD terindeks untuk persistensi data operasional prodi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper pembaca konfigurasi situs WordPress `get_site_settings` dan pembaruan pengaturan umum situs `update_site_settings` via REST API endpoint `/wp/v2/settings`.

15. **Generator Credential JSON-LD & Eksportir Qwik City MDX (`exporter.py`)**:
    - Generator Schema.org `EducationalOccupationalCredential` JSON-LD standar mikrokredensial akademik dan eksportir format dokumentasi Qwik City MDX dengan frontmatter YAML terintegrasi.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `spm`, `ca`, dan `p2mw` untuk operasionalisasi telekomunikasi dan tata kelola program wirausaha mahasiswa dari terminal CLI.
