# Operational & Automation Runbook

Panduan teknis otomasi dan operasi sistem editorial S1 Teknik Informatika Telkom University Purwokerto.

---

## 1. Automation Toolchain Overview

| Utility / Script | File Path | Fungsi Utama | Perintah CLI / Make |
|---|---|---|---|
| **Environment Doctor** | `scripts/env_doctor.py` | Diagnosa dependensi, API key, dan database | `make doctor` atau `python scripts/env_doctor.py` |
| **Database Backup** | `scripts/backup_db.py` | Backup ACID SQLite dengan retensi | `make backup` atau `python scripts/backup_db.py` |
| **Bulk SEO Auditor** | `scripts/bulk_audit.py` | Audit massal file HTML dan metadata | `make bulk-audit` atau `python scripts/bulk_audit.py` |
| **Editorial CLI** | `cli.py` | Operasi offline: audit, list, stats, search, export | `python cli.py [command]` |
| **Webhook Server** | `webhook_server.py` | Endpoint webhook Telegram & liveness check | `python webhook_server.py` |

---

## 2. Developer & Ops Automation Recipes

### Health Check & Environment Diagnosis
Jalankan sebelum deployment atau setelah perubahan konfigurasi `.env`:
```bash
make doctor
```
Untuk format JSON terstruktur (monitoring pipeline):
```bash
python scripts/env_doctor.py --json
```

### Database Backup & Retention
Backup online konsisten menggunakan SQLite Backup API:
```bash
make backup
```
Flag kustom:
```bash
python scripts/backup_db.py --dest /path/to/backup --max-backups 15
```

### Batch SEO Verification
Memverifikasi kepatuhan seluruh artikel terhadap kriteria Yoast SEO:
```bash
make bulk-audit
```

### Export Multi-Format Bundle
Ekspor artikel dari database ke format HTML terisolasi, halaman standalone, Markdown ber-frontmatter, dan Elementor template JSON:
```bash
python cli.py export --slug <slug-artikel> --out output/
```

### Telegram Bot & Webhook Server
Jalankan server webhook berkinerja tinggi untuk produksi:
```bash
python webhook_server.py
```
Endpoint yang tersedia:
- `GET /health` : Liveness and readiness probe
- `POST /webhook` : Telegram webhook receiver with token validation

---

## 3. Disaster Recovery & Database Restore

Jika database `editorial.db` mengalami korupsi atau kehilangan data:
1. Hentikan instance bot atau webhook server:
   ```bash
   pkill -f "python.*(bot|webhook_server)"
   ```
2. Temukan backup terbaru:
   ```bash
   ls -lt backups/editorial_backup_*.db | head -n 1
   ```
3. Salin file backup ke lokasi utama:
   ```bash
   cp backups/editorial_backup_YYYYMMDD_HHMMSS_XXXXXX.db editorial.db
   ```
4. Jalankan verifikasi integritas:
   ```bash
   python scripts/env_doctor.py
   ```
5. Nyalakan kembali service:
   ```bash
   make run
   ```
