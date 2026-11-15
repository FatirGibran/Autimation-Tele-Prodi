# Dokumentasi Perubahan Arsitektur Milestone Release v6.0.0

## 1. Ikhtisar Rilis
Milestone Release v6.0.0 menghadirkan ekspansi arsitektur menyeluruh pada stack rekayasa telekomunikasi, kepatuhan aksesibilitas web WCAG 2.1, serta evaluasi program wirausaha mahasiswa Belmawa PKM-K. Fitur-fitur utama mencakup pemodelan komunikasi optik nirkabel bawah air (Underwater Optical Wireless Communication - UWOC), kalkulasi throughput uplink dan adaptasi modulasi 5G NR PUSCH (3GPP TS 38.211 / TS 38.214), estimasi rotasi Faraday ionosfer pada propagasi satelit trans-ionosfer (ITU-R P.531), auditor aksesibilitas data table, ukuran touch target, nama unik landmark, dan keselamatan kedipan/kejang (seizure safety), serta sanitasi elemen HTML5 dialog autofocus, declarative shadow DOM, dan media track cues.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan HTML5 Terisolasi & Sandboxing (`sanitizer.py`)
- **Sanitasi Perangkap Autofocus Elemen Dialog `<dialog>`**: Menetralkan atribut `autofocus` dan pembukaan modal tanpa kontrol pembatalan pada elemen dialog guna mencegah jebakan fokus keyboard (keyboard focus trap) dan serangan denial-of-service interaksi pengguna.
- **Sanitasi Template Declarative Shadow DOM `<template shadowrootmode>`**: Menetralkan deklarasi template shadow DOM yang tidak tepercaya untuk mencegah injeksi template terisolasi dan eksekusi skrip lintas konteks (cross-context script execution).
- **Sanitasi Cue & Event Handler Elemen Media Track `<track>`**: Membersihkan berkas WebVTT dan penanganan event tersemat (`onload`, `onerror`, `oncuechange`) pada elemen track audio/video guna mencegah injeksi XSS berbasis media streaming.

### B. Algoritma Rekayasa Telekomunikasi & Evaluasi Belmawa PKM-K (`parser.py`)
- **Kalkulator Link Budget Komunikasi Optik Bawah Air (UWOC)**: Pemodelan transmisi optik laser biru-hijau (450–550 nm) pada 4 jenis perairan laut (Pure Sea, Clear Ocean, Coastal Ocean, Turbid Harbor) dengan koefisien kepunahan total $c(\lambda) = a(\lambda) + b(\lambda)$, rugi divergensi berkas geometrik, daya terima optik ($P_{rx}$), margin link, dan evaluasi kelayakan transmisi optik oseanik.
- **Kalkulator Efisiensi Spektral & Throughput 5G NR PUSCH (3GPP TS 38.211 / TS 38.214)**: Pemodelan Physical Uplink Shared Channel dengan alokasi PRB, numerologi fleksibel ($\mu \in \{0, 1, 2, 3\}$), simbol alokasi dan DMRS uplink, tabel modulasi adaptif MCS (QPSK hingga 256QAM), estimasi ukuran blok transpor (TBS), throughput puncak uplink, serta efisiensi spektral dalam bps/Hz.
- **Kalkulator Rotasi Faraday Ionosfer Propagasi Satelit (ITU-R P.531)**: Estimasi pergeseran sudut polarisasi gelombang radio terpolarisasi linier $\theta$ akibat interaksi medan magnetik bumi geomagnetik dan Total Electron Content (TEC) ionosfer pada pita frekuensi UHF/L-band/S-band.
- **Evaluator Proposal Wirausaha Mahasiswa Belmawa PKM-K**: Penilaian kelayakan komersial pasar (25%), kesiapan teknis produk berbasis teknologi (25%), kejelasan rencana bisnis (20%), proyeksi keuangan (15%), dan presentasi pitch deck (15%), integrasi batasan Turnitin (< 20%), penetapan pendanaan hibah Belmawa hingga Rp 9.000.000, serta ekuivalensi MBKM hingga 5 SKS.

