# Dokumentasi Perubahan Arsitektur v3.3.0 Milestone Release

Siklus pengembangan v3.3.0 Milestone Architectural Release menghadirkan ekspansi fungsional dan arsitektural terpadu pada portal otomasi editorial:
- **Sanitasi Media Responsif & Keamanan Interaktif**: Sanitasi elemen gambar responsif `<picture>` dan sub-elemen `<source>` dengan validasi atribut `srcset` dan `media` query breakpoint, sanitasi elemen modal `<dialog>` dan tombol interaksi form dialog (`formmethod="dialog"`), serta sanitasi atribut filter/sorting data tabular interaktif (`data-filter`, `data-sort`).
- **Parser Standar Akademik & Tata Kelola Kampus**: Parser sitasi biomedis/telemetri format Vancouver bernomor, auditor batas masa percobaan akademik dan surat peringatan (SP) mahasiswa, evaluator kepatuhan beban kerja dosen (BKD) per semester berbasis aturan Dikti, serta parser data penempatan mahasiswa KKN tematik pedesaan.
- **Auditor SEO & Standar Pengindeksan Web**: Kalkulator peluruhan kesegaran artikel (*publication freshness decay*), detektor pengenal reputasi konferensi internasional pemeringkatan CORE (A*, A, B, C), auditor integritas tautan jangkar daftar isi (*table of contents anchor integrity*), serta auditor aksesibilitas notasi matematika LaTeX dan tag MathJax/KaTeX.
- **Komponen Semantik Elementor Responsif**: Kartu profil desa mitra KKN tematik mahasiswa, kartu status kepatuhan BKD dosen per semester, kartu showcase makalah konferensi internasional bereputasi CORE, kartu konseling akademik dan rencana aksi kliring SP mahasiswa, serta kartu pameran riset laboratorium telemetri biomedis.
- **Format Pesan Telegram**: Format siaran penutupan diseminasi luaran KKN tematik pedesaan dan format siaran pencapaian presentasi makalah konferensi internasional berperingkat CORE.
- **Pengembangan Storage & Basis Data**: Tabel rekam penempatan proyek KKN desa (`kkn_village_projects`), tabel rekam beban kerja dosen per semester (`faculty_bkd_records`), serta tabel rekam jejak makalah konferensi internasional (`conference_presentations`).
- **Klien WordPress REST API**: Helper perolehan data komentar postingan (`get_comments_by_post_id`) dan helper pembuatan tag taksonomi baru (`create_tag`).
- **Generator Statis & Ekspor**: Generator Schema.org `Event`/`AcademicEvent` JSON-LD beranotasi tier CORE, serta eksportir markdown kompatibel generator blog statis Hexo (`to_hexo_markdown`).
- **Antarmuka Konsol CLI**: Subcommand baru `kkn`, `bkd`, dan `hexo`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 433 menjadi 460 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Media Responsif Picture & Source (`sanitizer.py`)**:
   - Memvalidasi elemen `<picture>` dan `<source>` serta mengamankan atribut `srcset`, `sizes`, `type`, dan `media` query dari skema berbahaya atau injeksi script.

2. **Sanitasi Elemen Dialog & Form Dialog Action (`sanitizer.py`)**:
   - Menjaga integritas elemen modal dialog HTML5 (`<dialog>`) dan atribut tombol pemicu aksi (`formmethod="dialog"`, `formaction`).

3. **Sanitasi Atribut Interaktif Data-Filter & Data-Sort (`sanitizer.py`)**:
   - Membersihkan atribut kontrol tabel interaktif (`data-filter`, `data-filter-value`, `data-sort`, `data-sort-order`) dari tag atau event handler inline.

4. **Parser Sitasi Akademik Format Vancouver (`parser.py`)**:
   - Mengurai format sitasi biomedis/telemetri numerik standar Vancouver menjadi struktur terdefinisi (penulis, judul artikel, jurnal, tahun, volume, edisi, halaman).

5. **Auditor Masa Percobaan Akademik Mahasiswa (`parser.py`)**:
   - Memverifikasi status evaluasi akademik mahasiswa berdasarkan IPK semester dan kumulatif, menentukan status SP1, SP2, SP3, atau kliring masa percobaan (clear).

6. **Evaluator Kepatuhan Beban Kerja Dosen BKD (`parser.py`)**:
   - Menghitung total SKS tridharma perguruan tinggi (pengajaran, penelitian, pengabdian, penunjang) dan memastikan rentang kepatuhan 12 - 16 SKS per semester.

7. **Parser Penempatan Mahasiswa KKN Tematik (`parser.py`)**:
   - Mengurai konfigurasi kelompok KKN tematik pedesaan (kode kelompok, desa, kecamatan, kabupaten, DPL, jumlah mahasiswa, fokus tema, luaran program).

