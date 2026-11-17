# Dokumentasi Perubahan Arsitektur Milestone Release v6.1.0

## 1. Ikhtisar Rilis
Milestone Release v6.1.0 menghadirkan ekspansi arsitektur lanjutan pada stack rekayasa telekomunikasi, kepatuhan aksesibilitas web WCAG 2.1, serta evaluasi program pengabdian kepada masyarakat mahasiswa Belmawa PKM-PM. Fitur-fitur utama mencakup pemodelan atenuasi fluktuasi troposferik satelit (ITU-R P.618), alokasi resource reference signal kanal 5G NR CSI-RS dan multiplexing Code Division Multiplexing (CDM) massive MIMO (3GPP TS 38.211 / TS 38.214), pergeseran fasa nonlinier Kerr dan akumulasi B-integral pada transmisi serat optik jarak jauh, auditor kontinuitas hierarki heading, validitas token autocomplete, jarak spasi minimum pointer sentuh, dan pengumuman dinamis aria-live, serta sanitasi elemen HTML5 SVG foreignObject, MathML markup, dan jebakan navigasi portal experimental.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan HTML5 Terisolasi & Sandboxing (`sanitizer.py`)
- **Sanitasi Elemen SVG `<foreignObject>`**: Menetralkan injeksi dokumen HTML bersarang di dalam grafis vektor SVG untuk mencegah serangan cross-site scripting (XSS) berbasis namespace XML/SVG.
- **Sanitasi Elemen MathML `<math>` & Malicious CDATA**: Membersihkan penanda matematika MathML, blok CDATA berbahaya, serta atribut event handler tersembunyi guna mencegah bypassing filter XSS berbasis parser MathML.
- **Sanitasi Jebakan Navigasi Portal Eksperimental `<portal>`**: Menetralkan elemen `<portal>` eksperimental dan manipulasi aktivasi transisi jendela navigasi guna mencegah serangan hijacking tampilan konteks halaman.

### B. Algoritma Rekayasa Telekomunikasi & Evaluasi Belmawa PKM-PM (`parser.py`)
- **Kalkulator Atenuasi Scintillation Satelit (ITU-R P.618)**: Pemodelan kedalaman fade fluktuasi sinyal satelit akibat turbulensi refraktivitas uap air troposfer $N_{wet}$, faktor perataan bukaan antena reflektor (aperture averaging factor $g(x)$), deviasi standar sinyal $\sigma$, dan estimasi kedalaman redaman $A_s(p)$ pada persentase waktu outage $p$.
- **Kalkulator Resource CSI-RS & Overhead 5G NR (3GPP TS 38.211 / TS 38.214)**: Pemodelan alokasi Resource Elements (REs) CSI-RS per PRB, penentuan skema multiplexing CDM (noCDM, cdm2-FD, cdm4-FD2-TD2, cdm8-FD2-TD4), perhitungan overhead slot seketika dan rata-rata berkala, serta evaluasi estimasi kanal 3D beamforming Massive MIMO.
- **Kalkulator Pergeseran Fasa Nonlinier & B-Integral Serat Optik**: Perhitungan akumulasi efek nonlinier Kerr self-phase modulation (SPM) dan integrasi koefisien nonlinier $\gamma$, daya optik peluncuran ($P_{in}$), panjang efektif serat optik ($L_{eff}$), dan nilai akumulasi B-integral untuk evaluasi stabilitas fase sinyal optik.
- **Evaluator Proposal Pengabdian Masyarakat Mahasiswa Belmawa PKM-PM**: Penilaian komposit urgensi permasalahan mitra sasaran (25%), ketepatan solusi teknologi telekomunikasi (25%), metodologi pelaksanaan program (20%), keberlanjutan program (15%), dan dampak sosial ekonomi masyarakat (15%), verifikasi batas toleransi kemiripan Turnitin (< 20%), penetapan rekomendasi pendanaan Belmawa hingga Rp 8.500.000, serta rekognisi MBKM hingga 5 SKS.

