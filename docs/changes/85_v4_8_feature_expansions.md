# Dokumentasi Perubahan Arsitektur v4.8.0 Milestone Release

Siklus pengembangan v4.8.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen kontrol tombol HTML5 `<button>` dengan pembatasan tipe aman (`button`, `submit`, `reset`) dan pembersihan parameter aksi URL `formaction` (`sanitize_html5_button_attributes`), sanitasi peta area navigasi `<map>` dan `<area>` dengan validasi bentuk `shape`, koordinat numerik `coords`, dan penegakan atribut teks alternatif aksesibilitas WCAG 2.1 (`sanitize_html5_area_map_attributes`), serta sanitasi atribut daftar HTML5 `<ol>`, `<ul>`, dan `<li>` dengan verifikasi tipe dan nilai numerik (`sanitize_html5_list_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator pergeseran fase nonlinier Cross-Phase Modulation (XPM) dan faktor reduksi dispersi walk-off pada sistem transmisi DWDM menurut teori optika nonlinier Agrawal (`calculate_optical_xpm_phase_shift`), kalkulator penguatan susunan beamforming dan kapasitas lapisan spasial 5G NR Massive MIMO menurut spesifikasi 3GPP TS 38.211 / TR 38.901 (`calculate_5g_nr_massive_mimo_gain`), kalkulator redaman gas atmosferik oksigen ($O_2$) dan uap air ($H_2O$) propagasi satelit bumi-angkasa menurut rekomendasi ITU-R P.676-12 (`calculate_satellite_gaseous_attenuation_itu_r_p676`), serta evaluator seleksi kelayakan proposal riset dan inovasi mahasiswa Program Kreativitas Mahasiswa (PKM) Simbelmawa Kemendikbudristek (`parse_pkm_proposal_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor penanda data terstruktur Schema.org `ScholarlyArticle` / `TechArticle` untuk artikel publikasi ilmiah dan tugas akhir skripsi mahasiswa (`audit_scholarly_article_schema`), auditor kepatuhan isolasi asal silang (Cross-Origin Isolation) meta COOP (`same-origin`) dan COEP (`require-corp` / `credentialless`) untuk eksekusi simulasi WebAssembly berkecepatan tinggi (`audit_coop_coep_cross_origin_isolation`), auditor aksesibilitas animasi CSS terhadap preferensi gerak tereduksi pengguna `@media (prefers-reduced-motion: reduce)` sesuai WCAG 2.1 SC 2.3.3 (`audit_prefers_reduced_motion_media`), serta auditor penanda kejelasan format tautan dokumen unduhan eksternal PDF/DOCX/ZIP sesuai WCAG 2.1 SC 3.2.4 (`audit_pdf_link_indicators`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri pergeseran fase nonlinier XPM dan panjang walk-off serat optik (`render_optical_xpm_card`), kartu penguatan planar array beamforming dan EIRP 5G NR Massive MIMO (`render_5g_nr_massive_mimo_card`), kartu evaluasi transparansi gelombang mikro redaman gas atmosfer satelit ITU-R P.676 (`render_satellite_gaseous_attenuation_card`), kartu capaian kelulusan dan pendanaan proposal PKM Simbelmawa (`render_pkm_proposal_card`), serta kartu visualisasi diagram polar kemudi berkas radiasi (beam steering) 5G NR Massive MIMO berbasis inline SVG responsif (`render_5g_nr_mimo_beam_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan telemetri redaman gas atmosfer satelit ITU-R P.676 (`format_satellite_gaseous_attenuation_telegram`) dan format pengumuman kelulusan pendanaan proposal PKM Simbelmawa (`format_pkm_proposal_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit redaman gas atmosfer satelit (`satellite_gaseous_records`), tabel rekam penguatan planar array 5G NR Massive MIMO (`nr_massive_mimo_records`), serta tabel rekam evaluasi & pendanaan proposal PKM mahasiswa (`pkm_proposal_records`).
- **Klien WordPress REST API**: Helper pembaca komentar moderasi berdasarkan status (`get_comments_by_status`) dan helper pembaruan massal status komentar editorial (`bulk_update_comment_status`) via endpoint `/wp/v2/comments`.
- **Generator Statis & Ekspor**: Generator Schema.org `SoftwareApplication` JSON-LD untuk perangkat lunak simulator rekayasa telekomunikasi prodi (`generate_software_application_json_ld`) serta eksportir dokumentasi framework modern Deno Fresh Islands MDX (`to_fresh_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `gas`, `massive_mimo`, dan `pkm_proposal`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 845 menjadi 872 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Kontrol Tombol `<button>` (`sanitizer.py`)**:
   - Memvalidasi elemen `<button>`, mensterilkan atribut `type` (hanya mengizinkan `button`, `submit`, `reset`), menolak skema URL berbahaya pada atribut `formaction` (`javascript:`, `data:`), serta membersihkan event handler inline dan atribut style rentan.

2. **Sanitasi Peta Area Navigasi `<area>` (`sanitizer.py`)**:
   - Memvalidasi elemen navigasi grafis `<map>` dan `<area>`, memastikan bentuk `shape` sah (`rect`, `circle`, `poly`), membersihkan koordinat numerik `coords`, mensterilkan URL `href`, serta menegakkan atribut teks alternatif `alt` untuk aksesibilitas tunanetra WCAG 2.1 SC 1.1.1.

3. **Sanitasi Atribut Elemen Daftar `<ol>`, `<ul>`, `<li>` (`sanitizer.py`)**:
   - Mensterilkan atribut daftar berurutan dan tidak berurutan, memvalidasi integritas nilai numerik `start` dan tipe `type` pada `<ol>`, serta nomor urut `value` pada `<li>`.

4. **Kalkulator Pergeseran Fase Nonlinier Cross-Phase Modulation (XPM) (`parser.py`)**:
   - Menghitung panjang efektif $L_{\text{eff}}$, parameter dispersi walk-off $d_{12} = D \cdot \Delta\lambda$, panjang interaksi pulsa walk-off $L_w = T_0 / |d_{12}|$, faktor supresi $\eta_{\text{XPM}} = 1/\sqrt{1 + (L_{\text{eff}}/L_w)^2}$, akumulasi pergeseran fase efektif $\phi_{\text{XPM,eff}} = 2\gamma P_{\text{pump}} L_{\text{eff}} \eta_{\text{XPM}}$, dan evaluasi penalti interferensi kanal pada jaringan transmisi DWDM berkecepatan tinggi.

5. **Kalkulator Penguatan Susunan 5G NR Massive MIMO 3GPP TS 38.211 (`parser.py`)**:
   - Menghitung penguatan koheren array beamforming $G_{\text{array}} = 10\log_{10}(M \cdot N)$ dBi untuk konfigurasi planar array $M \times N \times P$ (misal 64 hingga 128 elemen antena), estimasi Half-Power Beamwidth (HPBW) azimuth dan elevasi, Equivalent Isotropically Radiated Power (EIRP dBm dan Watt), serta batas kapasitas rank transmisi spatial multiplexing.

6. **Kalkulator Redaman Gas Atmosfer Satelit ITU-R P.676-12 (`parser.py`)**:
   - Menghitung koefisien serapan spesifik udara kering (resonansi oksigen $O_2$ di sekitar 60 GHz) $\gamma_o$ dB/km dan uap air ($H_2O$ di frekuensi 22.2 GHz) $\gamma_w$ dB/km pada rentang frekuensi 1–350 GHz, ketinggian skala ekivalen atmosfer $h_o$ dan $h_w$, total redaman zenith, dan redaman lintasan miring stasiun bumi (slant path attenuation $A_g$) di iklim tropis berkelembapan tinggi.

7. **Evaluator Seleksi Proposal Mahasiswa PKM Simbelmawa Kemendikbudristek (`parser.py`)**:
   - Mengevaluasi skor seleksi proposal Program Kreativitas Mahasiswa (PKM 8 Bidang & AI/GT) berdasarkan bobot penilaian nasional: 30% orisinalitas/kreativitas, 35% ketepatan metodologi & rancangan rekayasa, 20% potensi luaran publikasi/paten, dan 15% kelayakan tim & RAB, serta konversi rekognisi kurikulum hingga 4 SKS mata kuliah prodi.

8. **Auditor Skema ScholarlyArticle Schema.org (`seo_validator.py`)**:
   - Memvalidasi keberadaan penanda data terstruktur Schema.org `ScholarlyArticle` / `TechArticle` (JSON-LD atau Microdata) untuk publikasi repositori karya ilmiah dosen, hasil riset lab, dan naskah skripsi mahasiswa guna memperkuat sinyal E-E-A-T Google Scholar.

9. **Auditor Isolasi Asal Silang (COOP & COEP) WebAssembly (`seo_validator.py`)**:
   - Mengaudit keberadaan meta header `Cross-Origin-Opener-Policy` (COOP) dan `Cross-Origin-Embedder-Policy` (COEP) untuk menjamin pemenuhan lingkungan isolated process browser yang disyaratkan saat menjalankan simulator antena berbasis WebAssembly (Wasm) dan multi-threaded Web Workers.

10. **Auditor Aksesibilitas Animasi Prefers-Reduced-Motion WCAG 2.1 (`seo_validator.py`)**:
    - Mengaudit lembar gaya CSS terhadap deklarasi media query `@media (prefers-reduced-motion: reduce)` guna melindungi pengguna penderita gangguan vestibular dari animasi transisi yang berlebihan sesuai kriteria sukses WCAG 2.1 SC 2.3.3.

11. **Auditor Indikator Tautan Berkas Unduhan Dokumen & PDF (`seo_validator.py`)**:
    - Memverifikasi tautan dokumen biner non-HTML (`.pdf`, `.docx`, `.xlsx`, `.zip`) terhadap kewajiban pencantuman teks indikator ekstensi atau label aksesibilitas aria-label untuk menjamin kepatuhan WCAG 2.1 SC 3.2.4.

12. **Komponen Visualisasi Kemudi Berkas 5G NR Massive MIMO Inline SVG (`components.py`)**:
    - Kartu visualisasi representasi grafis pola radiasi antena beamforming 5G NR menampilkan main beam lobe dengan sudut kemudi terarah, Half-Power Beamwidth (HPBW), pelemahan sidelobe, dan alokasi multi-user spatial beams berbasis inline SVG responsif.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Skema tabel database `satellite_gaseous_records`, `nr_massive_mimo_records`, dan `pkm_proposal_records` dilengkapi metode CRUD terindeks untuk persistensi data operasional prodi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper pembaca antrean moderasi komentar berdasarkan status `get_comments_by_status` dan pembaruan massal `bulk_update_comment_status` via REST API endpoint `/wp/v2/comments`.

15. **Generator SoftwareApplication JSON-LD & Eksportir Fresh MDX (`exporter.py`)**:
    - Generator Schema.org `SoftwareApplication` JSON-LD untuk perangkat lunak simulator prodi dan eksportir format dokumentasi Deno Fresh (Islands Architecture) MDX dengan frontmatter YAML terintegrasi.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `gas`, `massive_mimo`, dan `pkm_proposal` untuk operasionalisasi langsung dari terminal CLI.
