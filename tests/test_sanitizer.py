import unittest
from sanitizer import HTMLSanitizer

class TestHTMLSanitizer(unittest.TestCase):
    def test_strip_script_tags(self):
        malicious = '<div class="tu-editorial-container"><script>alert(1)</script><p>Text</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(malicious)
        self.assertNotIn("<script>", clean)
        self.assertIn("Stripped dangerous <script>", warnings[0])

    def test_strip_inline_event_handler(self):
        malicious = '<div class="tu-editorial-container"><img src="x" onerror="alert(1)" /><p>Text</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(malicious)
        self.assertNotIn("onerror", clean)

    def test_enforce_outbound_noopener(self):
        html = '<div class="tu-editorial-container"><a href="https://ieee.org">IEEE</a></div>'
        clean, _ = HTMLSanitizer.sanitize(html)
        self.assertIn('rel="noopener noreferrer"', clean)
        self.assertIn('target="_blank"', clean)

    def test_enforce_image_loading_lazy(self):
        html = '<div class="tu-editorial-container"><img src="https://example.com/pic.jpg" alt="pic" /></div>'
        clean, _ = HTMLSanitizer.sanitize(html)
        self.assertIn('loading="lazy"', clean)
        self.assertIn('decoding="async"', clean)


    def test_strip_iframe_and_embed(self):
        malicious = '<div class="tu-editorial-container"><iframe src="https://attacker.com"></iframe><embed src="test.swf" /><p>Safe</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(malicious)
        self.assertNotIn("<iframe", clean)
        self.assertNotIn("<embed", clean)
        self.assertIn("Safe", clean)

    def test_strip_javascript_uri(self):
        html = '<div class="tu-editorial-container"><a href="javascript:alert(1)">Click Me</a></div>'
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn("javascript:", clean)
        self.assertIn('href="#"', clean)

    def test_sanitize_svg_elements(self):
        svg_html = '<div class="tu-editorial-container"><svg viewBox="0 0 10 10"><foreignObject><script>alert(1)</script></foreignObject><circle cx="5" cy="5" r="5"/></svg></div>'
        clean, warnings = HTMLSanitizer.sanitize(svg_html)
        self.assertNotIn("<foreignObject", clean)
        self.assertNotIn("<script", clean)
        self.assertIn("<circle", clean)
        self.assertTrue(any("SVG" in w for w in warnings))

    def test_normalize_table_structure_and_strip_attributes(self):
        raw = '<div class="tu-editorial-container"><table border="1" cellpadding="5" width="100%"><tr><td>Col</td></tr></table></div>'
        clean, warnings = HTMLSanitizer.sanitize(raw)
        self.assertIn('class="tu-table"', clean)
        self.assertNotIn('border="1"', clean)
        self.assertNotIn('cellpadding="5"', clean)
        self.assertNotIn('width="100%"', clean)
        self.assertTrue(any("Normalized table structure" in w for w in warnings))

    def test_preserve_and_sandbox_whitelisted_iframe(self):
        iframe_html = '<div class="tu-editorial-container"><iframe src="https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"></iframe></div>'
        clean, warnings = HTMLSanitizer.sanitize(iframe_html)
        self.assertIn('<iframe', clean)
        self.assertIn('sandbox="allow-scripts allow-same-origin allow-presentation"', clean)
        self.assertIn('loading="lazy"', clean)
        self.assertTrue(any("Sanitized iframe embeds" in w for w in warnings))

    def test_merge_existing_rel_attributes(self):
        link_html = '<div class="tu-editorial-container"><a href="https://github.com/prodi" rel="author">Github</a></div>'
        clean, _ = HTMLSanitizer.sanitize(link_html)
        self.assertIn('rel="author noopener noreferrer"', clean)
        self.assertIn('target="_blank"', clean)

    def test_strip_data_uri_in_img_src(self):
        data_uri_html = '<div class="tu-editorial-container"><img src="data:image/png;base64,iVBORw0KGgoAAA..." alt="bloated" /></div>'
        clean, warnings = HTMLSanitizer.sanitize(data_uri_html)
        self.assertIn('src=""', clean)
        self.assertNotIn("base64", clean)
        self.assertTrue(any("data URI" in w for w in warnings))

    def test_sanitize_abbr_title_attribute(self):
        abbr_html = '<div class="tu-editorial-container"><p><abbr title="Internet <script> of Things">IoT</abbr></p></div>'
        clean, _ = HTMLSanitizer.sanitize(abbr_html)
        self.assertIn('title="Internet script of Things"', clean)
        self.assertNotIn("<script>", clean)

    def test_strip_empty_paragraphs(self):
        empty_p_html = '<div class="tu-editorial-container"><p>Paragraf isi.</p><p></p><p>&nbsp;</p><p>Paragraf kedua.</p></div>'
        clean, _ = HTMLSanitizer.sanitize(empty_p_html)
        self.assertNotIn("<p></p>", clean)
        self.assertNotIn("<p>&nbsp;</p>", clean)
        self.assertIn("<p>Paragraf isi.</p>", clean)
        self.assertIn("<p>Paragraf kedua.</p>", clean)

    def test_sanitize_malformed_table_containers(self):
        malformed_table = '<div class="tu-editorial-container"><table><p><tr><td>Cell 1</td></tr></p></table></div>'
        clean, warnings = HTMLSanitizer.sanitize(malformed_table)
        self.assertIn("<tr><td>Cell 1</td></tr>", clean)
        self.assertNotIn("<p><tr>", clean)
        self.assertTrue(any("malformed container" in w for w in warnings))

    def test_sanitize_media_sources(self):
        insecure_media = '<div class="tu-editorial-container"><video src="http://example.com/demo.mp4"></video><audio src="data:audio/mp3;base64,XYZ123"></audio></div>'
        clean, warnings = HTMLSanitizer.sanitize(insecure_media)
        self.assertIn('src="https://example.com/demo.mp4"', clean)
        self.assertIn('src=""', clean)
        self.assertTrue(any("HTTPS" in w for w in warnings))
        self.assertTrue(any("dangerous media" in w for w in warnings))


    def test_strip_tracking_pixels(self):
        tracking_html = '<div class="tu-editorial-container"><p>Konten</p><img src="https://tracker.com/pixel.gif" width="1" height="1" /><img src="https://tracker.com/beacon.gif" style="display:none" /></div>'
        clean, warnings = HTMLSanitizer.sanitize(tracking_html)
        self.assertNotIn("pixel.gif", clean)
        self.assertNotIn("beacon.gif", clean)
        self.assertTrue(any("tracking pixel" in w for w in warnings))

if __name__ == "__main__":
    unittest.main()

