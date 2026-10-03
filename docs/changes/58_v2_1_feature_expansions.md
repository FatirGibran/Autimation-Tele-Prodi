# Perubahan #58: Rilis Fitur & Arsitektur v2.1.0

## Metadata Perubahan
- **ID**: #58
- **Modul**: `sanitizer.py`, `parser.py`, `seo_validator.py`, `components.py`, `storage.py`, `wordpress_client.py`, `exporter.py`, `cli.py`, `scripts/`
- **Test Suite**: `tests/` (120 Tests Passing, 100% Success Rate)

## Deskripsi Teknis
Pengembangan besar modul editorial dan otomasi Program Studi S1 Teknik Informatika Telkom University Purwokerto mencakup:
1. **Sanitasi HTML**: Penegakan struktur tabel semantik `tu-table`, pembersihan atribut presentasional legacy, pembatasan iframe edukatif ter-whitelist dengan sandbox, dan penegakan `rel="noopener noreferrer"`.
2. **Parser**: Generator excerpt otomatis (`generate_excerpt`), normalisasi tipografi bahasa Indonesia (`normalize_indonesian_typography`), parser catatan kaki akademik (`parse_markdown_footnotes`), dan ekstraktor n-gram frekuensi kata kunci (`extract_keyword_frequency`).
3. **Validator Yoast SEO**: Evaluasi kerapatan kata kunci (`evaluate_keyword_density`), batasan panjang paragraf 150 kata (`evaluate_paragraph_lengths`), auditor distribusi heading (`evaluate_subheading_distribution`), dan auditor profil tautan (`audit_links_profile`).
4. **Komponen Editorial Elementor**: Daftar Isi responsif (`render_table_of_contents`), Tim Penulis & Peneliti (`render_author_team`), Kartu Unduh Berkas/RPS (`render_download_card`), Wadah Video 16:9 (`render_video_embed`), Spanduk PMB (`render_admission_cta`), dan Badge Metrik KPI (`render_metric_callout`).
5. **Penyimpanan SQLite**: Siklus hidup soft delete & pemulihan artikel, metadata kustom key-value, audit event ekspor, dan mode konkurensi Write-Ahead Logging (WAL).
6. **WordPress Client**: Dukungan pembaruan draf (`update_post`), trashing (`delete_post`), dan pengunggahan biner media (`upload_media`).
7. **Sindikasi & Ekspor**: Generator feed Atom 1.0 (RFC 4287), JSON Feed v1.1, dan ekstraktor plain text bersih (`to_plain_text`).
8. **CLI Subcommands**: Penambahan perintah `trash`, `density`, `feed`, dan `meta`.
9. **Skrip Pemeliharaan**: Perkakas migrasi skema database terotomasi (`scripts/migrate_db.py`) dan benchmark performa (`scripts/benchmark_seo.py`).

## Dampak Teknis & Rationale
Memastikan kehandalan skalabilitas sistem, kecepatan respon, keamanan XSS, standar web editorial akademik, dan keselarasan penuh algoritma All-Green Yoast SEO institusional.
