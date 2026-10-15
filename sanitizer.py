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
    "meter", "progress"
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
            def sanitize_dialog(m):
                tag = m.group(0)
                tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                tag = re.sub(r'\s+(?:style|contenteditable)=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<dialog\b[^>]*>', sanitize_dialog, cleaned, flags=re.IGNORECASE)

            def sanitize_dialog_form(m):
                form_tag = m.group(0)
                form_tag = re.sub(r'action=["\']\s*(?:javascript:|data:text/html)[^"\']*["\']', 'action="#"', form_tag, flags=re.IGNORECASE)
                form_tag = re.sub(r'\s+on[a-z]+=["\'][^"\']*["\']', '', form_tag, flags=re.IGNORECASE)
                return form_tag
            cleaned = re.sub(r'<form\b[^>]*\bmethod=["\']dialog["\'][^>]*>', sanitize_dialog_form, cleaned, flags=re.IGNORECASE)
            warnings.append("Sanitized HTML5 dialog modal elements and form method attributes.")

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

        return cleaned, warnings










