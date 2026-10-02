# Perubahan #05: Penegakan Performa & Lazy Loading Gambar

## Metadata Perubahan
- **ID**: #05
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_image_attributes_enforced`

## Deskripsi Teknis
Menyuntikkan atribut loading='lazy' dan decoding='async' pada setiap tag <img> untuk optimalisasi Core Web Vitals (LCP dan CLS).

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
