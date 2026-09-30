import unittest
from parser import parse_telegram_input, parse_llm_response, clean_url, DEFAULT_PLACEHOLDER_IMG, calculate_reading_time

class TestParser(unittest.TestCase):
    def test_clean_url_with_markdown(self):
        url = "[https://example.com/image.png](https://example.com/image.png)"
        self.assertEqual(clean_url(url), "https://example.com/image.png")

    def test_clean_url_fallback(self):
        self.assertEqual(clean_url(""), DEFAULT_PLACEHOLDER_IMG)

    def test_clean_url_strips_tracking_params(self):
        url = "https://example.com/photo.jpg?utm_source=telegram&utm_medium=social&fbclid=abc123xyz&keep=true"
        cleaned = clean_url(url)
        self.assertEqual(cleaned, "https://example.com/photo.jpg?keep=true")

    def test_parse_telegram_input_numbered_bullets(self):
        raw = """Topik: Edge AI Monitoring
Tanggal: 1 Oktober 2026
Kategori: Artificial Intelligence
Image URL: https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/sample.jpg
Poin Utama:
1. Akselerasi inferensi NPU
2. Optimasi quantization int8
3. Efisiensi daya baterai
"""
        data = parse_telegram_input(raw)
        self.assertEqual(data["topik"], "Edge AI Monitoring")
        self.assertEqual(data["tanggal"], "1 Oktober 2026")
        self.assertEqual(len(data["poin_utama"]), 3)
        self.assertEqual(data["poin_utama"][0], "Akselerasi inferensi NPU")

    def test_parse_llm_response_fenced(self):
        response = """
### 1. YOAST SEO METADATA
- Focus Keyphrase: `Edge AI microcontrollers`
- SEO Title: Edge AI Microcontrollers: Komputasi Cerdas di Perangkat IoT
- Slug: `edge-ai-microcontrollers`
- Meta Description: Temukan efisiensi implementasi Edge AI microcontrollers untuk sensor cerdas hemat energi dan latensi rendah pada arsitektur modern di sini.

### 2. KODE HTML LENGKAP
```html
<div class="tu-editorial-container">
  <p>Test content</p>
</div>
```
"""
        parsed = parse_llm_response(response)
        self.assertEqual(parsed["focus_keyphrase"], "Edge AI microcontrollers")
        self.assertEqual(parsed["slug"], "edge-ai-microcontrollers")
        self.assertTrue(parsed["html_code"].startswith('<div class="tu-editorial-container">'))

    def test_extract_headings(self):
        from parser import extract_headings
        html = """
        <div class="tu-editorial-container">
            <h1>Judul Utama</h1>
            <h2>Subheading <strong>Pertama</strong></h2>
            <p>Paragraf</p>
            <h3>Sub-sub</h3>
        </div>
        """
        headings = extract_headings(html)
        self.assertEqual(len(headings), 3)
        self.assertEqual(headings[0], {"tag": "h1", "text": "Judul Utama"})
        self.assertEqual(headings[1], {"tag": "h2", "text": "Subheading Pertama"})
        self.assertEqual(headings[2], {"tag": "h3", "text": "Sub-sub"})

    def test_strip_markdown_formatting(self):
        from parser import strip_markdown_formatting
        raw = "### **Teks Tebal** dan *miring* serta `kode` dan [tautan](https://example.com)"
        cleaned = strip_markdown_formatting(raw)
        self.assertEqual(cleaned, "Teks Tebal dan miring serta kode dan tautan")

    def test_convert_markdown_table_to_html(self):
        from parser import convert_markdown_table_to_html
        md = """| Fitur | Docker | Wasm |
|---|---|---|
| Ukuran | 100MB | 2MB |"""
        html = convert_markdown_table_to_html(md)
        self.assertIn("tu-table-responsive", html)
        self.assertIn("<table class=\"tu-table\">", html)
        self.assertIn("<th>Fitur</th>", html)
        self.assertIn("<th>Docker</th>", html)
        self.assertIn("<td>100MB</td>", html)
        self.assertIn("<td>2MB</td>", html)

    def test_calculate_reading_time(self):
        short_text = "Kata " * 50
        medium_text = "Kata " * 400
        self.assertEqual(calculate_reading_time(""), "1 Menit Baca")
        self.assertEqual(calculate_reading_time(short_text), "1 Menit Baca")
        self.assertEqual(calculate_reading_time(medium_text), "2 Menit Baca")

    def test_parse_markdown_callouts(self):
        from parser import parse_markdown_callouts
        raw = """> [!NOTE]
> Ini adalah catatan editorial penting.
> Mohon diperhatikan baik-baik.
"""
        rendered = parse_markdown_callouts(raw)
        self.assertIn("tu-callout tu-callout-note", rendered)
        self.assertIn("Catatan", rendered)
        self.assertIn("Ini adalah catatan editorial penting.", rendered)

if __name__ == "__main__":
    unittest.main()
