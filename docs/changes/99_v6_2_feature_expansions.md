# Dokumentasi Perubahan Arsitektur Milestone Release v6.2.0

## 1. Ikhtisar Rilis
Milestone Release v6.2.0 menghadirkan ekspansi arsitektur menyeluruh pada modul rekayasa telekomunikasi, kepatuhan aksesibilitas web WCAG 2.1 tingkat AA/AAA, sanitasi atribut HTML5 modern, integrasi REST API WordPress tingkat lanjut, penyimpanan relasional SQLite, serta multi-format exporter dokumentasi. Fitur-fitur utama mencakup pemodelan figure of merit G/T dan suhu derau sistem stasiun bumi satelit (ITU-R S.733), atenuasi gas atmosfer bumi akibat uap air dan oksigen (ITU-R P.676), pemodelan terminal 5G NR Rel-17 RedCap (Reduced Capability / NR-Light) dan penghematan kompleksitas bill-of-materials (3GPP TS 38.306), penguat optik Raman terdistribusi (Distributed Fiber Raman Amplifier ITU-T G.665), auditor responsivitas reflow 320px, indikator visual fokus kontrol interaktif, alternatif gestur pointer tunggal, dan pencegahan kesalahan transaksi legal/finansial.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan HTML5 Terisolasi & Sandboxing (`sanitizer.py`)
- **Sanitasi Elemen Kustom Otonom HTML5 & Atribut `is`**: Menetralkan elemen kustom HTML5 tak terdaftar (Autonomous Custom Elements) dan atribut kustomisasi bawaan `is="..."` guna mencegah serangan injeksi DOM clobbering dan bypassing lifecycle callback scripting.
- **Sanitasi Atribut Pelacakan Anchor Ping HTML5**: Menghapus atribut pelacak navigasi `ping="..."` pada tag tautan `<a>` untuk melindungi privasi pengguna dari transmisi data suaka asinkronus ke server analitik pihak ketiga.
- **Sanitasi Elemen & Handler Animasi Vektor SVG**: Membersihkan elemen animasi berbasis SMIL (`<animate>`, `<animateTransform>`, `<animateMotion>`, `<set>`) dan atribut event handler animasi (`onbegin`, `onend`, `onrepeat`) yang sering disalahgunakan untuk mengeksekusi payload XSS berbasis grafis vektor.
- **Sanitasi Atribut Popover & Invoker Kontrol HTML5**: Menetralkan atribut popover dan tombol pemanggil kontrol antarmuka (`popover`, `popovertarget`, `popovertargetaction`) yang mengarah ke target tak dikenal untuk mencegah penipuan antarmuka (UI redress attack).

### B. Algoritma Rekayasa Telekomunikasi Lanjutan (`parser.py`)
- **Kalkulator Figure of Merit G/T Stasiun Bumi Satelit (ITU-R S.733)**: Perhitungan aperture gain antena parabola dari diameter reflektor dan efisiensi bukaan, suhu derau sistem $T_{sys}$ (derau antena, rugi saluran feed transmisi, dan angka derau LNA/LNB), serta penentuan nilai rasio penguatan terhadap suhu derau $G/T$ (dB/K) sesuai standar kelayakan gateway satelit geostasioner (GEO) maupun non-geostasioner (NGSO).
- **Kalkulator Atenuasi Gas Atmosfer Bumi (ITU-R P.676)**: Pemodelan penyerapan gelombang elektromagnetik atmosfer oleh molekul oksigen ($O_2$) dan resonansi uap air ($H_2O$) pada rentang frekuensi 1–350 GHz, memperhitungkan tekanan barometrik, temperatur lingkungan, kerapatan massa uap air ($\rho$), serta proyeksi panjang lintasan miring (slant-path attenuation) berdasarkan sudut elevasi antena.
- **Kalkulator Terminal 5G NR Rel-17 RedCap (3GPP TS 38.306 / TS 38.101-1)**: Estimasi throughput downlink dan uplink puncak perangkat IoT RedCap pada batas bandwidth saluran 20 MHz (FR1) / 100 MHz (FR2), konfigurasi antena 1R/2R (Single/Dual RX), modulasi 64QAM/256QAM, mode Half-Duplex FDD (HD-FDD), serta kalkulasi persentase reduksi kompleksitas bill-of-materials (BOM) hingga 65–70% dibanding terminal eMBB konvensional.
- **Kalkulator Penguat Raman Terdistribusi (ITU-T G.665 FRA / DRA)**: Perhitungan interaksi hamburan Raman terstimulasi (Stimulated Raman Scattering / SRS), integrasi panjang interaksi efektif serat optik ($L_{eff}$), penguatan sinyal on-off Raman gain, redaman pasif span serat optik, dan net gain transparansi span optik jarak jauh.

