# API & Payload Integration Specification

Dokumentasi spesifikasi teknis format data pemicu (input payload) dan skema respons dari bot otomasi editorial S1 Teknik Informatika Telkom University Purwokerto.

---

## 1. Input Trigger Payload (Telegram / CLI)

Format pesan teks yang diparsing oleh `parser.py`:

```text
Topik: [Judul Topik Berita / Riset]
Tanggal: [Tanggal Terbit Aktual, format: DD Bulan YYYY]
Kategori: [Kategori Berita, default: Cloud & Edge Computing]
Image URL: [URL gambar featured]
Poin Utama:
- [Poin Utama 1]
- [Poin Utama 2]
- [Poin Utama 3]
```

### Aturan Ekstraksi:
- **Image URL**: Mendukung URL polos (`https://...`) atau format tautan markdown (`[text](https://...)`). Jika kosong, otomatis diisi dengan URL placeholder baku kampus.
- **Poin Utama**: Mendukung penomoran angka (`1.`), strip (`-`), asterik (`*`), atau bullet (`•`).

---

## 2. Output Schema (Yoast SEO Metadata)

Respons metadata Yoast SEO yang dihasilkan:

```json
{
  "focus_keyphrase": "WebAssembly edge computing IoT",
  "seo_title": "WebAssembly Edge Computing IoT: Solusi Cerdas Perangkat Mikro",
  "slug": "webassembly-edge-computing-iot",
  "meta_description": "Pelajari implementasi WebAssembly edge computing IoT untuk perangkat berdaya rendah, isolasi sandbox memori, serta riset monitoring smart village di sini.",
  "meta_description_char_count": 154
}
```

---

## 3. WordPress REST API Mapping

Jika integrasi otomatis aktif (`WP_USERNAME` dan `WP_APP_PASSWORD` terisi di `.env`), bot mengirimkan request `POST /wp-json/wp/v2/posts` dengan payload:

| Field WordPress | Sumber Data Bot | Keterangan |
| :--- | :--- | :--- |
| `title` | `seo_title` | Judul artikel |
| `content` | `html_code` | HTML terisolasi di dalam `.tu-editorial-container` |
| `slug` | `slug` | Slug URL tervalidasi |
| `status` | `draft` | Draft awal untuk peninjauan redaksi |
| `meta._yoast_wpseo_focuskw` | `focus_keyphrase` | Focus keyphrase Yoast SEO |
| `meta._yoast_wpseo_title` | `seo_title` | SEO Title Yoast |
| `meta._yoast_wpseo_metadesc` | `meta_description` | Meta description Yoast |
