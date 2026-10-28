# Dokumentasi Perubahan Arsitektur v4.6.0 Milestone Release

Siklus pengembangan v4.6.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen riwayat revisi `<del>` dan `<ins>` dengan penegakan validasi URI `cite` dan format ISO 8601 `datetime` (`sanitize_html5_del_ins_elements`), sanitasi atribut aksi formulir dinamis HTML5 `formaction`, `formmethod`, `formtarget` (`sanitize_html5_form_input_attributes`), serta sanitasi daftar opsi saran formulir `<datalist>` dan `<option>` (`sanitize_html5_datalist_options`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator ambang batas hamburan Raman terstimulasi (SRS) serat optik DWDM menurut kaidah Stolen & Smith dan optika nonlinier Agrawal (`calculate_optical_srs_threshold`), kalkulator Equivalent Isotropically Radiated Power (EIRP) dan Power Spectral Density (PSD) pemancar seluler 5G NR menurut spesifikasi 3GPP TS 38.104 (`calculate_5g_nr_eirp_psd`), kalkulator perputaran polarisasi ionosfer Faraday satelit bumi-angkasa menurut rekomendasi ITU-R P.531 (`calculate_satellite_faraday_rotation`), serta evaluator rekognisi kurikulum program kolaborasi industri MBKM Praktisi Mengajar Kemendikbudristek (`parse_praktisi_mengajar_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor penanda data terstruktur Schema.org Person untuk profil dosen peneliti dan E-E-A-T signals (`audit_person_schema_markup`), auditor dimensi dan rasio aspek tag Open Graph image untuk pratinjau media sosial high-DPI (`audit_open_graph_image_dimensions`), auditor aksesibilitas zoom viewport mobile menurut kriteria sukses WCAG 2.1 SC 1.4.4 (`audit_viewport_scalable_accessibility`), serta auditor keamanan integritas sumber daya eksternal Subresource Integrity (SRI) pada script dan stylesheet pihak ketiga (`audit_subresource_integrity_sri`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri ambang batas daya nonlinier SRS serat optik (`render_optical_srs_card`), kartu kepatuhan radiasi daya EIRP & PSD seluler 5G NR (`render_5g_nr_eirp_psd_card`), kartu telemetri Faraday rotation satelit ITU-R P.531 (`render_satellite_faraday_card`), kartu rekognisi kolaborasi industri Praktisi Mengajar MBKM (`render_praktisi_mengajar_card`), serta kartu visualisasi diagram pola radiasi antena (radiation pattern) beamforming 5G NR berbasis inline SVG responsif (`render_5g_nr_radiation_pattern_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan telemetri Faraday rotation satelit ITU-R P.531 (`format_satellite_faraday_telegram`) dan format pengumuman kolaborasi MBKM Praktisi Mengajar industri (`format_praktisi_mengajar_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit ambang SRS serat optik (`optical_srs_records`), tabel kepatuhan daya terpancar 5G NR (`nr_eirp_records`), serta tabel rekam kolaborasi Praktisi Mengajar MBKM (`praktisi_mengajar_records`).
- **Klien WordPress REST API**: Helper pembuatan halaman statis WordPress baru (`create_page`) dan helper penghapusan halaman statis WordPress (`delete_page`).
- **Generator Statis & Ekspor**: Generator Schema.org `Person` JSON-LD standar profil dosen dan pakar akademisi (`generate_person_json_ld`) serta eksportir dokumentasi modern Remix / React Router v7 MDX (`to_remix_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `srs`, `eirp`, dan `praktisi`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 791 menjadi 819 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Riwayat Revisi `<del>` dan `<ins>` (`sanitizer.py`)**:
   - Memvalidasi elemen `<del>` dan `<ins>`, membersihkan atribut `cite` dari skema berbahaya, memvalidasi format timestamp `datetime` berstandar ISO 8601, serta membuang event handler inline.

2. **Sanitasi Atribut Aksi Form Input HTML5 (`sanitizer.py`)**:
   - Mensterilkan atribut `formaction`, `formmethod`, `formtarget`, `formenctype`, membatasi target form ke nilai aman (`_blank`, `_self`), dan mencegah eksekusi skrip berbahaya.

3. **Sanitasi Opsi Saran Datalist HTML5 (`sanitizer.py`)**:
   - Mengamankan elemen `<datalist>` dan `<option>`, memvalidasi atribut `value` dan `label`, serta membersihkan payload injeksi XSS.

4. **Kalkulator Ambang Hamburan Raman Terstimulasi (SRS) Serat Optik DWDM (`parser.py`)**:
   - Menghitung panjang efektif $L_{\text{eff}}$, ambang daya kritis Raman $P_{\text{th}} = \frac{16 A_{\text{eff}}}{g_R L_{\text{eff}}}$, margin redaman Raman depletion, dan klasifikasi tingkat keamanan transmisi WDM/DWDM.

5. **Kalkulator Radiasi Daya 5G NR EIRP & PSD 3GPP TS 38.104 (`parser.py`)**:
   - Menghitung conducted power, antenna gain, total radiated power EIRP (dBm dan Watt), Power Spectral Density (dBm/MHz), serta evaluasi ambang regulasi Kominfo dan 3GPP.

6. **Kalkulator Faraday Rotation Propagasi Satelit ITU-R P.531 (`parser.py`)**:
   - Menghitung sudut rotasi polarisasi $\Omega$ pada frekuensi gelombang mikro di ionosfer berdasarkan Total Electron Content (TEC) dan medan geomagnetik Bumi, serta rugi-rugi ketidakcocokan polarisasi (polarization mismatch loss).

7. **Evaluator Rekognisi MBKM Praktisi Mengajar Kolaborasi Industri (`parser.py`)**:
   - Mengevaluasi skor komposit studi kasus industri (40%), penilaian praktisi ahli (40%), evaluasi mahasiswa (20%), konversi nilai mutu, dan pengakuan hingga 4 SKS mata kuliah prodi.

8. **Auditor Skema Person Schema.org (`seo_validator.py`)**:
   - Memvalidasi ketersediaan dan integritas penanda Schema.org Person (JSON-LD atau Microdata) untuk author profile dosen, peneliti, dan staf akademik prodi guna meningkatkan sinyal E-E-A-T Google.

9. **Auditor Dimensi & Rasio Open Graph Image (`seo_validator.py`)**:
   - Memeriksa kelengkapan tag `<meta property="og:image">`, dimensi lebar dan tinggi (`og:image:width`, `og:image:height`), rasio aspek ideal 1.91:1, dan teks alternatif aksesibilitas (`og:image:alt`).

10. **Auditor Aksesibilitas Skalabilitas Viewport WCAG 2.1 (`seo_validator.py`)**:
    - Mengaudit deklarasi `<meta name="viewport">` terhadap larangan penonaktifan zoom pengguna (`user-scalable=no` atau pembatasan `maximum-scale <= 1.0`) sesuai kriteria WCAG 2.1 SC 1.4.4.

11. **Auditor Subresource Integrity (SRI) Keamanan Aset Eksternal (`seo_validator.py`)**:
    - Mengaudit aset script dan stylesheet CDN eksternal terhadap ketersediaan atribut hash kriptografis `integrity` (sha256/sha384/sha512) dan `crossorigin="anonymous"` untuk mencegah serangan supply chain.

12. **Komponen Visualisasi Pola Radiasi Antena 5G NR Inline SVG (`components.py`)**:
    - Kartu visualisasi diagram polar pola radiasi antena beamforming 5G NR menampilkan main lobe boresight, Half-Power Beamwidth (HPBW), dan penekanan sidelobe.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Tabel baru `optical_srs_records`, `nr_eirp_records`, dan `praktisi_mengajar_records` dilengkapi metode CRUD dan indeks terindeksasi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper manipulasi halaman statis WordPress `create_page` dan `delete_page` untuk administrasi konten halaman prodi.

15. **Generator Person JSON-LD & Eksportir Remix MDX (`exporter.py`)**:
    - Generator Schema.org `Person` JSON-LD standar profil akademisi dan eksportir format dokumentasi Remix / React Router v7 MDX.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `srs`, `eirp`, dan `praktisi` untuk operasionalisasi langsung dari terminal.
