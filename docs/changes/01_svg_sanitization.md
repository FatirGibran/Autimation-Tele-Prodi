# Perubahan #01: Sanitasi Inline SVG (Pencegahan Injeksi XSS)

## Metadata Perubahan
- **ID**: #01
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_svg_sanitization`

## Deskripsi Teknis
Menghapus tag anak berbahaya <foreignObject> dan <script> pada elemen inline SVG menggunakan regex multiline case-insensitive guna mencegah eksploitasi Cross-Site Scripting.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
