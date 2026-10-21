# Dokumentasi Perubahan Arsitektur v3.9.0 Milestone Release

Siklus pengembangan v3.9.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi kontainer gambar responsif `<picture>` dan elemen `<source>` dengan pencegahan injeksi protokol berbahaya pada atribut `srcset` (`sanitize_html5_picture_source_elements`), sanitasi grup kategori opsi `<optgroup>` dalam dropdown form (`sanitize_html5_optgroup_elements`), serta sanitasi pembungkus formulir `<fieldset>` dan teks judul `<legend>` (`sanitize_html5_fieldset_legend_elements`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator link budget komunikasi satelit downlink dan figure of merit G/T stasiun bumi (`calculate_satellite_link_budget`), kalkulator linearitas RF mixer dan supresi distorsi intermodulasi orde ketiga IIP3/IMD3 (`calculate_rf_intermod_distortion`), kalkulator penalti dispersi kromatik (CD) dan dispersi moda polarisasi (PMD) serat optik DWDM (`calculate_optical_fiber_dispersion`), serta evaluator kelulusan dan konversi SKS program Kampus Mengajar MBKM (`parse_kampus_mengajar_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor aksesibilitas kontrol pemutar audio dan transkrip teks pendamping (`audit_audio_accessibility_controls`), auditor kelengkapan pasangan semantik `<dl>`, `<dt>`, dan `<dd>` (`audit_semantic_definition_lists`), auditor pencegahan Cumulative Layout Shift (CLS) melalui penegakan dimensi eksplisit `width` dan `height` pada gambar (`audit_image_cls_dimensions`), serta auditor aksesibilitas notasi rumus matematika dan atribut display MathML (`audit_mathml_accessibility`).
- **Komponen Semantik Elementor Responsif**: Kartu kalkulasi link budget satelit dan stasiun bumi (`render_satellite_link_budget_card`), kartu analisis linearitas dan supresi IMD3 mixer RF (`render_rf_intermod_distortion_card`), kartu analisis penalti dispersi serat optik DWDM (`render_optical_fiber_dispersion_card`), kartu rekognisi kelulusan program Kampus Mengajar (`render_kampus_mengajar_recognition_card`), serta kartu visualisasi kerapatan daya spektral (PSD) dengan grafik SVG inline (`render_spectral_power_density_card`).
- **Format Pesan Telegram**: Format buletin Telegram audit link budget satelit (`format_satellite_link_announcement_telegram`) dan format buletin apresiasi kelulusan program Kampus Mengajar MBKM (`format_kampus_mengajar_announcement_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit link budget satelit (`satellite_link_budgets`), tabel rekam mahasiswa Kampus Mengajar (`student_kampus_mengajar`), serta tabel audit linearitas dan intermodulasi RF (`rf_intermod_records`).
- **Klien WordPress REST API**: Helper pengambilan postingan berdasarkan status publikasi dengan paginasi (`get_posts_by_status`) dan helper penggandaan artikel ke draf baru (`duplicate_post_as_draft`).
- **Generator Statis & Ekspor**: Generator Schema.org `EducationalOrganization` JSON-LD (`generate_educational_organization_json_ld`) serta eksportir markdown Next.js Contentlayer MDX (`to_nextjs_contentlayer_mdx`).
- **Antarmuka Konsol CLI**: Subcommand baru `satellite`, `mengajar`, dan `rf-intermod`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 597 menjadi 625 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen HTML5 Picture & Source (`sanitizer.py`)**:
   - Memvalidasi elemen `<picture>` dan anak `<source>`, membersihkan `srcset` terhadap payload berbahaya (`javascript:`, `data:text/html`), serta memvalidasi MIME type gambar.

2. **Sanitasi Elemen HTML5 Optgroup Dropdown (`sanitizer.py`)**:
   - Membersihkan elemen grup `<optgroup>`, mengamankan atribut `label`, dan melucuti event handler inline.

3. **Sanitasi Elemen HTML5 Fieldset & Legend (`sanitizer.py`)**:
   - Membersihkan kontainer formulir `<fieldset>` dan elemen label semantik `<legend>`, memastikan atribut `form` dan `disabled` aman.

4. **Kalkulator Link Budget Satelit & G/T Stasiun Bumi (`parser.py`)**:
   - Menghitung Free-Space Path Loss (FSPL) downlink, spectral noise density $C/N_0$, Carrier-to-Noise Ratio ($C/N$), dan link margin transmisi satelit DVB-S2.

5. **Kalkulator Linearitas RF Mixer IIP3 & Distorsi Intermodulasi (`parser.py`)**:
   - Menghitung Output IP3 (OIP3), daya produk intermodulasi orde ketiga (IMD3), dan rasio supresi linearitas $\Delta IM3$ pada penguat/mixer RF.

6. **Kalkulator Penalti Dispersi Serat Optik DWDM (`parser.py`)**:
   - Menghitung delay dispersi kromatik (CD), Differential Group Delay (DGD) PMD, rasio pelebaran pulsa terhadap slot bit, dan estimasi power penalty optik.

7. **Evaluator Rekognisi SKS Program Kampus Mengajar MBKM (`parser.py`)**:
   - Mengurai evaluasi kepala sekolah dan dosen pembimbing lapangan, menghitung skor komposit, konversi nilai mutu, dan ekuivalensi hingga 20 SKS kurikulum.

8. **Auditor Aksesibilitas Kontrol Audio & Transkrip Teks (`seo_validator.py`)**:
   - Memeriksa ketersediaan atribut `controls`, ketiadaan `autoplay` agresif, dan tautan transkrip teks pendamping pada elemen `<audio>`.

9. **Auditor Kelengkapan Semantic Definition List DL DT DD (`seo_validator.py`)**:
   - Memverifikasi kepatuhan hirarki `<dl>`, mencegah istilah yatim `<dt>` tanpa `<dd>`, serta memastikan konten istilah dan deskripsi tidak kosong.

10. **Auditor Pencegahan Cumulative Layout Shift (CLS) Gambar (`seo_validator.py`)**:
    - Memverifikasi keberadaan atribut eksplisit `width` dan `height` pada setiap tag `<img>` untuk stabilitas tata letak visual Core Web Vitals.

11. **Auditor Aksesibilitas Notasi Rumus MathML (`seo_validator.py`)**:
    - Memeriksa elemen `<math>`, atribut display mode (`inline` / `block`), dan ketersediaan anotasi alternatif (`alttext`, `aria-label`, `<annotation>`).

12. **Komponen Link Budget Satelit Downlink (`components.py`)**:
    - Kartu visual Elementor ringkasan parameter satelit (EIRP, G/T, $C/N$, link margin, status kelayakan).

13. **Komponen Linearitas & Intermodulasi Mixer RF (`components.py`)**:
    - Kartu visualisasi spesifikasi RF front-end dengan metrik Pin, Gain, IIP3, dan supresi IMD3.

14. **Komponen Analisis Penalti Dispersi Serat Optik (`components.py`)**:
    - Kartu kalkulasi transmisi optik jarak jauh dengan visualisasi delay CD, delay PMD, dan penalti daya redaman.

15. **Komponen Apresiasi Program Kampus Mengajar MBKM (`components.py`)**:
    - Kartu visual Elementor pengakuan pencapaian mahasiswa dalam penugasan asistensi mengajar di sekolah mitra.

16. **Komponen Visualisasi Kerapatan Daya Spektral PSD (`components.py`)**:
    - Kartu visualisasi domain frekuensi penganalisis spektrum RF dengan grafik polyline SVG inline terisolasi.

17. **Formatter Telegram Audit Link Budget Satelit (`formatters.py`)**:
    - Template pesan siaran resmi Telegram untuk hasil audit keandalan tautan komunikasi satelit transponder.

18. **Formatter Telegram Apresiasi Kelulusan Kampus Mengajar (`formatters.py`)**:
    - Template pesan siaran Telegram ucapan selamat atas kelulusan dan penyelesaian program Kampus Mengajar.

19. **Manajer Rekam Audit Link Budget Satelit (`storage.py`)**:
    - Skema tabel basis data `satellite_link_budgets` dan metode `record_satellite_link_budget`, `list_satellite_link_budgets`, `get_satellite_link_budget_by_id`.

20. **Manajer Rekam Mahasiswa Kampus Mengajar (`storage.py`)**:
    - Skema tabel `student_kampus_mengajar` dan metode `record_kampus_mengajar_student`, `list_kampus_mengajar_students`, `get_kampus_mengajar_by_nim`.

21. **Manajer Rekam Linearitas & Intermodulasi RF (`storage.py`)**:
    - Skema tabel `rf_intermod_records` dan metode `record_rf_intermod_distortion`, `list_rf_intermod_records`, `get_rf_intermod_by_id`.

22. **Helper WordPress Get Posts By Status Paginasi (`wordpress_client.py`)**:
    - Metode `get_posts_by_status` untuk mengambil daftar postingan terfilter berdasarkan status (draft, pending, publish, future, trash).

23. **Helper WordPress Duplicate Post As Draft (`wordpress_client.py`)**:
    - Metode `duplicate_post_as_draft` untuk mengkloning artikel terbitan/draf menjadi artikel draf baru.

24. **Generator Schema.org EducationalOrganization JSON-LD (`exporter.py`)**:
    - Metode `generate_educational_organization_json_ld` untuk standarisasi profil institusional program studi perguruan tinggi.

25. **Eksportir Markdown Next.js Contentlayer MDX (`exporter.py`)**:
    - Metode `to_nextjs_contentlayer_mdx` untuk transformasi artikel ke format Contentlayer MDX modern.

26. **Subcommand CLI `satellite` (`cli.py`)**:
    - Perintah konsol `satellite` untuk mencatat dan mengaudit kalkulasi link budget satelit.

27. **Subcommand CLI `mengajar` (`cli.py`)**:
    - Perintah konsol `mengajar` untuk mencatat dan menginventarisasi rekognisi SKS program Kampus Mengajar.

28. **Subcommand CLI `rf-intermod` (`cli.py`)**:
    - Perintah konsol `rf-intermod` untuk mencatat dan memantau linearitas modul RF.

29. **Peningkatan Suite Pengujian Unit (625 Tests Passing)**:
    - Seluruh modul teruji dengan 625 unit test tanpa error dan tanpa kegagalan (100% pass rate).
