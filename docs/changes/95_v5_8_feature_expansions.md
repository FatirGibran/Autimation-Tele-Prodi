# Dokumentasi Perubahan Arsitektur Milestone Release v5.8.0

## 1. Ikhtisar Rilis
Milestone Release v5.8.0 menambahkan kapabilitas baru pada stack otomasi editorial, telemetri rekayasa serat optik & nirkabel seluler-satelit LEO, pengujian aksesibilitas WCAG 2.1 form & landmark, serta skema evaluasi proposal mahasiswa Belmawa PKM Gagasan Futuristik Tertulis (PKM-GFT) untuk civitas akademika S1 Teknik Telekomunikasi Telkom University Purwokerto.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan Elemen HTML5 Terisolasi & Multimedia (`sanitizer.py`)
- **Sanitasi Elemen Privacy Sandbox `<fencedframe>`**: Penanganan dan sterilisasi tag fencedframe dengan melucuti atribut scripting inline, handler event, serta inline style mencurigakan guna menjamin isolasi dokumen iframe mode privasi.
- **Sanitasi Elemen Plugin & Media `<embed>`**: Menetralkan skema URL berbahaya (`javascript:`, `vbscript:`, arbitrer `data:`) dan memblokir eksekusi MIME types plugin rentan (Flash, Silverlight, Java applet).
- **Sanitasi Elemen Objek Multimedia `<object>` & `<param>`**: Melucuti atribut legacy ActiveX `classid`, data URL berbahaya, serta membatasi parameter `allowScriptAccess` secara paksa menjadi `value="never"`.

### B. Algoritma Rekayasa Telekomunikasi & Evaluasi Belmawa PKM-GFT (`parser.py`)
- **Kalkulator Penalti Dispersi Mode Polarisasi (PMD) & DGD Serat Optik (ITU-T G.652/G.655)**: Evaluasi nilai mean Differential Group Delay $\langle \Delta \tau \rangle = D_{PMD} \sqrt{L}$, estimasi puncak DGD distribusi Maxwellian $3 \langle \Delta \tau \rangle$, rasio terhadap periode bit transmisi, serta perhitungan penalti daya OSNR untuk link optik koheren polarisasi ganda.
- **Kalkulator Kapasitas & Link Budget 5G NR PRACH (3GPP TS 38.211)**: Pemodelan struktur preamble PRACH (Format long $L_{RA}=839$ dan format short $L_{RA}=139$), batasan jarak sel tanpa ambiguitas berdasarkan cyclic shift $N_{CS}$, kapasitas preamble orthogonal per root sequence, redaman lintasan ruang bebas (FSPL), dan margin deteksi receiver gNodeB.
- **Kalkulator Dinamika Slant Range & Pergeseran Doppler Satelit LEO**: Analisis orbit LEO melingkar via hukum gravitasi standar $\mu_{Earth}$, estimasi jarak pandang miring (slant range) berdasarkan elevasi antena stasiun bumi, komponen kecepatan line-of-sight relatif, frekuensi Doppler shift $\Delta f_D$, Doppler rate pada zenit, dan densitas carrier-to-noise $C/N_0$.
- **Evaluator Proposal Mahasiswa Belmawa PKM Gagasan Futuristik Tertulis (PKM-GFT)**: Penilaian komposit gagasan visioner Indonesia Emas 2045 dan target SDGs (visi futuristik 30%, orisinalitas 25%, kelayakan implementasi 25%, dampak sosial & keselarasan SDGs 20%), alokasi insentif nasional Belmawa Rp 3.000.000, serta rekognisi MBKM hingga 4 SKS.

