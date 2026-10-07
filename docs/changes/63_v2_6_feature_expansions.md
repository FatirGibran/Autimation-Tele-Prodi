# Dokumentasi Perubahan Arsitektur v2.6.0

Siklus pengembangan v2.6.0 memperluas kapabilitas otomatisasi editorial prodi melalui pengerasan sanitasi disclosure dan netralisasi form, validator kredit SKS dan gelar dosen, auditor hreflang dan canonical loop SEO, kartu showcase capstone project dan sertifikasi kompetensi, caching metrik membaca dan sistem langganan notifikasi multi-kanal, eksportir MDSveX SvelteKit dan schema seminar ilmiah, antarmuka CLI baru, skrip audit tipografi otomatis, serta ekspansi suite pengujian unit hingga 263 tes terverifikasi.

## Rincian Fitur Utama yang Ditambahkan:
1. **Sanitasi Semantic Disclosure Details & Summary (`sanitizer.py`)**:
   - Penegakan kelas visual `.tu-details` dan `.tu-summary` serta pembersihan atribut berbahaya.
2. **Stripping Tag Meta Refresh & Base Terbenam (`sanitizer.py`)**:
   - Penghapusan dan netralisasi tag `<meta http-equiv="refresh">` dan `<base href="...">` di dalam konten editorial.
3. **Netralisasi Form & Input Editorial Tidak Aman (`sanitizer.py`)**:
   - Pembersihan tag `<form>`, `<input>`, `<button>`, `<textarea>` non-resmi pada artikel untuk mencegah phishing.
4. **Kalkulator & Validator SKS Kurikulum Mahasiswa (`parser.py`)**:
   - Ekstraksi dan kalkulasi total beban SKS mata kuliah teori dan praktikum dari tabel atau teks kurikulum prodi.
5. **Validator Format Gelar Dosen Pembimbing & Penguji (`parser.py`)**:
   - Verifikasi penulisan gelar akademik nasional (S.Kom., M.T., Ph.D., Prof., Dr.) dan kepatuhan urutan gelar depan/belakang.
6. **Ekspansi Singkatan Akademik & Istilah Prodi (`parser.py`)**:
   - Penggantian otomatis singkatan formal (KRS, KHS, KP, TA, MBKM, SKPI, CPL, CPMK) menjadi kepanjangan baku dalam teks.
7. **Klasifikasi & Normalisasi Bahasa Blok Kode Markdown (`parser.py`)**:
   - Deteksi dan pemetaan otomatis alias bahasa pemrograman (py -> python, js/ts -> javascript/typescript, sh/bash -> bash) pada fenced code blocks.
8. **Validator Multilingual Hreflang & Bahasa Alternatif (`seo_validator.py`)**:
   - Audit keberadaan dan validitas tag link `rel="alternate" hreflang="..."` untuk lokalisasi bahasa (id, en).
9. **Auditor ARIA Landmarks & Skip Links Aksesibilitas (`seo_validator.py`)**:
   - Verifikasi keberadaan navigasi skip link dan landmark semantik ARIA (`role="main"`, `navigation`, `banner`).
10. **Deteksi Canonical URL Loop & Normalisasi Domain (`seo_validator.py`)**:
    - Pemeriksaan konsistensi tautan kanonikal, pencegahan loop pengalihan sendiri, dan penyeragaman protokol HTTPS.
11. **Auditor Irama & Panjang Paragraf Keterbacaan (`seo_validator.py`)**:
    - Analisis panjang kata per paragraf dan variasi ritme membaca untuk mencegah kelelahan pembaca.
12. **Komponen Kartu Capstone Project Mahasiswa (`components.py`)**:
    - Showcase karya tugas akhir mahasiswa dengan judul, abstrak, teknologi, link repositori, dan demo langsung.
