import re
from typing import Tuple, List

ALLOWED_TAGS = {
    "div", "style", "article", "header", "section", "figure", "figcaption",
    "footer", "h1", "h2", "h3", "h4", "p", "a", "img", "ul", "ol", "li",
    "span", "strong", "em", "code", "pre", "blockquote", "details", "summary", "dialog",
    "table", "thead", "tbody", "tr", "th", "td", "abbr", "dfn", "mark", "kbd", "samp", "sub", "sup",
    "svg", "path", "g", "circle", "rect", "line", "polygon", "polyline",
    "video", "audio", "source", "picture", "track", "canvas",
    "math", "mrow", "mi", "mo", "mn", "msup", "msub", "mfrac", "msqrt", "mroot", "mtext",
    "ruby", "rt", "rp", "rb", "rtc",
    "meter", "progress", "data", "template"
}



DISALLOWED_ATTR_PREFIXES = ("on", "javascript:")

class HTMLSanitizer:
    @classmethod
    def sanitize(cls, html_content: str) -> Tuple[str, List[str]]:
        warnings: List[str] = []
        cleaned = html_content.strip()

        # 1. Ensure root wrapper exists
        if not cleaned.startswith('<div class="tu-editorial-container">'):
            if '<div class="tu-editorial-container">' in cleaned:
                # Extract starting from the wrapper
                start_idx = cleaned.find('<div class="tu-editorial-container">')
                end_idx = cleaned.rfind('</div>') + 6
                cleaned = cleaned[start_idx:end_idx]
            else:
                warnings.append("Missing root .tu-editorial-container; auto-wrapping.")
                cleaned = f'<div class="tu-editorial-container">\n{cleaned}\n</div>'

        # 1b. Normalize table structures and strip obsolete presentation attributes
        if "<table" in cleaned.lower():
            def fix_table(match):
                tag = match.group(0)
                # Strip legacy attributes: border, cellpadding, cellspacing, width, bgcolor
                tag = re.sub(r'\s+(border|cellpadding|cellspacing|width|bgcolor)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-table">'
                elif 'tu-table' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-table"', tag)
                return tag
            cleaned = re.sub(r'<table[^>]*>', fix_table, cleaned, flags=re.IGNORECASE)
            warnings.append("Normalized table structure and stripped presentational attributes.")

            # Strip stray paragraph or div containers wrapping table rows
            if re.search(r'<table[^>]*>[\s\S]*?<(?:p|div|span)>\s*<tr', cleaned, re.IGNORECASE):
                cleaned = re.sub(r'(<table[^>]*>|<tbody[^>]*>|<thead[^>]*>)\s*<(?:p|div|span)>\s*(<tr)', r'\1\2', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'(</tr>)\s*</(?:p|div|span)>\s*(</tbody[^>]*>|</table[^>]*>)', r'\1\2', cleaned, flags=re.IGNORECASE)
                warnings.append("Sanitized malformed container tags inside table structure.")

        # 1c. Sanitize figure and figcaption elements with strict editorial classes
        if "<figure" in cleaned.lower() or "<figcaption" in cleaned.lower():
            def fix_figure(match):
                tag = match.group(0)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-figure">'
                elif 'tu-figure' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-figure"', tag)
                return tag

            def fix_figcaption(match):
                tag = match.group(0)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-figcaption">'
                elif 'tu-figcaption' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-figcaption"', tag)
                return tag

            fig_before = cleaned
            cleaned = re.sub(r'<figure\b[^>]*>', fix_figure, cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'<figcaption\b[^>]*>', fix_figcaption, cleaned, flags=re.IGNORECASE)
            if cleaned != fig_before:
                warnings.append("Sanitized figure and figcaption elements with editorial class attributes.")

        # 1d. Sanitize details and summary disclosure elements with editorial classes and strip ontoggle/event handlers
        if "<details" in cleaned.lower() or "<summary" in cleaned.lower():
            def fix_details(match):
                tag = match.group(0)
                tag = re.sub(r'\s+ontoggle=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-details">'
                elif 'tu-details' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-details"', tag)
                return tag

            def fix_summary(match):
                tag = match.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-summary">'
                elif 'tu-summary' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-summary"', tag)
                return tag

            det_before = cleaned
            cleaned = sanitize_html5_details_summary_elements(cleaned)
            cleaned = re.sub(r'<details\b[^>]*>', fix_details, cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'<summary\b[^>]*>', fix_summary, cleaned, flags=re.IGNORECASE)
            if cleaned != det_before:
                warnings.append("Sanitized details and summary disclosure elements and stripped event attributes.")

        # 1e. Sanitize HTML5 dialog and modal elements with editorial classes
        if "<dialog" in cleaned.lower():
            def fix_dialog(match):
                tag = match.group(0)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-dialog">'
                elif 'tu-dialog' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-dialog"', tag)
                return tag

            dia_before = cleaned
            cleaned = re.sub(r'<dialog\b[^>]*>', fix_dialog, cleaned, flags=re.IGNORECASE)
            if cleaned != dia_before:
                warnings.append("Sanitized dialog elements with editorial class attributes.")

        # 1f. Sanitize picture responsive art-direction containers
        if "<picture" in cleaned.lower():
            def fix_picture(match):
                tag = match.group(0)
                if 'class=' not in tag:
                    tag = tag.rstrip(">") + ' class="tu-picture">'
                elif 'tu-picture' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-picture"', tag)
                return tag

            pic_before = cleaned
            cleaned = re.sub(r'<picture\b[^>]*>', fix_picture, cleaned, flags=re.IGNORECASE)
            if cleaned != pic_before:
                warnings.append("Sanitized picture containers with editorial class attributes.")





        # 2. Strip dangerous script, object, and embed tags; sanitize/whitelist educational iframes
        if "<script" in cleaned.lower():
            warnings.append("Stripped dangerous <script> tag from HTML.")
            cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

        # Remove object and embed tags entirely
        if re.search(r"<(object|embed)", cleaned, re.IGNORECASE):
            warnings.append("Stripped dangerous embedded tags (object/embed).")
            cleaned = re.sub(r"<(object|embed)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r"<(object|embed)[^>]*/>", "", cleaned, flags=re.IGNORECASE)

        # Filter iframes: allow only whitelisted educational domains with strict sandbox
        ALLOWED_IFRAME_HOSTS = ("youtube.com", "youtube-nocookie.com", "youtu.be", "vimeo.com", "drive.google.com")
        if "<iframe" in cleaned.lower():
            def filter_iframe(match):
                tag = match.group(0)
                src_match = re.search(r'src=["\'](https?://[^"\']+)["\']', tag, re.IGNORECASE)
                if not src_match:
                    return ""
                src_url = src_match.group(1).lower()
                if any(host in src_url for host in ALLOWED_IFRAME_HOSTS):
                    open_tag_m = re.match(r'<iframe\b[^>]*>', tag, re.IGNORECASE)
                    tag_open = open_tag_m.group(0) if open_tag_m else tag
                    if 'sandbox=' in tag_open:
                        sb_match = re.search(r'sandbox=["\']([^"\']*)["\']', tag_open, re.IGNORECASE)
                        if sb_match:
                            tokens = set(sb_match.group(1).lower().split())
                            tokens.discard("allow-top-navigation")
                            tokens.discard("allow-top-navigation-by-user-activation")
                            tokens.discard("allow-pointer-lock")
                            tokens.add("allow-scripts")
                            tokens.add("allow-same-origin")
                            tokens.add("allow-presentation")
                            tag_open = re.sub(r'sandbox=["\'][^"\']*["\']', f'sandbox="{" ".join(sorted(tokens))}"', tag_open, flags=re.IGNORECASE)
                    else:
                        tag_open = tag_open.rstrip(" />").rstrip(">") + ' sandbox="allow-scripts allow-same-origin allow-presentation"'
                    if 'loading=' not in tag_open:
                        tag_open = tag_open.rstrip(" />").rstrip(">") + ' loading="lazy"'
                    tag_open = re.sub(r'\s+frameborder=["\'][^"\']*["\']', '', tag_open, flags=re.IGNORECASE)
                    return tag_open.rstrip(" />").rstrip(">") + '></iframe>'
                return ""

            old_cleaned = cleaned
            cleaned = re.sub(r'<iframe[^>]*>.*?</iframe>|<iframe[^>]*/>', filter_iframe, cleaned, flags=re.DOTALL | re.IGNORECASE)
            if cleaned != old_cleaned:
                warnings.append("Sanitized iframe embeds against domain whitelist.")

        # 3. Strip inline event handlers (onclick, onload, etc.) and javascript: schemes
        inline_handler_regex = r'\s+(on\w+)=["\'][^"\']*["\']'
        if re.search(inline_handler_regex, cleaned, re.IGNORECASE):
            warnings.append("Stripped inline event handlers.")
            cleaned = re.sub(inline_handler_regex, "", cleaned, flags=re.IGNORECASE)

        if "javascript:" in cleaned.lower():
            warnings.append("Removed javascript: URI pseudo-protocol.")
            cleaned = re.sub(r'(href|src)=["\']javascript:[^"\']*["\']', r'\1="#"', cleaned, flags=re.IGNORECASE)

        # 3b. Sanitize title attribute on definition and abbreviation tags
        if re.search(r'<(abbr|dfn)\b', cleaned, re.IGNORECASE):
            def clean_abbr(match):
                tag_name = match.group(1)
                title_val = match.group(2)
                safe_title = re.sub(r'[<>]', '', title_val).strip()
                return f'<{tag_name} title="{safe_title}">'
            cleaned = re.sub(r'<(abbr|dfn)\s+title=["\'](.*?)["\']>', clean_abbr, cleaned, flags=re.IGNORECASE)

        # 4. Enforce rel="noopener noreferrer" on external links and target="_blank"
        def fix_link(match):
            tag = match.group(0)
            href = match.group(1)
            # Internal domain whitelist
            is_internal = "telkomuniversity.ac.id" in href.lower() or href.startswith("/") or href.startswith("#")
            if not is_internal:
                if 'target=' not in tag:
                    tag = tag.rstrip(">").rstrip(" ") + ' target="_blank">'
                if 'rel=' not in tag:
                    tag = tag.rstrip(">").rstrip(" ") + ' rel="noopener noreferrer">'
                else:
                    rel_val = re.search(r'rel=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                    if rel_val:
                        tokens = set(rel_val.group(1).lower().split())
                        tokens.add("noopener")
                        tokens.add("noreferrer")
                        tag = re.sub(r'rel=["\'][^"\']*["\']', f'rel="{" ".join(sorted(tokens))}"', tag, flags=re.IGNORECASE)
            return tag

        cleaned = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', fix_link, cleaned, flags=re.IGNORECASE)

        # 5. Enforce loading="lazy" and decoding="async" on img tags; block bloated data URIs
        def fix_img(match):
            tag = match.group(0)
            if re.search(r'src=["\']data:', tag, re.IGNORECASE):
                warnings.append("Stripped dangerous or oversized data URI in image src.")
                tag = re.sub(r'src=["\']data:[^"\']*["\']', 'src=""', tag, flags=re.IGNORECASE)
            if 'loading=' not in tag:
                tag = tag.rstrip(" />").rstrip(">") + ' loading="lazy"'
            if 'decoding=' not in tag:
                tag = tag.rstrip(" />").rstrip(">") + ' decoding="async"'
            return tag.rstrip(" />").rstrip(">") + ' />'

        cleaned = re.sub(r'<img\s+[^>]+>', fix_img, cleaned, flags=re.IGNORECASE)

        # 5b. Enforce secure protocols and safe schemes on audio and video media tags
        if re.search(r'<(video|audio|source)\b', cleaned, re.IGNORECASE):
            def fix_media(match):
                tag = match.group(0)
                tag_name = match.group(1).lower()
                src_match = re.search(r'src=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if src_match:
                    src_url = src_match.group(1).strip()
                    if src_url.lower().startswith(("javascript:", "data:")):
                        warnings.append("Stripped dangerous media src protocol.")
                        tag = re.sub(r'src=["\'][^"\']*["\']', 'src=""', tag, flags=re.IGNORECASE)
                    elif src_url.lower().startswith("http://"):
                        warnings.append("Upgraded insecure HTTP media source to HTTPS.")
                        tag = re.sub(r'src=["\']http://', 'src="https://', tag, flags=re.IGNORECASE)
                srcset_match = re.search(r'srcset=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if srcset_match:
                    srcset_val = srcset_match.group(1).strip()
                    if srcset_val.lower().startswith(("javascript:", "data:")):
                        warnings.append("Stripped dangerous media srcset protocol.")
                        tag = re.sub(r'srcset=["\'][^"\']*["\']', 'srcset=""', tag, flags=re.IGNORECASE)
                    elif "http://" in srcset_val.lower():
                        warnings.append("Upgraded insecure HTTP source srcset to HTTPS.")
                        tag = re.sub(r'http://', 'https://', tag, flags=re.IGNORECASE)
                if tag_name in ("video", "audio"):
                    if "controls" not in tag.lower():
                        tag = tag.rstrip(">").rstrip("/") + ' controls>'
                    if "preload=" not in tag.lower():
                        tag = tag.rstrip(">").rstrip("/") + ' preload="metadata">'
                    if "autoplay" in tag.lower() and "muted" not in tag.lower():
                        tag = re.sub(r'\s+autoplay(=["\'][^"\']*["\'])?', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped unmuted autoplay from media element.")
                return tag
            cleaned = re.sub(r'<((?:video|audio|source))\b[^>]*>', fix_media, cleaned, flags=re.IGNORECASE)

        # 5c. Sanitize track subtitle elements inside audio/video
        if "<track" in cleaned.lower():
            def fix_track(match):
                tag = match.group(0)
                # Verify kind attribute
                kind_m = re.search(r'kind=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                valid_kinds = {"subtitles", "captions", "descriptions", "chapters", "metadata"}
                if not kind_m or kind_m.group(1).lower() not in valid_kinds:
                    if kind_m:
                        tag = re.sub(r'kind=["\'][^"\']*["\']', 'kind="subtitles"', tag, flags=re.IGNORECASE)
                    else:
                        tag = tag.rstrip(" />").rstrip(">") + ' kind="subtitles">'
                # Verify src attribute
                src_m = re.search(r'src=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if src_m:
                    src_url = src_m.group(1).strip()
                    if src_url.lower().startswith(("javascript:", "data:")):
                        tag = re.sub(r'src=["\'][^"\']*["\']', 'src=""', tag, flags=re.IGNORECASE)
                    elif src_url.lower().startswith("http://"):
                        tag = re.sub(r'src=["\']http://', 'src="https://', tag, flags=re.IGNORECASE)
                return tag
            track_before = cleaned
            cleaned = re.sub(r'<track\b[^>]*>', fix_track, cleaned, flags=re.IGNORECASE)
            if cleaned != track_before:
                warnings.append("Sanitized media track subtitle elements.")

        # 6. Sanitize inline SVG: strip dangerous nested tags and attributes

        if "<svg" in cleaned.lower():
            if re.search(r"<(script|foreignObject)", cleaned, re.IGNORECASE):
                warnings.append("Stripped dangerous tags from SVG.")
                cleaned = re.sub(r"<(script|foreignObject)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            if re.search(r"<(animate|animateTransform|set|handler|font|font-face)\b", cleaned, re.IGNORECASE):
                warnings.append("Stripped animation or embedded font elements from SVG.")
                cleaned = re.sub(r"<(animate|animateTransform|set|handler|font|font-face)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
                cleaned = re.sub(r"<(animate|animateTransform|set|handler|font|font-face)[^>]*/>", "", cleaned, flags=re.IGNORECASE)
            if re.search(r"<feImage\b", cleaned, re.IGNORECASE):
                def clean_feimage(m):
                    tag = m.group(0)
                    if re.search(r'(?:xlink:href|href)=["\'](?:https?://|javascript:|data:text/html)', tag, re.IGNORECASE):
                        warnings.append("Stripped unsafe external or script payload in SVG feImage.")
                        return ""
                    return tag
                cleaned = re.sub(r'<feImage\b[^>]*>', clean_feimage, cleaned, flags=re.IGNORECASE)
            if re.search(r"<use\b", cleaned, re.IGNORECASE):
                def clean_use(m):
                    tag = m.group(0)
                    href_m = re.search(r'(?:xlink:href|href)=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                    if href_m:
                        target = href_m.group(1).strip()
                        if target.lower().startswith(("javascript:", "data:")):
                            warnings.append("Stripped dangerous script URI from SVG use element.")
                            tag = re.sub(r'(?:xlink:href|href)=["\'][^"\']*["\']', 'href="#"', tag, flags=re.IGNORECASE)
                        elif re.match(r'^(?:https?:)?//', target, re.IGNORECASE):
                            warnings.append("Blocked external cross-origin symbol reference in SVG use element.")
                            tag = re.sub(r'(?:xlink:href|href)=["\'][^"\']*["\']', 'href="#"', tag, flags=re.IGNORECASE)
                    return tag
                cleaned = re.sub(r'<use\b[^>]*>', clean_use, cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'xlink:href=["\']javascript:[^"\']*["\']', 'xlink:href="#"', cleaned, flags=re.IGNORECASE)

        # 6b. Sanitize MathML equation tags and strip executable XML attributes
        if "<math" in cleaned.lower():
            if "<annotation-xml" in cleaned.lower():
                cleaned = re.sub(r"<annotation-xml[^>]*>.*?</annotation-xml>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
                warnings.append("Stripped dangerous annotation-xml from MathML.")
            if re.search(r'<math[^>]*\b(?:action|target)=["\']', cleaned, re.IGNORECASE):
                cleaned = re.sub(r'\s+(?:action|target)=["\'][^"\']*["\']', '', cleaned, flags=re.IGNORECASE)
                warnings.append("Stripped non-standard executable attributes from MathML.")
            if re.search(r'<(?:math|mrow|mi|mo|mn|mtext)[^>]*\s+(?:href|xlink:href)=', cleaned, re.IGNORECASE):
                cleaned = re.sub(r'(<(?:math|mrow|mi|mo|mn|mtext)[^>]*?)\s+(?:href|xlink:href)=["\'][^"\']*["\']', r'\1', cleaned, flags=re.IGNORECASE)
                warnings.append("Neutralized dangerous script link inside MathML elements.")
            warnings.append("Sanitized MathML equations.")

        # 7. Strip dangerous patterns from inline style attributes
        def fix_style(match):
            style_content = match.group(1)
            if re.search(r'(expression|@import|-moz-binding|javascript:|data:text/html)', style_content, re.IGNORECASE):
                warnings.append("Stripped dangerous expression from inline style attribute.")
                sanitized_style = re.sub(r'(expression\s*\([^)]*\)|@import[^;]*;?|-moz-binding[^;]*;?|javascript:[^;]*|data:text/html[^;]*)', '', style_content, flags=re.IGNORECASE).strip()
                return f'style="{sanitized_style}"' if sanitized_style else ''
            return match.group(0)

        cleaned = re.sub(r'style=["\']([^"\']*)["\']', fix_style, cleaned, flags=re.IGNORECASE)

        # 8. Clean up redundant empty paragraphs and whitespace placeholders
        if re.search(r'<p>\s*(?:&nbsp;|\s)*</p>', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'<p>\s*(?:&nbsp;|\s)*</p>\n?', '', cleaned, flags=re.IGNORECASE)

        # 8b. Strip zero-sized tracking pixels and invisible web beacons
        def check_tracking_pixel(match):
            tag = match.group(0)
            has_zero_dim = re.search(r'\b(width|height)=["\'](?:0|1)(?:px)?["\']', tag, re.IGNORECASE)
            has_hidden_style = re.search(r'style=["\'][^"\']*(display:\s*none|visibility:\s*hidden|opacity:\s*0)[^"\']*["\']', tag, re.IGNORECASE)
            if has_zero_dim or has_hidden_style:
                warnings.append("Stripped hidden tracking pixel or zero-dimension element.")
                return ""
            return tag

        cleaned = re.sub(r'<img\s+[^>]*>', check_tracking_pixel, cleaned, flags=re.IGNORECASE)

        # 8c. Strip suspicious high-entropy obfuscated attributes and hidden script comments
        if "<!--" in cleaned:
            if re.search(r'<!--[\s\S]*?(?:<script|javascript:|base64|eval\()[\s\S]*?-->', cleaned, re.IGNORECASE):
                cleaned = re.sub(r'<!--[\s\S]*?(?:<script|javascript:|base64|eval\()[\s\S]*?-->', '', cleaned, flags=re.IGNORECASE)
                warnings.append("Stripped suspicious hidden script or payload inside HTML comments.")

        if re.search(r'\s+data-(?:payload|encoded|blob)=["\'][A-Za-z0-9+/=]{80,}["\']', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'\s+data-(?:payload|encoded|blob)=["\'][A-Za-z0-9+/=]{80,}["\']', '', cleaned, flags=re.IGNORECASE)
            warnings.append("Stripped high-entropy obfuscated data attribute payload.")

        # 8d. Strip unsafe data-* attributes containing executable or script payloads
        if re.search(r'\s+data-[a-z0-9_-]+=["\'][^"\']*(?:javascript:|data:text/html|<script|eval\()[^"\']*["\']', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'\s+data-[a-z0-9_-]+=["\'][^"\']*(?:javascript:|data:text/html|<script|eval\()[^"\']*["\']', '', cleaned, flags=re.IGNORECASE)
            warnings.append("Stripped dangerous executable payload from custom data attribute.")

        # 8e. Strip unsafe meta refresh and base hijacking tags
        if re.search(r'<(meta\b[^>]*http-equiv|base\b)', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'<meta\b[^>]*http-equiv=["\']?refresh["\']?[^>]*>', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'<base\b[^>]*>', '', cleaned, flags=re.IGNORECASE)
            warnings.append("Stripped dangerous meta refresh or base hijacking tags.")

        # 8f. Neutralize unsafe interactive form elements
        if re.search(r'<(form|input|textarea|select)\b', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'</?form\b[^>]*>', '', cleaned, flags=re.IGNORECASE)
            def disable_input(m):
                tag = m.group(0)
                if 'disabled' not in tag.lower():
                    tag = tag.rstrip(">").rstrip("/") + ' disabled>'
                return tag
            cleaned = re.sub(r'<(?:input|textarea|select)\b[^>]*>', disable_input, cleaned, flags=re.IGNORECASE)
            warnings.append("Neutralized interactive form and input elements.")

        # 8g. Neutralize unsafe template and slot shadow DOM declarative markup
        if re.search(r'<(template|slot)\b', cleaned, re.IGNORECASE):
            cleaned = re.sub(r'<template\b[^>]*>.*?</template>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'</?slot\b[^>]*>', '', cleaned, flags=re.IGNORECASE)
            warnings.append("Stripped dangerous template and slot shadow DOM declarative elements.")

        # 8h. Sanitize HTML5 canvas elements and strip scriptable context attributes
        if "<canvas" in cleaned.lower():
            def sanitize_canvas(m):
                tag = m.group(0)
                # Strip non-standard or scriptable attributes like context, oncontextrestored, etc.
                tag = re.sub(r'\s+(?:context|on[a-z]+)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<canvas\b[^>]*>', sanitize_canvas, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 canvas element and stripped scriptable context attributes.")

        # 8i. Sanitize linguistic ruby annotation pronunciation elements
        if "<ruby" in cleaned.lower():
            def clean_ruby(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<(?:ruby|rt|rp|rb|rtc)\b[^>]*>', clean_ruby, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized linguistic ruby annotation elements.")

        # 8j. Sanitize HTML5 dialog modal elements and strip unpermitted script/event attributes
        if "<dialog" in cleaned.lower():
            def sanitize_dialog(m):
                tag = m.group(0)
                tag = re.sub(r'\s+(?:on[a-z]+|autofocus)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+autofocus\b', '', tag, flags=re.IGNORECASE)
                if 'class=' not in tag.lower():
                    tag = tag.rstrip(">") + ' class="tu-dialog">'
                elif 'tu-dialog' not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-dialog"', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<dialog\b[^>]*>', sanitize_dialog, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 dialog modal element and stripped autofocus/event attributes.")

        # 8k. Sanitize slot attribute on elements against prototype pollution and dangerous names
        if 'slot=' in cleaned.lower():
            def sanitize_slot_attr(m):
                tag = m.group(0)
                tag = re.sub(r'\s+slot=["\'](?:__proto__|constructor|prototype)["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<[a-z0-9_-]+\b[^>]*\bslot=["\'][^"\']*["\'][^>]*>', sanitize_slot_attr, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized element slot attribute against prototype pollution keys.")

        # 8l. Sanitize meter and progress elements against malicious attributes or invalid values
        if "<meter" in cleaned.lower() or "<progress" in cleaned.lower():
            def sanitize_meter_progress(m):
                tag = m.group(0)
                tag = re.sub(r'\s+(?:on[a-z]+|form)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                for attr in ("value", "min", "max", "low", "high", "optimum"):
                    val_match = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, flags=re.IGNORECASE)
                    if val_match:
                        raw_val = val_match.group(1).strip()
                        try:
                            num = float(raw_val)
                            if not (-1e9 <= num <= 1e9) or num != num:
                                tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', f' {attr}="0"', tag, flags=re.IGNORECASE)
                        except ValueError:
                            tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', f' {attr}="0"', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<(?:meter|progress)\b[^>]*>', sanitize_meter_progress, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized meter and progress elements and normalized numeric attributes.")

        # 8m. Sanitize picture and source responsive image elements
        if "<picture" in cleaned.lower() or "<source" in cleaned.lower():
            def sanitize_source_element(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'srcset=["\']\s*(?:javascript:|data:text/html)[^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<source\b[^>]*>', sanitize_source_element, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized responsive picture and source elements against unsafe schemes.")

        # 8n. Sanitize theme and color-scheme attributes against payload injection
        if re.search(r'\bdata-(?:theme|mode|color-scheme)=', cleaned, re.IGNORECASE):
            def sanitize_theme_attr(m):
                tag = m.group(0)
                for attr in ("data-theme", "data-mode", "data-color-scheme"):
                    val_match = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, flags=re.IGNORECASE)
                    if val_match:
                        raw_val = val_match.group(1).strip()
                        if not re.match(r'^[a-zA-Z0-9_-]{1,32}$', raw_val):
                            tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<[a-z0-9_-]+\b[^>]*\bdata-(?:theme|mode|color-scheme)=[^>]*>', sanitize_theme_attr, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized data-theme/mode attributes against unpermitted tokens.")

        # 8o. Sanitize audio and track media elements against dangerous source injection
        if "<audio" in cleaned.lower() or "<track" in cleaned.lower():
            def sanitize_audio(m):
                tag = m.group(0)
                # Strip event handlers and unprompted autoplay
                tag = re.sub(r'\s+(?:on[a-z]+|autoplay)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+autoplay\b', '', tag, flags=re.IGNORECASE)
                # Block dangerous URI schemes
                tag = re.sub(r'src=["\']\s*(?:javascript:|data:text/html)[^"\']*["\']', '', tag, flags=re.IGNORECASE)
                # Enforce controls so audio does not play unmonitored
                if "controls" not in tag.lower():
                    tag = tag.rstrip(">") + ' controls>'
                if "class=" not in tag.lower():
                    tag = tag.rstrip(">") + ' class="tu-audio">'
                elif "tu-audio" not in tag:
                    tag = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 tu-audio"', tag, flags=re.IGNORECASE)
                return tag

            def sanitize_track(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'src=["\']\s*(?:javascript:|data:text/html)[^"\']*["\']', '', tag, flags=re.IGNORECASE)
                # Validate kind attribute
                kind_m = re.search(r'\bkind=["\']([^"\']*)["\']', tag, flags=re.IGNORECASE)
                if kind_m:
                    kind_val = kind_m.group(1).strip().lower()
                    if kind_val not in ("subtitles", "captions", "descriptions", "chapters", "metadata"):
                        tag = re.sub(r'\bkind=["\'][^"\']*["\']', 'kind="subtitles"', tag, flags=re.IGNORECASE)
                return tag

            cleaned = re.sub(r'<audio\b[^>]*>', sanitize_audio, cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'<track\b[^>]*>', sanitize_track, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized audio and track media elements against dangerous media source injection.")

        # 8p. Sanitize kbd and samp computational terminal typography elements
        if "<kbd" in cleaned.lower() or "<samp" in cleaned.lower():
            def sanitize_kbd_samp(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<(?:kbd|samp)\b[^>]*>', sanitize_kbd_samp, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized kbd and samp computational typography elements.")

        # 8q. Sanitize tooltip and placement positioning attributes
        if re.search(r'\bdata-(?:placement|tooltip|title)=', cleaned, re.IGNORECASE):
            def fix_placement(m):
                pval = m.group(1).strip().lower()
                if pval not in ("top", "bottom", "left", "right"):
                    return ' data-placement="top"'
                return f' data-placement="{pval}"'

            def fix_tooltip(m):
                attr = m.group(1)
                raw_text = m.group(2)
                clean_text = re.sub(r'<[^>]+>', '', raw_text)
                clean_text = clean_text.replace('"', '&quot;').strip()[:200]
                return f'{attr}="{clean_text}"'

            cleaned = re.sub(r'\s+data-placement=["\']([^"\']*)["\']', fix_placement, cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\b(data-tooltip|data-title)=["\']([^"\']*)["\']', fix_tooltip, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized contextual tooltip and placement positioning attributes.")

        # 8r. Sanitize source media query breakpoint attributes
        if "<source" in cleaned.lower() and "media=" in cleaned.lower():
            def sanitize_source_media(m):
                tag = m.group(0)
                def clean_media_attr(attr_m):
                    media_val = attr_m.group(1).strip()
                    if re.search(r'(?:javascript|expression|@import|data:|vbscript|<|>|;)', media_val, re.IGNORECASE):
                        return ''
                    if not re.match(r'^[a-zA-Z0-9\s\(\)\:\-\,\.]+$', media_val):
                        return ''
                    return f'media="{media_val}"'
                tag = re.sub(r'\bmedia=["\']([^"\']*)["\']', clean_media_attr, tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s{2,}', ' ', tag)
                return tag
            cleaned = re.sub(r'<source\b[^>]*>', sanitize_source_media, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized source media query breakpoint attributes.")

        # 8s. Sanitize dialog modal elements and backdrop form method attributes
        if "<dialog" in cleaned.lower():
            cleaned = sanitize_html5_dialog_elements(cleaned)

            def sanitize_dialog_button(m):
                btn_tag = m.group(0)
                btn_tag = re.sub(r'formaction=["\']\s*(?:javascript:|data:text/html)[^"\']*["\']', 'formaction="#"', btn_tag, flags=re.IGNORECASE)
                btn_tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', btn_tag, flags=re.IGNORECASE)
                return btn_tag
            cleaned = re.sub(r'<button\b[^>]*\bformmethod=["\']dialog["\'][^>]*>', sanitize_dialog_button, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 dialog modal elements and button action attributes.")

        # 8t. Sanitize data-filter, data-sort, and data-category interactive tabular attributes
        if re.search(r'\bdata-(?:filter|sort|category)=', cleaned, re.IGNORECASE):
            def clean_tabular_data(m):
                attr = m.group(1).lower()
                val = m.group(2).strip()
                val = re.sub(r'<[^>]+>', '', val)
                if re.search(r'(?:javascript:|data:|expression|vbscript)', val, re.IGNORECASE):
                    return ''
                val = re.sub(r'[^a-zA-Z0-9_\-\,\.\s]', '', val).strip()[:100]
                return f'data-{attr}="{val}"'
            cleaned = re.sub(r'\bdata-(filter|sort|category)=["\']([^"\']*)["\']', clean_tabular_data, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized interactive tabular data-filter and data-sort attributes.")

        # 8u. Sanitize HTML5 <time> datetime attribute and block scriptable microdata
        if "<time" in cleaned.lower():
            def sanitize_time(m):
                tag = m.group(0)
                dt_match = re.search(r'datetime=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if dt_match:
                    dt_val = dt_match.group(1).strip()
                    if dt_val.lower().startswith(("javascript:", "data:")) or re.search(r'[<>"\'`]', dt_val):
                        tag = re.sub(r'\s+datetime=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped dangerous payload from time datetime attribute.")
                if re.search(r'\b(?:itemtype|itemprop)=["\']\s*(?:javascript:|data:)', tag, re.IGNORECASE):
                    tag = re.sub(r'\s+(?:itemtype|itemprop)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                    warnings.append("Stripped scriptable microdata from time element.")
                return tag
            cleaned = re.sub(r'<time\b[^>]*>', sanitize_time, cleaned, flags=re.IGNORECASE)

        # 8v. Sanitize HTML5 output calculation elements for telemetry formulas
        if "<output" in cleaned.lower():
            def sanitize_output(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                for_m = re.search(r'\bfor=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if for_m:
                    raw_for = for_m.group(1).strip()
                    if not re.match(r'^[a-zA-Z0-9_\-\s]+$', raw_for):
                        tag = re.sub(r'\s+for=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped invalid ID tokens from output for attribute.")
                name_m = re.search(r'\bname=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if name_m:
                    raw_name = name_m.group(1).strip()
                    if not re.match(r'^[a-zA-Z0-9_\-]+$', raw_name):
                        tag = re.sub(r'\s+name=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped invalid name attribute from output element.")
                return tag
            cleaned = re.sub(r'<output\b[^>]*>', sanitize_output, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 output calculation elements.")

        # 8w. Sanitize HTML5 track subtitle and timed text elements
        if "<track" in cleaned.lower():
            def sanitize_track(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                src_m = re.search(r'\bsrc=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if src_m:
                    src_val = src_m.group(1).strip()
                    if src_val.lower().startswith(("javascript:", "data:", "vbscript:")) or re.search(r'[<>"\'`]', src_val):
                        tag = re.sub(r'\s+src=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped dangerous URI payload from track src attribute.")
                kind_m = re.search(r'\bkind=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if kind_m:
                    kind_val = kind_m.group(1).strip().lower()
                    if kind_val not in {"subtitles", "captions", "descriptions", "chapters", "metadata"}:
                        tag = re.sub(r'\bkind=["\'][^"\']*["\']', 'kind="subtitles"', tag, flags=re.IGNORECASE)
                        warnings.append("Normalized unrecognized track kind attribute to subtitles.")
                return tag
            cleaned = re.sub(r'<track\b[^>]*>', sanitize_track, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 track subtitle elements.")

        # 8x. Sanitize HTML5 kbd and samp elements for technical telemetry documentation
        if "<kbd" in cleaned.lower() or "<samp" in cleaned.lower():
            def sanitize_kbdsamp(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<(?:kbd|samp)\b[^>]*>', sanitize_kbdsamp, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 kbd and samp technical documentation elements.")

        # 8y. Sanitize HTML5 data machine-readable token elements
        if "<data" in cleaned.lower():
            def sanitize_data(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                val_m = re.search(r'\bvalue=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if val_m:
                    val = val_m.group(1).strip()
                    if val.lower().startswith(("javascript:", "data:", "vbscript:")) or re.search(r'[<>"\'`]', val):
                        tag = re.sub(r'\s+value=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                        warnings.append("Stripped dangerous payload from data element value attribute.")
                return tag
            cleaned = re.sub(r'<data\b[^>]*>', sanitize_data, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 data token elements.")

        # 8z. Sanitize HTML5 meter telemetry threshold elements
        if "<meter" in cleaned.lower():
            def sanitize_meter(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                num_attrs = ["value", "min", "max", "low", "high", "optimum"]
                for attr in num_attrs:
                    attr_m = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                    if attr_m:
                        val = attr_m.group(1).strip()
                        if not re.match(r'^-?\d+(?:\.\d+)?$', val):
                            tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                            warnings.append(f"Stripped non-numeric {attr} attribute from meter element.")
                return tag
            cleaned = re.sub(r'<meter\b[^>]*>', sanitize_meter, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 meter telemetry elements.")

        # 8aa. Sanitize HTML5 progress gauge elements
        if "<progress" in cleaned.lower():
            def sanitize_progress(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                for attr in ["value", "max"]:
                    attr_m = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                    if attr_m:
                        val = attr_m.group(1).strip()
                        if not re.match(r'^\d+(?:\.\d+)?$', val):
                            tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                            warnings.append(f"Stripped invalid {attr} attribute from progress element.")
                return tag
            cleaned = re.sub(r'<progress\b[^>]*>', sanitize_progress, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 progress gauge elements.")

        return cleaned, warnings


def sanitize_html5_meter_elements(html: str) -> str:
    """
    Sanitizes HTML5 <meter> telemetry gauge elements by stripping scripting event handlers,
    style attributes, and ensuring that numeric boundaries (min, max, low, high, optimum, value)
    are strictly valid numeric quantities.
    """
    if not html or "<meter" not in html.lower():
        return html

    def sanitize_meter_tag(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        for attr in ["value", "min", "max", "low", "high", "optimum"]:
            attr_m = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if attr_m:
                val = attr_m.group(1).strip()
                if not re.match(r'^-?\d+(?:\.\d+)?$', val):
                    tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    return re.sub(r'<meter\b[^>]*>', sanitize_meter_tag, html, flags=re.IGNORECASE)


def sanitize_html5_progress_elements(html: str) -> str:
    """
    Sanitizes HTML5 <progress> gauge elements by removing scripting event handlers,
    style attributes, and verifying non-negative numeric progress quantities for value and max.
    """
    if not html or "<progress" not in html.lower():
        return html

    def sanitize_progress_tag(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        for attr in ["value", "max"]:
            attr_m = re.search(rf'\b{attr}=["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if attr_m:
                val = attr_m.group(1).strip()
                if not re.match(r'^\d+(?:\.\d+)?$', val):
                    tag = re.sub(rf'\s+{attr}=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    return re.sub(r'<progress\b[^>]*>', sanitize_progress_tag, html, flags=re.IGNORECASE)


def sanitize_time_duration_microdata(html: str) -> str:
    """
    Sanitizes HTML5 <time> duration microdata attributes (e.g. PT2H30M, P1D) by validating
    ISO 8601 duration syntax and stripping malformed or scriptable injection payloads.
    """
    if not html or "<time" not in html.lower():
        return html

    duration_regex = re.compile(
        r'^P(?:\d+Y)?(?:\d+M)?(?:\d+W)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$',
        re.IGNORECASE
    )

    def sanitize_time_tag(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        dt_m = re.search(r'datetime=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if dt_m:
            dt_val = dt_m.group(1).strip()
            if dt_val.upper().startswith("P"):
                if not duration_regex.match(dt_val) or dt_val.upper() == "P":
                    tag = re.sub(r'\s+datetime=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
            elif dt_val.lower().startswith(("javascript:", "data:", "vbscript:")) or re.search(r'[<>"\'`]', dt_val):
                tag = re.sub(r'\s+datetime=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    return re.sub(r'<time\b[^>]*>', sanitize_time_tag, html, flags=re.IGNORECASE)


def sanitize_html5_dialog_elements(html: str) -> str:
    """
    Sanitizes HTML5 <dialog> modal elements by removing scripting event handlers,
    style attributes, enforcing valid boolean open attributes, and stripping unsafe form actions.
    """
    if not html or "<dialog" not in html.lower():
        return html

    def sanitize_dialog_tag(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable|autofocus)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        open_m = re.search(r'\bopen=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if open_m:
            val = open_m.group(1).strip().lower()
            if val not in ("open", "", "true"):
                tag = re.sub(r'\s+open=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    return re.sub(r'<dialog\b[^>]*>', sanitize_dialog_tag, html, flags=re.IGNORECASE)


def sanitize_html5_details_summary_elements(html: str) -> str:
    """
    Sanitizes HTML5 <details> and <summary> disclosure elements by removing scripting event handlers,
    style attributes, ensuring valid open attributes on details, and enforcing safe class bindings.
    """
    if not html or ("<details" not in html.lower() and "<summary" not in html.lower()):
        return html

    def fix_details(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        open_m = re.search(r'\bopen=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if open_m:
            val = open_m.group(1).strip().lower()
            if val not in ("open", "", "true"):
                tag = re.sub(r'\s+open=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    def fix_summary(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    out = re.sub(r'<details\b[^>]*>', fix_details, html, flags=re.IGNORECASE)
    out = re.sub(r'<summary\b[^>]*>', fix_summary, out, flags=re.IGNORECASE)
    return out


def sanitize_html5_template_elements(html: str) -> str:
    """
    Sanitizes HTML5 <template> elements and declarative shadow DOM roots by neutralizing
    nested executable script tags, stripping unsafe shadowrootmode attributes, and scrubbing event handlers.
    """
    if not html or "<template" not in html.lower():
        return html

    def sanitize_template_block(m):
        full_tag = m.group(1)
        inner_content = m.group(2)
        full_tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', full_tag, flags=re.IGNORECASE)
        srm_m = re.search(r'\b(shadowrootmode|shadowroot)=["\']([^"\']*)["\']', full_tag, re.IGNORECASE)
        if srm_m:
            attr_name = srm_m.group(1)
            val = srm_m.group(2).strip().lower()
            if val not in ("open", "closed"):
                full_tag = re.sub(rf'\s+{attr_name}=["\'][^"\']*["\']', '', full_tag, flags=re.IGNORECASE)
        inner_cleaned = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', inner_content, flags=re.IGNORECASE)
        inner_cleaned = re.sub(r'<script\b[^>]*>', '', inner_cleaned, flags=re.IGNORECASE)
        inner_cleaned = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', inner_cleaned, flags=re.IGNORECASE)
        return f"{full_tag}{inner_cleaned}</template>"

    out = re.sub(r'(<template\b[^>]*>)([\s\S]*?)</template>', sanitize_template_block, html, flags=re.IGNORECASE)

    def sanitize_lone_template(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag
    out = re.sub(r'<template\b[^>]*>', sanitize_lone_template, out, flags=re.IGNORECASE)
    return out


def sanitize_html5_media_track_caption_elements(html: str) -> str:
    """
    Sanitizes HTML5 <track> timed text track elements for WebVTT subtitles, captions, and descriptions.
    Neutralizes script-bearing src protocols (javascript:, data:text/html), strips inline event handlers,
    and enforces standardized kind and srclang attributes.
    """
    if not html or "<track" not in html.lower():
        return html

    def fix_track(m):
        tag = m.group(0)
        # Strip script event handlers and inline styles
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        # Sanitize src protocol
        src_m = re.search(r'\bsrc=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if src_m:
            src_val = src_m.group(1).strip()
            src_lower = src_val.lower()
            if src_lower.startswith("javascript:") or "data:text/html" in src_lower or "<script" in src_lower:
                tag = re.sub(r'\s+src=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        # Validate kind attribute
        kind_m = re.search(r'\bkind=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if kind_m:
            kind_val = kind_m.group(1).strip().lower()
            allowed_kinds = ("subtitles", "captions", "descriptions", "chapters", "metadata")
            if kind_val not in allowed_kinds:
                tag = re.sub(r'\s+kind=["\'][^"\']*["\']', ' kind="subtitles"', tag, flags=re.IGNORECASE)

        # Validate srclang
        srclang_m = re.search(r'\bsrclang=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if srclang_m:
            srclang_val = srclang_m.group(1).strip()
            if not re.match(r'^[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,4})?$', srclang_val):
                tag = re.sub(r'\s+srclang=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        return tag

    return re.sub(r'<track\b[^>]*>', fix_track, html, flags=re.IGNORECASE)


def sanitize_html5_datalist_autocomplete_elements(html: str) -> str:
    """
    Sanitizes HTML5 <datalist> and nested <option> autocomplete elements for telecommunication search forms.
    Scans for valid alphanumeric id bindings, strips malicious script event handlers, and scrubs unsafe inline styling.
    """
    if not html or "<datalist" not in html.lower():
        return html

    def fix_datalist_block(m):
        full_tag = m.group(1)
        inner = m.group(2)
        # Scrub event handlers and unsafe styling on datalist tag
        full_tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', full_tag, flags=re.IGNORECASE)
        full_tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', full_tag, flags=re.IGNORECASE)

        # Sanitize id attribute
        id_m = re.search(r'\bid=["\']([^"\']*)["\']', full_tag, re.IGNORECASE)
        if id_m:
            id_val = id_m.group(1).strip()
            clean_id = re.sub(r'[^a-zA-Z0-9_\-]', '', id_val)
            if clean_id:
                full_tag = re.sub(r'\bid=["\'][^"\']*["\']', f'id="{clean_id}"', full_tag, flags=re.IGNORECASE)
            else:
                full_tag = re.sub(r'\s+id=["\'][^"\']*["\']', '', full_tag, flags=re.IGNORECASE)

        # Sanitize option tags inside
        def fix_option(opt_m):
            opt_tag = opt_m.group(0)
            opt_tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', opt_tag, flags=re.IGNORECASE)
            opt_tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', opt_tag, flags=re.IGNORECASE)
            return opt_tag

        clean_inner = re.sub(r'<option\b[^>]*>', fix_option, inner, flags=re.IGNORECASE)
        # Strip any nested script tags
        clean_inner = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', clean_inner, flags=re.IGNORECASE)
        return f"{full_tag}{clean_inner}</datalist>"

    out = re.sub(r'(<datalist\b[^>]*>)([\s\S]*?)</datalist>', fix_datalist_block, html, flags=re.IGNORECASE)

    def fix_lone_datalist(m):
        tag = m.group(0)
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        return tag

    out = re.sub(r'<datalist\b[^>]*>(?![\s\S]*?</datalist>)', fix_lone_datalist, out, flags=re.IGNORECASE)
    return out


def sanitize_html5_output_calculation_elements(html: str) -> str:
    """
    Sanitizes HTML5 <output> calculation elements used in engineering calculators (link budgets, BER, path loss).
    Removes malicious scripting event handlers, scrubs unsafe inline styles, and enforces validated 'for' and 'name' attributes.
    """
    if not html or "<output" not in html.lower():
        return html

    def fix_output(m):
        tag = m.group(0)
        # Scrub inline event handlers and styles
        tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
        tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        # Sanitize 'for' attribute (space-separated list of element IDs)
        for_m = re.search(r'\bfor=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if for_m:
            for_val = for_m.group(1).strip()
            tokens = [re.sub(r'[^a-zA-Z0-9_\-]', '', tok) for tok in for_val.split() if re.sub(r'[^a-zA-Z0-9_\-]', '', tok)]
            if tokens:
                tag = re.sub(r'\bfor=["\'][^"\']*["\']', f'for="{" ".join(tokens)}"', tag, flags=re.IGNORECASE)
            else:
                tag = re.sub(r'\s+for=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        # Sanitize 'name' attribute
        name_m = re.search(r'\bname=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if name_m:
            name_val = name_m.group(1).strip()
            clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '', name_val)
            if clean_name:
                tag = re.sub(r'\bname=["\'][^"\']*["\']', f'name="{clean_name}"', tag, flags=re.IGNORECASE)
            else:
                tag = re.sub(r'\s+name=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)

        return tag

    return re.sub(r'<output\b[^>]*>', fix_output, html, flags=re.IGNORECASE)



















