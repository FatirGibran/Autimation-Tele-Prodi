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

if __name__ == "__main__":
    unittest.main()
