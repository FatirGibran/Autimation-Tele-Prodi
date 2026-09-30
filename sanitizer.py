import re
from typing import Tuple, List

ALLOWED_TAGS = {
    "div", "style", "article", "header", "section", "figure", "figcaption",
    "footer", "h1", "h2", "h3", "h4", "p", "a", "img", "ul", "ol", "li",
    "span", "strong", "em", "code", "pre", "blockquote", "details", "summary",
    "table", "thead", "tbody", "tr", "th", "td",
    "svg", "path", "g", "circle", "rect", "line", "polygon", "polyline"
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

        # 2. Strip dangerous script, iframe, object, and embed tags
        if "<script" in cleaned.lower():
            warnings.append("Stripped dangerous <script> tag from HTML.")
            cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

        if re.search(r"<(iframe|object|embed)", cleaned, re.IGNORECASE):
            warnings.append("Stripped dangerous embedded tags (iframe/object/embed).")
            cleaned = re.sub(r"<(iframe|object|embed)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r"<(iframe|object|embed)[^>]*/>", "", cleaned, flags=re.IGNORECASE)

        # 3. Strip inline event handlers (onclick, onload, etc.) and javascript: schemes
        inline_handler_regex = r'\s+(on\w+)=["\'][^"\']*["\']'
        if re.search(inline_handler_regex, cleaned, re.IGNORECASE):
            warnings.append("Stripped inline event handlers.")
            cleaned = re.sub(inline_handler_regex, "", cleaned, flags=re.IGNORECASE)

        if "javascript:" in cleaned.lower():
            warnings.append("Removed javascript: URI pseudo-protocol.")
            cleaned = re.sub(r'(href|src)=["\']javascript:[^"\']*["\']', r'\1="#"', cleaned, flags=re.IGNORECASE)

        # 4. Enforce rel="noopener noreferrer" on external links
        def fix_link(match):
            tag = match.group(0)
            href = match.group(1)
            if "bif-pwt.telkomuniversity.ac.id" not in href:
                if 'rel=' not in tag:
                    tag = tag.rstrip(">") + ' rel="noopener noreferrer">'
                elif 'noopener' not in tag:
                    tag = re.sub(r'rel=["\'][^"\']*["\']', 'rel="noopener noreferrer"', tag)
                if 'target=' not in tag:
                    tag = tag.rstrip(">") + ' target="_blank">'
            return tag

        cleaned = re.sub(r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>', fix_link, cleaned, flags=re.IGNORECASE)

        # 5. Enforce loading="lazy" and decoding="async" on img tags
        def fix_img(match):
            tag = match.group(0)
            if 'loading=' not in tag:
                tag = tag.rstrip(" />").rstrip(">") + ' loading="lazy"'
            if 'decoding=' not in tag:
                tag = tag.rstrip(" />").rstrip(">") + ' decoding="async"'
            return tag.rstrip(" />").rstrip(">") + ' />'

        cleaned = re.sub(r'<img\s+[^>]+>', fix_img, cleaned, flags=re.IGNORECASE)

        # 6. Sanitize inline SVG: strip dangerous nested tags and attributes
        if "<svg" in cleaned.lower():
            if re.search(r"<(script|foreignObject)", cleaned, re.IGNORECASE):
                warnings.append("Stripped dangerous tags from SVG.")
                cleaned = re.sub(r"<(script|foreignObject)[^>]*>.*?</\1>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'xlink:href=["\']javascript:[^"\']*["\']', 'xlink:href="#"', cleaned, flags=re.IGNORECASE)

        return cleaned, warnings

