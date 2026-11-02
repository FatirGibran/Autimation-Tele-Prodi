# Dokumentasi Perubahan Arsitektur v5.1.0 Milestone Release

Siklus pengembangan v5.1.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen audio semantik HTML5 `<audio>` dan anak elemen `<source>` (`sanitize_html5_audio_attributes`), sanitasi elemen meteran dan indikator progres `<progress>` dan `<meter>` (`sanitize_html5_progress_meter_attributes`), serta sanitasi pengelompokan formulir semantik `<fieldset>` dan `<legend>` (`sanitize_html5_fieldset_legend_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator pergeseran fasa non-linear Self-Phase Modulation (SPM) dan B-integral transmisi serat optik DWDM menurut teori Govind P. Agrawal (`calculate_optical_spm_nonlinear_phase_shift`), penganalisis manajemen berkas gelombang milimeter 5G NR Beam Management sweeping & tracking 3GPP Rel-15/16 (`calculate_5g_nr_beam_management`), kalkulator kelambatan grup Total Electron Content (TEC) ionosferik satelit ITU-R P.531 (`calculate_satellite_ionospheric_tec_delay`), serta evaluator proposal prototipe rekayasa teknologi mahasiswa Belmawa PKM Karsa Cipta (PKM-KC) (`parse_pkm_kc_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor accessible name pada tombol dan tautan interaktif menurut WCAG 2.1 SC 4.1.2 dan SC 2.4.4 (`audit_button_and_link_accessible_names`), auditor dimensi eksplisit gambar dan rasio aspek CSS untuk eliminasi lonjakan tata letak Cumulative Layout Shift (CLS) (`audit_image_aspect_ratio_cls`), auditor semantik penandaan W3C HTML Microdata (`audit_microdata_attributes`), serta auditor keamanan tautan eksternal `target="_blank"` dan direktif kebijakan referrer (`audit_referral_policy_and_noopener`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk telemetri fasa non-linear SPM serat optik (`render_optical_spm_nonlinear_card`), kartu performansi sweeping 5G NR Beam Management (`render_5g_beam_sweeping_card`), kartu kelambatan ionosferik TEC satelit ITU-R P.531 (`render_satellite_tec_delay_card`), kartu capaian pendanaan prototipe mahasiswa PKM-KC Belmawa (`render_pkm_kc_proposal_card`), dan diagram arsitektur berkas Massive MIMO inline SVG responsif (`render_5g_beam_sweeping_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri peringatan non-linearitas SPM optik (`format_optical_spm_telegram_card`) dan pengumuman capaian kelulusan pendanaan prototipe PKM-KC mahasiswa (`format_pkm_kc_telegram_card`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `satellite_tec_records`, `nr_beam_management_records`, dan `pkm_kc_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca tag batch berdasarkan daftar ID numerik `get_tags_by_ids` dan helper pemulihan massal pos dari trash `batch_restore_posts` via REST API `/wp/v2/posts/{id}`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org TechArticle dan Product prototype JSON-LD untuk pendaftaran paten/HKI mahasiswa (`generate_prototype_patent_json_ld`) dan eksportir dokumentasi rute prerendered reactive SvelteKit MDSveX (`to_sveltekit_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `beam`, `tec`, dan `pkmkc` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga mencapai 953 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Audio `<audio>` & `<source>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_audio_attributes` memvalidasi atribut kontrol playback (`controls`, `preload`, `autoplay`, `loop`, `muted`) dan mensterilkan anak elemen `<source>` dengan MIME type audio resmi (`audio/mpeg`, `audio/ogg`, `audio/wav`).

2. **Sanitasi Elemen Progres & Meteran `<progress>` & `<meter>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_progress_meter_attributes` memvalidasi atribut numerik (`value`, `max`, `min`, `low`, `high`, `optimum`) dan mengeliminasi manipulasi DOM.

3. **Sanitasi Pengelompokan Formulir `<fieldset>` & `<legend>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_fieldset_legend_attributes` memvalidasi pengelompokan kontrol formulir, atribut boolean `disabled`, asosiasi atribut `form`, dan judul semantik `<legend>`.

4. **Kalkulator Fasa Non-Linear SPM Serat Optik DWDM (`parser.py`)**:
   - Metode `calculate_optical_spm_nonlinear_phase_shift` menghitung pergeseran fasa non-linear maksimum $\Phi_{\text{max}} = \gamma P_0 L_{\text{eff}}$, B-integral Agrawal, pelebaran chirp spektral, dan evaluasi risiko distorsi transmisi DWDM.

5. **Penganalisis 5G NR Beam Management 3GPP Rel-15/16 (`parser.py`)**:
   - Metode `calculate_5g_nr_beam_management` mengevaluasi beamforming gain array antena Massive MIMO, SINR terefinisi, efisiensi spektral Shannon, dan throughput estimasi multi-beam gNodeB.

6. **Kalkulator Kelambatan Ionosferik TEC Satelit ITU-R P.531 (`parser.py`)**:
   - Metode `calculate_satellite_ionospheric_tec_delay` menghitung Slant TEC, kelambatan grup nanodetik, deviasi eror jarak meter, dan klasifikasi level aktivitas badai geomagnetik menurut model ITU-R P.531.

7. **Evaluator Proposal Prototipe PKM-KC Belmawa Dikti (`parser.py`)**:
   - Metode `parse_pkm_kc_proposal_evaluation` mengkuantifikasi penilaian proposal rekayasa perangkat keras mahasiswa (kreativitas 30%, desain keteknikan 35%, kelayakan prototipe 20%, RAB/jadwal 15%), penentuan kelulusan pendanaan, target TRL, dan kesiapan paten.

8. **Auditor Accessible Name Tombol & Hyperlink WCAG 2.1 (`seo_validator.py`)**:
   - Metode `audit_button_and_link_accessible_names` mengaudit elemen tombol dan tautan untuk menjamin pemenuhan kriteria WCAG 2.1 SC 4.1.2 dan SC 2.4.4.

9. **Auditor Dimensi Gambar & Pencegahan CLS Core Web Vitals (`seo_validator.py`)**:
   - Metode `audit_image_aspect_ratio_cls` memeriksa keberadaan dimensi eksplisit width/height atau CSS aspect-ratio guna mengeliminasi lonjakan tata letak tak terduga.

10. **Auditor Penandaan HTML Microdata W3C (`seo_validator.py`)**:
    - Metode `audit_microdata_attributes` mengaudit atribut itemscope, itemtype, dan itemprop untuk validitas integrasi Schema.org.

11. **Auditor Keamanan Tautan Eksternal & Referrer Policy (`seo_validator.py`)**:
    - Metode `audit_referral_policy_and_noopener` memverifikasi atribut rel aman (noopener/noreferrer) pada tautan target blank dan meta Referrer-Policy dokumen.

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_spm_nonlinear_card`, `render_5g_beam_sweeping_card`, `render_satellite_tec_delay_card`, `render_pkm_kc_proposal_card`, dan `render_5g_beam_sweeping_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_optical_spm_telegram_card` dan `format_pkm_kc_telegram_card`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `satellite_tec_records`, `nr_beam_management_records`, dan `pkm_kc_proposal_records` dengan indeks pencarian teroptimasi.

15. **Integrasi WordPress REST API (`wordpress_client.py`)**:
    - Implementasi `get_tags_by_ids` untuk pembacaan batch tag dan `batch_restore_posts` untuk pemulihan massal pos dari tempat sampah.

16. **Generator Schema.org & Dokumentasi MDX Modern (`exporter.py`)**:
    - Implementasi `generate_prototype_patent_json_ld` untuk artikel rekayasa/paten mahasiswa dan `to_sveltekit_mdx` untuk integrasi dokumentasi SvelteKit MDSveX.

17. **Perintah Konsol CLI (`cli.py`)**:
    - Subcommand baru `beam`, `tec`, dan `pkmkc` dengan dukungan flag `--action list` dan `--action add`.

---

## Verifikasi Pengujian Unit
- Total unit test: **953 unit tests passing** (100% pass rate).
- Waktu eksekusi: **~12.8 detik**.
