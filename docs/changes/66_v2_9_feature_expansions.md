# Dokumentasi Perubahan Arsitektur v2.9.0

Siklus pengembangan v2.9.0 menghadirkan ekspansi arsitektural komprehensif pada ekosistem otomasi editorial:
- **Sanitasi Media & Keamanan DOM Lanjutan**: Sanitasi elemen fallback `<canvas>` HTML5 dengan pemblokiran scriptable context, sanitasi anotasi fonetik Ruby linguistik (`<ruby>`, `<rt>`, `<rp>`), dan netralisasi tautan eksternal serta skrip MathML.
- **Parser Spesifikasi & Standar Akademik**: Parser sitasi jurnal dan transaksi IEEE, parser urutan standar operasional prosedur (SOP) laboratorium, parser kriteria kelayakan beasiswa akademik, dan kalkulator konversi beban jam studi SKS ke ECTS standar Eropa.
- **Auditor SEO & Validasi Semantik Terstruktur**: Kalkulator indeks keterbacaan Gunning Fog teks akademik Indonesia, detektor tautan yatim (orphan links) dan broken internal anchors, validator kredensial akademik dan ORCID ID penulis, serta validator disclaimer lisensi Open Access / Creative Commons.
- **Komponen Semantik Elementor**: Kartu pemetaan capaian pembelajaran Taksonomi Bloom (C1 - C6), kartu protokol pengelolaan limbah B3 laboratorium, matriks transfer kredit pertukaran pelajar, kartu pameran paten dan HKI riset fakultas, dan kartu testimoni mitra industri studi penelusuran lulusan (tracer study).
- **Format Pesan Telegram**: Format pengumuman pendaftaran paten/HKI resmi dan format kartu persetujuan transfer kredit akademik mahasiswa pertukaran.
- **Pengembangan Storage & Basis Data**: Manajemen penugasan peer reviewer artikel (`article_reviewers`), pencatatan log sindikasi dan republikasi eksternal (`syndication_logs`), serta manajer checklist alur kerja verifikasi editorial (`editorial_checklists`).
- **Klien WordPress REST API**: Helper pembaruan massal kategori pos (`batch_update_post_categories`) dan helper pencarian pengguna berdasarkan slug (`get_user_by_slug`).
- **Generator Statis & Ekspor**: Generator Schema.org `TechArticle` JSON-LD untuk panduan lab teknik, dan eksportir markdown kompatibel Pelican static site generator.
- **Antarmuka Konsol CLI**: Perintah subcommand baru `reviewer`, `pelican`, dan `checklist`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 319 menjadi 347 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Fallback Canvas HTML5 (`sanitizer.py`)**:
   - Menjaga keutuhan elemen fallback aksesibilitas pada tag `<canvas>` sembari memblokir atribut manipulasi konteks grafis (`context`, `oncontextmenu`, ekspresi skrip).

2. **Sanitasi Anotasi Ruby Fonetik Linguistik (`sanitizer.py`)**:
   - Memvalidasi dan membersihkan penanda fonetik `<ruby>`, `<rt>`, `<rp>`, `<rb>`, `<rtc>` agar aman dari penyisipan payload XSS.

3. **Netralisasi Skrip & Tautan Eksternal MathML (`sanitizer.py`)**:
   - Memastikan formula matematis MathML tetap bersih dengan melucuti atribut `href`, `xlink:href`, dan atribut eksternal tak berizin.

4. **Parser Sitasi IEEE Journal & Transactions (`parser.py`)**:
   - Mengurai format rujukan sitasi IEEE standar menjadi data terstruktur (penulis, judul artikel, transaksi/jurnal, volume, edisi, halaman, tahun, DOI).

5. **Parser Standar Operasional Prosedur (SOP) Laboratorium (`parser.py`)**:
   - Mengurai langkah berurutan instruksi kerja lab, nomor tahapan, arahan praktikum, dan catatan kewaspadaan K3.

6. **Parser Kriteria Kelayakan Beasiswa Akademik (`parser.py`)**:
   - Mengekstrak informasi persyaratan IPK minimal, jenjang semester, berkas portofolio, dan batas waktu aplikasi beasiswa.

7. **Kalkulator Konversi Beban SKS ke ECTS (`parser.py`)**:
   - Mengonversi satuan kredit semester (SKS) Indonesia ke European Credit Transfer and Accumulation System (ECTS) dengan rasio resmi 1 SKS ≈ 1.6 ECTS.

