# Dokumentasi Perubahan Arsitektur Milestone Release v5.7.0

## 1. Ikhtisar Rilis
Milestone Release v5.7.0 menghadirkan ekspansi komprehensif pada stack otomasi editorial, telemetri telekomunikasi optik & nirkabel generasi lanjut, audit aksesibilitas semantik WCAG 2.1, serta skema evaluasi proposal mahasiswa Belmawa PKM Riset Sosial Humaniora (PKM-RSH) di lingkungan Program Studi S1 Teknik Telekomunikasi Telkom University Purwokerto.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Markup HTML5 (`sanitizer.py`)
- **Sanitasi Elemen `<hgroup>`**: Pembersihan atribut event handler inline, inline styles, dan sterilisasi container kelompok judul hierarki artikel akademik.
- **Sanitasi Elemen `<menu>`**: Sanitasi toolbar dan context menu terstruktur, menetralkan target javascript dan event handler.
- **Sanitasi Elemen `<portal>`**: Sanitasi embedding navigation portal HTML5 dengan pencegahan eksploitasi skema `javascript:` dan `data:text/html`.

### B. Algoritma Rekayasa Telekomunikasi & Evaluasi Akademik (`parser.py`)
- **Kalkulator Transponder Optik Koheren Dual-Polarization QAM**: Perhitungan SNR per simbol dari OSNR referensi 0.1 nm, estimasi Error Vector Magnitude (EVM % RMS), theoretical Pre-FEC BER (DP-QPSK, DP-16QAM, DP-64QAM), dan verifikasi kelulusan Hard-Decision FEC (3.8e-3) / Soft-Decision FEC (2.4e-2).
- **Kalkulator Kapasitas Kanal Kontrol 5G NR PUCCH (3GPP TS 38.211 / TS 38.213)**: Evaluasi format PUCCH (Format 0, 1, 2, 3, 4), alokasi PRB, jumlah simbol OFDM, durasi slot radio berdasarkan subcarrier spacing (SCS), batas kapasitas payload UCI (HARQ-ACK, SR, CSI), kapasitas multiplexing UE per PRB, dan target SNR threshold.
- **Kalkulator Depolarisasi Hujan & Indeks XPD Satelit (ITU-R P.618-13)**: Estimasi Cross-Polarization Discrimination (XPD) akibat redaman hujan nonsferikal canted raindrops, koreksi depolarisasi kristal es ($C_{ice}$), dan evaluasi kelayakan transmisi dual-polarization frequency reuse.
- **Evaluator Proposal Mahasiswa Belmawa PKM Riset Sosial Humaniora (PKM-RSH)**: Penilaian komposit proposal penelitian sosio-teknologi telekomunikasi dan kesenjangan digital (urgensi masalah 30%, tinjauan pustaka 15%, metodologi riset sosial & ethical clearance 30%, luaran kebijakan/policy brief 25%), penalti ketiadaan ethical clearance, alokasi dana Belmawa Dikti hingga Rp 10.000.000, serta konversi SKS MBKM hingga 5 SKS.

