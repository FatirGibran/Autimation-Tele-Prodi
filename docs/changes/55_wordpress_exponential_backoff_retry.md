# Perubahan #55: Mekanisme Exponential Backoff Retry WordPress

## Metadata Perubahan
- **ID**: #55
- **Modul**: `wordpress_client.py`
- **Fungsi / Simbol**: `WordPressClient._send_request`
- **Test Suite**: `tests/test_wordpress_client.py::test_retry_mechanism`

## Deskripsi Teknis
Mekanisme retry otomatis bertingkat (exponential backoff) maksimal 3 kali untuk menangani kegagalan jaringan atau server sementara.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