8. **Kalkulator Indeks Keterbacaan Gunning Fog Akademik Indonesia (`seo_validator.py`)**:
   - Menghitung tingkat kompleksitas teks akademik bahasa Indonesia berdasarkan panjang rata-rata kalimat dan densitas kata bersuku kata tinggi.

9. **Detektor Orphan Links & Broken Internal Anchors (`seo_validator.py`)**:
   - Memverifikasi apakah semua tautan jangkar lokal (`#id`) merujuk ke elemen HTML yang benar-benar ada dalam konten artikel.

10. **Validator Kredensial Akademik & ORCID ID Penulis (`seo_validator.py`)**:
    - Memvalidasi struktur format 16-digit ORCID ID berstandar internasional dan kepemilikan gelar akademik penulis.

11. **Validator Lisensi Open Access & Creative Commons (`seo_validator.py`)**:
    - Memverifikasi keberadaan pernyataan lisensi terbuka (CC BY / CC BY-SA) dan klausul atribusi pada karya ilmiah.

12. **Komponen Pemetaan Level Taksonomi Bloom C1-C6 (`components.py`)**:
    - Visualisasi hierarki capaian pembelajaran mata kuliah kurikulum OBE (Outcome-Based Education) untuk akreditasi nasional dan internasional.

13. **Komponen Protokol Pengelolaan Limbah B3 Laboratorium (`components.py`)**:
    - Tabel visual kategori limbah kimia/B3, spesifikasi wadah penampung, ruang penyimpanan aman, dan jadwal pembuangan.

14. **Komponen Matriks Transfer Kredit Mahasiswa Pertukaran (`components.py`)**:
    - Tabel ekuivalensi mata kuliah kampus mitra luar negeri dengan mata kuliah lokal beserta bobot SKS yang diakui.

15. **Komponen Kartu Pameran Paten & HKI Dosen (`components.py`)**:
    - Showcase resmi perlindungan hukum invensi riset dosen, nomor paten terdaftar, susunan inventor, dan abstrak inovasi.

16. **Komponen Testimoni Mitra Industri Tracer Study (`components.py`)**:
    - Kartu umpan balik pimpinan industri mitra dan metrik daya serap lulusan prodi di dunia kerja nyata.

17. **Format Pengumuman Pendaftaran Paten Telegram (`formatters.py`)**:
    - Format pesan pengumuman pencapaian perolehan hak paten terdaftar untuk kanal siaran Telegram prodi.

18. **Format Persetujuan Transfer Kredit Telegram (`formatters.py`)**:
    - Format pesan notifikasi resmi hasil konversi nilai dan kredit mata kuliah pertukaran mahasiswa.

19. **Manajer Penugasan Reviewer Editorial (`storage.py`)**:
    - Skema tabel `article_reviewers` serta fungsi penugasan, pemantauan, dan pembaruan status peer review per artikel.

20. **Manajer Log Sindikasi Eksternal Artikel (`storage.py`)**:
    - Skema tabel `syndication_logs` untuk pencatatan riwayat distribusi artikel ke Medium, LinkedIn, dan portal riset.

21. **Manajer Checklist Alur Kerja Editorial (`storage.py`)**:
    - Skema tabel `editorial_checklists` untuk verifikasi kelayakan praterbit (plagiarism audit, fact checking, proofreading).

22. **Helper Batch Update Kategori WordPress (`wordpress_client.py`)**:
    - Otomasi pembaruan kategori secara massal pada sekumpulan pos WordPress via REST API.

23. **Helper Pencarian User Berdasarkan Slug WordPress (`wordpress_client.py`)**:
    - Pengambilan detail informasi penulis/user berdasarkan slug unik dari WordPress REST API.

24. **Generator Schema.org TechArticle JSON-LD (`exporter.py`)**:
    - Metadata terstruktur khusus tutorial rekayasa dan panduan teknis laboratorium.

25. **Generator Markdown Kompatibel Pelican SSG (`exporter.py`)**:
    - Generator berkas Markdown kompatibel static site generator Pelican dengan format header colon-delimited.

26. **Subcommand CLI `reviewer` (`cli.py`)**:
    - Perintah konsol penugasan dan pelacakan status peer reviewer editorial.

27. **Subcommand CLI `pelican` (`cli.py`)**:
    - Perintah konsol ekspor artikel langsung ke format markdown Pelican SSG.

28. **Subcommand CLI `checklist` (`cli.py`)**:
    - Perintah konsol manajemen checklist verifikasi praterbit editorial.

29. **Ekspansi Pengujian Unit Terpadu (347 Tests Passing)**:
    - Seluruh pengujian lolos 100% tanpa regresi maupun kegagalan.
