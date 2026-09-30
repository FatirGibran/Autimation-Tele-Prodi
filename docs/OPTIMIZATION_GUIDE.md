# Panduan Optimasi Arsitektur & Fitur Editorial

Dokumen ini mendokumentasikan serangkaian optimasi fitur, peningkatan performa, sanitasi keamanan, serta ekstensi antarmuka editorial yang diimplementasikan pada proyek Automasi Tele Prodi.

---

## 1. Sanitasi & Pengerasan Keamanan (Security Hardening)
- **Inline SVG Sanitization**: Pembersihan tag `<svg>` untuk mencegah injeksi XSS melalui elemen `<foreignObject>`, tag `<script>`, dan manipulasi atribut `xlink:href` bernilai pseudo-protokol `javascript:`.
- **CSS Style Attribute Sanitizer**: Filter ekspresi inline style berbahaya yang memblokir eksekusi `expression()`, `@import`, `-moz-binding`, pseudo-protokol `javascript:`, dan embedding skrip via data URI.

---

## 2. Optimasi Parser Konten Editorial
- **Query Tracking Parameter Stripper**: Fungsi `clean_url` otomatis mengeliminasi parameter pelacak analitik pihak ketiga (`utm_*`, `fbclid`, `gclid`, `mc_eid`, `ref`) demi kebersihan tautan internal/eksternal dan optimalisasi caching.
- **Adaptive Reading Time Calculator**: Algoritma kalkulasi estimasi durasi baca artikel ilmiah berbahasa Indonesia berbasis densitas kata riil dan kecepatan baca standar 200 WPM.
- **Markdown Callout & Admonition Parser**: Konversi format penulisan callout GitHub (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, `> [!IMPORTANT]`, `> [!CAUTION]`) menjadi kartu peringatan responsif Elementor.

---

## 3. Peningkatan Kualitas Yoast SEO & Keterbacaan
- **Hitung Suku Kata & Skor Kemudahan Membaca**: Implementasi penghitung suku kata adaptif bahasa Indonesia untuk penilaian skor kemudahan membaca (Reading Ease Index).
- **Audit Kualitas Anchor Text**: Deteksi tautan dengan teks jangkar generik yang merugikan peringkat SEO (misal: "klik di sini", "link", "baca selengkapnya").
- **Deteksi Kanibalisasi Kata Kunci**: Pemeriksaan kesamaan semantik kata kunci fokus terhadap korpus artikel yang telah terbit menggunakan metrik Jaccard similarity.

---

## 4. Komponen Visual Elementor
- **Timeline / Roadmap Akademik**: Komponen visual vertikal untuk peta jalan kurikulum, milestone riset, dan jadwal kegiatan prodi.
- **Kartu Testimoni Alumni**: Kartu kutipan kesuksesan alumni dengan informasi angkatan, peran profesional, perusahaan, dan foto profil ter-optimasi.
- **Matriks Komparasi Kurikulum**: Tabel komparasi fitur dengan visualisasi centang (`✓`), silang (`✗`), dan layout responsif pada layar perangkat mobile.

---

## 5. Optimalisasi Database & Penyimpanan SQLite
- **Pencarian Multi-Kolom Full-Text**: Fitur pencarian kata kunci di seluruh metadata dan isi HTML dengan ekstraksi cuplikan konteks kecocokan (snippet).
- **Integritas & Pemadatan Database**: Eksekusi perintah `PRAGMA integrity_check` dan `VACUUM` untuk merawat performa I/O dan meminimalkan ukuran berkas database.
- **Snapshot Revisi Versi Artikel**: Penyimpanan riwayat revisi berkas draf sebelum dilakukan penimpaan konten (versioning history).

---

## 6. Generator Ekspor & Metadata Sosial
- **OpenGraph & Twitter Cards Generator**: Pembuatan paket metadata media sosial otomatis untuk pratinjau tautan di platform perpesanan dan media sosial.
- **JSON-LD BreadcrumbList Schema**: Struktur data skema breadcrumb untuk menghasilkan rich snippet hierarki halaman di hasil pencarian Google.

---

## 7. Ekstensi Antarmuka Baris Perintah (CLI)
- `python cli.py optimize`: Pemeliharaan basis data SQLite berkala dan verifikasi integritas tabel.
- `python cli.py sitemap`: Pembuatan berkas XML sitemap standar untuk seluruh artikel yang tersimpan di repositori.
