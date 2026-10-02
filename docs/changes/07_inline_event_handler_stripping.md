# Perubahan #07: Pembersihan Event Handler Inline

## Metadata Perubahan
- **ID**: #07
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_inline_event_handler_stripped`

## Deskripsi Teknis
Melucuti atribut event handler inline seperti onclick, onload, onerror, dan onmouseover menggunakan regex filter.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
