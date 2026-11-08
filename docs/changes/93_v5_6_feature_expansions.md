# Dokumentasi Perubahan Arsitektur v5.6.0 Milestone Release

Siklus pengembangan v5.6.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi kontrol interaktif formulir pemilihan `<select>` dan `<optgroup>` (`sanitize_html5_select_optgroup_attributes`), sanitasi elemen media akademik `<figure>` dan `<figcaption>` (`sanitize_html5_figure_figcaption_attributes`), serta sanitasi pengelompokan teknis `<fieldset>` dan `<legend>` (`sanitize_html5_fieldset_legend_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator ambang batas hamburan Brillouin terdorong Stimulated Brillouin Scattering (SBS) serat optik (`calculate_optical_sbs_threshold_power`), kalkulator kapasitas multiplexing dan sounding coverage 5G NR Sounding Reference Signal (SRS) 3GPP TS 38.211 (`calculate_5g_nr_srs_capacity_and_coverage`), kalkulator indeks sintilasi ionosfer S4 dan margin redaman satelit ITU-R P.531 (`calculate_satellite_ionospheric_scintillation_s4_itu_r_p531`), serta evaluator proposal mahasiswa Belmawa PKM Video Gagasan Konstruktif (PKM-VGK) (`parse_pkm_vgk_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor struktur skema navigasi remah roti breadcrumb list WCAG 2.1 (`audit_breadcrumb_navigation_schema`), auditor transkrip teks dan deskripsi audio multimedia WCAG 2.1 SC 1.2.1 (`audit_audio_media_transcripts`), auditor token atribut autocomplete isian formulir WCAG 2.1 SC 1.3.5 (`audit_form_input_autocomplete_tokens`), serta auditor keamanan atribut rel tautan eksternal target blank (`audit_external_link_security_attributes`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk ambang batas nonlinear SBS optik (`render_optical_sbs_threshold_card`), kartu kapasitas sounding 5G NR SRS (`render_5g_srs_sounding_card`), kartu sintilasi ionosfer satelit S4 ITU-R P.531 (`render_satellite_ionospheric_scintillation_card`), kartu evaluasi proposal PKM-VGK Belmawa (`render_pkm_vgk_proposal_card`), dan diagram vektor inline SVG responsif pola sisir subcarrier comb interleaving dan slot timing 5G NR SRS (`render_5g_srs_comb_pattern_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri kapasitas sounding 5G NR SRS (`format_5g_nr_srs_telegram`) dan pengumuman capaian kelulusan pendanaan video gagasan konstruktif mahasiswa PKM-VGK (`format_pkm_vgk_telegram`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `satellite_ionospheric_scintillation_records`, `nr_srs_records`, dan `pkm_vgk_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca tag batch berdasarkan daftar ID numerik `get_tags_by_ids` dan helper pembaruan massal deskripsi taksonomi kategori `batch_update_category_descriptions` via REST API `/wp/v2/categories`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org VideoObject JSON-LD untuk video gagasan konstruktif mahasiswa PKM-VGK SDGs (`generate_constructive_video_json_ld`) dan eksportir dokumentasi fullstack RedwoodJS React MDX (`to_redwoodjs_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `ionoscint`, `nrsrs`, dan `pkmvgk` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga melampaui 1.090 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Select & Optgroup Interactive Controls (`sanitizer.py`)**:
   - Metode `sanitize_html5_select_optgroup_attributes` memvalidasi atribut kontrol formulir (`size` integer positif, pembersihan atribut label), mensterilkan event handler skrip inline (`onchange`, `onfocus`, dll.), serta memblokir payload berbahaya pada elemen opsi seleksi.

2. **Sanitasi HTML5 Figure & Figcaption Media Elements (`sanitizer.py`)**:
   - Metode `sanitize_html5_figure_figcaption_attributes` mensterilkan atribut berbahaya pada elemen gambar akademik, diagram, dan takarir keterangan gambar, memblokir `contenteditable` dan inline event handler.

3. **Sanitasi HTML5 Fieldset & Legend Form Grouping Elements (`sanitizer.py`)**:
   - Metode `sanitize_html5_fieldset_legend_attributes` menetralkan inline styling dan event handler berbahaya pada kontainer pengelompokan formulir teknis.

4. **Kalkulator Ambang Batas SBS Serat Optik (`parser.py`)**:
   - Metode `calculate_optical_sbs_threshold_power` menghitung daya ambang batas Stimulated Brillouin Scattering (SBS) berdasarkan model Smith, menghitung panjang interaksi efektif $L_{eff}$, pelebaran spektral linewidth laser $\Delta\nu_p$, dan koefisien penguatan Brillouin $g_B$.

5. **Kalkulator Kapasitas Sounding 5G NR SRS 3GPP TS 38.211 (`parser.py`)**:
   - Metode `calculate_5g_nr_srs_capacity_and_coverage` mengalkulasi alokasi subcarrier comb (Comb-2/Comb-4), kapasitas orthogonal cyclic shifts per slot, total UE termultiplexing per periode, dan overhead persentase simbol sounding uplink.

6. **Kalkulator Sintilasi Ionosfer Satelit S4 ITU-R P.531 (`parser.py`)**:
   - Metode `calculate_satellite_ionospheric_scintillation_s4_itu_r_p531` mengestimasi indeks fluktuasi amplitudo $S_4$, faktor geometri obliquity lintasan miring, fluktuasi peak-to-peak carrier, dan margin redaman disyaratkan untuk keandalan link satelit bumi-ruang angkasa.

7. **Evaluator Proposal Mahasiswa Belmawa PKM Video Gagasan Konstruktif (PKM-VGK) (`parser.py`)**:
   - Metode `parse_pkm_vgk_proposal_evaluation` mengkuantifikasi penilaian proposal video futuristik mahasiswa (urgensi gagasan SDGs 30%, sinematografi/storyboard 30%, dampak solusi masa depan 25%, potensi diseminasi 15%), penalti ketidaksesuaian durasi (2-4 menit), pendanaan Belmawa, dan konversi SKS MBKM.

8. **Auditor Skema Navigasi Remah Roti Breadcrumb List (`seo_validator.py`)**:
   - Metode `audit_breadcrumb_navigation_schema` memeriksa kelengkapan struktur navigasi breadcrumb semantik (JSON-LD BreadcrumbList, Microdata, atau nav aria-label), memastikan urutan nomor posisi teratur dan minimal 2 tingkat hierarki.

9. **Auditor Transkrip Multimedia Audio WCAG 2.1 SC 1.2.1 (`seo_validator.py`)**:
   - Metode `audit_audio_media_transcripts` memvalidasi keberadaan transkrip teks pendukung, penandaan `aria-describedby`, atau takarir deskripsi teks bagi rekaman audio materi perkuliahan dan siniar.

10. **Auditor Token Autocomplete Formulir WCAG 2.1 SC 1.3.5 (`seo_validator.py`)**:
    - Metode `audit_form_input_autocomplete_tokens` memverifikasi bahwa bidang isian yang mengumpulkan data identitas pribadi mahasiswa/pengguna menyertakan token `autocomplete` standar HTML5 / WCAG yang sah.

11. **Auditor Keamanan Tautan Eksternal Target Blank (`seo_validator.py`)**:
    - Metode `audit_external_link_security_attributes` memeriksa tautan keluar dengan `target="_blank"` guna memastikan penegakan `rel="noopener noreferrer"` guna mencegah kerentanan Reverse Tabnabbing.

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_sbs_threshold_card`, `render_5g_srs_sounding_card`, `render_satellite_ionospheric_scintillation_card`, `render_pkm_vgk_proposal_card`, dan `render_5g_srs_comb_pattern_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_5g_nr_srs_telegram` dan `format_pkm_vgk_telegram`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `satellite_ionospheric_scintillation_records`, `nr_srs_records`, dan `pkm_vgk_proposal_records` dengan indeks pencarian teroptimasi.

15. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper `get_tags_by_ids` untuk pembacaan batch data tag dan `batch_update_category_descriptions` untuk pembaruan massal taksonomi kategori.

16. **Generator Schema.org VideoObject & Eksportir RedwoodJS MDX (`exporter.py`)**:
    - Generator `generate_constructive_video_json_ld` untuk penandaan terstruktur video SDGs mahasiswa dan `to_redwoodjs_mdx` untuk dokumentasi fullstack RedwoodJS React MDX.

17. **Antarmuka CLI Konsol (`cli.py`)**:
    - Subcommand CLI baru `ionoscint`, `nrsrs`, dan `pkmvgk` untuk operasionalisasi telemetri sintilasi satelit, sounding 5G NR SRS, dan evaluasi proposal PKM-VGK mahasiswa.
