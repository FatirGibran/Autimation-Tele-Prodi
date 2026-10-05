import re
from typing import Tuple, List

ALLOWED_TAGS = {
    "div", "style", "article", "header", "section", "figure", "figcaption",
    "footer", "h1", "h2", "h3", "h4", "p", "a", "img", "ul", "ol", "li",
    "span", "strong", "em", "code", "pre", "blockquote", "details", "summary",
    "table", "thead", "tbody", "tr", "th", "td", "abbr", "dfn", "mark", "kbd", "sub", "sup",
    "svg", "path", "g", "circle", "rect", "line", "polygon", "polyline",
    "video", "audio", "source"
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
                    # Ensure sandbox and lazy loading
                    if 'sandbox=' not in tag:
                        tag = tag.rstrip(" />").rstrip(">") + ' sandbox="allow-scripts allow-same-origin allow-presentation"'
                    if 'loading=' not in tag:
                        tag = tag.rstrip(" />").rstrip(">") + ' loading="lazy"'
                    return tag.rstrip(" />").rstrip(">") + '></iframe>'
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
                src_match = re.search(r'src=["\']([^"\']*)["\']', tag, re.IGNORECASE)
                if src_match:
                    src_url = src_match.group(1).strip()
                    if src_url.lower().startswith(("javascript:", "data:")):
                        warnings.append("Stripped dangerous media src protocol.")
                        tag = re.sub(r'src=["\'][^"\']*["\']', 'src=""', tag, flags=re.IGNORECASE)
                    elif src_url.lower().startswith("http://"):
                        warnings.append("Upgraded insecure HTTP media source to HTTPS.")
                        tag = re.sub(r'src=["\']http://', 'src="https://', tag, flags=re.IGNORECASE)
                return tag
            cleaned = re.sub(r'<(video|audio|source)[^>]*>', fix_media, cleaned, flags=re.IGNORECASE)

        # 6. Sanitize inline SVG: strip dangerous nested tags and attributes

        if "<svg" in cleaned.lower():
            if re.search(r"<(script|foreignObject)", cleaned, re.IGNORECASE):
                warnings.append("Stripped dangerous tags from SVG.")
                cleaned = re.sub(r"<(script|foreignObject)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'xlink:href=["\']javascript:[^"\']*["\']', 'xlink:href="#"', cleaned, flags=re.IGNORECASE)

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

        return cleaned, warnings


