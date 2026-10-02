# Perubahan #08: Penghapusan Tag Sematan Tidak Aman

## Metadata Perubahan
- **ID**: #08
- **Modul**: `sanitizer.py`
- **Fungsi / Simbol**: `HTMLSanitizer.sanitize`
- **Test Suite**: `tests/test_sanitizer.py::test_dangerous_tags_stripped`

## Deskripsi Teknis
Menghapus tag <script>, <iframe>, <object>, dan <embed> beserta isinya untuk mencegah penyusupan konten pihak ketiga yang tidak terotorisasi.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
