# Perubahan #52: Verifikasi Webhook HMAC SHA-256

## Metadata Perubahan
- **ID**: #52
- **Modul**: `webhook_server.py`
- **Fungsi / Simbol**: `verify_hmac_sha256`
- **Test Suite**: `tests/test_webhook_server.py::test_hmac_sha256_verification`

## Deskripsi Teknis
Validasi tanda tangan HMAC SHA-256 menggunakan hmac.compare_digest untuk mencegah eksploitasi timing attack pada webhook.

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
