# Dokumentasi Perubahan Arsitektur v3.0.0 Milestone Release

Siklus pengembangan v3.0.0 Milestone Architectural Release menghadirkan ekspansi arsitektural komprehensif pada ekosistem otomasi editorial:
- **Sanitasi Media & Keamanan DOM Lanjutan**: Sanitasi elemen dialog/modal HTML5 (`<dialog>`), elemen interaktif `<details>` dan `<summary>`, serta proteksi atribut slot Web Components terhadap ancaman prototype pollution (`__proto__`, `constructor`, `prototype`).
- **Parser Spesifikasi & Standar Akademik**: Parser sitasi prosiding dan transaksi ACM (Association for Computing Machinery), kalkulator rubrik skor berbobot sidang skripsi (dengan konversi huruf mutu dan IPK standar Indonesia), parser logbook mingguan magang bersertifikat MBKM, serta parser log riwayat pemeliharaan dan kalibrasi instrumen laboratorium.
- **Auditor SEO & Validasi Semantik Terstruktur**: Kalkulator indeks keterbacaan Coleman-Liau untuk teks akademik Indonesia, auditor urutan hierarki heading berjenjang tanpa loncatan level, detektor klausul pengakuan dana hibah riset (LPDP, BRIN, Kemendikbudristek) beserta nomor kontrak/SPK, dan auditor aksesibilitas gambar serta pencegahan Cumulative Layout Shift (CLS) dengan atribut dimensi eksplisit.
- **Komponen Semantik Elementor**: Kartu stepper milestone proyek akhir capstone mahasiswa, kartu banner pendaftaran workshop lab open house, kartu pameran pengalaman magang industri MBKM, kartu pameran monograf/buku ajar dosen ber-ISBN, dan kartu profil universitas mitra pertukaran internasional.
- **Format Pesan Telegram**: Format pengumuman undangan workshop/webinar akademik prodi dan format siaran jadwal sidang tugas akhir mahasiswa.
- **Pengembangan Storage & Basis Data**: Pelacak sitasi akademik eksternal pada artikel (`article_citations`), manajer komentar peninjauan editorial inline per paragraf (`editorial_comments`), serta perpustakaan snippet konten markup terpakai-ulang (`content_snippets`).
- **Klien WordPress REST API**: Helper pembaruan massal tag pos (`batch_update_post_tags`) dan helper pencarian tag pos berdasarkan slug (`get_tag_by_slug`).
- **Generator Statis & Ekspor**: Generator Schema.org `Dataset` JSON-LD untuk dataset riset terbuka laboratorium telematika, dan eksportir markdown kompatibel Docusaurus static documentation generator.
- **Antarmuka Konsol CLI**: Perintah subcommand baru `snippet`, `docusaurus`, dan `comment`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 347 menjadi 375 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Elemen Dialog & Modal HTML5 (`sanitizer.py`)**:
   - Menjaga integritas elemen `<dialog>` dengan melucuti atribut event handler dan skrip tidak berizin.

2. **Sanitasi Tag Interaktif Details & Summary (`sanitizer.py`)**:
   - Memvalidasi elemen disclosure `<details>` dan `<summary>` dengan mempertahankan atribut standar `open` dan memblokir injeksi eksternal.

3. **Sanitasi Atribut Slot Web Components (`sanitizer.py`)**:
   - Mencegah teknik prototype pollution dengan memvalidasi nilai atribut `slot` terhadap kata kunci berbahaya.

4. **Parser Sitasi ACM Conference & Transactions (`parser.py`)**:
   - Mengurai format rujukan sitasi ACM standar menjadi data terstruktur (penulis, judul artikel, nama konferensi/transaksi, tahun, volume, issue, DOI).

5. **Kalkulator Rubrik Penilaian Sidang Skripsi (`parser.py`)**:
   - Menghitung nilai akhir berbobot sidang skripsi (presentasi, penguasaan materi, naskah, produk) serta konversi huruf mutu (A, AB, B, BC, C, D, E) dan IPK.

6. **Parser Logbook Mingguan Magang MBKM (`parser.py`)**:
   - Mengekstrak catatan aktivitas mingguan magang bersertifikat industri, total jam aktivitas, dan ringkasan pencapaian kompetensi mahasiswa.

7. **Parser Log Kalibrasi & Pemeliharaan Alat Lab (`parser.py`)**:
   - Mengekstrak data riwayat servis, jadwal kalibrasi, nama teknisi penanggung jawab, dan status kelayakan alat laboratorium.