### C. Auditor Aksesibilitas Web & Pengalaman Pengguna WCAG 2.1 (`seo_validator.py`)
- **Auditor Responsivitas Reflow Konten 320px (WCAG 2.1 SC 1.4.10)**: Memverifikasi tata letak dokumen dan kontainer styling agar konten teks dan elemen layout dapat ditata ulang (reflow) pada resolusi layar sempit (lebar setara 320 CSS pixels) tanpa memicu scroll horizontal yang membatasi keterbacaan.
- **Auditor Indikator Fokus Visual Kontrol Interaktif (WCAG 2.1 SC 2.4.7 & SC 1.4.11)**: Memastikan elemen kontrol interaktif (tautan, tombol, input formulir) tidak menghilangkan penanda fokus visual (`outline: none` atau `outline: 0`) tanpa menyediakan gaya visual fokus alternatif berkontras tinggi bagi pengguna papan ketik.
- **Auditor Alternatif Gestur Pointer Tunggal (WCAG 2.1 SC 2.5.1)**: Memverifikasi fungsi yang dioperasikan melalui gestur multipoint (seperti pinch-to-zoom) atau jalur gestur kompleks memiliki alternatif pengoperasian satu sentuhan (single-pointer) sederhana.
- **Auditor Pencegahan Kesalahan Komitmen Legal & Finansial (WCAG 2.1 SC 3.3.4)**: Mengaudit formulir transaksi sensitif, pembayaran biaya kuliah/akademik, atau komitmen legal agar memiliki mekanisme konfirmasi, ringkasan tinjauan ulang, atau pembatalan transaksi sebelum data dikirimkan.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Figure of Merit G/T Stasiun Bumi Satelit**: Kartu visual Elementor menampilkan diameter reflektor antena, frekuensi operasi downlink, penguatan antena dBi, suhu derau sistem, nilai G/T dB/K, dan kategori penerima standar ITU-R S.733.
- **Kartu Telemetri Atenuasi Gas Atmosfer Bumi (ITU-R P.676)**: Kartu analitik Elementor menampilkan frekuensi pembawa, sudut elevasi, tekanan udara permukaan, suhu lingkungan, kerapatan uap air, koefisien redaman jenis oksigen & uap air, serta redaman lintasan miring total.
- **Kartu Telemetri Terminal 5G NR Rel-17 RedCap**: Kartu metrik Elementor menampilkan pita frekuensi 5G, alokasi PRB, batas bandwidth saluran 20 MHz, konfigurasi antena 1R1T, throughput DL/UL puncak, dan persentase penghematan kompleksitas BOM.
- **Kartu Telemetri Penguat Raman Terdistribusi (ITU-T G.665 FRA)**: Kartu visual Elementor menampilkan panjang fisik serat, daya pompa laser, panjang gelombang pompa & sinyal, panjang interaksi efektif $L_{eff}$, Raman on-off gain, dan status transparansi span.
- **Diagram Koeksistensi BWP 5G NR RedCap Inline SVG**: Diagram vektor responsif visualisasi koeksistensi pita frekuensi 20 MHz RedCap di dalam pembawa eMBB lebar 100 MHz, pemisahan blok Initial BWP, penempatan SSB/CORESET#0, alokasi PDSCH bersama, dan palet warna standar industri telekomunikasi.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Telemetri G/T Stasiun Bumi Satelit**: Templat siaran Telegram memuat parameter antena parabola, frekuensi, suhu derau, nilai figure of merit G/T, dan tautan NMS stasiun bumi.
- **Formatter Telemetri 5G NR Rel-17 RedCap**: Templat siaran Telegram memuat identitas terminal, band 5G, kapasitas throughput DL/UL, efisiensi BOM, dan profil penerapan industri IoT.
- **Formatter Telemetri Penguat Raman Terdistribusi**: Templat siaran Telegram memuat parameter panjang span, daya laser pompa, panjang interaksi efektif, penguatan Raman on-off, dan net span gain.

### F. Manajemen Rekam Database Relasional SQLite (`storage.py`)
- **Tabel `satellite_earth_station_gt_records`**: Penyimpanan relasional metrik kalkulasi G/T dan suhu derau sistem stasiun bumi satelit ITU-R S.733.
- **Tabel `nr_redcap_ue_records`**: Penyimpanan spesifikasi terminal 5G NR Rel-17 RedCap, alokasi PRB, throughput puncak, dan persentase reduksi BOM.
- **Tabel `fiber_raman_amplifier_records`**: Penyimpanan hasil evaluasi penguat Raman terdistribusi, daya pompa, panjang efektif, dan gain kompensasi rugi span.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Metode `get_media_by_mime_type`**: Pengambilan berkas media terpaginasi dari WordPress REST API yang difilter secara langsung berdasarkan tipe MIME spesifik (`GET /wp/v2/media?mime_type={mime_type}&page={page}&per_page={per_page}`).
- **Metode `get_post_by_slug`**: Pencarian dan pengambilan dokumen artikel publikasi WordPress berdasarkan slug unik artikel (`GET /wp/v2/posts?slug={slug}`).

### H. Ekspor Multi-Format & Metadata Mesin Pencari (`exporter.py`)
- **Generator Schema.org TechArticle & ScholarlyArticle JSON-LD (`generate_tech_article_scholarly_json_ld`)**: Pembuatan metadata terstruktur Google Schema.org untuk publikasi riset ilmiah teknik telekomunikasi dengan identifier DOI serta atribusi profil author IEEE/ORCID.
- **Eksportir Dokumentasi Docusaurus v3 MDX (`to_docusaurus_v3_mdx`)**: Konversi naskah teknis editorial ke format Docusaurus v3 MDX lengkap dengan frontmatter YAML, posisi navigasi sidebar, tag kategori, dan kontainer admonition callout `:::info`.

### I. Antarmuka Command Line Interface / CLI (`cli.py`)
- Subcommand `satgt`: Perhitungan dan inventarisasi parameter G/T stasiun bumi satelit ITU-R S.733.
- Subcommand `nrredcap`: Kalkulasi kapasitas data rate dan efisiensi BOM terminal 5G NR Rel-17 RedCap.
- Subcommand `fra`: Perhitungan penguatan distributed Raman amplifier, panjang interaksi efektif, dan transparansi transmisi serat optik ITU-T G.665.
