# Katalog Komponen HTML Elementor (Editorial S1 Teknik Informatika)

Katalog komponen semantik HTML dan CSS terisolasi (`components.py`) yang siap disalin langsung ke widget Custom HTML Elementor pada WordPress Program Studi S1 Teknik Informatika Telkom University Purwokerto (`bif-pwt.telkomuniversity.ac.id`).

Semua komponen dibungkus di dalam kelas induk `.tu-editorial-container` agar CSS tidak bentrok dengan tema WordPress atau gaya default Elementor.

---

## 1. Hero Header (`render_hero`)

Menampilkan kategori topik, tanggal terbit, estimasi waktu baca, judul artikel (H1), dan paragraf pembuka (*lead paragraph*).

```html
<header class="tu-hero-header">
  <div class="tu-badge-wrap">
    <span class="tu-badge">Kategori</span>
    <span class="tu-meta-info">28 September 2026 &bull; 4 Menit Baca</span>
  </div>
  <h1 class="tu-article-title">Judul Artikel Lengkap</h1>
  <p class="tu-lead-paragraph">Paragraf pengantar artikel dengan bobot font 500 dan kontras tinggi.</p>
</header>
```

---

## 2. Gambar Utama & Keterangan (`render_figure`)

Menampilkan gambar beresolusi tinggi dengan penegakan otomatis atribut performa (`loading="lazy"`, `decoding="async"`, `alt`, serta `figcaption`).

```html
<figure class="tu-figure">
  <img src="https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/sample.jpg" alt="Deskripsi gambar" loading="lazy" decoding="async" />
  <figcaption class="tu-figcaption">Keterangan visual: Arsitektur node edge berbasis WebAssembly.</figcaption>
</figure>
```

---

## 3. Grid Komparasi Solusi (`render_comparison_grid`)

Membandingkan pendekatan konvensional (*legacy*) dengan pendekatan modern secara visual berdampingan pada layar desktop dan responsif turun ke 1 kolom pada ponsel.

```html
<div class="tu-comparison-grid">
  <div class="tu-card-col legacy">
    <h3>Pendekatan Konvensional</h3>
    <ul>
      <li>Ukuran binary besar (> 100 MB)</li>
      <li>Cold start lambat (> 500 ms)</li>
    </ul>
  </div>
  <div class="tu-card-col modern">
    <h3>Pendekatan Modern (Wasm)</h3>
    <ul>
      <li>Ukuran binary ringkas (< 2 MB)</li>
      <li>Cold start instan (< 5 ms)</li>
    </ul>
  </div>
</div>
```

---

## 4. Kartu Poin Kunci (`render_key_takeaways`)

Menyorot kesimpulan penting atau intisari riset dengan aksen warna hijau emerald lembut.

```html
<div class="tu-takeaways-card">
  <h3>Poin-Poin Kunci</h3>
  <ul>
    <li>Isolasi memori linier menjamin keamanan di node edge.</li>
    <li>Efisiensi energi sensor meningkat hingga 40%.</li>
  </ul>
</div>
```

---

## 5. Grid Metrik & Statistik Riset (`render_stat_grid`)

Menampilkan angka capaian riset atau tolok ukur performa dalam tata letak kartu berbasis grid.

```html
<div class="tu-stat-grid">
  <div class="tu-stat-card">
    <div class="tu-stat-number">95%</div>
    <div class="tu-stat-label">Efisiensi Memori</div>
  </div>
  <div class="tu-stat-card">
    <div class="tu-stat-number">10x</div>
    <div class="tu-stat-label">Kecepatan Cold Start</div>
  </div>
</div>
```

---

## 6. Akordion Tanya Jawab (`render_faq_accordion`)

Menggunakan elemen semantik `<details>` dan `<summary>` standar HTML5 tanpa dependensi pustaka JavaScript tambahan.

```html
<h2>Pertanyaan Umum (FAQ)</h2>
<div class="tu-faq-wrap">
  <details class="tu-faq-item">
    <summary class="tu-faq-question">Apa itu WebAssembly?</summary>
    <div class="tu-faq-answer">WebAssembly adalah format instruksi biner tingkat rendah portabel.</div>
  </details>
  <details class="tu-faq-item">
    <summary class="tu-faq-question">Apakah aman untuk IoT?</summary>
    <div class="tu-faq-answer">Sangat aman berkat model memori linier yang terisolasi dalam sandbox.</div>
  </details>
</div>
```

---

## 7. Blok Cuplikan Kode (`render_code_block`)

Wadah kode program dengan latar gelap, indikator bahasa pemrograman, dan penanganan sanitasi entitas karakter.

```html
<div class="tu-code-container">
  <div class="tu-code-header">
    <span>sensor_module.rs</span>
    <span class="tu-code-badge">rust</span>
  </div>
  <pre class="tu-code-body"><code>fn main() {
    println!("WebAssembly on Edge IoT");
}</code></pre>
</div>
```

---

## 8. Tabel Responsif (`convert_markdown_table_to_html`)

Tabel data teknis yang terbungkus container `.tu-table-responsive` untuk navigasi horizontal pada perangkat seluler.

```html
<div class="tu-table-responsive">
  <table class="tu-table">
    <thead>
      <tr>
        <th>Metrik</th>
        <th>Docker Container</th>
        <th>WebAssembly (Wasm)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Ukuran Modul</td>
        <td>120 MB</td>
        <td>1.8 MB</td>
      </tr>
      <tr>
        <td>Waktu Booting</td>
        <td>450 ms</td>
        <td>4.2 ms</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 9. Blok Sitasi & Referensi Ilmiah (`render_references_block`)

Daftar pustaka bernomor terstruktur untuk publikasi jurnal, prosiding seminar, dan dokumen standar resmi.

```html
<section class="tu-references-box">
  <h3>Referensi &amp; Publikasi Terkait</h3>
  <ol class="tu-references-list">
    <li>Haas, A. et al. (2017). Bringing the Web up to Speed with WebAssembly. ACM SIGPLAN.</li>
    <li>World Wide Web Consortium (W3C). WebAssembly Core Specification.</li>
  </ol>
</section>
```

---

## 10. Profil Penulis Riset (`render_author_card`)

Informasi profil dosen atau mahasiswa pengkaji riset beserta bidang keahlian.

```html
<div class="tu-author-card">
  <div class="tu-author-info">
    <h4>Dr. Budi Santoso, S.T., M.Kom.</h4>
    <p class="tu-author-role">Dosen Riset IoT &amp; Komputasi Terdistribusi</p>
    <p class="tu-author-bio">Fokus riset pada integrasi smart village dan optimasi sensor berdaya rendah.</p>
  </div>
</div>
```

---

## 11. Penutup & Hak Cipta Artikel (`render_footer`)

Kotak rangkuman akhir artikel dengan atribusi resmi Program Studi.

```html
<footer class="tu-footer-box">
  <h3>Kesimpulan &amp; Rekomendasi</h3>
  <p>Penerapan WebAssembly membuka peluang baru arsitektur komputasi hemat energi di kampus dan industri.</p>
  <div class="tu-footer-meta">
    Dipublikasikan oleh Tim Editorial &amp; Riset S1 Teknik Informatika Telkom University Purwokerto.
  </div>
</footer>
```