8. **Kalkulator Indeks Keterbacaan Coleman-Liau (`seo_validator.py`)**:
   - Menghitung indeks keterbacaan teks bahasa Indonesia berbasis jumlah huruf dan kalimat per 100 kata.

9. **Auditor Hierarki Heading Berjenjang (`seo_validator.py`)**:
   - Memeriksa urutan heading agar berjenjang secara berurutan tanpa lompatan level tingkat (seperti H2 melompat ke H4).

10. **Detektor Pengakuan Dana Hibah Riset (`seo_validator.py`)**:
    - Mendeteksi klausul pendanaan penelitian dari lembaga pemberi hibah beserta ekstraksi nomor kontrak atau SPK.

11. **Auditor Aksesibilitas Gambar & Pencegahan CLS (`seo_validator.py`)**:
    - Memverifikasi keberadaan atribut `width`, `height`, dan deskriptivitas `alt` pada elemen gambar untuk menghindari pergeseran tata letak layout.

12. **Komponen Stepper Milestone Capstone Proyek Akhir (`components.py`)**:
    - Kartu tahapan interaktif penyelesaian tugas akhir mahasiswa dari proposal hingga sidang akhir.

13. **Komponen Banner Workshop Open House Lab (`components.py`)**:
    - Kartu promosi agenda pelatihan dan open house fasilitas riset laboratorium program studi.

14. **Komponen Portofolio Magang Industri MBKM (`components.py`)**:
    - Kartu pengalaman magang mahasiswa di industri teknologi mitra beserta ringkasan proyek yang dikerjakan.

15. **Komponen Pameran Monograf Publikasi Buku Dosen (`components.py`)**:
    - Showcase penerbitan monograf dan buku referensi dosen dengan nomor registrasi ISBN.

16. **Komponen Profil Mitra Pertukaran Mahasiswa Internasional (`components.py`)**:
    - Kartu profil universitas mitra global, peringkat dunia, negara, dan kuota beasiswa pertukaran.

17. **Formatter Undangan Workshop & Webinar Telegram (`formatters.py`)**:
    - Templat pesan siaran resmi informasi workshop dan webinar teknologi untuk disiarkan ke Telegram.

18. **Formatter Pengumuman Jadwal Sidang Tugas Akhir Telegram (`formatters.py`)**:
    - Templat pesan siaran jadwal sidang skripsi mahasiswa, dewan penguji, ruang, dan waktu pelaksanaan.

19. **Pelacak Sitasi Akademik Eksternal (`storage.py`)**:
    - Penyimpanan dan pelacakan sitasi artikel prodi oleh jurnal dan prosiding eksternal (`article_citations`).

20. **Manajer Komentar Peninjauan Editorial Inline (`storage.py`)**:
    - Sistem review editorial per artikel dan paragraf untuk kolaborasi revisi naskah (`editorial_comments`).

21. **Perpustakaan Snippet Konten Terpakai-Ulang (`storage.py`)**:
    - Penyimpanan komponen HTML reusable (callout, disclaimer, pengumuman PMB) dalam tabel `content_snippets`.

22. **Helper Bulk Update Tags Klien WordPress (`wordpress_client.py`)**:
    - Pembaruan tag jamak pada pos WordPress dalam satu operasi batch.

23. **Helper Pencarian Tag Berdasarkan Slug WordPress (`wordpress_client.py`)**:
    - Pengambilan objek tag WordPress via REST API berdasarkan slug.

24. **Generator Schema.org Dataset JSON-LD (`exporter.py`)**:
    - Metadata terstruktur skema Dataset untuk repositori data riset terbuka laboratorium telematika.

25. **Generator Markdown Kompatibel Docusaurus SSG (`exporter.py`)**:
    - Ekspor artikel ke format Markdown Docusaurus lengkap dengan frontmatter id, label, posisi sidebar, dan tags.

26. **Subcommand CLI `snippet` (`cli.py`)**:
    - Perintah konsol untuk menyimpan, mengambil, dan melihat daftar snippet konten reusable.

27. **Subcommand CLI `docusaurus` (`cli.py`)**:
    - Perintah konsol untuk mengekspor artikel langsung ke format markdown Docusaurus.

28. **Subcommand CLI `comment` (`cli.py`)**:
    - Perintah konsol untuk menambah, memeriksa, dan menyelesaikan catatan komentar editorial naskah.

29. **Ekspansi Suite Pengujian Unit (375 Tests Passing)**:
    - 375 unit test otomatis dengan tingkat kelulusan 100% mencakup seluruh modul arsitektur.
