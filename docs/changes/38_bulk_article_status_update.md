# Perubahan #38: Pembaruan Massal Status Artikel (Bulk Update)

## Metadata Perubahan
- **ID**: #38
- **Modul**: `storage.py`
- **Fungsi / Simbol**: `StorageManager.bulk_update_status`
- **Test Suite**: `tests/test_storage.py::test_bulk_update_status`

## Deskripsi Teknis
Efisiensi pembaruan status sekelompok artikel sekaligus dalam satu transaksi SQLite WHERE id IN (...).

## Dampak Teknis & Rationale
Pembaruan ini memastikan kepatuhan terhadap standar keamanan, performa Core Web Vitals, atau algoritma evaluasi editorial All-Green Yoast SEO institusional Program Studi S1 Teknik Informatika Telkom University Purwokerto.
