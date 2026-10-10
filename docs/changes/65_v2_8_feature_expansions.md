# Dokumentasi Perubahan Arsitektur v2.8.0

Siklus pengembangan v2.8.0 menghadirkan ekspansi arsitektural komprehensif pada ekosistem otomasi editorial:
- **Sanitasi Media & Keamanan DOM**: Sanitasi elemen subtitle/caption `<track>` HTML5 audio/video, pelucutan filter SVG primitif berbahaya (`<feImage>`, `<filter>`), dan sanitasi deklaratif template Web Components `<slot>` & `<template>`.
- **Parser Spesifikasi & Standar Akademik**: Parser tabel inventaris laboratorium perangkat keras, parser sitasi jurnal ilmiah format APA edisi ke-7, parser rubrik penilaian sidang tugas akhir/skripsi, dan konverter skala nilai mutu huruf ke IPK standar Indonesia.
- **Auditor SEO & Validasi Semantik Terstruktur**: Detektor repetisi kata pembuka kalimat berurutan (consecutive sentence starts), evaluator distribusi penanda transisi paragraf bahasa Indonesia, validator ajakan bertindak (CTA) pada meta description, dan pemeriksa sintaks serta atribut wajib embedded JSON-LD Schema.org.
- **Komponen Semantik Elementor**: Kartu visual alur prasyarat mata kuliah (prerequisite flow), kartu checklist protokol APD keselamatan lab, tabel kuota pertukaran pelajar internasional, kartu milestone progres luaran hibah riset dosen, dan histogram visual distribusi gaji pertama lulusan alumni (tracer study).
- **Format Pesan Telegram**: Format pengumuman pembukaan beasiswa pendidikan dan kartu siaran publikasi artikel jurnal internasional bereputasi tinggi.
- **Pengembangan Storage & Basis Data**: Manajemen papan catatan kolaborasi editorial artikel (`article_notes`), pencatatan log pengiriman webhook publikasi (`publishing_webhook_logs`), dan resolver sinonim/alias istilah taksonomi akademik (`taxonomy_synonyms`).
- **Klien WordPress REST API**: Helper penghapusan massal pos (`batch_trash_posts`) dan helper penelusuran media berdasarkan slug (`get_media_by_slug`).
- **Generator Statis & Ekspor**: Generator Schema.org `ScholarlyArticle` JSON-LD lengkap dengan entitas penulis berantai, dan eksportir markdown kompatibel Zola SSG dengan format frontmatter TOML `+++`.
- **Antarmuka Konsol CLI**: Perintah subcommand baru `note`, `zola`, dan `webhook-logs`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 291 menjadi 319 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Subtitle & Caption HTML5 Audio/Video (`sanitizer.py`)**:
   - Menjaga integritas elemen `<track>` dengan penegakan atribut keamanan `kind`, `srclang`, `label`, serta pembersihan URL `src`.

2. **Pelucutan Primitif Filter SVG Berbahaya (`sanitizer.py`)**:
   - Menghapus elemen `<filter>`, `<feImage>`, `<feDisplacementMap>`, dan atribut `filter="url(...)"` guna mencegah serangan CSS-based exfiltration.

3. **Sanitasi Deklaratif Shadow DOM Template & Slot (`sanitizer.py`)**:
   - Membersihkan elemen `<template>` dan `<slot>` dari injeksi kode tak terpercaya dalam declarative shadow root.

4. **Parser Inventaris & Spesifikasi Laboratorium (`parser.py`)**:
   - Mengekstrak data peralatan laboratorium, nomor seri, produsen, dan status kalibrasi dari format markdown terstruktur.

5. **Parser Sitasi Akademik APA 7th Edition (`parser.py`)**:
   - Mengurai referensi jurnal standar APA 7 menjadi dictionary terstruktur (penulis, tahun, judul, jurnal, volume, halaman, DOI).

6. **Parser Rubrik Penilaian Sidang Tugas Akhir (`parser.py`)**:
   - Mengurai kriteria penilaian sidang skripsi, persentase bobot nilai, dan deskripsi capaian kompetensi mahasiswa.

7. **Konverter Skala Nilai Mutu Huruf ke IPK (`parser.py`)**:
   - Mengonversi nilai huruf resmi perguruan tinggi Indonesia (A, AB, B, BC, C, D, E) ke bobot indeks prestasi kumulatif (4.00 - 0.00).

8. **Detektor Kalimat Berawalan Kata Sama Berurutan (`seo_validator.py`)**:
   - Mengaudit teks untuk mendeteksi 3 atau lebih kalimat berturut-turut yang diawali dengan kata identik guna menghindari repetisi monoton.

