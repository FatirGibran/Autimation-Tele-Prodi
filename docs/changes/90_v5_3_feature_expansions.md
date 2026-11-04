# Dokumentasi Perubahan Arsitektur v5.3.0 Milestone Release

Siklus pengembangan v5.3.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen dialog modal `<dialog>` beserta backdrop dan atribut fokus (`sanitize_html5_dialog_attributes`), sanitasi elemen kanvas grafis `<canvas>` beserta restriksi konteks scriptable (`sanitize_html5_canvas_attributes`), serta sanitasi elemen penanda landmark semantik `<search>` (`sanitize_html5_search_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator penguatan on-off dan noise figure amplifier Raman terdistribusi serat optik DWDM (`calculate_optical_raman_amplifier_gain`), kalkulator latensi 5G NR Bandwidth Part (BWP) switching dan adaptasi numerologi subcarrier spacing (`calculate_5g_nr_bwp_switching_latency`), kalkulator redaman fluktuasi sintilasi troposferik satelit bumi ITU-R P.618 (`calculate_satellite_tropospheric_scintillation_itu_r_p618`), serta evaluator proposal pengabdian masyarakat mahasiswa Belmawa PKM Pengabdian Masyarakat (PKM-PM) (`parse_pkm_pm_proposal_evaluation`).
- **Audit SEO On-Page, Core Web Vitals, & Aksesibilitas WCAG 2.1**: Auditor ruang lingkup header tabel `scope` dan caption menurut WCAG 2.1 SC 1.3.1 (`audit_table_headers_scope_and_caption`), auditor atribut input autocomplete formulir menurut WCAG 2.1 SC 1.3.5 (`audit_form_input_autocomplete`), auditor ukuran target sentuh interaktif (Target Size Minimum Area) menurut WCAG 2.1 SC 2.5.5 (`audit_touch_target_size`), serta auditor petunjuk sumber daya DNS-prefetch dan preconnect Core Web Vitals (`audit_resource_hints_preconnect`).
- **Visualisasi Komponen Elementor & Diagram SVG Responsif**: Komponen kartu visual Elementor untuk penguatan Raman terdistribusi (`render_optical_raman_card`), kartu latensi 5G NR BWP switching (`render_5g_bwp_switching_card`), kartu sintilasi troposferik satelit ITU-R P.618 (`render_satellite_tropospheric_scintillation_card`), kartu evaluasi proposal mahasiswa PKM-PM Belmawa (`render_pkm_pm_proposal_card`), dan diagram vektor inline SVG responsif garis waktu BWP switching (`render_5g_bwp_switching_timeline_svg`).
- **Format Notifikasi Telegram Bot**: Template buletin resmi Telegram untuk telemetri penguatan Raman terdistribusi (`format_optical_raman_telegram_card`) dan pengumuman capaian kelulusan pendanaan pengabdian mahasiswa PKM-PM (`format_pkm_pm_telegram_card`).
- **Penyimpanan Terstruktur SQLite**: Tabel database `optical_raman_records`, `nr_bwp_switching_records`, dan `pkm_pm_proposal_records` disertai indeks pencarian dan metode CRUD terisolasi.
- **Klien WordPress REST API**: Helper pembaca pengguna WordPress batch berdasarkan daftar ID numerik `get_users_by_ids` dan helper pembaruan massal kategori pos `batch_update_post_categories` via REST API `/wp/v2/users` dan `/wp/v2/posts`.
- **Ekspor Dokumen & Data Terstruktur Schema.org**: Generator Schema.org SocialMediaPosting JSON-LD untuk sosialisasi kegiatan pengabdian masyarakat mahasiswa (`generate_social_media_posting_json_ld`) dan eksportir dokumentasi rute fullstack Remix Run React framework (`to_remix_run_mdx`).
- **Antarmuka Konsol CLI**: Perintah subcommand terminal sistem operasi `raman`, `bwp`, dan `pkmpm` untuk operasionalisasi langsung dari terminal.
- **Suite Pengujian Unit Terpadu**: Ekspansi menyeluruh cakupan pengujian unit hingga melampaui 1.000 test terverifikasi (100% pass rate).

---

## Rincian Modul & Fungsionalitas Baru

1. **Sanitasi HTML5 Modal Dialog `<dialog>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_dialog_attributes` memvalidasi atribut kontrol dialog (`open`, `aria-modal`, `aria-labelledby`, `aria-describedby`), mensterilkan atribut autofocus yang mengganggu aksesibilitas navigasi papan ketik, dan membatasi manipulasi DOM modal.

2. **Sanitasi Elemen Kanvas Grafis HTML5 `<canvas>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_canvas_attributes` memvalidasi atribut dimensi (`width`, `height`), memastikan kepatuhan fallback accessibility, dan mensterilkan penanganan skrip langsung pada kontainer grafis kanvas.

3. **Sanitasi Elemen Landmark Pencarian Semantik HTML5 `<search>` (`sanitizer.py`)**:
   - Metode `sanitize_html5_search_elements` memvalidasi atribut `role="search"`, mensterilkan atribut tidak aman, dan memastikan integritas landmark pencarian semantik HTML5 modern.

4. **Kalkulator Penguatan Optical Raman Terdistribusi DWDM (`parser.py`)**:
   - Metode `calculate_optical_raman_amplifier_gain` mengevaluasi panjang efektif fiber ($L_{\text{eff}}$), penguatan Raman on-off ($G_{\text{on-off}}$), penguatan bersih transmisi ($G_{\text{net}}$), equivalent noise figure ($NF_{\text{eq}}$), dan status kesehatan span optik.

5. **Kalkulator Latensi 5G NR BWP Switching & Adaptasi Numerologi (`parser.py`)**:
   - Metode `calculate_5g_nr_bwp_switching_latency` mengalkulasi latensi switching BWP menurut spesifikasi 3GPP Rel-15/16 TS 38.133, slot interupsi UE ($N_{\text{slot}}$), penundaan retuning RF Type 1 dan Type 2, serta klasifikasi tingkat kinerja latensi.

6. **Kalkulator Sintilasi Troposferik Satelit ITU-R P.618 (`parser.py`)**:
   - Metode `calculate_satellite_tropospheric_scintillation_itu_r_p618` menghitung varians indeks refraksi atmosfer, deviasi standar fluktuasi sinyal $\sigma$, pelemahan redaman sintilasi pada persentil waktu $p\%$, dan penentuan fade margin adaptif.

7. **Evaluator Proposal Mahasiswa PKM Pengabdian Masyarakat (PKM-PM) (`parser.py`)**:
   - Metode `parse_pkm_pm_proposal_evaluation` mengkuantifikasi penilaian proposal pengabdian masyarakat mahasiswa (ketepatan diagnosis 25%, ketepatan solusi 35%, keberlanjutan perubahan perilaku 25%, kewajaran RAB & jadwal 15%), penentuan pendanaan Belmawa Dikti, dan rekomendasi konversi SKS MBKM.

8. **Auditor Ruang Lingkup Header Tabel `scope` & Keterangan `<caption>` WCAG 2.1 (`seo_validator.py`)**:
   - Metode `audit_table_headers_scope_and_caption` memverifikasi keberadaan atribut `scope="col"` atau `scope="row"` pada setiap elemen `<th>` serta kehadiran elemen `<caption>` menurut WCAG 2.1 SC 1.3.1.

9. **Auditor Atribut Autocomplete Formulir WCAG 2.1 (`seo_validator.py`)**:
   - Metode `audit_form_input_autocomplete` memverifikasi atribut `autocomplete` yang sesuai standar HTML5 pada input formulir pengguna (`name`, `email`, `tel`, `address`, dll.) menurut WCAG 2.1 SC 1.3.5.

10. **Auditor Ukuran Target Sentuh (Target Size) WCAG 2.1 (`seo_validator.py`)**:
    - Metode `audit_touch_target_size` memeriksa ukuran elemen interaktif (`<a>`, `<button>`, `<input>`) agar memenuhi batas minimum dimensi sentuh (minimal 24x24 px untuk kriteria AA dan 44x44 px untuk kriteria AAA) menurut WCAG 2.1 SC 2.5.5.

11. **Auditor Petunjuk Sumber Daya DNS-Prefetch & Preconnect (`seo_validator.py`)**:
    - Metode `audit_resource_hints_preconnect` memverifikasi penerapan tautan `<link rel="dns-prefetch">` dan `<link rel="preconnect">` pada domain pihak ketiga (CDN, analitik, font) untuk optimasi latensi koneksi Core Web Vitals.

12. **Komponen Visual Elementor & SVG Responsif (`components.py`)**:
    - Implementasi `render_optical_raman_card`, `render_5g_bwp_switching_card`, `render_satellite_tropospheric_scintillation_card`, `render_pkm_pm_proposal_card`, dan `render_5g_bwp_switching_timeline_svg`.

13. **Format Buletin Notifikasi Telegram Bot (`formatters.py`)**:
    - Implementasi `format_optical_raman_telegram_card` dan `format_pkm_pm_telegram_card`.

14. **Penyimpanan Database Terisolasi SQLite (`storage.py`)**:
    - Tabel baru `optical_raman_records`, `nr_bwp_switching_records`, dan `pkm_pm_proposal_records` dengan indeks pencarian teroptimasi.

15. **Integrasi WordPress REST API (`wordpress_client.py`)**:
    - Implementasi `get_users_by_ids` untuk pembacaan batch pengguna/penulis dan `batch_update_post_categories` untuk pembaruan massal kategori pos editorial.

16. **Generator Schema.org & Dokumentasi MDX Modern (`exporter.py`)**:
    - Implementasi `generate_social_media_posting_json_ld` untuk artikel sosialisasi kegiatan pengabdian masyarakat mahasiswa dan `to_remix_run_mdx` untuk integrasi dokumentasi Remix Run React framework.

17. **Perintah Konsol CLI (`cli.py`)**:
    - Subcommand baru `raman`, `bwp`, dan `pkmpm` dengan dukungan flag `--action list` dan `--action add`.

---

## Verifikasi Pengujian Unit
- Total unit test: **1.005 unit tests passing** (100% pass rate).
- Waktu eksekusi: **~15.1 detik**.
