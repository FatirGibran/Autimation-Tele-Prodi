import re
from typing import Dict, Any, List, Optional

DEFAULT_PLACEHOLDER_IMG = "https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/placeholder.jpg"

def clean_url(raw_url: str) -> str:
    if not raw_url:
        return DEFAULT_PLACEHOLDER_IMG
    # Extract URL from markdown link syntax [text](http://...)
    md_match = re.search(r'\((https?://[^\s\)]+)\)', raw_url)
    if md_match:
        url = md_match.group(1).strip()
    else:
        # Plain URL regex
        url_match = re.search(r'(https?://[^\s\]\>]+)', raw_url)
        if url_match:
            url = url_match.group(1).strip()
        else:
            return DEFAULT_PLACEHOLDER_IMG

    import urllib.parse as urlparse
    parsed = urlparse.urlsplit(url)
    if parsed.query:
        tracking_params = {
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "fbclid", "gclid", "ref", "mc_eid", "igshid"
        }
        query_pairs = urlparse.parse_qsl(parsed.query, keep_blank_values=True)
        filtered_pairs = [(k, v) for k, v in query_pairs if k.lower() not in tracking_params]
        new_query = urlparse.urlencode(filtered_pairs)
        url = urlparse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))

    return url

def parse_telegram_input(raw_text: str) -> Dict[str, Any]:
    """
    Parses structured Telegram text trigger into a normalized dictionary.
    Supports bullet formats, markdown links, and auto-detects missing fields.
    """
    lines = raw_text.strip().splitlines()
    data: Dict[str, Any] = {
        "topik": "",
        "tanggal": "",
        "kategori": "Berita & Riset",
        "image_url": DEFAULT_PLACEHOLDER_IMG,
        "poin_utama": [],
        "estimasi_baca": "4 Menit Baca"
    }
    
    current_key: Optional[str] = None
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        lower_line = line_clean.lower()
        if lower_line.startswith("topik:"):
            data["topik"] = line_clean.split(":", 1)[1].strip()
            current_key = "topik"
        elif lower_line.startswith("tanggal:"):
            data["tanggal"] = line_clean.split(":", 1)[1].strip()
            current_key = "tanggal"
        elif lower_line.startswith("kategori:"):
            data["kategori"] = line_clean.split(":", 1)[1].strip()
            current_key = "kategori"
        elif lower_line.startswith("image url:") or lower_line.startswith("image:") or lower_line.startswith("gambar:"):
            raw_url = line_clean.split(":", 1)[1].strip()
            data["image_url"] = clean_url(raw_url)
            current_key = "image_url"
        elif lower_line.startswith("estimasi:") or lower_line.startswith("estimasi baca:"):
            data["estimasi_baca"] = line_clean.split(":", 1)[1].strip()
            current_key = "estimasi_baca"
        elif lower_line.startswith("poin utama:") or lower_line.startswith("poin-poin:"):
            current_key = "poin_utama"
        elif current_key == "poin_utama":
            # Strip standard list markers: -, *, •, or 1.
            cleaned_bullet = re.sub(r'^[\-\*\•\d\.]+\s*', '', line_clean)
            if cleaned_bullet:
                data["poin_utama"].append(cleaned_bullet)
                
    if not data["image_url"]:
        data["image_url"] = DEFAULT_PLACEHOLDER_IMG
        
    return data

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Extracts Yoast SEO metadata and HTML block from LLM output.
    """
    result = {
        "focus_keyphrase": "",
        "seo_title": "",
        "slug": "",
        "meta_description": "",
        "html_code": ""
    }
    
    fk_match = re.search(r"Focus Keyphrase:\s*`?([^`\n]+)`?", response_text, re.IGNORECASE)
    if fk_match:
        result["focus_keyphrase"] = fk_match.group(1).strip()
        
    title_match = re.search(r"SEO Title:\s*`?([^`\n]+)`?", response_text, re.IGNORECASE)
    if title_match:
        result["seo_title"] = title_match.group(1).strip()
        
    slug_match = re.search(r"Slug:\s*`?([^`\n]+)`?", response_text, re.IGNORECASE)
    if slug_match:
        result["slug"] = slug_match.group(1).strip()
        
    meta_match = re.search(r"Meta Description:\s*`?([^`\n]+)`?", response_text, re.IGNORECASE)
    if meta_match:
        result["meta_description"] = meta_match.group(1).strip()
        
    # Search for HTML block inside markdown code fence
    html_match = re.search(r"```(?:html)?\s*(<div class=\"tu-editorial-container\".*?</div>)\s*```", response_text, re.DOTALL)
    if html_match:
        result["html_code"] = html_match.group(1).strip()
    else:
        # Fallback if markdown fence was omitted
        raw_div = re.search(r"(<div class=\"tu-editorial-container\".*?</div>)", response_text, re.DOTALL)
        if raw_div:
            result["html_code"] = raw_div.group(1).strip()

    return result

def extract_headings(html_content: str) -> List[Dict[str, str]]:
    """
    Extracts structured headings (h1-h6) from HTML markup.
    """
    headings: List[Dict[str, str]] = []
    pattern = re.compile(r"<(h[1-6])[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(html_content):
        tag = match.group(1).lower()
        raw_text = match.group(2)
        clean_text = re.sub(r"<[^>]+>", "", raw_text).strip()
        headings.append({"tag": tag, "text": clean_text})
    return headings

def strip_markdown_formatting(text: str) -> str:
    """
    Strips common Markdown formatting symbols leaving clean text.
    """
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()

def convert_markdown_table_to_html(md_table: str) -> str:
    """
    Converts a standard Markdown table into responsive semantic HTML.
    """
    lines = [line.strip() for line in md_table.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        return md_table

    header_cells = [c.strip() for c in lines[0].strip("|").split("|")]
    if not re.match(r"^\|?[\s\-:|]+\|?$", lines[1]):
        return md_table

    thead_html = "        <tr>\n" + "\n".join(f"          <th>{c}</th>" for c in header_cells) + "\n        </tr>"
    rows_html = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        row_tds = "\n".join(f"          <td>{c}</td>" for c in cells)
        rows_html.append(f"        <tr>\n{row_tds}\n        </tr>")

    tbody_html = "\n".join(rows_html)
    return f"""    <div class="tu-table-responsive">
      <table class="tu-table">
        <thead>
{thead_html}
        </thead>
        <tbody>
{tbody_html}
        </tbody>
      </table>
    </div>"""

def calculate_reading_time(text: str, wpm: int = 200) -> str:
    """
    Calculates estimated reading time in Indonesian format based on word count.
    Default rate is 200 words per minute for academic/technical editorial copy.
    """
    if not text:
        return "1 Menit Baca"
    clean_text = re.sub(r"<[^>]+>", " ", text)
    words = re.findall(r"\b\w+\b", clean_text)
    count = len(words)
    if count == 0:
        return "1 Menit Baca"
    minutes = max(1, round(count / wpm))
    return f"{minutes} Menit Baca"

def parse_markdown_callouts(text: str) -> str:
    """
    Parses GitHub-flavored markdown callouts/admonitions (> [!TYPE]) into styled Elementor callout cards.
    """
    callout_pattern = re.compile(
        r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*\n((?:>.*(?:\n|$))+)",
        re.MULTILINE | re.IGNORECASE
    )

    title_labels = {
        "NOTE": "Catatan",
        "TIP": "Tips Penting",
        "IMPORTANT": "Perhatian",
        "WARNING": "Peringatan",
        "CAUTION": "Peringatan Kritis"
    }

    def replace_callout(match):
        c_type = match.group(1).upper()
        raw_body = match.group(2)
        body_lines = [re.sub(r"^>\s?", "", line).strip() for line in raw_body.splitlines()]
        body_text = " ".join(line for line in body_lines if line)
        title = title_labels.get(c_type, c_type.capitalize())
        css_modifier = c_type.lower()
        return f'<div class="tu-callout tu-callout-{css_modifier}">\n  <strong class="tu-callout-title">{title}</strong>\n  <p>{body_text}</p>\n</div>'

    return callout_pattern.sub(replace_callout, text)


def generate_excerpt(html_content: str, max_length: int = 160) -> str:
    """
    Extracts a clean, tag-stripped text excerpt suitable for meta description or RSS summary.
    Truncates at the nearest word boundary without splitting words.
    """
    if not html_content:
        return ""
    clean = re.sub(r"<[^>]+>", " ", html_content)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) <= max_length:
        return clean
    truncated = clean[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return f"{truncated}..."


def normalize_indonesian_typography(text: str) -> str:
    """
    Normalizes typographic characters, non-breaking spaces, and quotes
    to standard editorial characters for consistent CMS rendering.
    """
    if not text:
        return ""
    replacements = {
        "\u201c": '"',  # Left double quotation mark
        "\u201d": '"',  # Right double quotation mark
        "\u2018": "'",  # Left single quotation mark
        "\u2019": "'",  # Right single quotation mark
        "\u2014": " -- ", # Em-dash
        "\u2013": "-",  # En-dash
        "\u2026": "...", # Ellipsis
        "\u00a0": " ",  # Non-breaking space
        "\u200b": "",   # Zero-width space
        "\ufeff": "",   # Byte order mark
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Collapse multiple spaces but preserve newlines
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse_markdown_footnotes(text: str) -> str:
    """
    Parses Markdown footnotes ([^1] and [^1]: ...) into academic HTML footnotes
    with bidirectional reference anchors and backlink navigation.
    """
    if not text:
        return ""
    # Extract footnote definitions
    footnote_def_pattern = re.compile(r"^\[\^([a-zA-Z0-9_\-]+)\]:\s*(.+)$", re.MULTILINE)
    definitions = footnote_def_pattern.findall(text)
    if not definitions:
        return text

    # Remove definitions from body text
    body_text = footnote_def_pattern.sub("", text).strip()

    # Replace inline footnote references
    for label, _ in definitions:
        inline_pattern = re.compile(rf"\[\^{re.escape(label)}\]")
        ref_html = f'<sup class="tu-footnote-ref"><a href="#fn-{label}" id="fnref-{label}">[{label}]</a></sup>'
        body_text = inline_pattern.sub(ref_html, body_text)

    # Build footnotes section
    items_html = []
    for label, content in definitions:
        backlink = f' <a href="#fnref-{label}" class="tu-footnote-backref" title="Kembali ke teks">&#8617;</a>'
        items_html.append(f'    <li id="fn-{label}"><p>{content.strip()}{backlink}</p></li>')

    footnotes_section = (
        '<div class="tu-footnotes">\n'
        '  <hr class="tu-footnotes-divider" />\n'
        '  <ol>\n' + "\n".join(items_html) + "\n  </ol>\n</div>"
    )
    return f"{body_text}\n\n{footnotes_section}"
