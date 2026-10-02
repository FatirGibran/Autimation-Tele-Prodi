# Perubahan #04: Penegakan Atribut Keamanan Tautan Eksternal

## Metadata Perubahan
- **ID**: #04
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_external_link_sanitization`

## Deskripsi Teknis
Menambahkan atribut target='_blank' dan rel='noopener noreferrer' secara otomatis untuk seluruh hyperlink yang mengarah ke luar domain kampus bif-pwt.telkomuniversity.ac.id.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
