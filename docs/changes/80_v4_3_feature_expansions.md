# Dokumentasi Perubahan Arsitektur v4.3.0 Milestone Release

Siklus pengembangan v4.3.0 Milestone Architectural Release menghadirkan ekspansi fungsional terpadu pada portal otomasi editorial Prodi S1 Teknik Telekomunikasi:
- **Sanitasi DOM Spesifik & Keamanan Elemen HTML5**: Sanitasi elemen waktu semantik `<time>` dengan validasi format ISO-8601 dan pencegahan XSS (`sanitize_html5_time_datetime`), pengamanan elemen grafis vektor `<svg>` sub-elemen `<use>` dan `<symbol>` terhadap penyusupan referensi eksternal berbahaya (`sanitize_svg_use_and_symbols`), serta sanitasi elemen pemutus kata `<wbr>` dan eliminasi karakter tak kasat mata zero-width yang merusak evaluasi keterbacaan (`sanitize_html5_wbr_and_zero_width_spaces`).
- **Parser Standar Akademik & Rekayasa Telekomunikasi**: Kalkulator dispersi mode polarisasi serat optik (PMD) dan penundaan grup diferensial (mean DGD) menurut statistik Maxwellian ITU-T G.650.2 (`calculate_polarization_mode_dispersion`), kalkulator model empiris rugi propagasi seluler COST 231 Hata pada rentang frekuensi 1500-2000 MHz (`calculate_cost231_hata_path_loss`), kalkulator redaman hujan gelombang mikro terestrial dan estimasi ketersediaan tautan menurut rekomendasi ITU-R P.838 / P.530 (`calculate_rain_attenuation_itu_r`), serta evaluator rekognisi kurikulum program MBKM Studi & Riset Independen Bersertifikat (SIB) hingga 20 SKS (`parse_studi_independen_evaluation`).
- **Auditor SEO & Standar Aksesibilitas Tingkat Lanjut (WCAG 2.1 & Core Web Vitals)**: Auditor lokalisasi tag hreflang dan alternatif bahasa internasional (`audit_hreflang_localization_tags`), auditor direktif robots meta dan pengindeksan sitemap XML (`audit_sitemap_xml_and_robots_meta`), auditor penanda data terstruktur Schema.org FAQPage (`audit_faqpage_schema_markup`), serta auditor aksesibilitas elemen tabel data tabular, caption, dan summary (`audit_table_caption_and_summary`).
- **Komponen Semantik Elementor Responsif**: Kartu telemetri dispersi PMD dan DGD serat optik (`render_pmd_dispersion_card`), kartu analisis propagasi seluler COST 231 Hata (`render_cost231_hata_card`), kartu redaman hujan gelombang mikro ITU-R P.838 (`render_rain_attenuation_card`), kartu rekognisi sertifikasi MBKM Studi Independen Bersertifikat (`render_studi_independen_card`), serta kartu visualisasi diagram skema kompensasi dispersi serat SMF-28 + DCF berbasis responsif inline SVG (`render_dispersion_compensation_svg_card`).
- **Format Pesan Telegram**: Format buletin Telegram laporan redaman hujan gelombang mikro terestrial (`format_rain_attenuation_telegram`) dan format apresiasi penuntasan MBKM Studi Independen Bersertifikat mahasiswa (`format_studi_independen_telegram`).
- **Pengembangan Storage & Basis Data**: Tabel audit PMD serat optik (`optical_pmd_records`), tabel audit propagasi seluler COST 231 Hata (`cost231_propagation_records`), serta tabel rekam mahasiswa MBKM Studi Independen (`student_studi_independen`).
- **Klien WordPress REST API**: Helper perolehan objek tag WordPress berdasarkan tag ID numerik (`get_tag_by_id`) dan helper perolehan objek kategori WordPress berdasarkan category ID numerik (`get_category_by_id`).
- **Generator Statis & Ekspor**: Generator Schema.org `FAQPage` JSON-LD standar pencarian Google FAQ rich snippet (`generate_faq_page_json_ld`) serta eksportir markdown format dokumentasi teknis MkDocs Material (`to_mkdocs_material_markdown`).
- **Antarmuka Konsol CLI**: Subcommand konsol baru `pmd`, `cost231`, dan `independen`.
- **Peningkatan Suite Pengujian Unit**: Jumlah pengujian bertambah dari 706 menjadi 735 unit test terverifikasi (100% pass rate).

---

## Rincian Fitur Utama yang Ditambahkan:

1. **Sanitasi Atribut Datetime Elemen Time (`sanitizer.py`)**:
   - Memvalidasi elemen `<time datetime="...">`, mensterilkan format tanggal/waktu ISO-8601, membersihkan payload injeksi pseudo-protokol JavaScript, dan menghapus event handler inline.

