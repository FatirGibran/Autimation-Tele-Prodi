# Perubahan #02: Netralisasi Pseudo-Protokol JavaScript pada SVG

## Metadata Perubahan
- **ID**: #02
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_svg_sanitization`

## Deskripsi Teknis
Mengganti atribut xlink:href bernilai javascript: pseudo-protocol menjadi xlink:href='#' untuk menonaktifkan trigger eksekusi skrip saat tautan grafik SVG diklik.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
