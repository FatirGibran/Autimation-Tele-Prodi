# Perubahan #09: Eliminasi Parameter URL Tracking / UTM

## Metadata Perubahan
- **ID**: #09
- **Modul**: `parser.py`
- **Fungsi / Simbol**: `clean_url`
- **Test Suite**: `tests/test_parser.py::test_clean_url_strips_utm_parameters`

## Deskripsi Teknis
Mem-parse URL dan membuang query parameter analitik (utm_source, utm_medium, utm_campaign, fbclid, gclid, ref, mc_eid) untuk kebersihan kanonisasi URL.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
