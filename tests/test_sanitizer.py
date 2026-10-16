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

    def test_sanitize_mathml_equations(self):
        mathml_html = '<div class="tu-editorial-container"><math href="javascript:alert(1)"><annotation-xml><script>evil()</script></annotation-xml><mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow></math></div>'
        clean, warnings = HTMLSanitizer.sanitize(mathml_html)
        self.assertNotIn("href=\"javascript:", clean)
        self.assertNotIn("<script>", clean)
        self.assertIn("<mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow>", clean)
        self.assertTrue(any("MathML" in w for w in warnings))

    def test_strip_obfuscated_payloads_and_comments(self):
        blob_html = (
            '<div class="tu-editorial-container">'
            '<!-- <script>hidden_exec()</script> -->'
            '<p data-payload="' + 'A' * 90 + '">Safe text</p>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(blob_html)
        self.assertNotIn("hidden_exec", clean)
        self.assertNotIn("data-payload", clean)
        self.assertIn("Safe text", clean)
        self.assertTrue(any("obfuscated" in w or "suspicious" in w for w in warnings))

    def test_sanitize_iframe_sandbox_bypass_tokens(self):
        iframe_html = '<div class="tu-editorial-container"><iframe src="https://www.youtube.com/embed/xyz" sandbox="allow-scripts allow-top-navigation" frameborder="0"></iframe></div>'
        clean, _ = HTMLSanitizer.sanitize(iframe_html)
        self.assertNotIn("allow-top-navigation", clean)
        self.assertNotIn('frameborder="0"', clean)
        self.assertIn("allow-presentation", clean)
        self.assertIn("allow-scripts", clean)

    def test_sanitize_figure_and_figcaption(self):
        fig_html = '<div class="tu-editorial-container"><figure><img src="https://example.com/demo.jpg" alt="demo" /><figcaption>Laboratorium IoT</figcaption></figure></div>'
        clean, warnings = HTMLSanitizer.sanitize(fig_html)
        self.assertIn('<figure class="tu-figure">', clean)
        self.assertIn('<figcaption class="tu-figcaption">', clean)
        self.assertTrue(any("figure and figcaption" in w for w in warnings))

    def test_strip_unsafe_custom_data_attributes(self):
        payload_html = '<div class="tu-editorial-container"><p data-payload-action="javascript:alert(1)" data-extra="data:text/html,<script>eval()</script>">Aman</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(payload_html)
        self.assertNotIn("javascript:alert", clean)
        self.assertNotIn("data-payload-action", clean)
        self.assertNotIn("data-extra", clean)
        self.assertIn("Aman", clean)
        self.assertTrue(any("dangerous executable payload" in w for w in warnings))

    def test_enforce_media_controls_and_preload(self):
        media_html = '<div class="tu-editorial-container"><video src="https://example.com/demo.mp4" autoplay></video></div>'
        clean, warnings = HTMLSanitizer.sanitize(media_html)
        self.assertIn('controls', clean)
        self.assertIn('preload="metadata"', clean)
        self.assertNotIn('autoplay', clean)
        self.assertTrue(any("autoplay" in w for w in warnings))

    def test_sanitize_details_and_summary(self):
        det_html = '<div class="tu-editorial-container"><details><summary>Panduan Praktikum</summary><p>Isi panduan.</p></details></div>'
        clean, warnings = HTMLSanitizer.sanitize(det_html)
        self.assertIn('<details class="tu-details">', clean)
        self.assertIn('<summary class="tu-summary">', clean)
        self.assertTrue(any("details and summary" in w for w in warnings))

    def test_strip_unsafe_meta_refresh_and_base(self):
        bad_html = '<div class="tu-editorial-container"><meta http-equiv="refresh" content="0;url=https://evil.com"><base href="https://evil.com"><p>Konten</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(bad_html)
        self.assertNotIn("<meta", clean)
        self.assertNotIn("<base", clean)
        self.assertIn("Konten", clean)
        self.assertTrue(any("meta refresh" in w for w in warnings))

    def test_neutralize_unsafe_form_elements(self):
        form_html = '<div class="tu-editorial-container"><form action="https://phishing.com"><input type="text" name="pwd"><textarea></textarea></form></div>'
        clean, warnings = HTMLSanitizer.sanitize(form_html)
        self.assertNotIn("<form", clean)
        self.assertNotIn("</form>", clean)
        self.assertIn("disabled", clean)
        self.assertTrue(any("interactive form" in w for w in warnings))

    def test_sanitize_dialog_element(self):
        dia_html = '<div class="tu-editorial-container"><dialog open><p>Modal pengumuman akademik.</p></dialog></div>'
        clean, warnings = HTMLSanitizer.sanitize(dia_html)
        self.assertIn('<dialog open class="tu-dialog">', clean)
        self.assertIn("Modal pengumuman akademik.", clean)
        self.assertTrue(any("dialog elements" in w for w in warnings))

    def test_strip_svg_animation_tags(self):
        svg_html = (
            '<div class="tu-editorial-container"><svg viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="40"/>'
            '<animate attributeName="r" from="40" to="20" dur="1s"/>'
            '<set attributeName="fill" to="red"/>'
            '</svg></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(svg_html)
        self.assertNotIn("<animate", clean)
        self.assertNotIn("<set", clean)
        self.assertIn("<circle", clean)
        self.assertTrue(any("animation or embedded font" in w for w in warnings))

    def test_sanitize_picture_and_source(self):
        pic_html = (
            '<div class="tu-editorial-container"><picture>'
            '<source srcset="http://cdn.example.com/hero.webp" type="image/webp">'
            '<img src="https://cdn.example.com/hero.jpg" alt="Hero">'
            '</picture></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(pic_html)
        self.assertIn('<picture class="tu-picture">', clean)
        self.assertIn('srcset="https://cdn.example.com/hero.webp"', clean)
        self.assertTrue(any("picture containers" in w for w in warnings))

    def test_sanitize_track_subtitle_elements(self):
        video_html = (
            '<div class="tu-editorial-container"><video src="https://example.com/lecture.mp4">'
            '<track src="http://example.com/sub.vtt" kind="captions" srclang="id">'
            '<track src="javascript:alert(1)" kind="invalid_kind">'
            '</video></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(video_html)
        self.assertIn('src="https://example.com/sub.vtt"', clean)
        self.assertIn('kind="captions"', clean)
        self.assertNotIn('src="javascript:alert(1)"', clean)
        self.assertIn('kind="subtitles"', clean)
        self.assertTrue(any("track subtitle" in w for w in warnings))

    def test_strip_svg_feimage_external_payload(self):
        svg_html = (
            '<div class="tu-editorial-container"><svg>'
            '<filter id="blur"><feImage xlink:href="https://attacker.com/evil.svg"/></filter>'
            '</svg></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(svg_html)
        self.assertNotIn('xlink:href="https://attacker.com/evil.svg"', clean)
        self.assertTrue(any("SVG feImage" in w for w in warnings))

    def test_sanitize_template_and_slot_elements(self):
        bad_html = (
            '<div class="tu-editorial-container">'
            '<template shadowroot="open"><p>Shadow DOM Injected</p></template>'
            '<slot name="custom-slot"></slot>'
            '<p>Konten Sah</p>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(bad_html)
        self.assertNotIn('<template', clean)
        self.assertNotIn('Shadow DOM Injected', clean)
        self.assertNotIn('<slot', clean)
        self.assertIn('Konten Sah', clean)
        self.assertTrue(any("template and slot" in w for w in warnings))

    def test_sanitize_canvas_fallback_and_attributes(self):
        canvas_html = (
            '<div class="tu-editorial-container">'
            '<canvas width="600" height="400" context="webgl" oncontextlost="evil()">'
            '<p>Browser Anda tidak mendukung canvas rendering.</p>'
            '</canvas></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(canvas_html)
        self.assertIn('<canvas width="600" height="400">', clean)
        self.assertNotIn('context="webgl"', clean)
        self.assertNotIn('oncontextlost', clean)
        self.assertIn('Browser Anda tidak mendukung canvas', clean)
        self.assertTrue(any("canvas element" in w for w in warnings))

    def test_sanitize_ruby_annotation_markup(self):
        ruby_html = (
            '<div class="tu-editorial-container">'
            '<ruby onclick="evil()">明日 <rp>(</rp><rt>Ashita</rt><rp>)</rp></ruby>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(ruby_html)
        self.assertIn('<ruby>', clean)
        self.assertNotIn('onclick', clean)
        self.assertIn('<rt>Ashita</rt>', clean)
        self.assertTrue(any("ruby annotation" in w for w in warnings))

    def test_neutralize_mathml_script_links(self):
        math_html = (
            '<div class="tu-editorial-container"><math>'
            '<mi href="javascript:steal()">x</mi>'
            '<mo>+</mo><mn>2</mn>'
            '</math></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(math_html)
        self.assertNotIn('javascript:steal()', clean)
        self.assertIn('<mi>x</mi>', clean)
        self.assertTrue(any("script link inside MathML" in w for w in warnings))

    def test_sanitize_dialog_modal_events(self):
        html = '<div class="tu-editorial-container"><dialog autofocus onclose="alert(1)"><p>Modal dialog</p></dialog></div>'
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('<dialog class="tu-dialog">', clean)
        self.assertNotIn('autofocus', clean)
        self.assertNotIn('onclose', clean)
        self.assertTrue(any("dialog modal" in w for w in warnings))

    def test_sanitize_details_summary_ontoggle(self):
        html = '<div class="tu-editorial-container"><details ontoggle="doBadThing()"><summary onclick="hack()">Klik</summary><p>Detail info</p></details></div>'
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('<details class="tu-details">', clean)
        self.assertIn('<summary class="tu-summary">', clean)
        self.assertNotIn('ontoggle', clean)
        self.assertNotIn('onclick', clean)

    def test_sanitize_slot_prototype_pollution(self):
        html = '<div class="tu-editorial-container"><span slot="__proto__">Payload</span><p slot="valid-slot">Aman</p></div>'
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('slot="__proto__"', clean)
        self.assertIn('slot="valid-slot"', clean)
        self.assertTrue(any("slot attribute" in w for w in warnings))

    def test_sanitize_meter_and_progress_elements(self):
        html = (
            '<div class="tu-editorial-container">'
            '<meter value="75" min="0" max="100" form="login_form" onchange="steal()">75%</meter>'
            '<progress value="invalid" max="100"></progress>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('<meter value="75" min="0" max="100">', clean)
        self.assertNotIn('form="login_form"', clean)
        self.assertNotIn('onchange', clean)
        self.assertIn('<progress value="0" max="100">', clean)
        self.assertTrue(any("meter and progress" in w for w in warnings))

    def test_sanitize_picture_source_responsive_markup(self):
        html = (
            '<div class="tu-editorial-container"><picture>'
            '<source srcset="javascript:alert(1)" media="(min-width: 800px)">'
            '<source srcset="/images/hero.webp" media="(min-width: 600px)" onload="run()">'
            '<img src="/images/hero.jpg" alt="Hero">'
            '</picture></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('srcset="javascript:alert(1)"', clean)
        self.assertNotIn('onload="run()"', clean)
        self.assertIn('srcset="/images/hero.webp"', clean)
        self.assertTrue(any("picture and source" in w for w in warnings))

    def test_sanitize_theme_attributes(self):
        html = (
            '<div class="tu-editorial-container">'
            '<div data-theme="dark" data-mode="evil:javascript:void(0)">Konten Dark</div>'
            '<section data-color-scheme="telkom-red">Telkom Theme</section>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('data-theme="dark"', clean)
        self.assertNotIn('data-mode="evil:javascript:void(0)"', clean)
        self.assertIn('data-color-scheme="telkom-red"', clean)
        self.assertTrue(any("data-theme/mode" in w for w in warnings))

    def test_sanitize_audio_track_elements(self):
        html = (
            '<div class="tu-editorial-container">'
            '<audio src="https://example.com/lecture.mp3" autoplay onplay="steal()">'
            '<track kind="unknown-format" src="javascript:alert(1)">'
            '</audio>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('autoplay', clean)
        self.assertNotIn('onplay="steal()"', clean)
        self.assertIn('controls', clean)
        self.assertIn('class="tu-audio"', clean)
        self.assertNotIn('src="javascript:alert(1)"', clean)
        self.assertIn('kind="subtitles"', clean)
        self.assertTrue(any("audio and track" in w for w in warnings))

    def test_sanitize_kbd_samp_elements(self):
        html = (
            '<div class="tu-editorial-container">'
            '<p>Tekan <kbd onclick="evil()"><kbd>Ctrl</kbd>+<kbd>C</kbd></kbd> untuk salin.</p>'
            '<samp style="color:red;" contenteditable="true">Output: 200 OK</samp>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('onclick="evil()"', clean)
        self.assertNotIn('contenteditable="true"', clean)
        self.assertNotIn('style="color:red;"', clean)
        self.assertIn('<kbd><kbd>Ctrl</kbd>+<kbd>C</kbd></kbd>', clean)
        self.assertIn('<samp>Output: 200 OK</samp>', clean)
        self.assertTrue(any("kbd and samp" in w for w in warnings))

    def test_sanitize_tooltip_placement_attributes(self):
        html = (
            '<div class="tu-editorial-container">'
            '<button data-placement="diagonal-down" data-tooltip="<b>Klik</b> & info">Hover</button>'
            '<span data-placement="bottom" data-title="Penjelasan singkat">Info</span>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('data-placement="top"', clean)
        self.assertIn('data-placement="bottom"', clean)
        self.assertNotIn('<b>Klik</b>', clean)
        self.assertIn('data-tooltip="Klik & info"', clean)
        self.assertIn('data-title="Penjelasan singkat"', clean)
        self.assertTrue(any("contextual tooltip" in w for w in warnings))

    def test_sanitize_source_media_breakpoint_attributes(self):
        html = (
            '<div class="tu-editorial-container"><picture>'
            '<source srcset="/img/large.webp" media="(min-width: 1024px)">'
            '<source srcset="/img/bad.webp" media="javascript:alert(1)">'
            '<source srcset="/img/evil.webp" media="expression(body.scrollLeft)">'
            '<img src="/img/fallback.jpg" alt="Responsive">'
            '</picture></div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('media="(min-width: 1024px)"', clean)
        self.assertNotIn('javascript:alert', clean)
        self.assertNotIn('expression(', clean)
        self.assertTrue(any("source media query" in w for w in warnings))

    def test_sanitize_dialog_and_dialog_form(self):
        html = (
            '<div class="tu-editorial-container">'
            '<dialog open onclose="steal()" style="position:fixed;">'
            '<button formmethod="dialog" formaction="javascript:leak()" onclick="leak()">Tutup</button>'
            '</dialog>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('onclose="steal()"', clean)
        self.assertNotIn('style="position:fixed;"', clean)
        self.assertNotIn('formaction="javascript:leak()"', clean)
        self.assertNotIn('onclick="leak()"', clean)
        self.assertIn('formaction="#"', clean)
        self.assertIn('formmethod="dialog"', clean)
        self.assertTrue(any("dialog modal" in w for w in warnings))

    def test_sanitize_data_filter_sort_attributes(self):
        html = (
            '<div class="tu-editorial-container">'
            '<table data-sort="asc" data-filter="semester-5, kurikulum-2024">'
            '<tr data-category="<script>alert(1)</script>pilihan">'
            '<td data-filter="javascript:exploit()">Mata Kuliah</td>'
            '</tr>'
            '</table>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('data-sort="asc"', clean)
        self.assertIn('data-filter="semester-5, kurikulum-2024"', clean)
        self.assertNotIn('<script>', clean)
        self.assertIn('data-category="pilihan"', clean)
        self.assertNotIn('javascript:exploit()', clean)
        self.assertTrue(any("tabular data-filter" in w for w in warnings))

    def test_sanitize_svg_use_xlink_href(self):
        html = (
            '<div class="tu-editorial-container">'
            '<svg viewBox="0 0 100 100">'
            '<use xlink:href="https://attacker.com/sprite.svg#icon" />'
            '<use href="javascript:alert(1)" />'
            '<use href="#safe-local-symbol" />'
            '</svg>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertNotIn('https://attacker.com/sprite.svg#icon', clean)
        self.assertNotIn('javascript:alert(1)', clean)
        self.assertIn('href="#safe-local-symbol"', clean)
        self.assertTrue(any("SVG use" in w for w in warnings))

    def test_sanitize_html5_time_datetime_microdata(self):
        html = (
            '<div class="tu-editorial-container">'
            '<time datetime="2026-10-16T09:00:00" itemprop="startDate">16 Oktober 2026</time>'
            '<time datetime="javascript:steal()">Invalid Date</time>'
            '<time datetime="2026-10-16" itemprop="javascript:exploit()">Safe Date</time>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('datetime="2026-10-16T09:00:00"', clean)
        self.assertNotIn('datetime="javascript:steal()"', clean)
        self.assertNotIn('itemprop="javascript:exploit()"', clean)
        self.assertTrue(any("time datetime" in w or "microdata" in w for w in warnings))

    def test_sanitize_html5_output_calculation_elements(self):
        html = (
            '<div class="tu-editorial-container">'
            '<output name="snr_result" for="noise_val signal_val">24.5 dB</output>'
            '<output name="bad name()" for="a b payload:evil()" onclick="steal()">Result</output>'
            '</div>'
        )
        clean, warnings = HTMLSanitizer.sanitize(html)
        self.assertIn('name="snr_result"', clean)
        self.assertIn('for="noise_val signal_val"', clean)
        self.assertNotIn('bad name()', clean)
        self.assertNotIn('payload:evil()', clean)
        self.assertNotIn('onclick="steal()"', clean)
        self.assertTrue(any("output calculation" in w for w in warnings))



if __name__ == "__main__":
    unittest.main()




