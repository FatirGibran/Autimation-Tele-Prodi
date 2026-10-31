# Dokumentasi Perubahan Arsitektur v4.9.0 Milestone Release

Siklus pengembangan v4.9.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen informasi kontak semantik HTML5 `<address>` (`sanitize_html5_address_attributes`), sanitasi atribut kutipan sumber `cite` pada elemen kutipan blok `<blockquote>` dan kutipan inline `<q>` (`sanitize_html5_blockquote_attributes`), serta sanitasi atribut binding saran input formulir HTML5 `list` dengan elemen `<datalist>` (`sanitize_html5_input_datalist_attributes`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator pergeseran fase dan efisiensi Four-Wave Mixing (FWM) transmisi serat optik DWDM menurut teori optika nonlinier Agrawal (`calculate_optical_fwm_phase_matching`), kalkulator perbaikan SINR dan peningkatan throughput sel tepi (cell-edge) 5G NR Coordinated Multi-Point (CoMP) Joint Transmission menurut spesifikasi 3GPP TS 36.819 / TS 38.300 (`calculate_5g_nr_comp_joint_transmission`), kalkulator redaman pudar sintilasi troposferik link satelit bumi-angkasa menurut rekomendasi ITU-R P.618-13 (`calculate_satellite_tropospheric_scintillation`), serta evaluator seleksi proposal pemberdayaan desa Program Peningkatan Kapasitas Organisasi Kemahasiswaan (PPK Ormawa) Belmawa Kemendikbudristek (`parse_ppk_ormawa_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor penanda data terstruktur Schema.org `WebPage`, `AboutPage`, dan `ContactPage` JSON-LD (`audit_webpage_schema_markup`), auditor deklarasi direktif keamanan browser `Permissions-Policy` dan `Feature-Policy` terhadap proteksi sensor privasi kamera, mikrofon, dan lokasi (`audit_permissions_policy_directive`), auditor kepatuhan atribut `autocomplete` pada formulir kontak dan identitas sesuai kriteria aksesibilitas WCAG 2.1 SC 1.3.5 (`audit_form_autocomplete_accessibility`), serta auditor petunjuk telemetri performansi Resource Timing (`Timing-Allow-Origin`) dan metrik `Server-Timing` Core Web Vitals (`audit_resource_timing_hints`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri FWM phase matching dan efisiensi nonlinieritas transmisi serat optik DWDM (`render_optical_fwm_card`), kartu performansi peningkatan throughput sel tepi 5G NR CoMP Joint Transmission (`render_5g_nr_comp_card`), kartu redaman sintilasi troposfer satelit ITU-R P.618 (`render_satellite_scintillation_card`), kartu capaian kelulusan dan alokasi dana hibah PPK Ormawa Belmawa Dikti (`render_ppk_ormawa_card`), serta kartu visualisasi topologi arsitektur koordinasi multi-sel 5G NR CoMP berbasis inline SVG responsif (`render_5g_nr_comp_topology_svg_card`).
- **Format Pesan Telegram**: Format buletin telemetri DWDM FWM phase matching (`format_optical_fwm_telegram`) dan format buletin pengumuman kelulusan pendanaan PPK Ormawa Belmawa Kemendikbudristek (`format_ppk_ormawa_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit DWDM FWM phase matching (`optical_fwm_phase_records`), tabel rekam performansi kluster 5G NR CoMP (`nr_comp_records`), serta tabel rekam evaluasi & pendanaan proposal PPK Ormawa (`ppk_ormawa_records`).
- **Klien WordPress REST API**: Helper filter komentar berdasarkan alamat surel penulis (`get_comments_by_author_email`) dan helper penghapusan massal komentar editorial (`batch_delete_comments`) via endpoint `/wp/v2/comments`.
- **Generator Statis & Ekspor**: Generator Schema.org `AboutPage` & `ContactPage` JSON-LD terstruktur (`generate_about_contact_page_json_ld`) serta eksportir dokumentasi framework full-stack modern TanStack Start MDX (`to_tanstack_start_mdx`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `fwm_phase`, `comp`, dan `ormawa`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 872 menjadi 900+ unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Semantik `<address>` (`sanitizer.py`)**:
   - Memvalidasi elemen kontak pengarang/prodi `<address>`, mengizinkan elemen inline semantik yang sah (`<a>`, `<span>`, `<br>`, `<strong>`), mensterilkan skema tautan surel (`mailto:`) dan telepon (`tel:`), serta menghapus event handler inline dan script execution.

2. **Sanitasi Atribut Kutipan `cite` pada Elemen `<blockquote>` & `<q>` (`sanitizer.py`)**:
   - Memvalidasi elemen kutipan blok dan kutipan sebaris, mensterilkan URL rujukan pustaka pada atribut `cite` terhadap skema yang aman (`http:`, `https:`, `/`), serta memblokir skema berbahaya (`javascript:`, `vbscript:`, `data:`).

3. **Sanitasi Binding Form Input Datalist `list` (`sanitizer.py`)**:
   - Mensterilkan asosiasi elemen `<input>` dengan `<datalist>` melalui atribut `list`, memastikan nilai identifier token alphanumeric yang valid, serta mencegah DOM clobbering dan injection manipulasi id formulir.

4. **Kalkulator Four-Wave Mixing (FWM) Phase-Matching DWDM (`parser.py`)**:
   - Menghitung parameter dispersi kecepatan grup $\beta_2 = -\frac{\lambda^2}{2\pi c} D$, ketidakcocokan fase $\Delta\beta = \beta_2 (2\pi \Delta f)^2$, panjang koherensi interaksi $L_c = \frac{2\pi}{|\Delta\beta|}$, efisiensi pembentukan gelombang nonlinier $\eta_{\text{FWM}}$, daya crosstalk FWM (dBm), dan klasifikasi risiko degradasi transmisi DWDM berkecepatan tinggi.

5. **Kalkulator 3GPP 5G NR CoMP Joint Transmission (`parser.py`)**:
   - Menghitung konversi daya sel koordinasi dari interferensi menjadi sinyal koheren konstruktif menurut 3GPP TS 36.819 / TS 38.300, gain SINR CoMP dibanding non-CoMP baseline, efisiensi spektral Shannon, serta persentase peningkatan throughput pengguna di tepi sel (cell-edge UE).

6. **Kalkulator Redaman Sintilasi Troposferik Satelit ITU-R P.618-13 (`parser.py`)**:
   - Menghitung parameter refraktivitas radio basah $N_{\text{wet}}$, deviasi standar fluktuasi sinyal $\sigma_x$, faktor perata apertura antena parabola $g(x)$, kedalaman redaman pudar sintilasi (fade depth $A_s(p)$ dB) pada persentase waktu tahunan $p \le 50\%$, serta peningkatan sinyal akibat pemfokusan troposferik.

7. **Evaluator Proposal Pemberdayaan Desa PPK Ormawa Belmawa Dikti (`parser.py`)**:
   - Mengevaluasi skor proposal mahasiswa Program Penguatan Kapasitas Organisasi Kemahasiswaan berdasarkan kriteria nasional: 25% ketajaman identifikasi masalah desa, 35% keunggulan solusi teknologi/IoT, 25% peta jalan & kemitraan strategis, dan 15% tata kelola anggaran, disertai status pendanaan hingga Rp 40.000.000 dan rekognisi konversi SKS kurikulum prodi.

8. **Auditor Skema WebPage, AboutPage, ContactPage Schema.org (`seo_validator.py`)**:
   - Memvalidasi data terstruktur JSON-LD untuk halaman profil institusional, halaman tentang prodi, dan kontak prodi, memastikan kehadiran atribut wajib `name`, `description`, `url`, `isPartOf`, dan `breadcrumb` guna klasifikasi entitas Google Knowledge Graph.

9. **Auditor Direktif Keamanan Browser Permissions-Policy (`seo_validator.py`)**:
   - Mengaudit keberadaan meta header `Permissions-Policy` (dan kompatibilitas mundur `Feature-Policy`) untuk memastikan bahwa kapabilitas perangkat keras peramban berisiko tinggi (kamera, mikrofon, geolokasi) terkunci dari eksfiltrasi iframe pihak ketiga tak tepercaya.

10. **Auditor Aksesibilitas Autocomplete Formulir WCAG 2.1 SC 1.3.5 (`seo_validator.py`)**:
    - Memeriksa elemen `<input>` formulir yang meminta data identitas atau kontak pengguna terhadap keberadaan atribut `autocomplete` standar HTML5 (`name`, `email`, `tel`, `street-address`, dll.) untuk mendukung navigasi pengguna dengan disabilitas dan integrasi pengisian otomatis peramban.

11. **Auditor Petunjuk Telemetri Resource Timing & Server-Timing (`seo_validator.py`)**:
    - Mengaudit header meta `Timing-Allow-Origin` untuk mengizinkan observasi waterfall aset lintas asal, serta mengurai metrik durasi `Server-Timing` guna analisis profiling latensi backend server.

12. **Komponen Visualisasi Topologi Arsitektur 5G NR CoMP Inline SVG (`components.py`)**:
    - Kartu grafis interaktif menggambarkan jaringan seluler gNodeB serving dan titik transmisi koordinasi (cooperating TPs) yang terhubung melalui mesh backhaul fiber Xn/eXn C-RAN, memancarkan berkas RF terkoordinasi secara koheren ke arah Cell-Edge UE berbasis inline SVG responsif.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Menambahkan skema tabel database `optical_fwm_phase_records`, `nr_comp_records`, dan `ppk_ormawa_records` disertai indeks performa dan metode operasi CRUD terisolasi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Menambahkan helper pembaca komentar terfilter email penulis `get_comments_by_author_email` dan penghapusan massal komentar `batch_delete_comments` via REST API endpoint `/wp/v2/comments`.

15. **Generator AboutPage/ContactPage JSON-LD & Eksportir TanStack Start MDX (`exporter.py`)**:
    - Menghasilkan penanda JSON-LD Schema.org komprehensif untuk halaman institusi dan kontak, serta mengekspor artikel editorial ke format type-safe fullstack SSR framework modern TanStack Start MDX dengan frontmatter terintegrasi.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `fwm_phase`, `comp`, dan `ormawa` untuk pengoperasian langsung dari terminal sistem operasi.
