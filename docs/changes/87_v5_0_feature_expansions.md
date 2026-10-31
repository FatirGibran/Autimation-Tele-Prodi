# Dokumentasi Perubahan Arsitektur v5.0.0 Milestone Release

Siklus pengembangan v5.0.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen waktu semantik HTML5 `<time>` (`sanitize_html5_time_attributes`), sanitasi elemen kontainer media gambar responsif HTML5 `<picture>` dan anak elemen `<source>` (`sanitize_html5_picture_attributes`), serta sanitasi elemen modal dialog HTML5 `<dialog>` dan binding aksesibilitas atribut ARIA (`sanitize_html5_dialog_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator ambang daya nonlinear hamburan balik Stimulated Brillouin Scattering (SBS) transmisi serat optik DWDM menurut teori Govind P. Agrawal (`calculate_optical_sbs_threshold`), penganalisis zero-interruption handover 5G NR Dual Active Protocol Stack (DAPS) menurut spesifikasi 3GPP Rel-16 TS 38.300 / TS 38.323 (`calculate_5g_nr_daps_handover`), kalkulator indeks sintilasi ionosferik $S_4$ dan kedalaman pudar sinyal radio satelit ITU-R P.531 (`calculate_satellite_ionospheric_scintillation_s4_itu_r_p531`), serta evaluator proposal rekayasa sosio-teknologi pemberdayaan pedesaan mahasiswa Innovillage Telkom Indonesia (`parse_innovillage_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor struktur aksesibilitas tabel data HTML5 `<caption>` dan `<th scope>` WCAG 2.1 SC 1.3.1 (`audit_table_caption_and_scope`), auditor direktif delegasi peramban Client Hints `Accept-CH` (`audit_client_hints_meta`), auditor kelengkapan atribut bahasa ISO `lang` dan arah teks `dir` WCAG 2.1 SC 3.1.1 (`audit_document_language_and_dir`), serta auditor pemuatan spekulatif peramban DNS prefetch, preconnect, dan W3C Speculation Rules (`audit_dns_prefetch_and_prerender`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk telemetri ambang SBS serat optik (`render_optical_sbs_card`), kartu performansi zero-interruption handover 5G NR DAPS (`render_nr_daps_card`), kartu redaman sintilasi ionosferik satelit $S_4$ ITU-R P.531 (`render_satellite_s4_scintillation_card`), kartu kelulusan pendanaan proposal Innovillage Telkom (`render_innovillage_proposal_card`), dan diagram arsitektur dual stack protokol 5G NR DAPS berbasis inline SVG responsif (`render_nr_daps_dual_stack_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri mitigasi nonlinearitas SBS optik (`format_optical_sbs_telegram_card`) dan pengumuman kelulusan pendanaan proposal mahasiswa Innovillage (`format_innovillage_telegram_card`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `optical_sbs_records`, `nr_daps_records`, dan `innovillage_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca sub-kategori hierarkis berdasarkan ID induk `get_categories_by_parent` dan penghapusan massal pos ke tempat sampah `batch_trash_posts` via `/wp/v2/posts`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org Event/Hackathon JSON-LD untuk kompetisi inovasi mahasiswa (`generate_student_competition_json_ld`) dan eksportir dokumentasi rute fine-grained reactive framework modern SolidStart MDX (`to_solidstart_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `sbs`, `daps`, dan `innovillage` untuk operasionalisasi langsung dari terminal.

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Waktu Semantik `<time>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_time_attributes` memvalidasi atribut tanggal/waktu ISO 8601 (`datetime`) dan flag boolean penerbitan artikel `pubdate`, sekaligus mensterilkan muatan skrip berbahaya.

2. **Sanitasi Elemen Gambar Responsif `<picture>` & `<source>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_picture_attributes` memvalidasi URL pada `srcset`, memeriksa media query aman pada atribut `media`, membatasi MIME type gambar modern pada `type` (seperti `image/webp` dan `image/avif`), serta memvalidasi atribut dimensi `sizes`.

3. **Sanitasi Elemen Modal Dialog HTML5 `<dialog>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_dialog_attributes` mensterilkan elemen dialog interaktif, mengelola atribut boolean `open`, dan memvalidasi binding aksesibilitas ARIA (`aria-modal`, `aria-labelledby`, `aria-describedby`) guna mengantisipasi risiko clickjacking dan DOM entrapment.

4. **Kalkulator Ambang Daya SBS Optik DWDM (`parser.py`)**:
   - Metode `calculate_optical_sbs_threshold` menghitung panjang efektif serat $L_{\text{eff}} = \frac{1 - e^{-\alpha L}}{\alpha}$, pergeseran frekuensi Brillouin $\Omega_B \approx 11$ GHz, linewidth enhancement factor, daya ambang $P_{\text{th}} \approx \frac{21 A_{\text{eff}}}{g_B L_{\text{eff}}} (1 + \frac{\Delta\nu_L}{\Delta\nu_B})$ dalam mW dan dBm, serta mengklasifikasikan risiko hamburan balik Stokes dalam jaringan DWDM.

5. **Penganalisis Handover 5G NR DAPS 3GPP Rel-16 (`parser.py`)**:
   - Metode `calculate_5g_nr_daps_handover` mengevaluasi perbedaan latensi interupsi tradisional (30-50 ms) vs DAPS (0.0 ms), estimasi kebutuhan ukuran buffer PDCP dual stack, dan keandalan transmisi layanan ultra-reliable (99.999%).

6. **Kalkulator Sintilasi Ionosferik Satelit $S_4$ ITU-R P.531 (`parser.py`)**:
   - Metode `calculate_satellite_ionospheric_scintillation_s4_itu_r_p531` menghitung deviasi fluktuasi intensitas radio $S_4$, tingkat keparahan turbulensi plasma ionosfer, dan kedalaman pudar sinyal (fade depth dB) menurut distribusi statistik Nakagami-m.

7. **Evaluator Proposal Sosio-Teknologi Innovillage Telkom (`parser.py`)**:
   - Metode `parse_innovillage_proposal_evaluation` mengkuantifikasi penilaian proposal pengabdian mahasiswa berbasis bobot standar nasional, menentukan kelulusan pendanaan Innovillage Telkom, alokasi dana hibah IDR, dan ekuivalensi konversi 4 SKS MBKM.

8. **Auditor Aksesibilitas Tabel HTML `<caption>` & `<th scope>` (`seo_validator.py`)**:
   - Metode `audit_table_caption_and_scope` mengaudit tabel dalam konten editorial untuk memastikan pemenuhan kriteria WCAG 2.1 SC 1.3.1 (Info and Relationships).

9. **Auditor Direktif Browser Client Hints (`seo_validator.py`)**:
   - Metode `audit_client_hints_meta` memverifikasi kehadiran direktif `Accept-CH` dan delegasi privasi `Permissions-Policy` untuk optimasi perenderan aset Core Web Vitals.

10. **Auditor Atribut Bahasa & Arah Dokumen WCAG 2.1 SC 3.1.1 (`seo_validator.py`)**:
    - Metode `audit_document_language_and_dir` memverifikasi atribut `lang` dan `dir` pada kontainer dokumen utama.

11. **Auditor Pemuatan Spekulatif Peramban (`seo_validator.py`)**:
    - Metode `audit_dns_prefetch_and_prerender` memeriksa penerapan resource hints DNS prefetch, preconnect, dan script W3C Speculation Rules.

12. **Visualisasi Kartu Elementor & Diagram Arsitektur Inline SVG (`components.py`)**:
    - Komponen `render_optical_sbs_card`, `render_nr_daps_card`, `render_satellite_s4_scintillation_card`, `render_innovillage_proposal_card`, dan diagram vektor interaktif responsif `render_nr_daps_dual_stack_svg`.

13. **Format Buletin Notifikasi Telegram (`formatters.py`)**:
    - Formatter `format_optical_sbs_telegram_card` dan `format_innovillage_telegram_card` untuk publikasi otomatis telemetri jaringan optik dan kabar pendanaan mahasiswa ke kanal Telegram editorial.

14. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Skema tabel database `optical_sbs_records`, `nr_daps_records`, dan `innovillage_proposal_records` disertai indeks performa dan operasi query terisolasi.

15. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Metode `get_categories_by_parent` untuk mengelompokkan kategori anak secara hierarkis dan `batch_trash_posts` untuk pembersihan atau pengarsipan pos massal ke tong sampah WordPress.

16. **Generator Data Terstruktur Schema.org & Eksportir MDX SolidStart (`exporter.py`)**:
    - Metode `generate_student_competition_json_ld` menghasilkan struktur metadata Google Event/Hackathon untuk kompetisi mahasiswa, dan metode `to_solidstart_mdx` mengekspor artikel editorial ke format reactive framework SolidStart MDX dengan frontmatter terintegrasi.

17. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `sbs`, `daps`, dan `innovillage` untuk kemudahan pengoperasian langsung dari terminal sistem operasi.
