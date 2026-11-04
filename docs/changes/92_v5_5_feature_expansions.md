# Dokumentasi Perubahan Arsitektur v5.5.0 Milestone Release

Siklus pengembangan v5.5.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen audio responsif `<audio>`, `<source>`, dan `<track>` (`sanitize_html5_audio_source_track_attributes`), sanitasi atribut kolom tabel `<colgroup>` dan `<col>` (`sanitize_html5_table_colgroup_attributes`), serta sanitasi penelusuran revisi teks editorial `<del>` dan `<ins>` (`sanitize_html5_del_ins_datetime_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator saturasi penguatan dan noise figure optical EDFA C/L-band (`calculate_optical_edfa_saturation_noise_figure`), kalkulator latensi 5G NR Carrier Aggregation Cross-Carrier Scheduling (CCS) dan CIF 3GPP Rel-16 (`calculate_5g_nr_cross_carrier_scheduling_latency`), kalkulator redaman awan dan kabut stasiun bumi satelit ITU-R P.840 (`calculate_satellite_cloud_attenuation_itu_r_p840`), serta evaluator proposal mahasiswa Belmawa PKM Karya Inovatif (PKM-KI) (`parse_pkm_ki_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor struktur sel header baris dan kolom tabel data WCAG 2.1 SC 1.3.1 (`audit_table_row_and_column_headers`), auditor pesan status dinamis dan live regions ARIA WCAG 2.1 SC 4.1.3 (`audit_aria_live_status_regions`), auditor konsistensi label visual dan accessible name interaktif WCAG 2.1 SC 2.5.3 (`audit_label_in_name_consistency`), serta auditor deskriptor densitas dan resolusi gambar responsif srcset (`audit_image_srcset_density_descriptors`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk saturasi penguatan amplifier EDFA (`render_optical_edfa_saturation_card`), kartu latensi 5G NR Cross-Carrier Scheduling (`render_5g_cross_carrier_scheduling_card`), kartu redaman awan satelit ITU-R P.840 (`render_satellite_cloud_attenuation_card`), kartu evaluasi proposal prototipe PKM-KI Belmawa (`render_pkm_ki_proposal_card`), dan diagram vektor inline SVG responsif garis waktu penjadwalan silang 5G NR CCS (`render_5g_cross_carrier_scheduling_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri saturasi penguat serat optik EDFA (`format_optical_edfa_telegram`) dan pengumuman capaian kelulusan pendanaan karya inovatif mahasiswa PKM-KI (`format_pkm_ki_telegram`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `optical_edfa_records`, `nr_cross_carrier_records`, dan `pkm_ki_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca kategori batch berdasarkan daftar ID numerik `get_categories_by_ids` dan helper pembaruan massal deskripsi taksonomi tag `batch_update_tag_descriptions` via REST API `/wp/v2/tags`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org CreativeWork / Invention JSON-LD untuk invensi prototipe dan permohonan paten mahasiswa (`generate_innovative_invention_json_ld`) dan eksportir dokumentasi rute fullstack Gatsby React MDX (`to_gatsby_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `edfa`, `ccs`, dan `pkmki` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga melampaui 1.055 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Audio, Source, & Track Media Elements (`sanitizer.py`)**:
   - Metode `sanitize_html5_audio_source_track_attributes` memvalidasi atribut kontrol pemutar audio (`preload`, `src`, `controls`), mensterilkan event handler skrip inline (`onplay`, `onerror`, dll.), serta memblokir payload berbahaya pada elemen media audio.

2. **Sanitasi Tabel Colgroup & Col Layout Elements (`sanitizer.py`)**:
   - Metode `sanitize_html5_table_colgroup_attributes` memvalidasi batas nilai integer positif pada atribut `span`, membersihkan styling berbahaya, dan menetralkan atribut clobbering pada kontainer kolom tabel.

3. **Sanitasi Editorial Revision Tags Del & Ins (`sanitizer.py`)**:
   - Metode `sanitize_html5_del_ins_datetime_attributes` memvalidasi atribut tautan kutipan `cite` terhadap skema URI aman dan memeriksa keabsahan format cap waktu `datetime` pada elemen revisi editorial teks.

4. **Kalkulator Saturasi Penguatan & Derau EDFA (`parser.py`)**:
   - Metode `calculate_optical_edfa_saturation_noise_figure` menyelesaikan persamaan nonlinear penguatan jenuh sinyal optik C/L-band, menghitung daya keluaran jenuh, kompresi gain, derau ASE (0.1 nm), dan noise figure NF.

5. **Kalkulator Latensi 5G NR Cross-Carrier Scheduling 3GPP Rel-16 (`parser.py`)**:
   - Metode `calculate_5g_nr_cross_carrier_scheduling_latency` mengalkulasi latensi penjadwalan downlink dan uplink antarkomponen carrier dengan perbedaan numerologi $\mu$, jitter batas slot, dan overhead decoding field CIF 3-bit pada PDCCH DCI.

6. **Kalkulator Redaman Awan & Kabut Satelit ITU-R P.840 (`parser.py`)**:
   - Metode `calculate_satellite_cloud_attenuation_itu_r_p840` mengestimasi redaman spesifik gelombang mikro/milimeter berdasarkan permitivitas dielektrik air cair, kerapatan air awan, ketebalan lapisan awan, sudut elevasi antena, dan panjang lintasan miring.

7. **Evaluator Proposal Mahasiswa Belmawa PKM Karya Inovatif (PKM-KI) (`parser.py`)**:
   - Metode `parse_pkm_ki_proposal_evaluation` mengkuantifikasi penilaian proposal inovasi prototipe fungsional mahasiswa (kebaruan & potensi HKI 30%, fungsi prototipe 35%, desain sistem & utilitas 20%, kewajaran anggaran 15%), penentuan pendanaan Belmawa Dikti, dan konversi SKS MBKM.

8. **Auditor Header Baris & Kolom Tabel WCAG 2.1 SC 1.3.1 (`seo_validator.py`)**:
   - Metode `audit_table_row_and_column_headers` memeriksa kelengkapan sel header `<th>` dengan atribut `scope` (`col`, `row`, `colgroup`, `rowgroup`) yang valid serta keberadaan takarir `<caption>` atau label aksesibel pada tabel data.

9. **Auditor Status Messages & Live Region ARIA WCAG 2.1 SC 4.1.3 (`seo_validator.py`)**:
   - Metode `audit_aria_live_status_regions` memvalidasi penerapan atribut `aria-live` (`polite`, `assertive`, `off`) dan semantik peran status/alert guna memastikan pengumuman dinamis dapat diakses oleh pembaca layar.

10. **Auditor Konsistensi Label Visual & Accessible Name WCAG 2.1 SC 2.5.3 (`seo_validator.py`)**:
    - Metode `audit_label_in_name_consistency` memverifikasi bahwa seluruh teks yang terlihat secara visual pada kontrol interaktif (tombol, tautan) tercakup secara utuh dalam atribut programmatic name (`aria-label`).

11. **Auditor Deskriptor Densitas Gambar Responsif Srcset (`seo_validator.py`)**:
    - Metode `audit_image_srcset_density_descriptors` memeriksa konsistensi deskriptor densitas layar (`x`) dan lebar layar (`w`), serta memvalidasi kehadiran atribut `sizes` saat deskriptor lebar digunakan.

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_edfa_saturation_card`, `render_5g_cross_carrier_scheduling_card`, `render_satellite_cloud_attenuation_card`, `render_pkm_ki_proposal_card`, dan `render_5g_cross_carrier_scheduling_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_optical_edfa_telegram` dan `format_pkm_ki_telegram`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `optical_edfa_records`, `nr_cross_carrier_records`, dan `pkm_ki_proposal_records` dengan indeks pencarian teroptimasi.

15. **Integrasi WordPress REST API (`wordpress_client.py`)**:
    - Implementasi `get_categories_by_ids` untuk pembacaan batch kategori dan `batch_update_tag_descriptions` untuk pembaruan deskripsi taksonomi tag secara massal.

16. **Generator Schema.org & Dokumentasi MDX Modern (`exporter.py`)**:
    - Implementasi `generate_innovative_invention_json_ld` untuk struktur metadata permohonan paten/prototipe mahasiswa dan `to_gatsby_mdx` untuk integrasi dokumentasi Gatsby React Head API framework.

17. **Perintah Konsol CLI (`cli.py`)**:
    - Subcommand baru `edfa`, `ccs`, dan `pkmki` dengan dukungan flag `--action list` dan `--action add`.