9. **Evaluator Distribusi Transisi Paragraf Indonesia (`seo_validator.py`)**:
   - Menghitung proporsi paragraf yang memuat kata sambung antar-kalimat bahasa Indonesia untuk menjamin kelancaran alur baca.

10. **Validator Ajakan Bertindak (CTA) Meta Description (`seo_validator.py`)**:
    - Memverifikasi keberadaan kata kerja pemicu klik (*pelajari*, *simak*, *temukan*, *baca*, *daftar*) pada deskripsi penelusuran.

11. **Validator Embedded JSON-LD Schema.org (`seo_validator.py`)**:
    - Memvalidasi sintaks JSON serta kepatuhan properti wajib tipe skema (`headline`, `name`, `startDate`, dll.) pada blok `<script type="application/ld+json">`.

12. **Komponen Alur Prasyarat Mata Kuliah Kurikulum (`components.py`)**:
    - Kartu grafis modern yang memvisualisasikan prasyarat sebelum mengambil mata kuliah serta rantai mata kuliah lanjutan yang terbuka.

13. **Komponen Checklist APD Keselamatan Laboratorium (`components.py`)**:
    - Kartu protokol OHS (K3) laboratorium dengan tabel APD wajib, standar sertifikasi, dan kontak darurat tanggap cepat.

14. **Komponen Tabel Kuota Pertukaran Mahasiswa (`components.py`)**:
    - Tabel visual informasi universitas mitra luar negeri, kuota mahasiswa, syarat IPK minimal, dan persyaratan kemahiran bahasa.

15. **Komponen Milestone Progres Hibah Riset Dosen (`components.py`)**:
    - Kartu pencapaian luaran riset dengan visualisasi anggaran dalam format mata uang Rupiah dan progress bar persentase tahapan.

16. **Komponen Histogram Distribusi Gaji Alumni (`components.py`)**:
    - Visualisasi grafik batang rentang gaji pertama lulusan prodi disertai lencana median pendapatan kerja.

17. **Formatter Pengumuman Beasiswa Telegram (`formatters.py`)**:
    - Format pesan siaran Telegram mencakup lembaga sponsor, cakupan pembiayaan, batas waktu registrasi, dan syarat pendaftaran.

18. **Formatter Notifikasi Publikasi Jurnal Cepat Telegram (`formatters.py`)**:
    - Format siaran kilat pencapaian penerbitan artikel pada jurnal bereputasi tinggi (Scopus Q1/Q2) dengan tautan DOI langsung.

19. **Manajer Catatan Kolaborasi Editorial Artikel (`storage.py`)**:
    - Tabel `article_notes` untuk catatan internal antar-penulis/editor yang mendukung penambahan, penelusuran, dan penghapusan catatan.

20. **Manajer Log Webhook Publikasi Outbound (`storage.py`)**:
    - Tabel `publishing_webhook_logs` untuk mencatat riwayat event, URL tujuan, kode status HTTP, dan cuplikan muatan notifikasi.

21. **Resolver Sinonim & Alias Taksonomi Akademik (`storage.py`)**:
    - Tabel `taxonomy_synonyms` dan metode pemetaan alias bahasa asing/singkatan ke istilah kanonikal resmi prodi.

22. **Helper Bulk Trash Posts Klien WordPress (`wordpress_client.py`)**:
    - Metode pengiriman permintaan penghapusan pos secara berurutan dengan laporan status sukses dan gagal.

23. **Helper Pencarian Media Berdasarkan Slug (`wordpress_client.py`)**:
    - Pengambilan berkas gambar atau dokumen dari pustaka media WordPress menggunakan slug spesifik.

24. **Generator Schema.org ScholarlyArticle JSON-LD (`exporter.py`)**:
    - Konstruksi data terstruktur publikasi ilmiah lengkap dengan metadata DOI, abstrak, afiliasi institusi, dan penulis jamak.

25. **Eksportir Markdown Kompatibel Zola SSG (`exporter.py`)**:
    - Transformasi artikel ke format SSG Zola berbasis frontmatter TOML (`+++`), taksonomi kategori, dan array tag.

26. **Subcommand CLI `note` (`cli.py`)**:
    - Perintah terminal untuk melihat daftar, menambah, dan menghapus catatan kolaborasi editorial pada artikel.

27. **Subcommand CLI `zola` (`cli.py`)**:
    - Perintah terminal untuk mengekspor artikel ke berkas markdown siap pakai pada generator situs statis Zola.

28. **Subcommand CLI `webhook-logs` (`cli.py`)**:
    - Perintah terminal untuk memantau riwayat pengiriman event webhook publikasi artikel.

29. **Ekspansi Suite Pengujian Unit Terpadu (319 Tests Passing)**:
    - Seluruh 319 unit test pada suite pengujian lulus 100% tanpa regresi atau kesalahan.
