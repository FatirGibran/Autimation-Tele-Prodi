# Automation Tele Prodi (Editorial Specialist Bot)

Sistem otomasi produksi artikel berita dan riset mingguan Program Studi S1 Teknik Informatika Telkom University Purwokerto (`bif-pwt.telkomuniversity.ac.id`), dirancang untuk menghasilkan kode HTML siap tempel ke widget Custom HTML Elementor serta metadata Yoast SEO dengan skor hijau (*All Green*).

---

## 1. Arsitektur dan Skema Alur Kerja

```
[Telegram User] 
       │ (Kirim: Topik + Gambar + Tanggal + Poin Utama)
       ▼
[Telegram Bot Service] (bot.py)
       │ 
       ▼
[LLM Engine] (Gemini 2.5 Flash / Antigravity Engine)
       │  ├── Injeksi Master System Prompt (prompts/system_prompt.md)
       │  └── Validasi Standar Desain & SEO Kampus
       ▼
[Response Parser & Validator] (parser.py)
       │  ├── Ekstraksi Metadata Yoast SEO (Title, Slug, Keyphrase, Meta Desc)
       │  └── Verifikasi Batas Karakter & Kontras Desain
       ▼
[Telegram Bot Output]
       │  ├── Output 1: Yoast SEO Metadata Markdown
       │  └── Output 2: File .html Lengkap Siap Pakai
       ▼
[WordPress WP-Admin (bif-pwt.telkomuniversity.ac.id)]
       ├── Panel Yoast SEO: Input Keyphrase, SEO Title, Slug, Meta Description
       └── Post Editor: Tempel Kode ke Widget Custom HTML / Elementor HTML
```

---

## 2. Struktur Repositori

```
Autimation Tele Prodi/
├── .env.example                                      # Contoh konfigurasi kredensial bot & API
├── .gitignore                                        # Rule pengabaian file Git
├── README.md                                         # Dokumentasi teknis & operasional
├── bot.py                                            # Telegram bot handler & workflow engine
├── parser.py                                         # Regex parser payload input & output validator
├── requirements.txt                                  # Dependensi pustaka Python
├── prompts/
│   └── system_prompt.md                             # Master system prompt editorial Telkom University
└── articles/
    ├── 2026-09-28-webassembly-edge-computing-iot.html # Output artikel HTML siap terbit
    └── 2026-09-28-webassembly-edge-computing-iot-metadata.json # Metadata Yoast SEO tervalidasi
```

---

## 3. Format Pesan Pemicu (Telegram Trigger)

Gunakan struktur teks berikut saat mengirim permintaan artikel ke bot Telegram:

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

## 4. Standar Desain & Yoast SEO

| Parameter | Aturan Standar |
| :--- | :--- |
| **Focus Keyphrase** | 3–5 kata spesifik, muncul di awal Title, Paragraf 1, H2, Alt Gambar, Slug, dan Meta Description |
| **Meta Description** | Tepat 140–156 karakter, persuasif, memuat Focus Keyphrase |
| **Internal Link** | Wajib mengarah ke domain kampus: `https://bif-pwt.telkomuniversity.ac.id/kurikulum/` |
| **Outbound Link** | Mengarah ke referensi global terverifikasi (`bytecodealliance.org`, `ieee.org`, dll.) dengan `target="_blank" rel="noopener noreferrer"` |
| **Panjang Artikel** | 350–480 kata berkonten teknis padat |
| **Palet Warna** | Merah Telkom (`#c53030`), Orange (`#dd6b20`), Gelap (`#0f172a`), Soft BG (`#fff5f5`/`#f8fafc`) |
| **CSS Scoping** | Terisolasi penuh di dalam `<div class="tu-editorial-container">` |

---

## 5. Panduan Publikasi ke WordPress

1. Buka dashboard WordPress `bif-pwt.telkomuniversity.ac.id/wp-admin`.
2. Masuk ke menu **Posts > Add New Post**.
3. Salin nilai **SEO Title** ke kolom judul postingan utama.
4. Tambahkan blok **Custom HTML** atau buka widget **Elementor HTML**, lalu salin seluruh isi file HTML artikel ke dalamnya.
5. Pada panel metabox **Yoast SEO**:
   - Salin **Focus keyphrase**.
   - Salin **Slug URL**.
   - Salin **SEO Title** dan **Meta description**.
   - Pastikan indikator Yoast SEO menyala hijau (*All Green*).
6. Pada panel samping kanan:
   - Pilih kategori (misal: *Berita* atau *Artikel Ilmiah*).
   - Tetapkan **Featured Image** dari Media Library agar thumbnail pada halaman utama `/berita-dan-artikel/` tampil presisi.
7. Klik **Publish**.

---

## 6. Instalasi & Menjalankan Bot Lokal

1. Pasang dependensi pustaka:
   ```bash
   pip install -r requirements.txt
   ```
2. Buat file `.env` dari salinan `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Isi token Telegram dan Google Gemini API:
   ```env
   TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   GEMINI_API_KEY="your_gemini_api_key"
   ```
4. Jalankan bot:
   ```bash
   python bot.py
   ```
