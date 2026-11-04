# Dokumentasi Perubahan Arsitektur v5.4.0 Milestone Release

Siklus pengembangan v5.4.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen gambar responsif `<picture>` dan `<source>` (`sanitize_html5_picture_source_attributes`), sanitasi elemen autocomplete formulir `<datalist>` dan `<option>` (`sanitize_html5_datalist_elements`), serta sanitasi elemen rumus matematika MathML `<math>` dan elemen presentasi formula (`sanitize_html5_mathml_math_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator Optical Signal-to-Noise Ratio (OSNR) dan margin batas Forward Error Correction (FEC) kanal transmisi DWDM ITU-T G.692/G.977 (`calculate_optical_dwdm_osnr_ber_margin`), kalkulator throughput agregasi kanal 5G NR Carrier Aggregation (CA) 3GPP TS 38.306 (`calculate_5g_nr_carrier_aggregation_throughput`), kalkulator Figure of Merit ($G/T$) dan temperatur derau sistem stasiun bumi satelit ITU-R S.733 (`calculate_satellite_g_over_t_system_noise`), serta evaluator proposal mahasiswa Belmawa PKM Penerapan Iptek (PKM-PI) (`parse_pkm_pi_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor audio deskripsi dan teks takarir video WCAG 2.1 SC 1.2.3/1.2.5 (`audit_video_audio_description_and_subtitles`), auditor identifikasi pesan kesalahan formulir berlandaskan atribut ARIA WCAG 2.1 SC 3.3.1 (`audit_form_error_identification_aria`), auditor rasio kontras komponen non-teks dan indikator grafis UI WCAG 2.1 SC 1.4.11 (`audit_non_text_contrast_ratio`), serta auditor strategi eksekusi async/defer skrip pihak ketiga Core Web Vitals (`audit_third_party_script_loading_strategy`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk telemetri OSNR kanal DWDM (`render_optical_dwdm_osnr_card`), kartu kapasitas agregasi 5G NR CA (`render_5g_carrier_aggregation_card`), kartu Figure of Merit ($G/T$) stasiun bumi satelit (`render_satellite_g_over_t_card`), kartu evaluasi proposal alih teknologi PKM-PI Belmawa (`render_pkm_pi_proposal_card`), dan diagram vektor inline SVG responsif alokasi spektrum 5G NR CA (`render_5g_carrier_aggregation_spectrum_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri kualitas kanal serat optik DWDM (`format_optical_dwdm_telegram`) dan pengumuman capaian kelulusan pendanaan penerapan iptek mahasiswa PKM-PI (`format_pkm_pi_telegram`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `optical_dwdm_records`, `nr_ca_records`, dan `pkm_pi_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca komentar batch berdasarkan daftar ID numerik `get_comments_by_ids` dan helper pembaruan massal status moderasi komentar `batch_update_comment_status` via REST API `/wp/v2/comments`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org TechArticle & HowTo JSON-LD untuk panduan alih teknologi implementasi mahasiswa (`generate_tech_transfer_how_to_json_ld`) dan eksportir dokumentasi rute fullstack SolidStart reactive framework (`to_solidstart_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `dwdm`, `ca`, dan `pkmpi` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga melampaui 1.030 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Responsive Picture & Source `<picture>` / `<source>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_picture_source_attributes` memvalidasi atribut kontrol sumber gambar (`srcset`, `media`, `type`), mensterilkan skrip berbahaya, membersihkan ekspresi CSS berbahaya pada media query, dan membatasi tipe MIME hanya pada gambar yang aman (`image/webp`, `image/avif`, `image/jpeg`, dll.).

2. **Sanitasi Autocomplete Elemen Datalist `<datalist>` & `<option>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_datalist_elements` memvalidasi kontainer `<datalist>` beserta opsi `<option>`, mensterilkan atribut event handler, memblokir DOM clobbering pada atribut identifier `id`, dan membersihkan payload skrip pada nilai atribut `value` dan `label`.

3. **Sanitasi Formula Matematika MathML `<math>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_mathml_math_elements` mensterilkan kontainer MathML `<math>` dan elemen presentasi matematika (`<mrow>`, `<mi>`, `<mo>`, `<mn>`, `<msup>`, `<mfrac>`), memblokir skrip tersembunyi pada blok `<annotation-xml>`, menetralkan atribut link `href` / `xlink:href`, dan memvalidasi atribut `display`.

4. **Kalkulator OSNR & Margin FEC Kanal Optik DWDM ITU-T G.692/G.977 (`parser.py`)**:
   - Metode `calculate_optical_dwdm_osnr_ber_margin` mengevaluasi rasio daya sinyal terhadap akumulasi derau ASE dalam lebar pita referensi 0.1 nm, menghitung margin headroom di atas ambang batas deteksi koreksi kesalahan FEC, estimasi faktor kualitas $Q$, dan probabilitas Bit Error Rate (BER) sebelum FEC.

5. **Kalkulator Throughput 5G NR Carrier Aggregation (CA) 3GPP TS 38.306 (`parser.py`)**:
   - Metode `calculate_5g_nr_carrier_aggregation_throughput` mengalkulasi laju data puncak teoritis gabungan Primary Cell (PCell) dan Secondary Cells (SCells) berdasarkan alokasi PRB, tingkat modulasi hingga 256/1024-QAM, lapisan spasial MIMO 4x4, durasi slot OFDM 14 simbol, dan rasio overhead kontrol radio.

6. **Kalkulator Figure of Merit $G/T$ Stasiun Bumi Satelit ITU-R S.733 (`parser.py`)**:
   - Metode `calculate_satellite_g_over_t_system_noise` menghitung penguatan antena parabola ($G$), temperatur derau antena pada sudut elevasi stasiun bumi ($T_a$), penalti redaman feed, temperatur derau LNA, total derau sistem ($T_{\text{sys}}$), dan rasio kelayakan $G/T$ dalam satuan dB/K.

7. **Evaluator Proposal Mahasiswa Belmawa PKM Penerapan Iptek (PKM-PI) (`parser.py`)**:
   - Metode `parse_pkm_pi_proposal_evaluation` mengkuantifikasi penilaian proposal alih teknologi mahasiswa ke mitra produktif UMKM/industri (diagnosis permasalahan 25%, ketepatan solusi teknologi 35%, peningkatan produktivitas 25%, efisiensi anggaran 15%), penentuan pendanaan Belmawa Dikti, dan konversi SKS MBKM.

8. **Auditor Audio Deskripsi & Subtitle Video WCAG 2.1 SC 1.2.3/1.2.5 (`seo_validator.py`)**:
   - Metode `audit_video_audio_description_and_subtitles` memvalidasi kehadiran trek narasi audio deskripsi (`<track kind="descriptions">`) atau atribut `aria-describedby` serta ketersediaan takarir sinkron untuk pengguna berkebutuhan khusus.

9. **Auditor Pesan Kesalahan Formulir ARIA WCAG 2.1 SC 3.3.1 (`seo_validator.py`)**:
   - Metode `audit_form_error_identification_aria` memeriksa kepatuhan aksesibilitas elemen kontrol input yang berstatus `aria-invalid="true"`, memastikan tautan keterbacaan pesan kesalahan melalui `aria-errormessage` atau `aria-describedby` ke elemen DOM yang valid.

10. **Auditor Rasio Kontras Non-Teks UI Komponen WCAG 2.1 SC 1.4.11 (`seo_validator.py`)**:
    - Metode `audit_non_text_contrast_ratio` menguji batas visual tombol, ikon grafis, dan elemen interaktif lainnya terhadap warna latar belakang yang berdekatan dengan batas rasio kontras minimum 3.0:1.

11. **Auditor Pemuatan Skrip Pihak Ketiga Async/Defer Core Web Vitals (`seo_validator.py`)**:
    - Metode `audit_third_party_script_loading_strategy` memverifikasi seluruh dependensi skrip eksternal pihak ketiga agar menggunakan atribut `async` atau `defer`, mencegah penghambatan rendering antarmuka pengguna (parser-blocking).

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_dwdm_osnr_card`, `render_5g_carrier_aggregation_card`, `render_satellite_g_over_t_card`, `render_pkm_pi_proposal_card`, dan `render_5g_carrier_aggregation_spectrum_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_optical_dwdm_telegram` dan `format_pkm_pi_telegram`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `optical_dwdm_records`, `nr_ca_records`, dan `pkm_pi_proposal_records` dengan indeks pencarian teroptimasi.

15. **Integrasi WordPress REST API (`wordpress_client.py`)**:
    - Implementasi `get_comments_by_ids` untuk pembacaan batch komentar dan `batch_update_comment_status` untuk pembaruan status moderasi komentar secara massal.

16. **Generator Schema.org & Dokumentasi MDX Modern (`exporter.py`)**:
    - Implementasi `generate_tech_transfer_how_to_json_ld` untuk panduan implementasi alih teknologi mahasiswa dan `to_solidstart_mdx` untuk integrasi dokumentasi SolidStart reactive framework.

17. **Perintah Konsol CLI (`cli.py`)**:
    - Subcommand baru `dwdm`, `ca`, dan `pkmpi` dengan dukungan flag `--action list` dan `--action add`.

---

## Verifikasi Pengujian Unit
- Total unit test: **1.030 unit tests passing** (100% pass rate).
- Waktu eksekusi: **~14.5 detik**.
