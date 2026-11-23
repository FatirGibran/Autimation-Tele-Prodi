# Dokumentasi Perubahan Arsitektur Milestone Release v6.3.0

## 1. Ikhtisar Rilis
Milestone Release v6.3.0 menghadirkan siklus ekspansi arsitektur menyeluruh untuk otomasi portal editorial Program Studi S1 Teknik Telekomunikasi Telkom University Purwokerto. Rilis ini memperluas kapabilitas kalkulasi rekayasa transmisi satelit non-terestrial, fotonika terintegrasi silikon, dispersi serat optik orde tinggi, dan propagasi 5G NTN Rel-17. Pada lapisan antarmuka dan aksesibilitas, ditambahkan auditor kepatuhan WCAG 2.1 dan WCAG 2.2, penguatan sanitasi keamanan HTML5, penyempurnaan integrasi WordPress REST API terpaginasi berbasis slug, skema relasional SQLite komprehensif, serta eksportir dokumentasi modern berbasis Rspress MDX dan Schema.org Dataset.

## 2. Rincian Modul & Fitur Baru

### A. Sanitasi Keamanan HTML5 Terisolasi & Sandboxing (`sanitizer.py`)
- **Sanitasi HTML5 Inert Interaction Traps**: Menetralkan manipulasi atribut global `inert` yang disalahgunakan untuk mengunci interaksi formulir atau memblokir aksesibilitas pembaca layar pada elemen navigasi utama.
- **Sanitasi HTML5 Formaction & Formmethod Hijacking**: Menghapus atribut penimpa pengiriman formulir (`formaction`, `formmethod`, `formtarget`, `formenctype`) pada elemen `<button>` dan `<input type="submit">` guna mencegah pembajakan data credential dan token sesi ke endpoint eksternal berbahaya.
- **Sanitasi CSS Behavior & Expression Executable dalam Gaya Inline**: Membersihkan fungsi eksekusi skrip dinamis warisan Microsoft IE/Edge seperti `behavior: url(...)`, `-moz-binding`, dan `expression(...)` di dalam atribut `style="..."` yang berpotensi memicu eksekusi kode berbahaya.
- **Sanitasi Tainted Canvas Rasterization & Fallback Markup**: Membersihkan kontainer kanvas grafis HTML5 `<canvas>` dari pemanggilan fungsi rasterisasi berbahaya yang memicu kontaminasi memori grafis dan penyusupan skrip DOM melalui markup fallback.

### B. Algoritma Rekayasa Telekomunikasi Lanjutan (`parser.py`)
- **Kalkulator Kepadatan Carrier-to-Noise Satelit (ITU-R S.524 / S.1061 C/N₀)**: Perhitungan lengkap link budget satelit uplink/downlink, estimasi Free Space Path Loss (FSPL), redaman atmosferik, penerimaan stasiun bumi ($G/T$), kerapatan daya derau termal Boltzman, nilai $C/N_0$ (dB-Hz), serta Carrier-to-Noise Ratio (CNR) untuk mengevaluasi kelayakan modulasi tinggi DVB-S2X (16APSK/32APSK).
- **Kalkulator Dispersi Polarisasi Orde Kedua (ITU-T G.650.2 SOPMD & Depolarisasi)**: Pemodelan fenomena Second-Order Polarization Mode Dispersion (SOPMD) pada serat optik mode tunggal (SMF), pemisahan komponen laju depolarisasi vektor Stokes ($\omega \times \vec{\tau}$) dan dispersi kromatik polarisasi (PCD), serta kalkulasi rasio pelebaran pulsa optik pada laju transmisi koheren 100G/400G+.
- **Kalkulator Propagasi 5G NR Rel-17 NTN Delay & Doppler (3GPP TR 38.821 / TS 38.300)**: Pemodelan lintasan transmisi orbit satelit bumi rendah (LEO/MEO/GEO), estimasi jarak miring (*slant range*), waktu tunda satu arah (*one-way delay*), Service Link Round Trip Time (RTT), kebutuhan kompensasi Common Timing Advance (TA), pergeseran Doppler puncak ($\pm \Delta f$), serta laju perubahan Doppler (*Doppler rate* in Hz/s).
- **Kalkulator Filter Micro-Ring Resonator Silikon Fotonik (Silicon Photonic MRR)**: Analisis spektral resonator cincin mikro terintegrasi pada pandu gelombang silikon (*Silicon-on-Insulator* / SOI), menghitung keliling optik, Free Spectral Range (FSR dalam nm dan GHz), Full Width at Half Maximum (FWHM linewidth), finesse ($\mathcal{F}$), faktor kualitas ($Q$), serta evaluasi rezim kopling (*critical coupling*, *under-coupled*, *over-coupled*).

### C. Auditor Aksesibilitas Web & Pengalaman Pengguna WCAG 2.1 & WCAG 2.2 (`seo_validator.py`)
- **Auditor Adaptasi Perenggangan Teks (WCAG 2.1 SC 1.4.12)**: Memverifikasi bahwa dokumen HTML tidak menggunakan deklarasi `!important` pada styling `line-height`, `letter-spacing`, atau `word-spacing` yang mencegah pengguna merenggangkan teks untuk kenyamanan membaca.
- **Auditor Konten pada Hover atau Fokus (WCAG 2.1 SC 1.4.13)**: Memastikan elemen pemicu konten mengambang (tooltip, popover menu) memiliki mekanisme penutupan tanpa memindahkan pointer (dapat ditutup via tombol Escape atau atribut dismissible) dan tidak hilang saat pointer melintas di atas konten tambahan.
- **Auditor Pintasan Karakter Tunggal (WCAG 2.1 SC 2.1.4)**: Mengaudit penggunaan atribut `accesskey` atau `data-shortcut` berbasis karakter tunggal tanpa tombol pengubah (modifier seperti Ctrl/Alt) guna mencegah benturan pintasan tombol bawaan pada pembaca layar dan perangkat kontrol suara.
- **Auditor Alternatif Pergerakan Dragging (WCAG 2.2 SC 2.5.7)**: Memeriksa elemen interaktif yang mendukung operasi seret (*dragging* seperti penyortiran daftar) memiliki kontrol tombol penunjuk tunggal sederhana (*single-pointer click*) sebagai alternatif fungsional.