13. **Komponen Badge Sertifikasi Kompetensi Internasional (`components.py`)**:
    - Showcase sertifikasi industri mahasiswa dan dosen (AWS, Cisco CCNA, Google Cloud, RedHat) dengan nomor lisensi.
14. **Komponen Banner Milestone Kalender Akademik Semester (`components.py`)**:
    - Banner penanda linimasa penting semester (awal perkuliahan, UTS, UAS, batas pengumpulan nilai, yudisium).
15. **Komponen Kartu Reservasi Laboratorium & Perangkat Riset (`components.py`)**:
    - Visualisasi peminjaman fasilitas laboratorium komputer/jaringan, kapasitas kuota, dan status ketersediaan.
16. **Komponen Kartu Testimoni & Transfer SKS Student Exchange (`components.py`)**:
    - Showcase pengalaman mahasiswa pertukaran pelajar internasional/MBKM beserta pengakuan SKS mitra.
17. **Formatter Kartu Pengumuman Sidang Skripsi Telegram (`formatters.py`)**:
    - Desain kartu siaran jadwal sidang tugas akhir mahasiswa, dewan penguji, ruang/tautan, dan topik riset.
18. **Formatter Kartu Ringkasan Editorial Mingguan Telegram (`formatters.py`)**:
    - Digest mingguan statistik jumlah publikasi, kategori terpopuler, dan catatan sorotan redaksi.
19. **Caching Metrik Waktu Baca & Jumlah Kata Artikel (`storage.py`)**:
    - Tabel `article_reading_metrics` dan metode penyimpanan/pengambilan statistik durasi membaca pembaca.
20. **Manajer Langganan Notifikasi Editorial Multi-Kanal (`storage.py`)**:
    - Tabel `editorial_subscribers` dan manajemen pendaftaran user ke kategori artikel tertentu (Telegram/Email).
21. **Helper Komparasi Dift Revisi Tersimpan Artikel (`storage.py`)**:
    - Metode `compare_revisions` untuk analisis selisih jumlah kata, karakter, dan perubahan deskripsi meta antar versi.
22. **Pengatur Ringkasan Excerpt Postingan WordPress (`wordpress_client.py`)**:
    - Metode `update_post_excerpt` untuk memperbarui kutipan ringkasan artikel pada WordPress REST API.
23. **Konfigurasi Status Komentar & Pingback Postingan WordPress (`wordpress_client.py`)**:
    - Metode `set_post_comment_status` untuk membuka/menutup interaksi komentar dan trackback.
24. **Generator JSON-LD AcademicEvent & Seminar Ilmiah (`exporter.py`)**:
    - Skema data terstruktur Schema.org `EducationEvent` untuk seminar, lokakarya, dan konferensi akademik prodi.
25. **Generator Markdown Kompatibel MDSveX / SvelteKit (`exporter.py`)**:
    - Metode `to_sveltekit_markdown` untuk ekspor draf artikel ke format SvelteKit dengan frontmatter terstruktur.
26. **Subcommand CLI `subscribe` (`cli.py`)**:
    - Perintah konsol untuk manajemen pendaftaran dan peninjauan subscriber kanal redaksi.
27. **Subcommand CLI `diff-rev` (`cli.py`)**:
    - Perintah konsol untuk membandingkan statistik kata dan karakter dua revisi artikel secara instan.
28. **Subcommand CLI `svelte` (`cli.py`)**:
    - Perintah konsol untuk mengekspor artikel langsung ke berkas MDSveX SvelteKit.
29. **Skrip Auditor Tipografi & Keseimbangan Kutipan Otomatis (`scripts/check_typography.py`)**:
    - Perkakas audit konsistensi tanda petik kurawal Indonesia, gelar akademik, dan spasi tanda baca.
30. **Ekspansi Suite Pengujian Unit Terpadu (263 Tests Passing)**:
    - Penambahan pengujian unit menyeluruh di seluruh modul baru tanpa regresi dengan tingkat kelulusan 100%.