### C. Auditor SEO & Aksesibilitas Web WCAG 2.1 (`seo_validator.py`)
- **Auditor Semantik Scope Header Tabel (WCAG 2.1 SC 1.3.1)**: Memverifikasi keberadaan header `<th>` dengan atribut `scope` (`col` atau `row`) atau asosiasi `id`/`headers` untuk aksesibilitas pembaca layar (screen reader).
- **Auditor Rasio Kontras Warna Inline CSS (WCAG 2.1 SC 1.4.3)**: Memeriksa kontras warna teks dan latar belakang pada inline styles menggunakan relative luminance sRGB, menuntut rasio minimal 4.5:1 untuk teks normal.
- **Auditor Subtag Bahasa Kutipan (WCAG 2.1 SC 3.1.2)**: Memvalidasi deklarasi atribut `lang` pada cuplikan teks asing/istilah teknis sesuai format standar IETF BCP 47.
- **Auditor Ukuran Target Sentuh Interaktif (WCAG 2.1 SC 2.5.5 / 2.5.8)**: Mengaudit dimensi inline tombol dan link klik agar tidak berada di bawah ukuran minimum 24x24px.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Transponder Optik Koheren Dual-Polarization QAM**: Visualisasi format modulasi, laju transmisi Gbps, OSNR, SNR simbol, EVM RMS, dan status margin koreksi FEC.
- **Kartu Konfigurasi Kapasitas 5G NR PUCCH**: Visualisasi spesifikasi format kontrol uplink, PRB, simbol, kapasitas multiplexing UE, dan overhead persentase slot.
- **Kartu Estimasi Depolarisasi Hujan Satelit ITU-R P.618**: Visualisasi frekuensi carrier, sudut elevasi, redaman XPD hujan, koreksi kristal es, dan status keandalan dual-polarization.
- **Kartu Evaluasi Proposal Belmawa PKM-RSH**: Visualisasi profil pengusul, judul riset sosial humaniora, skor komposit, status pendanaan Belmawa, dan rekognisi SKS MBKM.
- **Diagram Responsif Inline SVG Grid Sumber Daya 5G NR PUCCH**: Diagram vektor interaktif visualisasi alokasi Resource Grid PUCCH format short/long pada tepi frekuensi slot radio dengan transisi intra-slot frequency hopping.

### E. Formatter Buletin Telegram Bot (`formatters.py`)
- **Formatter Telegram Kapasitas 5G NR PUCCH**: Template notifikasi broadcast telemetri konfigurasi format PUCCH, kapasitas alokasi PRB, dan overhead transmisi.
- **Formatter Telegram Pendanaan Mahasiswa PKM-RSH**: Template pengumuman resmi capaian kelulusan pendanaan riset sosial humaniora dan advokasi kebijakan publik mahasiswa ke kanal prodi.

### F. Manajemen Basis Data SQLite (`storage.py`)
- **Tabel `optical_coherent_qam_records`**: Penyimpanan telemetri modulasi DP-QAM, bitrate, OSNR, SNR, EVM, BER, dan status koreksi FEC.
- **Tabel `nr_pucch_records`**: Penyimpanan spesifikasi alokasi format PUCCH, PRB, simbol OFDM, numerologi SCS, dan kapasitas multiplexing UE.
- **Tabel `pkm_rsh_proposal_records`**: Penyimpanan rekam evaluasi proposal mahasiswa PKM-RSH, judul, topik, skor komposit, status dana, dan SKS MBKM.

### G. Integrasi Klien WordPress REST API (`wordpress_client.py`)
- **Helper `get_media_by_ids`**: Pembacaan kumpulan data media library WordPress berdasarkan list ID numerik (`/wp/v2/media?include=...`).
- **Helper `batch_update_tag_slugs`**: Pembaruan URL slug sekumpulan taksonomi tag WordPress secara massal via REST API (`POST /wp/v2/tags/{id}`).

### H. Generator Metadata & Eksportir Dokumentasi (`exporter.py`)
- **Generator Schema.org `ScholarlyArticle` JSON-LD**: Struktur metadata Google Scholar untuk karya riset sosial humaniora (PKM-RSH) dan policy brief.
- **Eksportir Dokumentasi Stripe Markdoc (`to_stripe_markdoc`)**: Konversi konten artikel editorial ke format dokumentasi Stripe Markdoc dengan frontmatter YAML dan tag deklaratif `{% callout %}`.

### I. Antarmuka Baris Perintah CLI (`cli.py`)
- Subcommand `cohqam`: Perintah terminal untuk evaluasi dan logging transponder optik koheren dual-polarization QAM.
- Subcommand `nrpucch`: Perintah terminal untuk kalkulasi kapasitas dan overhead kanal kontrol 5G NR PUCCH.
- Subcommand `pkmrsh`: Perintah terminal untuk evaluasi kuantitatif proposal riset sosial humaniora Belmawa PKM-RSH.

### J. Pengujian Terpadu Unit Test Suite (`tests/`)
- Penambahan 33 unit test baru pada seluruh modul yang diperluas, melampaui total 1.120 tests dengan tingkat kelulusan 100% pass rate.