8. **Kalkulator Peluruhan Kesegaran Konten Publikasi (`seo_validator.py`)**:
   - Menghitung indeks kesegaran artikel (*freshness score*) berdasarkan tanggal terbit dan modifikasi untuk optimasi visibilitas *evergreen content* pada mesin pencari.

9. **Detektor Peringkat Konferensi Internasional CORE (`seo_validator.py`)**:
   - Mengidentifikasi konferensi internasional bidang ilmu komputer dan telekomunikasi berdasarkan akronim dan memetakan ke peringkat CORE (A*, A, B, C).

10. **Auditor Integritas Tautan Jangkar Daftar Isi (`seo_validator.py`)**:
    - Memverifikasi tautan internal daftar isi (TOC) menuju ID heading target pada dokumen artikel untuk mencegah *broken anchor*.

11. **Auditor Aksesibilitas Notasi Matematika LaTeX (`seo_validator.py`)**:
    - Memeriksa konsistensi delimiter matematika (`$...$`, `$$...$$`) serta memverifikasi ketersediaan atribut label aksesibilitas aria/alt teks bagi pembaca layar (*screen reader*).

12. **Komponen Profil Desa KKN Tematik (`components.py`)**:
    - Kartu responsif pameran pengabdian desa mitra mahasiswa lengkap dengan program unggulan dan DPL.

13. **Komponen Kepatuhan Beban Kerja Dosen BKD (`components.py`)**:
    - Kartu visualisasi evaluasi SKS tridharma dosen per semester lengkap dengan badge kepatuhan ambang batas.

14. **Komponen Konferensi Internasional CORE (`components.py`)**:
    - Kartu showcase presentasi hasil riset di konferensi internasional bereputasi CORE dengan lencana tier.

15. **Komponen Konseling Kliring SP Mahasiswa (`components.py`)**:
    - Kartu rencana bimbingan konseling akademik bagi mahasiswa dalam masa perbaikan indeks prestasi.

16. **Komponen Riset Telemetri Biomedis (`components.py`)**:
    - Kartu pameran hasil pengujian perangkat telemetri kesehatan dan biosensor laboratorium.

17. **Formatter Siaran Penutupan KKN Tematik Telegram (`formatters.py`)**:
    - Format bulletin penutupan dan diseminasi proyek pengabdian masyarakat kelompok KKN tematik prodi.

18. **Formatter Siaran Presentasi Konferensi CORE Telegram (`formatters.py`)**:
    - Format kartu ucapan selamat atas keberhasilan presentasi makalah pada konferensi internasional berperingkat CORE.

19. **Manajer Rekam Proyek KKN Tematik Desa (`storage.py`)**:
    - Tabel basis data SQLite `kkn_village_projects` untuk menyimpan dan meninjau program KKN pedesaan mahasiswa.

20. **Manajer Rekam Kepatuhan BKD Dosen (`storage.py`)**:
    - Tabel basis data `faculty_bkd_records` untuk monitoring beban kerja dan kepatuhan SKS pengajar prodi.

21. **Manajer Rekam Konferensi Internasional (`storage.py`)**:
    - Tabel basis data `conference_presentations` untuk rekam jejak diseminasi riset di forum internasional.

22. **Helper WordPress Get Comments By Post ID (`wordpress_client.py`)**:
    - Mengambil data komentar pengguna pada artikel postingan WordPress via REST API.

23. **Helper WordPress Create Post Tag (`wordpress_client.py`)**:
    - Membuat taksonomi tag baru pada WordPress via REST API secara terprogram.

24. **Generator Schema.org AcademicEvent Konferensi (`exporter.py`)**:
    - Pembuatan metadata terstruktur JSON-LD untuk forum seminar/konferensi ilmiah internasional dengan anotasi peringkat CORE.

25. **Eksportir Markdown Kompatibel Hexo Static Blog (`exporter.py`)**:
    - Ekspor artikel ke format blog statis Hexo dengan konfigurasi frontmatter tanggal, kategori, dan tag.

26. **Subcommand CLI `kkn` (`cli.py`)**:
    - Perintah konsol manajemen rekam penempatan KKN tematik mahasiswa (list, add).

27. **Subcommand CLI `bkd` (`cli.py`)**:
    - Perintah konsol pencatatan dan evaluasi kepatuhan beban kerja dosen (list, add).

28. **Subcommand CLI `hexo` (`cli.py`)**:
    - Perintah konsol ekspor artikel ke format markdown blog statis Hexo.

29. **Pengujian Unit Terpadu (`tests/`)**:
    - Penambahan puluhan kasus uji unit pada modul sanitizer, parser, seo validator, komponen, formatters, storage, wp client, exporter, dan cli.

30. **Dokumentasi Rilis & Catatan Perubahan (`docs/`)**:
    - Pembaruan dokumen ringkasan arsitektur, release changelog, dan sinkronisasi rincian rilis v3.3.0.
