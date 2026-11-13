# Dokumentasi Perubahan Arsitektur Milestone Release v5.9.0

## 1. Ikhtisar Rilis
Milestone Release v5.9.0 menambahkan arsitektur menyeluruh pada stack otomasi editorial, telemetri komunikasi optik ruang bebas (Free Space Optics - FSO), alokasi kapasitas kanal kontrol 5G NR PDCCH dan CCE, pola radiasi antena stasiun bumi satelit ITU-R S.580, pengujian kepatuhan aksesibilitas web WCAG 2.1 (orientasi layar, pengalihan meta refresh, auto-submit, dan urutan fokus alami tabindex), serta evaluasi dan rekognisi publikasi ilmiah mahasiswa Belmawa PKM Artikel Ilmiah (PKM-AI) untuk civitas akademika S1 Teknik Telekomunikasi Telkom University Purwokerto.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan Elemen HTML5 Terisolasi & Executables (`sanitizer.py`)
- **Sanitasi Elemen Manipulasi URL Basis `<base>`**: Penanganan dan sterilisasi injeksi elemen `<base href="...">` guna mencegah URL hijacking, form hijacking, dan pemalsuan resolusi path berkas relatif.
- **Sanitasi Elemen Animasi Teks Bergerak `<marquee>`**: Normalisasi elemen animasi legacy marquee dengan membatasi laju scroll (`scrollamount` $\le 10$) serta menanggalkan atribut interaktif agresif guna memenuhi standar aksesibilitas visual.
- **Sanitasi Elemen Plugin Executable Legacy `<applet>`**: Sterilisasi total elemen legacy applet Java dan arsip eksekusi (`codebase`, `archive`) dengan melucuti atribut eksekusi biner tidak aman.

### B. Algoritma Rekayasa Telekomunikasi & Evaluasi Belmawa PKM-AI (`parser.py`)
- **Kalkulator Link Budget & Redaman Kabut Komunikasi Nirkabel Optik Ruang Bebas (FSO)**: Pemodelan transmisi laser atmosferik via model hamburan Mie Kim/Kruse, kalkulasi redaman geometrik berkas laser transmitter-receiver, daya terima fotodioda ($P_{rx}$), serta evaluasi margin fading link optik terestrial.
- **Kalkulator Kapasitas & Agregasi 5G NR PDCCH & CCE (3GPP TS 38.211 / TS 38.213)**: Pemodelan kisi sumber daya Control Resource Set (CORESET), pengelompokan REG ke dalam Control Channel Elements (1 CCE = 6 REG), evaluasi kuota hibah DCI konkuren per level agregasi (AL 1, 2, 4, 8, 16), batas kandidat blind decoding, dan deteksi kondisi blocking kapasitas kanal kontrol.
- **Kalkulator Pola Radiasi & Sidelobe Envelope Antena Stasiun Bumi Satelit (ITU-R S.580)**: Analisis boresight peak gain ($G_{max}$), Half-Power Beamwidth (HPBW), serta envelope penekanan sidelobe off-axis ($29 - 25 \log \phi$) untuk koordinasi orbit satelit geostasioner (GSO).
- **Evaluator Proposal Artikel Ilmiah Mahasiswa Belmawa PKM-AI**: Penilaian komposit publikasi ilmiah mahasiswa (judul & abstrak 15%, pendahuluan & state of the art 25%, metode eksperimen 25%, pembahasan hasil 25%, kesimpulan & referensi 10%), penalti plagiarisme Turnitin, penetapan insentif nasional Belmawa Rp 3.000.000, serta rekognisi konversi MBKM hingga 4 SKS.