2. **Sanitasi Elemen SVG Use & Symbol (`sanitizer.py`)**:
   - Mengamankan elemen `<use>` dan `<symbol>` pada grafis vektor inline SVG, memastikan atribut `href` dan `xlink:href` hanya mereferensikan identifier internal lokal (`#id`) dan menolak URI jarak jauh (remote URI injection).

3. **Sanitasi Elemen WBR & Zero-Width Spaces (`sanitizer.py`)**:
   - Membersihkan elemen `<wbr>` dari atribut yang tidak semantik dan menyaring karakter tak kasat mata (zero-width spaces `\u200B`, `\u200C`, `\u200D`, `\uFEFF`) yang merusak indeks mesin pencari.

4. **Kalkulator Dispersi Mode Polarisasi (PMD) Serat Optik (`parser.py`)**:
   - Mengalkulasi mean Differential Group Delay (DGD) $\langle\Delta\tau\rangle = D_{\text{pmd}} \sqrt{L}$, rasio degradasi periode bit modulasi, estimasi laju bit maksimum $B_{\text{max}}$, dan analisis risiko outage transmisi berkecepatan 10G/40G/100G.

5. **Kalkulator Rugi Propagasi Seluler COST 231 Hata (`parser.py`)**:
   - Menghitung path loss empiris perkotaan dan pinggiran kota (1500-2000 MHz) berdasarkan tinggi BTS, tinggi antena mobile, jarak jangkauan, dan faktor koreksi area metropolitan.

6. **Kalkulator Redaman Hujan ITU-R P.838 / P.530 (`parser.py`)**:
   - Mengalkulasi redaman spesifik hujan $\gamma_R = k R^{\alpha}$, faktor reduksi jarak $r$, redaman total $A_{\text{rain}}$, dan margin sisa (excess fade margin) untuk menjamin ketersediaan link microwave terestrial $\ge 99.999\%$.

7. **Evaluator Rekognisi MBKM Studi Independen Bersertifikat (`parser.py`)**:
   - Menghitung skor komposit penilaian mentor industri, milestone teknis, dan sidang capstone defense, konversi nilai mutu huruf, serta pemetaan hingga 20 SKS mata kuliah prodi.

8. **Auditor Lokalisasi Hreflang SEO (`seo_validator.py`)**:
   - Memverifikasi keberadaan tag `<link rel="alternate" hreflang="...">`, format kode bahasa ISO 639-1, fallback `x-default`, dan konsistensi tautan bidirectional.

9. **Auditor Sitemap XML & Direktif Robots Meta (`seo_validator.py`)**:
   - Memeriksa direktif robots meta (`index, follow`), pencegahan tagging kontradiktif `noindex`, dan validasi deklarasi lokasi sitemap XML.

10. **Auditor Skema FAQPage Schema.org (`seo_validator.py`)**:
    - Memvalidasi keberadaan struktur JSON-LD atau Microdata FAQPage, pasangan pertanyaan-jawaban yang valid, dan kepatuhan terhadap pedoman Google Rich Results.

11. **Auditor Aksesibilitas Elemen Tabel Data (`seo_validator.py`)**:
    - Mengaudit ketersediaan elemen `<caption>`, atribut `scope="col"` atau `scope="row"` pada header `<th>`, serta struktur semantik `<thead>` dan `<tbody>` sesuai pedoman WCAG 2.1 AA.

12. **Komponen Visualisasi Kompensasi Dispersi Serat DCF SVG (`components.py`)**:
    - Kartu antarmuka visual diagram kompensasi dispersi SMF-28 (+D) dan Dispersion Compensating Fiber (-D) berbasis inline SVG interaktif dan responsif.

13. **Manajer Penyimpanan Database SQLite (`storage.py`)**:
    - Tabel baru `optical_pmd_records`, `cost231_propagation_records`, dan `student_studi_independen` dilengkapi metode CRUD dan indeks terindeksasi.

14. **Klien WordPress REST API (`wordpress_client.py`)**:
    - Helper query `get_tag_by_id` dan `get_category_by_id` untuk pengambilan metadata taksonomi secara presisi berdasarkan identifier numerik.

15. **Generator FAQPage JSON-LD & Eksportir MkDocs (`exporter.py`)**:
    - Generator Schema.org `FAQPage` JSON-LD standar rich snippets dan eksportir format dokumentasi teknis MkDocs Material.

16. **Subcommand Konsol CLI (`cli.py`)**:
    - Subcommand `pmd`, `cost231`, dan `independen` untuk operasionalisasi langsung dari terminal.