### C. Auditor Aksesibilitas Web & Antarmuka WCAG 2.1 (`seo_validator.py`)
- **Auditor Kontinuitas Hierarki Heading (WCAG 2.1 SC 1.3.1)**: Memverifikasi urutan tingkat heading dokumen (`<h1>` hingga `<h6>`) terstruktur secara berkesinambungan tanpa lompatan level (misalnya `<h1>` langsung meloncat ke `<h3>`) untuk navigasi pembaca layar.
- **Auditor Token Atribut Autocomplete (WCAG 2.1 SC 1.3.5)**: Memvalidasi token nilai pada atribut `autocomplete` bidang formulir HTML input pengguna sesuai standar HTML5/WCAG 2.1 autofill tokens.
- **Auditor Jarak Spasi Sasaran Pointer Sentuh (WCAG 2.1 SC 2.5.8)**: Mengaudit jarak spasi minimum antar elemen interaktif (pointer target spacing) setidaknya berjarak spasi aman untuk mencegah kesalahan aktivasi pada antarmuka sentuh.
- **Auditor Pengumuman Status Pesan Dinamis ARIA-Live (WCAG 2.1 SC 4.1.3)**: Memverifikasi ketersediaan atribut `aria-live` (`polite` atau `assertive`) atau role status (`status`, `alert`, `log`) pada kontainer pembaruan pesan dinamis agar pembaca layar menerima informasi tanpa interupsi fokus.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Scintillation Satelit**: Kartu visual Elementor menampilkan frekuensi operasi satelit, sudut elevasi antena bumi, diameter reflektor antena, refraktivitas troposfer $N_{wet}$, faktor aperture averaging, standar deviasi fluktuasi sinyal, dan kedalaman fade redaman scintillation.
- **Kartu Telemetri 5G NR CSI-RS**: Kartu metrik Elementor menampilkan identitas sel gNodeB, alokasi PRB, jumlah antenna ports, skema CDM, periodisitas slot transmisi, lapisan MIMO, serta persentase overhead seketika dan rata-rata.
- **Kartu Telemetri Pergeseran Fasa Nonlinier Serat Optik**: Kartu visual Elementor menampilkan koefisien nonlinier $\gamma$, daya luncur optik, panjang efektif serat optik $L_{eff}$, pergeseran fase nonlinier $\Phi_{NL}$, dan nilai akumulasi B-integral.
- **Kartu Profil Pengabdian Masyarakat Mahasiswa Belmawa PKM-PM**: Kartu profil ketua pelaksana, komunitas mitra sasaran, judul proposal, wilayah domisili mitra, skor kelayakan, status hibah pendanaan Belmawa, dan ekuivalensi MBKM.
- **Diagram Kisi Sumber Daya 5G NR CSI-RS Inline SVG**: Diagram vektor responsif visualisasi kisi resource elements (REs) dalam slot 14 simbol OFDM dan 12 subcarrier per PRB, penempatan simbol referensi CSI-RS dengan kode warna skema CDM, simbol muatan data PDSCH, guard interval, serta legenda palet warna telekomunikasi berstandar SVG.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Telemetri 5G NR CSI-RS & Antenna Ports**: Notifikasi Telegram untuk konfigurasi alokasi CSI-RS, antenna ports (hingga 32 port), skema CDM, persentase overhead rata-rata, dan status kesiapan kanal spatial Massive MIMO.
- **Formatter Pengumuman Pendanaan Belmawa PKM-PM**: Format buletin Telegram untuk pengumuman penetapan pendanaan hibah pengabdian masyarakat mahasiswa Belmawa, nama komunitas mitra, besaran hibah, dan rekognisi konversi SKS MBKM.

### F. Manajemen Rekam Database SQLite (`storage.py`)
- **Tabel `satellite_scintillation_records`**: Penyimpanan relasional metrik atenuasi tropospheric scintillation satelit ITU-R P.618.
- **Tabel `nr_csi_rs_records`**: Penyimpanan metrik alokasi resource elements, antenna ports, CDM multiplexing, dan overhead 5G NR CSI-RS.
- **Tabel `pkm_pm_community_empowerment_records`**: Penyimpanan data pengusul proposal PKM-PM, mitra sasaran, skor komposit, status pendanaan, dan rekognisi MBKM.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Metode `get_revisions_by_post_id`**: Pengambilan riwayat revisi artikel WordPress berdasarkan ID postingan dengan dukungan paginasi (`page` dan `per_page`) via REST API (`GET /wp/v2/posts/{post_id}/revisions`).
- **Metode `compare_post_revisions`**: Pembandingan struktural dua revisi historis artikel WordPress yang menghasilkan selisih judul, panjang konten, dan perubahan jumlah kata secara komprehensif.

### H. Ekspor Multi-Format & Metadata Mesin Pencari (`exporter.py`)
- **Generator Schema.org SocialEvent & MonetaryGrant JSON-LD (`generate_community_service_grant_json_ld`)**: Pembuatan metadata terstruktur Google Schema.org untuk program pengabdian masyarakat mahasiswa PKM-PM lengkap dengan profil mitra sasaran, rincian hibah Belmawa, dan konversi SKS MBKM.
- **Eksportir Dokumentasi TypeDoc Markdown (`to_typedoc_markdown`)**: Konversi konten artikel editorial ke format dokumentasi TypeDoc API dengan frontmatter YAML, label modul package, dan hierarki tipografi teknis.

### I. Antarmuka Command Line Interface / CLI (`cli.py`)
- Subcommand `troposcint` (kalkulasi dan inventarisasi atenuasi tropospheric scintillation satelit ITU-R P.618).
- Subcommand `nrcsirs` (analisis alokasi resource elements, antenna ports, dan overhead 5G NR CSI-RS).
- Subcommand `pkmcommunity` (evaluasi berkas proposal pengabdian kepada masyarakat Belmawa PKM-PM, hibah program, dan ekuivalensi MBKM).
