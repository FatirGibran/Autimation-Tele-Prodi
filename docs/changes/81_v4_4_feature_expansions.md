# Dokumentasi Perubahan Arsitektur v4.4.0 Milestone Release

Siklus pengembangan v4.4.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen gambar responsif `<picture>` dan sub-elemen `<source>` dengan penegakan validasi atribut `srcset`, `media`, dan `type` (`sanitize_html5_picture_and_source`), pengamanan elemen input terminal `<kbd>` dan `<samp>` dari penyusupan atribut asing (`sanitize_html5_kbd_and_samp`), serta sanitasi elemen pengukur `<meter>` dan kemajuan `<progress>` dengan validasi parameter numerik (`sanitize_html5_meter_and_progress`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator efisiensi pencampuran empat gelombang (Four-Wave Mixing / FWM) sistem transmisi DWDM menurut rekomendasi ITU-T G.692 dan optika nonlinier Agrawal (`calculate_optical_four_wave_mixing`), kalkulator kapasitas trafik teleponi dan radio seluler trunking Erlang-B / Erlang-C (`calculate_erlang_traffic_capacity`), kalkulator redaman gas atmosfer spesifik oksigen dan uap air lintasan miring satelit menurut rekomendasi ITU-R P.676 (`calculate_satellite_gas_attenuation_itu_r`), serta evaluator rekognisi kurikulum program Program Kreativitas Mahasiswa (PKM) dan PIMNAS hingga 20 SKS MBKM (`parse_pkm_mbkm_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor Web App Manifest dan konfigurasi meta PWA mobile (`audit_webapp_manifest_and_pwa_meta`), auditor sekuens kanonikal penomoran halaman serial rel next/prev (`audit_pagination_rel_next_prev`), auditor penanda data terstruktur Schema.org HowTo (`audit_howto_schema_markup`), serta auditor ketersediaan deskripsi audio dan aksesibilitas media (`audit_audio_description_and_media_accessibility`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri crosstalk nonlinier FWM serat optik (`render_optical_fwm_card`), kartu analisis kapasitas trafik trunking seluler Erlang (`render_erlang_traffic_card`), kartu redaman gas atmosfer satelit ITU-R P.676 (`render_satellite_gas_attenuation_card`), kartu rekognisi prestasi PKM dan PIMNAS mahasiswa (`render_pkm_pimnas_achievement_card`), serta kartu visualisasi diagram alokasi spektrum grid frekuensi ITU DWDM berbasis inline SVG responsif (`render_dwdm_spectrum_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan telemetri redaman atmosfer satelit ITU-R P.676 (`format_satellite_gas_attenuation_telegram`) dan format apresiasi prestasi dan pendanaan PKM/PIMNAS mahasiswa (`format_pkm_pimnas_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit FWM serat optik (`optical_fwm_records`), tabel audit kapasitas trafik seluler Erlang (`erlang_traffic_records`), serta tabel rekam capaian mahasiswa PKM dan PIMNAS (`student_pkm_records`).
- **Klien WordPress REST API**: Helper perolehan objek pengguna/penulis WordPress berdasarkan ID numerik (`get_user_by_id`) dan helper perolehan item pustaka media berdasarkan slug URL aset (`get_media_by_slug`).
- **Generator Statis & Ekspor**: Generator Schema.org `HowTo` JSON-LD standar tutorial Google Rich Results (`generate_how_to_json_ld`) serta eksportir dokumentasi interaktif MDX Docusaurus (`to_docusaurus_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `fwm`, `erlang`, dan `pimnas`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 735 menjadi 763 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Picture & Source Responsif (`sanitizer.py`)**:
   - Memvalidasi elemen `<picture>` dan `<source>`, membersihkan format media query, mensterilkan daftar URL pada `srcset`, dan mengeliminasi event handler inline serta skema URI berbahaya.

2. **Sanitasi Elemen Terminal KBD & SAMP (`sanitizer.py`)**:
   - Mengamankan elemen `<kbd>` dan `<samp>` untuk dokumentasi kode terminal, menghapus atribut yang tidak semantik dan mencegah eksekusi skrip berbahaya.

3. **Sanitasi Elemen Meter & Progress Gauge (`sanitizer.py`)**:
   - Mensterilkan elemen indikator visual `<meter>` dan `<progress>`, memvalidasi batas nilai numerik (`value`, `min`, `max`, `low`, `high`, `optimum`), dan menolak payload berbasis event.

4. **Kalkulator Four-Wave Mixing (FWM) Serat Optik DWDM (`parser.py`)**:
   - Menghitung phase mismatch parameter $\Delta\beta$, efisiensi pencampuran $\eta_{\text{fwm}}$, daya crosstalk nonlinier dalam dBm, dan supresi crosstalk dBc untuk menganalisis degradasi kanal DWDM pada dispersi rendah.

5. **Kalkulator Kapasitas Trafik Seluler Erlang B & C (`parser.py`)**:
   - Mengalkulasi probabilitas pemblokiran panggilan Erlang-B secara iteratif, probabilitas antrean Erlang-C, carried traffic dalam Erlang, rata-rata waktu tunggu antrean, dan status Grade of Service (GoS).

6. **Kalkulator Redaman Gas Atmosfer Satelit ITU-R P.676 (`parser.py`)**:
   - Mengalkulasi koefisien redaman spesifik oksigen $\gamma_o$ dan uap air $\gamma_w$ (dB/km), tinggi skala ekuivalen atmosfer, pemetaan cosecant sudut elevasi stasiun bumi, dan redaman total lintasan miring downlink/uplink satelit.

7. **Evaluator Rekognisi MBKM PKM & PIMNAS (`parser.py`)**:
   - Mengevaluasi skor komposit proposal, penilaian kemajuan PKP2, dan presentasi akhir, status kualifikasi kontingen PIMNAS nasional dan perolehan medali, dengan konversi nilai mutu hingga 20 SKS mata kuliah prodi.

8. **Auditor Web App Manifest & PWA Meta (`seo_validator.py`)**:
   - Memvalidasi keberadaan tag `<link rel="manifest">`, atribut mobile viewport responsif, deklarasi `theme-color`, dan ikon aplikasi untuk kesiapan PWA Core Web Vitals.

9. **Auditor Navigasi Pagination Rel Next & Prev (`seo_validator.py`)**:
   - Memeriksa konsistensi deklarasi tautan kanonikal serial pagination `<link rel="next">` dan `<link rel="prev">` guna mengoptimalkan perayapan Googlebot pada arsip multi-halaman.

10. **Auditor Skema HowTo Schema.org (`seo_validator.py`)**:
    - Memverifikasi keberadaan struktur data terstruktur Schema.org HowTo (JSON-LD atau Microdata), kelengkapan langkah instruksional HowToStep, estimasi waktu totalTime, dan atribut HowToSupply/HowToTool.

11. **Auditor Deskripsi Audio & Aksesibilitas Media (`seo_validator.py`)**:
    - Memvalidasi elemen `<audio>` dan `<video>` pada konten multimedia, ketersediaan trek keterangan tertulis `<track kind="captions">` atau deskripsi audio `<track kind="descriptions">` sesuai standar WCAG 2.1 AA.

12. **Komponen Visualisasi Spektrum Kanal DWDM Inline SVG (`components.py`)**:
    - Kartu antarmuka visual diagram alokasi pita spektrum C-Band frekuensi kanal grid ITU DWDM berbasis inline SVG responsif.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Tabel baru `optical_fwm_records`, `erlang_traffic_records`, dan `student_pkm_records` dilengkapi metode CRUD dan indeks terindeksasi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper query `get_user_by_id` dan `get_media_by_slug` untuk pengambilan metadata pengguna dan pustaka media WordPress secara presisi.

15. **Generator HowTo JSON-LD & Eksportir Docusaurus MDX (`exporter.py`)**:
    - Generator Schema.org `HowTo` JSON-LD standar tutorial Google Rich Results dan eksportir format dokumentasi modern MDX Docusaurus.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `fwm`, `erlang`, dan `pimnas` untuk operasionalisasi langsung dari terminal.