### C. Auditor Aksesibilitas Web & Form Kontrol WCAG 2.1 (`seo_validator.py`)
- **Auditor Asosiasi Label Programatik Form (WCAG 2.1 SC 3.3.2)**: Memverifikasi kontrol form `<input>`, `<select>`, `<textarea>` memiliki label programatik via `<label for="...">`, pembungkusan bersarang (nesting), `aria-label`, `aria-labelledby`, atau `title`.
- **Auditor Mekanisme Lewati Blok Navigasi / Skip Links (WCAG 2.1 SC 2.4.1)**: Memeriksa keberadaan tautan lewati (skip link) dengan target ID yang valid atau tersedianya kontainer semantik primer `<main>` / `role="main"`.
- **Auditor Indikator Status Visual Berbasis Warna Saja (WCAG 2.1 SC 1.4.1)**: Mengaudit status badge dan indikator lingkaran agar tidak menyampaikan status atau makna semata-mata mengandalkan kode warna tanpa label tekstual komplementer atau atribut ARIA.
- **Auditor Pemotongan Teks CSS Ellipsis (WCAG 2.1 SC 1.4.4 / 1.3.1)**: Memeriksa elemen dengan properti CSS `text-overflow: ellipsis` atau pemotongan teks agar tetap menyediakan teks lengkap melalui atribut `title` atau `aria-label`.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Penalti PMD & DGD Serat Optik**: Kartu metrik visual Elementor untuk koefisien PMD, mean DGD, rasio periode bit, penalti daya OSNR, dan rekomendasi mitigasi dispersi.
- **Kartu Konfigurasi Kapasitas 5G NR PRACH**: Kartu visual Elementor untuk format preamble, alokasi root sequence, kapasitas preamble, radius sel aman, dan margin penerima gNodeB.
- **Kartu Dinamika Orbit & Doppler Satelit LEO**: Kartu visual Elementor untuk ketinggian orbit, sudut elevasi, pergeseran frekuensi Doppler, laju perubahan Doppler, dan margin densitas $C/N_0$.
- **Kartu Evaluasi Proposal Belmawa PKM-GFT**: Kartu profil mahasiswa, tema futuristik, skor evaluasi komposit, capaian insentif Belmawa, dan ekuivalensi MBKM.
- **Diagram Slot Timing Preamble 5G NR PRACH Inline SVG**: Diagram vektor responsif visualisasi Cyclic Prefix ($T_{CP}$), Zadoff-Chu Preamble Sequence ($T_{SEQ}$), Guard Time ($T_{GT}$), dan durasi total slot subframe 1.0 ms.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Buletin 5G NR PRACH**: Notifikasi Telegram untuk kapasitas preamble random access, alokasi cyclic shift, batasan radius sel, dan status margin sinyal uplink gNodeB.
- **Formatter Pengumuman Insentif Belmawa PKM-GFT**: Format resmi Telegram untuk pengumuman capaian kelulusan insentif nasional gagasan futuristik tertulis mahasiswa beserta ekuivalensi kurikulum MBKM.

### F. Skema Database SQLite Repository (`storage.py`)
- **Tabel `optical_pmd_dgd_records`**: Penyimpanan terstruktur telemetri dispersi polarisasi serat optik, panjang tautan, rasio dispersi, dan kategori status operasional.
- **Tabel `nr_prach_records`**: Penyimpanan terstruktur telemetri konfigurasi PRACH seluler, format sequence, margin deteksi gNodeB, dan status kepatuhan cakupan sel.
- **Tabel `pkm_gft_proposal_records`**: Penyimpanan arsip evaluasi proposal PKM-GFT mahasiswa, tema futuristik, skor komposit, status insentif nasional, dan rekognisi SKS MBKM.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Helper `get_users_by_roles`**: Pengambilan daftar pengguna situs WordPress berdasarkan filter peran (misalnya administrator, editor, author) melalui endpoint `/wp/v2/users?roles=...`.
- **Helper `batch_update_media_alt_texts`**: Pembaruan massal atribut teks alternatif aksesibilitas (`alt_text`) pada pustaka media WordPress via `POST /wp/v2/media/{id}`.

### H. Multi-Format Documentation & Schema.org Metadata (`exporter.py`)
- **Generator Schema.org `CreativeWork` Technology Foresight**: Penanda metadata JSON-LD terstruktur untuk proposal visioner PKM-GFT dan gagasan transformasi teknologi masa depan.
- **Eksportir Dokumentasi Mintlify MDX**: Konversi artikel ke format dokumentasi Mintlify dengan frontmatter YAML, tag `<Info>`, dan pemformatan Markdown/HTML standar.

### I. Command Line Interface / CLI (`cli.py`)
- Subcommand konsol baru:
  - `pmdpen`: Operasionalisasi dan pencatatan penalti dispersi PMD/DGD serat optik.
  - `nrprach`: Evaluasi dan pencatatan link budget kapasitas 5G NR PRACH.
  - `pkmgft`: Evaluasi dan pencatatan capaian proposal mahasiswa Belmawa PKM-GFT.
