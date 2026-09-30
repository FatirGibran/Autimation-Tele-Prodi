# Automation Tele Prodi (Editorial Specialist Bot)

Sistem otomasi produksi artikel berita dan riset mingguan Program Studi S1 Teknik Informatika Telkom University Purwokerto (`bif-pwt.telkomuniversity.ac.id`), dirancang untuk memproduksi kode HTML siap tempel ke widget Custom HTML Elementor serta metadata Yoast SEO dengan skor hijau (*All Green*).

---

## 1. Arsitektur dan Skema Alur Kerja

```
[Telegram User] 
       │ (Kirim: Topik + Gambar + Tanggal + Poin Utama)
       ▼
[Telegram Bot Service] (bot.py / webhook_server.py)
       │ 
       ▼
[LLM Engine] (Gemini 2.5 Flash / Antigravity Engine)
       │  ├── Injeksi Master System Prompt (prompts/system_prompt.md)
       │  └── Validasi Standar Desain & SEO Kampus
       ▼
[Response Parser & Sanitizer] (parser.py, sanitizer.py)
       │  ├── Ekstraksi Metadata Yoast SEO (Title, Slug, Keyphrase, Meta Desc)
       │  ├── Sanitasi Tag HTML & Penegakan rel="noopener noreferrer"
       │  └── Pengecekan Duplikasi Keyphrase (storage.py)
       ▼
[Yoast SEO Evaluator] (seo_validator.py)
       │  └── Verifikasi 10 Parameter All Green Yoast SEO
       ▼
[Telegram Bot Output & Exporter] (formatters.py, exporter.py)
       │  ├── Output 1: Yoast SEO Metadata Markdown + Tombol Interaktif
       │  └── Output 2: File .html Lengkap Siap Tempel ke Elementor
       ▼
[WordPress WP-Admin (bif-pwt.telkomuniversity.ac.id)]
       ├── Otomatis: Publish Draft via WordPress REST API (wordpress_client.py)
       └── Manual: Copy-paste ke Post Editor & Panel Yoast SEO
```

---

## 2. Struktur Repositori

```
Autimation Tele Prodi/
├── .github/workflows/
│   ├── ci.yml                                        # Automated CI testing
│   └── seo_audit.yml                                 # Automated Yoast SEO audit for articles
├── .env.example                                      # Contoh kredensial & environment
├── .gitignore                                        # Rule git ignore
├── Dockerfile                                        # Multi-stage lightweight dockerfile
├── docker-compose.yml                                # Docker compose definition
├── Makefile                                          # Developer automation tasks
├── README.md                                         # Dokumentasi utama proyek
├── bot.py                                            # Telegram bot handler & workflow engine
├── cli.py                                            # Command-Line Interface untuk audit & list
├── components.py                                     # Modular semantic HTML component builder
├── config.py                                         # Centralized typed configuration
├── exporter.py                                       # Export Elementor JSON & Markdown
├── formatters.py                                     # Telegram message & inline keyboard builders
├── parser.py                                         # Multi-format Telegram trigger & output parser
├── requirements.txt                                  # Dependensi Python
├── sanitizer.py                                      # HTML sanitizer & CSS isolation guard
├── seo_validator.py                                  # Evaluator 10 parameter Yoast SEO All-Green
├── storage.py                                        # SQLite database pencegah kanibalisasi keyphrase
├── webhook_server.py                                 # Webhook server & health check
├── articles/                                         # Arsip artikel siap terbit
│   ├── 2026-09-28-webassembly-edge-computing-iot.html
│   └── 2026-09-28-webassembly-edge-computing-iot-metadata.json
├── docs/
│   ├── API.md                                       # Spesifikasi teknis payload & API
│   ├── AUTOMATION_RUNBOOK.md                         # Runbook operasional & pemeliharaan berkala
│   ├── COMPONENTS_CATALOG.md                         # Katalog komponen semantik HTML Elementor
│   ├── DEPLOYMENT.md                                 # Panduan deployment Docker, Systemd, Cloud Run
│   └── EDITORIAL_GUIDE.md                           # Panduan brand & prinsip anti-slop
├── prompts/
│   ├── system_prompt.md                             # Master system prompt editorial
│   ├── research_spotlight.md                        # Template riset & publikasi ilmiah
│   ├── campus_achievement.md                        # Template berita prestasi mahasiswa
│   └── community_service.md                         # Template pengabdian masyarakat (Abdimas)
└── tests/                                            # Test suite terotomasi
    ├── test_components.py
    ├── test_exporter.py
    ├── test_parser.py
    ├── test_sanitizer.py
    ├── test_seo_validator.py
    └── test_wordpress_client.py
```

---

## 3. Format Pesan Pemicu (Telegram Trigger)

Kirimkan pesan ke bot dengan struktur berikut:

```text
Topik: WebAssembly (Wasm) untuk Edge Computing Cerdas di Jaringan IoT
Tanggal: 28 September 2026
Kategori: Cloud & Edge Computing
Image URL: https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/2026/09/Pin-on-h.jpeg
Poin Utama:
- Keunggulan cold start Wasm dibanding container Docker di perangkat edge
- Keamanan isolasi memori linier (sandbox)
- Implementasi pada smart village sensor monitoring
```

---

## 4. Perintah Developer (Makefile & CLI)

Jalankan perintah pengujian dan utilitas dengan mudah:

```bash
# Menjalankan seluruh test suite unit test
make test

# Menjalankan audit Yoast SEO pada artikel terbitan
make audit

# Menampilkan daftar artikel di database lokal
make cli-list

# Menjalankan bot secara lokal
make run
```

---

## 5. Standar Yoast SEO All-Green

| Parameter | Aturan Standar |
| :--- | :--- |
| **Focus Keyphrase** | 3–5 kata spesifik, muncul di awal Title, Paragraf 1, H2, Alt Gambar, Slug, dan Meta Description |
| **Meta Description** | Tepat 140–156 karakter, persuasif, memuat Focus Keyphrase |
| **Internal Link** | Mengarah ke ranah web kampus: `https://bif-pwt.telkomuniversity.ac.id/kurikulum/` |
| **Outbound Link** | Mengarah ke rujukan riset/standar global dengan `target="_blank" rel="noopener noreferrer"` |
| **Panjang Artikel** | 350–480 kata berkonten teknis padat |
| **Palet Warna** | Merah Telkom (`#c53030`), Orange (`#dd6b20`), Gelap (`#0f172a`), Soft BG (`#fff5f5`/`#f8fafc`) |
| **CSS Scoping** | Terisolasi penuh di dalam `<div class="tu-editorial-container">` |

---

## 6. Panduan Publikasi ke WordPress

1. Buka dashboard WordPress `bif-pwt.telkomuniversity.ac.id/wp-admin`.
2. Masuk ke **Posts > Add New Post**.
3. Salin nilai **SEO Title** ke judul post WordPress.
4. Masukkan blok **Custom HTML** atau widget **Elementor HTML**, lalu tempel kode HTML artikel lengkap.
5. Pada metabox **Yoast SEO**:
   - Isi **Focus keyphrase**.
   - Isi **Slug URL**.
   - Isi **SEO Title** dan **Meta description**.
   - Indikator Yoast SEO otomatis menyala hijau (*All Green*).
6. Di tab panel kanan:
   - Pilih kategori (misal: *Berita*).
   - Tetapkan **Featured Image** dari Media Library.
7. Klik **Publish**.