### C. Auditor Aksesibilitas Web & Antarmuka WCAG 2.1 (`seo_validator.py`)
- **Auditor Pembatasan Kunci Orientasi Layar (WCAG 2.1 SC 1.3.4)**: Memverifikasi CSS viewport media queries dan inline style agar tidak membatasi atau mengunci tampilan visual hanya pada satu orientasi (portrait atau landscape).
- **Auditor Pengalihan Waktu Meta HTTP-Equiv (WCAG 2.1 SC 2.2.1)**: Memeriksa tag `<meta http-equiv="refresh" content="...">` untuk mendeteksi pengalihan otomatis dengan penundaan waktu yang membingungkan pengguna pembaca layar.
- **Auditor Form Auto-Submitting pada Input Change (WCAG 2.1 SC 3.2.2)**: Mengaudit atribut `onchange="this.form.submit()"` pada elemen `<select>` atau `<input>` untuk mencegah perubahan konteks tak terduga tanpa tombol kirim eksplisit.
- **Auditor Nilai Tabindex Positif & Urutan Fokus Alami (WCAG 2.1 SC 2.1.1)**: Mengaudit atribut `tabindex` bernilai bilangan bulat positif yang merusak alur fokus navigasi keyboard alami DOM.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Link Budget FSO**: Kartu metrik visual Elementor untuk jarak link, koefisien redaman kabut, rugi geometrik, margin fading link, dan panduan mitigasi transmisi optik atmosfer.
- **Kartu Evaluasi Kapasitas 5G NR PDCCH & CCE**: Kartu visual Elementor untuk konfigurasi CORESET, kapasitas total CCE, jumlah hibah DCI maksimum, utilitas UE, dan status blocking kanal kontrol.
- **Kartu Pola Radiasi Antena Stasiun Bumi ITU-R S.580**: Kartu visual Elementor untuk diameter parabola, frekuensi pembawa, rasio $D/\lambda$, gain boresight, sudut off-axis, dan tingkat supresi sidelobe.
- **Kartu Evaluasi Mahasiswa Belmawa PKM-AI**: Kartu profil penulis utama, judul naskah ilmiah, rumpun keilmuan, skor komposit, status insentif nasional Belmawa, dan ekuivalensi MBKM.
- **Diagram Kisi Sumber Daya 5G NR PDCCH CORESET & CCE Inline SVG**: Diagram vektor responsif visualisasi pengelompokan REG menjadi CCE (CCE #0, CCE #1, CCE #2), alokasi Aggregation Level DCI, serta batas bandwidth frekuensi-waktu CORESET berbasis inline SVG.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Buletin 5G NR PDCCH & CCE**: Notifikasi Telegram untuk kapasitas CCE CORESET, agregasi DCI, utilisasi sumber daya gNodeB, dan status ambang blocking.
- **Formatter Pengumuman Insentif Belmawa PKM-AI**: Format resmi Telegram untuk publikasi kelulusan insentif nasional artikel ilmiah mahasiswa beserta rekognisi kredit MBKM.

### F. Manajemen Rekam Database SQLite (`storage.py`)
- **Tabel `fso_link_records`**: Penyimpanan relasional metrik link budget optik FSO terestrial.
- **Tabel `nr_pdcch_records`**: Penyimpanan kapasitas CCE, alokasi CORESET, dan penjadwalan DCI 5G NR.
- **Tabel `pkm_ai_proposal_records`**: Penyimpanan evaluasi artikel ilmiah mahasiswa, uji Turnitin, insentif Belmawa, dan rekognisi MBKM.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Metode `get_posts_by_taxonomies`**: Pengambilan artikel WordPress terfilter kombinasi beberapa kategori dan tag secara simultan dengan paginasi.
- **Metode `batch_update_post_featured_media`**: Pembaruan massal ID featured media gambar unggulan pada kumpulan artikel WordPress via REST API.

### H. Ekspor Multi-Format & Metadata Mesin Pencari (`exporter.py`)
- **Generator Schema.org ScholarlyArticle JSON-LD (`generate_scientific_article_publication_json_ld`)**: Pembuatan metadata terstruktur Google ScholarlyArticle untuk publikasi artikel ilmiah mahasiswa PKM-AI lengkap dengan afiliasi program studi dan konversi MBKM.
- **Eksportir Dokumentasi Vocs MDX (`to_vocs_mdx`)**: Konversi konten artikel editorial ke format dokumentasi Vocs (Wevm) dengan frontmatter YAML dan tag admonition `:::info`.

### I. Antarmuka Command Line Interface / CLI (`cli.py`)
- Subcommand `fsolink` (kalkulasi dan inventarisasi link budget transmisi optik nirkabel FSO).
- Subcommand `nrpdcch` (evaluasi kapasitas kanal kontrol PDCCH, CCE CORESET, dan penjadwalan DCI 5G NR).
- Subcommand `pkmai` (evaluasi berkas artikel ilmiah PKM-AI, penalti Turnitin, insentif Belmawa, dan ekuivalensi MBKM).
