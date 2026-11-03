# Dokumentasi Perubahan Arsitektur v5.2.0 Milestone Release

Siklus pengembangan v5.2.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen video track `<track>` untuk subtitle, caption, dan deskripsi media (`sanitize_html5_video_track_attributes`), sanitasi elemen disclosure `<details>` dan `<summary>` (`sanitize_html5_details_summary_attributes`), serta sanitasi elemen Web Components modern `<template>` dan `<slot>` (`sanitize_html5_template_slot_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator rugi-rugi insersi dan crosstalk isolasi Optical Wavelength Selective Switch (WSS) / Optical Cross-Connect (OXC) ROADM (`calculate_optical_wss_oxc_insertion_loss`), kalkulator 3GPP Rel-15/16 5G NR Timing Advance (TA) dan estimasi jarak propagasi radio UE (`calculate_5g_nr_timing_advance_distance`), kalkulator redaman propagasi hujan satelit bumi ITU-R P.618 (`calculate_satellite_rain_attenuation_itu_r_p618`), serta evaluator proposal penelitian mahasiswa Belmawa PKM Riset Eksakta (PKM-RE) (`parse_pkm_re_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor urutan hierarki heading dan deteksi lonjakan tingkat heading tanpa runtut menurut WCAG 2.1 SC 1.3.1 (`audit_heading_hierarchy_sequence`), auditor struktur daftar semantik `<ul>`/`<ol>` dan elemen yatim piatu (`audit_semantic_list_structure`), auditor transkrip dan caption trek media audio/video menurut WCAG 2.1 SC 1.2.2 (`audit_media_transcript_and_captions`), serta auditor web font preload dan font-display swap Core Web Vitals (`audit_web_font_preload_and_display`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk telemetri rugi-rugi optical WSS/OXC ROADM (`render_optical_wss_oxc_card`), kartu estimasi jarak 5G NR Timing Advance (`render_5g_timing_advance_card`), kartu redaman hujan satelit ITU-R P.618 (`render_satellite_rain_attenuation_card`), kartu evaluasi proposal mahasiswa PKM-RE Belmawa (`render_pkm_re_proposal_card`), dan diagram vektor inline SVG responsif propagasi 5G NR Timing Advance RTT (`render_5g_timing_advance_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri rugi-rugi optik ROADM WSS (`format_optical_wss_telegram_card`) dan pengumuman capaian kelulusan pendanaan riset mahasiswa PKM-RE (`format_pkm_re_telegram_card`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `optical_wss_oxc_records`, `nr_timing_advance_records`, dan `pkm_re_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca media batch berdasarkan daftar ID numerik `get_media_by_ids` dan helper pembaruan massal takarir gambar `batch_update_media_captions` via REST API `/wp/v2/media`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org ScholarlyArticle JSON-LD untuk publikasi riset akademik mahasiswa (`generate_scholarly_article_json_ld`) dan eksportir dokumentasi rute fullstack AnalogJS Angular meta-framework (`to_angular_analog_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `wss`, `ta`, dan `pkmre` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga mencapai 979 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Track Subtitle & Caption `<track>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_video_track_attributes` memvalidasi atribut kontrol trek (`kind`, `src`, `srclang`, `label`, `default`) dan mensterilkan skrip berbahaya atau URI javascript.

2. **Sanitasi Elemen Rincian HTML5 `<details>` & `<summary>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_details_summary_attributes` memvalidasi atribut `open` dan `name`, memastikan keberadaan anak elemen `<summary>`, dan mencegah manipulasi DOM.

3. **Sanitasi Web Components `<template>` & `<slot>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_template_slot_elements` memvalidasi atribut `name` pada slot, mensterilkan konten template, dan memblokir DOM clobbering.

4. **Kalkulator Rugi-Rugi Optical WSS / OXC ROADM (`parser.py`)**:
   - Metode `calculate_optical_wss_oxc_insertion_loss` mengevaluasi rugi-rugi insersi matriks, penalti degree ROADM, polarisasi dependent loss (PDL), crosstalk port isolation, dan penalti degradasi OSNR.

5. **Kalkulator 5G NR Timing Advance & Jarak Propagasi Radio (`parser.py`)**:
   - Metode `calculate_5g_nr_timing_advance_distance` mengalkulasi durasi Timing Advance menurut spesifikasi 3GPP Rel-15/16, round-trip time (RTT), keterlambatan satu arah, estimasi jarak UE, dan penentuan zona sel.

6. **Kalkulator Redaman Hujan Satelit ITU-R P.618 (`parser.py`)**:
   - Metode `calculate_satellite_rain_attenuation_itu_r_p618` menghitung redaman spesifik curah hujan, lintasan miring efektif stasiun bumi, faktor reduksi lintasan horizontal, dan ambang batas fade margin.

7. **Evaluator Proposal Mahasiswa PKM Riset Eksakta (PKM-RE) (`parser.py`)**:
   - Metode `parse_pkm_re_proposal_evaluation` mengkuantifikasi penilaian proposal penelitian mahasiswa (kebaruan 30%, metodologi 35%, kelayakan luaran jurnal/paten 20%, efisiensi RAB 15%), penentuan pendanaan, dan konversi SKS MBKM.

8. **Auditor Urutan Hierarki Heading WCAG 2.1 (`seo_validator.py`)**:
   - Metode `audit_heading_hierarchy_sequence` memverifikasi struktur heading bertingkat (H1 ke H6), memastikan keberadaan H1 tunggal, dan mendeteksi lonjakan tingkat heading yang membingungkan screen reader.

9. **Auditor Struktur Daftar Semantik WCAG 2.1 (`seo_validator.py`)**:
   - Metode `audit_semantic_list_structure` memeriksa validitas anak langsung elemen `<ul>` dan `<ol>` (`<li>`), mendeteksi elemen daftar kosong, dan mendeteksi elemen `<li>` yatim piatu di luar daftar.

10. **Auditor Transkrip & Trek Takarir Media WCAG 2.1 (`seo_validator.py`)**:
    - Metode `audit_media_transcript_and_captions` memvalidasi ketersediaan transkrip tekstual atau trek takarir `<track kind="captions">` pada elemen `<video>` dan `<audio>`.

11. **Auditor Web Font Preload & Font Display Swap (`seo_validator.py`)**:
    - Metode `audit_web_font_preload_and_display` memverifikasi deklarasi preload sumber daya web font (`rel="preload" as="font"`) dan parameter rendering teks `font-display: swap` untuk mencegah FOIT.

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_wss_oxc_card`, `render_5g_timing_advance_card`, `render_satellite_rain_attenuation_card`, `render_pkm_re_proposal_card`, dan `render_5g_timing_advance_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_optical_wss_telegram_card` dan `format_pkm_re_telegram_card`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `optical_wss_oxc_records`, `nr_timing_advance_records`, dan `pkm_re_proposal_records` dengan indeks pencarian teroptimasi.

15. **Integrasi WordPress REST API (`wordpress_client.py`)**:
    - Implementasi `get_media_by_ids` untuk pembacaan batch lampiran media dan `batch_update_media_captions` untuk pembaruan massal takarir gambar.

16. **Generator Schema.org & Dokumentasi MDX Modern (`exporter.py`)**:
    - Implementasi `generate_scholarly_article_json_ld` untuk artikel riset akademik mahasiswa dan `to_angular_analog_mdx` untuk integrasi dokumentasi AnalogJS Angular.

17. **Perintah Konsol CLI (`cli.py`)**:
    - Subcommand baru `wss`, `ta`, dan `pkmre` dengan dukungan flag `--action list` dan `--action add`.

---

## Verifikasi Pengujian Unit
- Total unit test: **979 unit tests passing** (100% pass rate).
- Waktu eksekusi: **~13.7 detik**.
