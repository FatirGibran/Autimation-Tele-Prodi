# Dokumentasi Perubahan Arsitektur v3.4.0 Milestone Release

Siklus pengembangan v3.4.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi DOM Spesifik & Keamanan Telemetri**: Sanitasi elemen `<use>` SVG terhadap referensi eksternal cross-origin (`xlink:href` dan `href`), validasi format waktu ISO 8601 pada atribut `datetime` elemen `<time>`, serta sanitasi elemen komputasi `<output>` dari injeksi manipulasi formulir kalkulasi telemetri.
- **Parser Standar Akademik & Regulasi Telekomunikasi**: Resolver dan normalizer DOI publikasi ilmiah IEEE Transactions, evaluator proposal hibah riset BIMA Kemdikbudristek dosen, evaluator kelayakan penempatan kerja praktik (KP) industri mahasiswa, serta parser izin stasiun radio (ISR) dan pemetaan spektrum frekuensi radio laboratorium.
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut**: Auditor URL profil dan skor SINTA Kemdikbud dosen, auditor pelompatan level heading (*heading hierarchy level skipping*), auditor meta tag multimedia Open Graph audio/video, serta auditor aksesibilitas caption dan deskripsi tabel data.
- **Komponen Semantik Elementor Responsif**: Kartu pameran penghargaan hibah riset BIMA Kemdikbud, kartu laporan penempatan kerja praktik industri mahasiswa, kartu status alokasi spektrum frekuensi ISR lab, kartu pameran profil luaran SINTA dosen, serta kartu topologi jaringan transmisi serat optik kampus.
- **Format Pesan Telegram**: Format siaran bulletin penghargaan dana riset BIMA Kemdikbud dan format siaran showcase penempatan kerja praktik industri mahasiswa.
- **Pengembangan Storage & Basis Data**: Tabel rekam usulan hibah riset dosen (`bima_grant_proposals`), tabel rekam penempatan kerja praktik mahasiswa (`kerja_praktik_placements`), serta tabel inventaris alokasi spektrum frekuensi lab (`lab_spectrum_allocations`).
- **Klien WordPress REST API**: Helper perolehan daftar artikel berdasarkan ID penulis (`get_posts_by_author`) dan helper penghapusan tag taksonomi (`delete_tag`).
- **Generator Statis & Ekspor**: Generator Schema.org `GovernmentService` JSON-LD untuk program hibah penelitian kementerian, serta eksportir markdown kompatibel generator dokumentasi statis VitePress (`to_vitepress_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `bima`, `kp`, dan `vitepress`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 460 menjadi 488 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi SVG Use Cross-Origin Reference (`sanitizer.py`)**:
   - Memvalidasi elemen `<use>` dan menolak referensi URI eksternal pada atribut `href` dan `xlink:href`, hanya memperbolehkan referensi lokal fragment identifier (`#id`).

2. **Sanitasi Atribut Waktu HTML5 Datetime ISO 8601 (`sanitizer.py`)**:
   - Menjaga integritas elemen `<time>` dengan memastikan atribut `datetime` menggunakan format tanggal/waktu standar ISO 8601 dan membuang skrip manipulasi microdata.

3. **Sanitasi Elemen Komputasi Output Telemetri (`sanitizer.py`)**:
   - Membersihkan elemen `<output>` dari atribut handler dinamis serta memvalidasi token atribut `for` dan `name`.

4. **Resolver DOI Publikasi Ilmiah IEEE Transactions (`parser.py`)**:
   - Mengurai dan menormalisasi string DOI IEEE (`10.1109/...`) menjadi URL HTTPS kanonikal IEEE Xplore Digital Library.

5. **Evaluator Usulan Hibah Riset BIMA Kemdikbud (`parser.py`)**:
   - Menilai kelayakan usulan proposal penelitian berdasarkan skema riset Ditjen Diktiristek, format NIDN dosen pengusul, dan batas pagu anggaran.

6. **Evaluator Penempatan Kerja Praktik Mahasiswa (`parser.py`)**:
   - Memvalidasi kelayakan penempatan kerja praktik (KP) mahasiswa berdasarkan sektor industri, kesesuaian durasi minimal (8 minggu), dan pembimbing lapangan.

7. **Parser Alokasi Spektrum Frekuensi & Lisensi ISR Lab (`parser.py`)**:
   - Mengurai parameter frekuensi tengah (MHz), lebar pita bandwidth (MHz), dan daya pancar (dBm) untuk klasifikasi pita ISM dan kepatuhan perizinan ISR.

8. **Auditor URL Profil & Skor SINTA Dosen (`seo_validator.py`)**:
   - Memverifikasi format tautan profil SINTA Kemdikbud dosen pengajar serta memvalidasi ketersediaan metadata metrik sitasi.

9. **Auditor Kepatuhan Hirarki Heading Level Skipping (`seo_validator.py`)**:
   - Mendeteksi adanya lompatan hierarki tag heading HTML (seperti H2 melompat ke H4 tanpa H3 perantara) demi kepatuhan WCAG 2.1 dan SEO terstruktur.

10. **Auditor Tag Multimedia Open Graph Audio & Video (`seo_validator.py`)**:
    - Memverifikasi kelengkapan meta tag `og:audio` dan `og:video` beserta spesifikasi MIME type dan protokol secure URL.

11. **Auditor Aksesibilitas Keterangan Tabel Data (`seo_validator.py`)**:
    - Memeriksa ketersediaan elemen `<caption>` dan deskripsi ringkasan pada tabel HTML untuk memastikan aksesibilitas pembaca layar (*screen reader*).

12. **Komponen Hibah Penelitian BIMA Kemdikbud (`components.py`)**:
    - Kartu pameran penghargaan dana hibah penelitian dosen lengkap dengan skema, pagu anggaran, dan nomor kontrak.

13. **Komponen Laporan Penempatan Kerja Praktik (`components.py`)**:
    - Kartu responsif showcase penempatan magang industri mahasiswa di mitra telekomunikasi bereputasi.

14. **Komponen Status Spektrum Frekuensi ISR Lab (`components.py`)**:
    - Kartu visualisasi izin frekuensi radio laboratorium dengan badge legalitas ISR aktif.

15. **Komponen Profil Metrik Skor SINTA Dosen (`components.py`)**:
    - Kartu showcase capaian skor SINTA dan luaran publikasi ilmiah dosen pengajar prodi.

16. **Komponen Jaringan Transmisi Serat Optik Kampus (`components.py`)**:
    - Kartu pameran topologi jaringan backbone fiber optik kampus dengan metrik kapasitas gigabit.

17. **Formatter Siaran Pengumuman Hibah BIMA Telegram (`formatters.py`)**:
    - Format pesan siaran pencapaian penerima hibah BIMA Kemdikbud di kanal Telegram prodi.

18. **Formatter Siaran Penempatan Kerja Praktik Telegram (`formatters.py`)**:
    - Format buletin pengumuman penempatan mahasiswa di program magang industri telekomunikasi.

19. **Manajer Rekam Usulan Hibah BIMA Kemdikbud (`storage.py`)**:
    - Tabel basis data SQLite `bima_grant_proposals` untuk mencatat dan mengelola rekam usulan proposal riset dosen.

20. **Manajer Rekam Penempatan Kerja Praktik Mahasiswa (`storage.py`)**:
    - Tabel basis data `kerja_praktik_placements` untuk monitoring penempatan magang kerja praktik mahasiswa.

21. **Manajer Rekam Alokasi Spektrum Frekuensi Lab (`storage.py`)**:
    - Tabel basis data `lab_spectrum_allocations` untuk inventaris izin stasiun radio dan alokasi frekuensi eksperimen lab.

22. **Helper WordPress Get Posts By Author ID (`wordpress_client.py`)**:
    - Mengambil daftar postingan artikel berdasarkan ID pengguna penulis melalui WordPress REST API.

23. **Helper WordPress Delete Post Tag (`wordpress_client.py`)**:
    - Menghapus tag taksonomi artikel secara terprogram dengan flag force via WordPress REST API.

24. **Generator Schema.org GovernmentService Hibah Riset (`exporter.py`)**:
    - Pembuatan metadata terstruktur JSON-LD untuk program hibah riset kementerian dengan informasi pagu dana dan penerima.

25. **Eksportir Markdown Kompatibel VitePress Static Docs (`exporter.py`)**:
    - Ekspor artikel ke format dokumentasi statis modern VitePress dengan konfigurasi frontmatter terstruktur.

26. **Subcommand CLI `bima` (`cli.py`)**:
    - Perintah konsol pencatatan dan peninjauan usulan hibah riset BIMA Kemdikbud (list, add).

27. **Subcommand CLI `kp` (`cli.py`)**:
    - Perintah konsol pencatatan dan peninjauan penempatan kerja praktik industri mahasiswa (list, add).

28. **Subcommand CLI `vitepress` (`cli.py`)**:
    - Perintah konsol ekspor artikel ke format markdown VitePress static documentation.