### C. Auditor Aksesibilitas Web & Antarmuka WCAG 2.1 (`seo_validator.py`)
- **Auditor Asosiasi Programatik Header Tabel Data (WCAG 2.1 SC 1.3.1)**: Memverifikasi tabel data HTML memiliki header `<th>` dengan atribut `scope="col"` atau `scope="row"`, atau relasi `headers` dan `id` guna memastikan keterbacaan oleh pembaca layar.
- **Auditor Ukuran Minimum Sasaran Sentuh (WCAG 2.1 SC 2.5.5)**: Memeriksa dimensi minimum elemen interaktif (tombol, tautan, ikon kontrol) setidaknya $44 \times 44$ piksel atau memiliki jarak spasi yang memadai untuk kemudahan navigasi perangkat sentuh.
- **Auditor Nama Unik Aksesibel Landmark (WCAG 2.1 SC 1.3.1)**: Memverifikasi elemen landmark berulang (`<nav>`, `<aside>`, `<section>`) memiliki nama aksesibel unik via `aria-label` atau `aria-labelledby`.
- **Auditor Keselamatan Kedipan & Kejang Visual (WCAG 2.1 SC 2.3.1)**: Mengaudit animasi CSS, tag `<blink>`, dan manipulasi interval yang berkedip lebih dari 3 kali per detik pada area layar yang luas guna mencegah risiko fotosensitif kejang epileptik.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Link Budget UWOC**: Kartu metrik Elementor untuk tipe perairan laut, koefisien atenuasi, panjang gelombang laser, jarak link, daya pancar optik, daya terima, margin link, dan rekomendasi kanal optik laut.
- **Kartu Telemetri Throughput 5G NR PUSCH**: Kartu visual Elementor untuk identitas sel, alokasi PRB, numerologi $\mu$, indeks MCS, jenis modulasi, ukuran transport block (TBS), throughput puncak uplink, dan efisiensi spektral.
- **Kartu Telemetri Rotasi Faraday Satelit**: Kartu visual Elementor untuk frekuensi operasi, nilai ionospheric TEC, medan geomagnetik komponen sejajar $B \cos \theta$, sudut rotasi Faraday dalam derajat/radian, serta rekomendasi mitigasi polarisasi sirkular.
- **Kartu Profil Wirausaha Mahasiswa Belmawa PKM-K**: Kartu profil ketua pengusul, komoditas usaha tekno-wirausaha, skor kelayakan, status hibah pendanaan Belmawa, dan ekuivalensi MBKM.
- **Diagram Kisi Sumber Daya 5G NR PUSCH DMRS Inline SVG**: Diagram vektor responsif visualisasi slot uplink 14 simbol OFDM, pemetaan subcarrier kisi PRB, simbol DMRS (simbol 2 dan 11), simbol data muatan PUSCH, guard period, serta legenda palet warna telekomunikasi berstandar SVG.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Telemetri 5G NR PUSCH Uplink**: Notifikasi Telegram untuk kapasitas alokasi PRB, indeks MCS, modulasi orde tinggi, TBS bits, throughput uplink dalam Mbps, dan status link adaptation.
- **Formatter Pengumuman Pendanaan Belmawa PKM-K**: Format resmi Telegram untuk pengumuman penetapan pendanaan hibah wirausaha mahasiswa, besaran modal usaha, dan rekognisi konversi SKS MBKM.

### F. Manajemen Rekam Database SQLite (`storage.py`)
- **Tabel `uwoc_link_records`**: Penyimpanan relasional metrik link budget optik bawah air UWOC.
- **Tabel `nr_pusch_records`**: Penyimpanan metrik throughput uplink, MCS, modulasi, dan PRB 5G NR PUSCH.
- **Tabel `pkm_k_proposal_records`**: Penyimpanan data pengusul proposal PKM-K, kategori komoditas, skor komposit, status pendanaan, dan rekognisi MBKM.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Metode `get_posts_by_date_range`**: Pengambilan artikel WordPress berdasarkan rentang tanggal publikasi ISO 8601 (`after` dan `before`) dengan paginasi dan filter status.
- **Metode `batch_update_post_status`**: Pembaruan massal status publikasi kumpulan artikel WordPress (e.g. `publish`, `draft`, `pending`) via endpoint REST API.

### H. Ekspor Multi-Format & Metadata Mesin Pencari (`exporter.py`)
- **Generator Schema.org BusinessEvent & MonetaryGrant JSON-LD (`generate_business_venture_funding_json_ld`)**: Pembuatan metadata terstruktur Google Schema.org untuk wirausaha rintisan teknologi mahasiswa PKM-K lengkap dengan rincian hibah dan konversi MBKM.
- **Eksportir Dokumentasi Fumadocs MDX (`to_fumadocs_mdx`)**: Konversi konten artikel editorial ke format dokumentasi Fumadocs (Next.js) dengan frontmatter YAML dan komponen `<Callout type="info">`.

### I. Antarmuka Command Line Interface / CLI (`cli.py`)
- Subcommand `uwoc` (kalkulasi dan inventarisasi link budget komunikasi optik bawah air).
- Subcommand `nrpusch` (kalkulasi throughput uplink dan adaptasi MCS 5G NR PUSCH).
- Subcommand `pkmk` (evaluasi berkas proposal tekno-wirausaha Belmawa PKM-K, hibah modal usaha, dan ekuivalensi MBKM).
