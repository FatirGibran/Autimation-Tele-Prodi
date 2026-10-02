# Perubahan #03: Pembersihan Atribut Inline CSS Berbahaya

## Metadata Perubahan
- **ID**: #03
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_style_attribute_sanitization`

## Deskripsi Teknis
Melucuti ekspresi CSS berbahaya seperti expression(), @import, -moz-binding, javascript:, dan payload data:text/html dari atribut style.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