### D. Komponen UI Elementor & Diagram Vektor Responsif SVG (`components.py`)
- **Kartu Telemetri Kepadatan C/N₀ Satelit**: Kartu Elementor responsif menampilkan parameter EIRP satelit, redaman FSPL, rugi atmosferik, figure of merit $G/T$, lebar pita, nilai $C/N_0$, CNR, serta rekomendasi modulasi ITU-R S.524.
- **Kartu Telemetri SOPMD Serat Optik**: Kartu visual Elementor menampilkan rerata DGD orde pertama, total SOPMD orde kedua (ps²), laju depolarisasi, komponen PCD, laju data transmisi (Gbps), serta rasio pelebaran pulsa optik.
- **Kartu Telemetri Propagasi 5G NR Rel-17 NTN**: Kartu metrik Elementor menampilkan ketinggian orbit LEO, sudut elevasi, frekuensi pembawa RF, slant range, Service Link RTT, Common TA, deviasi pergeseran Doppler puncak, dan laju perubahan Doppler.
- **Kartu Telemetri Filter Micro-Ring Resonator Silikon**: Kartu analitik Elementor menampilkan radius cincin mikro, group index pandu gelombang, FSR (nm & GHz), lebar pita FWHM 3dB, finesse, dan faktor kualitas $Q$ resonator terintegrasi.
- **Diagram Arsitektur Link Satelit 5G NR NTN Inline SVG**: Diagram vektor responsif menggambarkan segmen antariksa payload LEO gNodeB, Feeder Link Ka-Band ke Gateway stasiun bumi, Service Link S-Band ke perangkat pengguna (UE), serta koneksi terestrial 5G Core.

### E. Format Notifikasi Telegram Bot (`formatters.py`)
- **Formatter Telemetri Link Budget C/N₀ Satelit**: Templat pesan markdown Telegram untuk monitoring berkala kualitas sinyal carrier-to-noise density link satelit ITU-R S.524.
- **Formatter Telemetri Propagasi 5G NR Rel-17 NTN**: Templat notifikasi Telegram menampilkan metrik RTT satelit LEO, penyesuaian Common TA, dan kompensasi deviasi Doppler 3GPP Rel-17.
- **Formatter Telemetri Micro-Ring Resonator Silikon**: Templat Telegram menyajikan parameter FSR, linewidth FWHM, dan selektivitas kanal WDM pada sirkuit fotonika terintegrasi.

### F. Manajemen Rekam Database Relasional SQLite (`storage.py`)
- **Tabel `satellite_link_cn0_records`**: Tabel relasional menyimpan riwayat kalkulasi kepadatan $C/N_0$, redaman link, $G/T$, CNR, dan indeks pencarian `link_id`.
- **Tabel `nr_ntn_delay_doppler_records`**: Tabel relasional menyimpan spesifikasi sel satelit NTN, elevasi, slant range, RTT, Common TA, deviasi Doppler, dan indeks pencarian `cell_id`.
- **Tabel `optical_micro_ring_resonator_records`**: Tabel relasional menyimpan karakteristik desain filter cincin silikon fotonik, radius, group index, FSR, finesse, faktor $Q$, dan indeks pencarian `device_id`.

### G. Integrasi REST API WordPress Client (`wordpress_client.py`)
- **Metode `get_posts_by_category_slug`**: Mengambil daftar artikel terpublikasi berdasarkan slug kategori WordPress dengan resolusi otomatis ID taksonomi dan paginasi terisolasi (`GET /wp/v2/categories?slug={slug}` dilanjutkan `GET /wp/v2/posts?categories={cat_id}`).
- **Metode `get_posts_by_tag_slug`**: Mengambil daftar artikel teknis yang ditandai dengan tag slug tertentu secara efisien (`GET /wp/v2/tags?slug={slug}` dilanjutkan `GET /wp/v2/posts?tags={tag_id}`).

### H. Ekspor Multi-Format & Metadata Mesin Pencari (`exporter.py`)
- **Generator Schema.org Dataset JSON-LD (`generate_telecom_dataset_json_ld`)**: Pembuatan metadata terstruktur Google Schema.org untuk repositori dataset eksperimen telekomunikasi yang dilengkapi tautan unduhan JSON dan CSV serta lisensi Creative Commons CC-BY-4.0.
- **Eksportir Dokumentasi Rspress MDX (`to_rspress_mdx`)**: Mengonversi naskah teknis editorial ke format Rspress MDX berbasis Rsbuild dengan dukungan frontmatter metadata, konfigurasi sidebar otomatis, dan callout `:::tip`.

### I. Antarmuka Command Line Interface / CLI (`cli.py`)
- Subcommand `satcn0`: Kalkulasi dan penyimpanan metrik carrier-to-noise density $C/N_0$ link satelit ITU-R S.524.
- Subcommand `nrntn`: Perhitungan waktu tunda propagasi RTT, Common Timing Advance, dan pergeseran Doppler 5G NTN 3GPP Rel-17.
- Subcommand `mrr`: Analisis karakteristik Free Spectral Range (FSR) dan faktor kualitas $Q$ filter micro-ring resonator silikon fotonik.
