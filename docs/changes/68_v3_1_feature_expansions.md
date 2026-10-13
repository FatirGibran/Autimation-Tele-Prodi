# Dokumentasi Perubahan Arsitektur v3.1.0 Milestone Release

Siklus pengembangan v3.1.0 Milestone Architectural Release menghadirkan ekspansi arsitektural menyeluruh pada ekosistem otomasi editorial:
- **Sanitasi Media & Keamanan DOM Lanjutan**: Sanitasi elemen ukuran dan indikator progress HTML5 (`<meter>`, `<progress>`), sanitasi elemen gambar responsif (`<picture>`, `<source>`), serta pengamanan atribut tema dan mode tampilan (`data-theme`, `data-mode`) dari injeksi CSS-in-attribute.
- **Parser Standar Akademik & Tata Kelola Kampus**: Parser sitasi akademik Springer Lecture Notes in Computer Science (LNCS/LSCS), validator kelayakan checklist pendaftaran ujian proposal skripsi, parser log kegiatan pengabdian kepada masyarakat (PKM), serta parser audit kepatuhan keselamatan kerja (K3) laboratorium.
- **Auditor SEO & Standar Pengindeksan Web**: Detektor duplikasi atribut `id` elemen HTML untuk navigasi anchor internal, pendeteksi akreditasi dan peringkat jurnal nasional SINTA 1-6, auditor direktif indexing mesin pencari (`robots` directives), serta auditor kesiapan metadata media sosial (Open Graph dan Twitter Cards).
- **Komponen Semantik Elementor Responsif**: Kartu showcase program pengabdian masyarakat (PKM), kartu pameran prestasi kejuaraan inovasi mahasiswa, kartu badge direktori jurnal terakreditasi SINTA, kartu pengumuman rekrutmen asisten praktikum laboratorium, dan kartu standar K3 lab beserta panduan tanggap darurat dan denah APAR.
- **Format Pesan Telegram**: Format siaran pengumuman kegiatan pengabdian masyarakat prodi dan format siaran perayaan kemenangan prestasi mahasiswa pada kompetisi teknologi.
- **Pengembangan Storage & Basis Data**: Tabel pencatatan rekam jejak prestasi kompetisi mahasiswa (`competition_achievements`), direktori katalog jurnal ilmiah terakreditasi (`journal_indexings`), serta log riwayat inspeksi keselamatan kerja lab (`safety_inspections`).
- **Klien WordPress REST API**: Helper perolehan kategori turunan berdasarkan parent category ID (`get_categories_by_parent`) dan helper ping kesehatan konektivitas REST API beserta validasi kredensial pengguna (`ping_api`).
- **Generator Statis & Ekspor**: Generator Schema.org `SpecialAnnouncement` JSON-LD untuk instruksi dan maklumat akademik darurat, serta eksportir markdown kompatibel generator situs statis Material for MkDocs (`to_mkdocs_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `achievement`, `mkdocs`, dan `safety-log`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 375 menjadi 404 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Meter & Progress HTML5 (`sanitizer.py`)**:
   - Memvalidasi atribut `value`, `min`, `max`, `low`, `high`, dan `optimum` serta menolak nilai non-numerik berbahaya atau injeksi script.

2. **Sanitasi Gambar Responsif Picture & Source (`sanitizer.py`)**:
   - Mengamankan elemen `<picture>` dan `<source>` dengan memfilter skema URI `srcset` dan memverifikasi MIME type atribut `type` (seperti `image/webp`, `image/avif`).

3. **Sanitasi Atribut Tema & Tampilan (`sanitizer.py`)**:
   - Membersihkan atribut `data-theme` dan `data-mode` agar hanya menerima token alfanumerik yang valid, menangkal serangan CSS expression injection.

4. **Parser Sitasi Springer LNCS & LSCS (`parser.py`)**:
   - Mengurai format rujukan prosiding dan buku berseri Springer LNCS menjadi data terstruktur (penulis, judul artikel, volume LNCS, tahun penerbitan, DOI, dan penerbit).

5. **Validator Kelayakan Ujian Proposal Skripsi (`parser.py`)**:
   - Memvalidasi persyaratan administrasi mahasiswa untuk mendaftar seminar proposal (minimal SKS lulus, IPK kumulatif, pemenuhan mata kuliah prasyarat, dan tanda tangan pembimbing).

6. **Parser Log Kegiatan Pengabdian Masyarakat PKM (`parser.py`)**:
   - Mengekstrak data kegiatan PKM dosen dan mahasiswa (judul program, mitra sasaran, lokasi desa binaan, sumber pendanaan, dan luaran penerapan teknologi).

7. **Parser Audit Checklist Keselamatan K3 Lab (`parser.py`)**:
   - Mengurai kepatuhan keselamatan kerja di ruang laboratorium komputer dan telekomunikasi (APAR, kotak P3K, grounding listrik, jalur evakuasi).

8. **Auditor ID Elemen Duplikat Semantik (`seo_validator.py`)**:
   - Memeriksa keunikan atribut `id` pada seluruh elemen HTML dokumen guna menjamin standar aksesibilitas WCAG dan keandalan deep link anchor.

9. **Detektor Akreditasi Jurnal SINTA (`seo_validator.py`)**:
   - Mengidentifikasi pengakuan status akreditasi jurnal ilmiah nasional Republik Indonesia dari peringkat SINTA 1 (tertinggi) hingga SINTA 6.

10. **Auditor Direktif Meta Robots Indexing (`seo_validator.py`)**:
    - Menganalisis tag `<meta name="robots">` untuk memastikan artikel terindeks optimal dan mendeteksi tag larangan crawl yang keliru.

11. **Auditor Metadata Sosial Open Graph & Twitter Cards (`seo_validator.py`)**:
    - Memeriksa kelengkapan prasyarat sharing media sosial (`og:title`, `og:description`, `og:image`, `twitter:card`, `twitter:image`).

12. **Komponen Showcase Pengabdian Masyarakat PKM (`components.py`)**:
    - Kartu responsif visualisasi kontribusi keilmuan civitas akademika kepada masyarakat dan industri daerah.

13. **Komponen Prestasi Kejuaraan Mahasiswa (`components.py`)**:
    - Kartu pencapaian piala, medali, dan penghargaan mahasiswa dalam ajang kompetisi sains dan teknologi informasi nasional/internasional.

14. **Komponen Badge & Profil Jurnal SINTA (`components.py`)**:
    - Kartu profil jurnal prodi dengan lencana peringkat akreditasi SINTA resmi dan informasi ruang lingkup ilmiah.

15. **Komponen Rekrutmen Asisten Praktikum Lab (`components.py`)**:
    - Kartu publikasi lowongan asisten laboratorium praktikum dengan kualifikasi mata kuliah dan lini masa rekrutmen.

16. **Komponen Standar K3 Laboratorium & Posisi APAR (`components.py`)**:
    - Kartu panduan keselamatan kerja di lab lengkap dengan instruksi evakuasi bencana dan nomor kontak darurat kampus.

17. **Formatter Pengabdian Masyarakat Telegram (`formatters.py`)**:
    - Penataan format pesan pengumuman kegiatan PKM untuk kanal publikasi Telegram resmi prodi.

18. **Formatter Perayaan Juara Mahasiswa Telegram (`formatters.py`)**:
    - Penataan format siaran ucapan selamat atas raihan juara kompetisi mahasiswa di kanal Telegram.

19. **Manajer Rekam Jejak Prestasi Mahasiswa (`storage.py`)**:
    - Manajemen basis data SQLite tabel `competition_achievements` dengan filter pencarian per tahun dan nama tim.

20. **Manajer Katalog Jurnal SINTA (`storage.py`)**:
    - Manajemen direktori tabel `journal_indexings` dengan filter peringkat minimum SINTA dan ISSN.

21. **Manajer Log Inspeksi K3 Lab (`storage.py`)**:
    - Tabel `safety_inspections` untuk penyimpanan hasil audit rutin kepatuhan keselamatan laboratorium.

22. **Helper Kategori Turunan WordPress (`wordpress_client.py`)**:
    - Pengambilan kategori anak berdasarkan ID induk melalui REST API WordPress.

23. **Helper Ping Kesehatan & Validasi Akun WordPress (`wordpress_client.py`)**:
    - Pengujian latensi konektivitas dan validasi hak akses kredensial bot pada endpoint `/wp-json/wp/v2/users/me`.

24. **Generator Schema.org SpecialAnnouncement JSON-LD (`exporter.py`)**:
    - Konstruksi schema terstruktur untuk pengumuman mendesak, tanggap darurat, dan maklumat akademik prodi.

25. **Generator Markdown Kompatibel MkDocs Material (`exporter.py`)**:
    - Ekspor artikel ke format Material for MkDocs SSG dengan frontmatter standar dan header hierarkis.

26. **Subcommand CLI `achievement` (`cli.py`)**:
    - Manajemen rekam jejak prestasi kompetisi mahasiswa secara langsung lewat baris perintah konsol.

27. **Subcommand CLI `mkdocs` (`cli.py`)**:
    - Ekspor konten artikel di basis data langsung ke berkas markdown siap pakai MkDocs.

28. **Subcommand CLI `safety-log` (`cli.py`)**:
    - Pencatatan dan audit log keselamatan kerja laboratorium melalui baris perintah konsol.

29. **Ekspansi Suite Pengujian Unit Terpadu (404 Tests Passing)**:
    - 404 unit tests terverifikasi dengan tingkat kelulusan 100% tanpa regresi pada kode sebelumnya.
