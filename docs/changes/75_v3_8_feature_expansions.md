# Dokumentasi Perubahan Arsitektur v3.8.0 Milestone Release

Siklus pengembangan v3.8.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi track media subtitle/keterangan visual `<track>` dengan penegakan protokol aman `kind`, `srclang`, dan netralisasi URL berbahaya (`sanitize_media_track_element`), sanitasi opsi autocomplete input datalist HTML5 `<datalist>` (`sanitize_datalist_options`), serta sanitasi elemen komputasi output semantik `<output>` dengan penegakan atribut `for` dan pencegahan injeksi event listener inline (`sanitize_output_element`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator link budget komunikasi laser optik ruang bebas FSO (`calculate_fso_link_budget`), evaluator konversi SKS magang bersertifikat MSIB Kampus Merdeka (`parse_msib_internship_credit_conversion`), kalkulator Polarisasi Antena PLF dan Rasio Aksial RF (`calculate_antenna_polarization_loss_factor`), serta parser proposal hibah pengabdian masyarakat dosen PKM LPPM (`parse_lecturer_pkm_grant_proposal`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1)**: Auditor navigasi hierarki rekam jejak breadcrumb semantik terstruktur (`audit_breadcrumb_navigation_accessibility`), auditor metadata durasi dan thumbnail skema video (`audit_video_schema_and_duration_accessibility`), auditor kepatuhan rel noopener external hyperlink keamanan tab baru (`audit_target_blank_rel_noopener`), serta auditor atribusi kutipan semantik blockquote dan cite (`audit_semantic_blockquote_attribution`).
- **Komponen Semantik Elementor Responsif**: Kartu kalkulasi transmisi laser ruang bebas FSO (`render_fso_link_budget_card`), kartu apresiasi dan pengakuan magang bersertifikat MSIB (`render_msib_internship_recognition_card`), kartu kalkulasi ketidaksesuaian polarisasi antena PLF (`render_antenna_polarization_card`), kartu pameran proyek hibah pengabdian masyarakat PKM dosen (`render_pkm_grant_project_card`), serta kartu wadah osiloskop sinyal responsif canvas HTML5 (`render_responsive_canvas_oscilloscope_card`).
- **Format Pesan Telegram**: Format buletin Telegram apresiasi penyelesaian magang industri MSIB (`format_msib_completion_telegram`) dan format buletin pengumuman pemenang dana hibah pengabdian masyarakat PKM (`format_pkm_grant_award_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel rekam magang industri MSIB (`student_msib_internships`), tabel pencatatan hibah pengabdian masyarakat dosen PKM (`lecturer_pkm_grants`), serta tabel audit kalkulasi link budget FSO (`fso_link_budget_records`).
- **Klien WordPress REST API**: Helper perolehan seluruh berkas lampiran media berdasarkan ID postingan (`get_media_attachments_by_post_id`) dan helper pembaruan status sticky postingan (`update_post_sticky_status`).
- **Generator Statis & Ekspor**: Generator Schema.org `Project` dan `CommunityAction` JSON-LD (`generate_community_action_project_json_ld`) serta eksportir markdown Docusaurus v3 MDX dengan dukungan tab interaktif (`to_docusaurus_v3_tabs_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `msib`, `pkm`, dan `fso`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 570 menjadi 597 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Media Track Subtitle HTML5 (`sanitizer.py`)**:
   - Memvalidasi elemen `<track>`, mengizinkan atribut `kind`, `srclang`, `label`, `default`, serta menetralisasi skrip berbahaya pada atribut `src`.

2. **Sanitasi Elemen HTML5 Datalist Autocomplete (`sanitizer.py`)**:
   - Membersihkan elemen interaktif `<datalist>` dan anak `<option>`, memvalidasi atribut `value` dan `label`, serta melucuti atribut event handler inline.

3. **Sanitasi Elemen HTML5 Output Komputasi (`sanitizer.py`)**:
   - Membersihkan elemen semantik `<output>`, memvalidasi atribut asosiasi `for` dan `name`, serta mencegah injeksi skrip.

4. **Kalkulator Link Budget Laser Ruang Bebas FSO (`parser.py`)**:
   - Menghitung geometric path loss, total redaman atmosferik, daya terima optik, serta link margin transmisi laser terestrial FSO.

5. **Evaluator Konversi SKS Magang Bersertifikat MSIB (`parser.py`)**:
   - Mengurai nilai mentor industri, mengonversi nilai angka ke huruf mutu standar, dan menetapkan ekuivalensi hingga 20 SKS Kampus Merdeka.

6. **Kalkulator Polarization Loss Factor (PLF) & Rasio Aksial Antena (`parser.py`)**:
   - Menghitung faktor kerugian polarisasi mismatch antara antena pemancar dan penerima berdasarkan sudut orientasi dan axial ratio dB.

7. **Parser Usulan Hibah Pengabdian Masyarakat Dosen PKM (`parser.py`)**:
   - Mengurai proposal hibah pengabdian masyarakat, bidang fokus LPPM, pagu usulan, lokasi mitra sasaran, dan alokasi anggaran yang disetujui.

8. **Auditor Aksesibilitas Breadcrumb Navigation Structured List (`seo_validator.py`)**:
   - Memeriksa elemen `<nav aria-label="Breadcrumb">`, urutan list `<ol>` atau `<ul>`, dan penandaan `aria-current="page"` pada item aktif.

9. **Auditor Metadata Schema & Durasi Video (`seo_validator.py`)**:
   - Memvalidasi elemen video, durasi ISO 8601, poster thumbnail gambar, dan kepatuhan teks deskripsi aksesibilitas video.

10. **Auditor Kepatuhan External Rel Noopener Link Baru (`seo_validator.py`)**:
    - Memverifikasi keberadaan atribut `rel="noopener noreferrer"` pada tautan target baru `target="_blank"` guna memitigasi celah tabnabbing.

11. **Auditor Atribusi Kutipan Blockquote & Cite (`seo_validator.py`)**:
    - Memeriksa semantik elemen `<blockquote>` dan ketersediaan atribusi rujukan sumber `<cite>` atau atribut `cite="..."`.

12. **Komponen Kalkulasi Transmisi Laser FSO (`components.py`)**:
    - Kartu visual Elementor kalkulasi link budget optik nirkabel dengan daya pemancar, penerima, dan indikator margin tautan.

13. **Komponen Pengakuan Magang Bersertifikat MSIB (`components.py`)**:
    - Kartu visual Elementor apresiasi mahasiswa berprestasi peserta program magang bersertifikat Kampus Merdeka di industri mitra.

14. **Komponen Ketidaksesuaian Polarisasi Antena PLF (`components.py`)**:
    - Kartu kalkulasi teknis RF ketidaksesuaian polarisasi gelombang elektromagnetik dan axial ratio antena telekomunikasi.

15. **Komponen Proyek Hibah Pengabdian Masyarakat PKM Dosen (`components.py`)**:
    - Kartu showcase pameran dan publikasi kegiatan pengabdian kepada masyarakat berbasis penerapan teknologi informasi.

16. **Komponen Wadah Osiloskop Gelombang Responsif Canvas (`components.py`)**:
    - Kontainer HTML5 semantik `<canvas>` terisolasi untuk visualisasi bentuk gelombang sinyal RF dan modulasi digital.

17. **Formatter Telegram Apresiasi Magang MSIB (`formatters.py`)**:
    - Template buletin resmi Telegram ucapan selamat atas kelulusan dan konversi SKS program magang bersertifikat MSIB.

18. **Formatter Telegram Pengumuman Hibah PKM LPPM (`formatters.py`)**:
    - Template pengumuman resmi Telegram penerima pendanaan program pengabdian masyarakat bagi sivitas akademika prodi.

19. **Manajer Rekam Magang MSIB Mahasiswa (`storage.py`)**:
    - Skema tabel basis data `student_msib_internships` dan metode `record_msib_internship`, `list_msib_internships`, `get_msib_by_nim`.

20. **Manajer Rekam Hibah Pengabdian Masyarakat PKM (`storage.py`)**:
    - Skema tabel `lecturer_pkm_grants` dan metode `record_pkm_grant`, `list_pkm_grants`, `get_pkm_grant_by_id`.

21. **Manajer Rekam Audit Kalkulasi Link Budget FSO (`storage.py`)**:
    - Skema tabel `fso_link_budget_records` dan metode `record_fso_link_budget`, `list_fso_link_budgets`, `get_fso_link_budget_by_id`.

22. **Helper WordPress Get Media Attachments By Post ID (`wordpress_client.py`)**:
    - Metode `get_media_attachments_by_post_id` untuk mengambil seluruh berkas media yang dilampirkan pada postingan tertentu via REST API.

23. **Helper WordPress Update Post Sticky Status (`wordpress_client.py`)**:
    - Metode `update_post_sticky_status` untuk menetapkan atau melepas status sticky/sematan pada artikel WordPress.

24. **Generator Schema.org Project & CommunityAction JSON-LD (`exporter.py`)**:
    - Metode `generate_community_action_project_json_ld` untuk standarisasi luaran pengabdian masyarakat dan proyek Tridharma.

25. **Eksportir Markdown Docusaurus v3 MDX Tabs (`exporter.py`)**:
    - Metode `to_docusaurus_v3_tabs_markdown` untuk transformasi artikel ke format dokumentasi Docusaurus v3 MDX dengan tab interaktif.

26. **Subcommand CLI `msib` (`cli.py`)**:
    - Perintah konsol `msib` untuk mencatat dan menginventarisasi konversi kredit magang bersertifikat mahasiswa.

27. **Subcommand CLI `pkm` (`cli.py`)**:
    - Perintah konsol `pkm` untuk mencatat dan memantau usulan hibah pengabdian masyarakat dosen.

28. **Subcommand CLI `fso` (`cli.py`)**:
    - Perintah konsol `fso` untuk mencatat dan mengaudit kalkulasi link budget transmisi optik nirkabel.

29. **Peningkatan Suite Pengujian Unit (597 Tests Passing)**:
    - Seluruh modul teruji dengan 597 unit test tanpa error dan tanpa kegagalan (100% pass rate).
