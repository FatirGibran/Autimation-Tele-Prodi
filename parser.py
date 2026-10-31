import re
import math
from typing import Dict, Any, List, Optional, Tuple

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


def extract_keyword_frequency(text: str, n_gram: int = 1, top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Extracts high-frequency n-grams from text content excluding Indonesian and English stop words.
    Useful for keyword density analysis and SEO content optimization.
    """
    if not text:
        return []
    clean_text = re.sub(r"<[^>]+>", " ", text).lower()
    tokens = re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", clean_text)

    stop_words = {
        "yang", "untuk", "pada", "dengan", "adalah", "sebagai", "dalam", "dari",
        "ini", "itu", "dan", "atau", "oleh", "akan", "juga", "dapat", "secara",
        "antara", "karena", "bagi", "setelah", "saat", "lebih", "telah", "bisa",
        "the", "and", "for", "with", "that", "this", "from", "are", "were"
    }

    filtered_tokens = [t for t in tokens if t not in stop_words and not t.isdigit()]
    if n_gram <= 1:
        candidates = filtered_tokens
    else:
        candidates = [
            " ".join(filtered_tokens[i:i + n_gram])
            for i in range(len(filtered_tokens) - n_gram + 1)
        ]

    counts: Dict[str, int] = {}
    for item in candidates:
        counts[item] = counts.get(item, 0) + 1

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[:top_n]


def parse_math_blocks(text: str) -> str:
    """
    Parses LaTeX/Math syntax ($$...$$ display blocks and $...$ inline math)
    into semantic styled HTML math elements for academic papers.
    """
    if not text:
        return ""
    # 1. Display math blocks ($$...$$)
    def replace_block(match):
        code = match.group(1).strip()
        return f'<div class="tu-math-block"><code>{code}</code></div>'

    text = re.sub(r"\$\$\s*([\s\S]*?)\s*\$\$", replace_block, text)

    # 2. Inline math ($...$), ensuring it's not preceded/followed by digits (currency protection)
    def replace_inline(match):
        code = match.group(1).strip()
        return f'<span class="tu-math-inline"><code>{code}</code></span>'

    text = re.sub(r"(?<![\w\$])\$([^\$\n]+?)\$(?![\w\$])", replace_inline, text)
    return text


def get_indonesian_reading_level_label(score: float) -> str:
    """
    Categorizes the Indonesian adapted Flesch Reading Ease score into editorial audience bands.
    """
    if score >= 80.0:
        return "Sangat Mudah Dipahami (Populer / Umum)"
    elif score >= 60.0:
        return "Standar Editorial Edukasi & Blog"
    elif score >= 40.0:
        return "Teks Teknis & Akademik Mahasiswa"
    elif score >= 20.0:
        return "Jurnal Ilmiah & Makalah Riset Lanjutan"
    else:
        return "Monograf Riset Khusus / Sangat Padat"


def parse_markdown_task_lists(text: str) -> str:
    """
    Parses Markdown task lists (- [ ] and - [x]) into semantic HTML checklists.
    """
    if not text:
        return ""

    def replace_task_block(match):
        block = match.group(0)
        items = []
        for line in block.strip().splitlines():
            line_str = line.strip()
            checked_match = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)$", line_str)
            if checked_match:
                is_checked = checked_match.group(1).lower() == "x"
                label = checked_match.group(2)
                chk_attr = " checked" if is_checked else ""
                items.append(f'  <li class="tu-task-item"><input type="checkbox"{chk_attr} disabled /> <span>{label}</span></li>')
        return '<ul class="tu-task-list">\n' + "\n".join(items) + "\n</ul>"

    pattern = re.compile(r"^(?:[-*]\s+\[[ xX]\]\s+.*(?:\n|$))+", re.MULTILINE)
    return pattern.sub(replace_task_block, text)


def generate_unique_heading_slugs(headings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Computes unique, url-safe anchor slugs for a list of headings, automatically
    resolving duplicate heading text collisions.
    """
    slug_counts: Dict[str, int] = {}
    enriched = []
    for h in headings:
        text = h.get("text", "").strip()
        base_slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
        base_slug = re.sub(r"[-\s]+", "-", base_slug) or "heading"
        if base_slug in slug_counts:
            slug_counts[base_slug] += 1
            final_slug = f"{base_slug}-{slug_counts[base_slug]}"
        else:
            slug_counts[base_slug] = 1
            final_slug = base_slug

        item = dict(h)
        item["slug"] = final_slug
        enriched.append(item)
    return enriched


def parse_academic_citations(text: str) -> str:
    """
    Parses Pandoc-style academic citation brackets ([@key], [@key, p. 12])
    into semantic <cite class="tu-citation" data-key="..."> markup.
    """
    if not text:
        return ""
    citation_pattern = re.compile(r'\[([^\]]*?@([a-zA-Z0-9_\-]+)[^\]]*?)\]')

    def replace_citation(match):
        full_cite = match.group(1)
        primary_key = match.group(2)
        return f'<cite class="tu-citation" data-cite-key="{primary_key}">[{full_cite.strip()}]</cite>'

    return citation_pattern.sub(replace_citation, text)


def extract_citation_keys(text: str) -> List[str]:
    """
    Extracts all distinct academic citation keys (@key) referenced in text.
    """
    if not text:
        return []
    keys = re.findall(r'@([a-zA-Z0-9_\-]+)', text)
    seen = set()
    result = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            result.append(k)
    return result


DEFAULT_ACADEMIC_GLOSSARY: Dict[str, str] = {
    "KRS": "Kartu Rencana Studi",
    "KHS": "Kartu Hasil Studi",
    "SKS": "Satuan Kredit Semester",
    "MBKM": "Merdeka Belajar Kampus Merdeka",
    "RPS": "Rencana Pembelajaran Semester",
    "CPL": "Capaian Pembelajaran Lulusan",
    "CPMK": "Capaian Pembelajaran Mata Kuliah",
    "TA": "Tugas Akhir",
    "PA": "Pembimbing Akademik",
    "LPPM": "Lembaga Penelitian dan Pengabdian kepada Masyarakat",
    "IKU": "Indikator Kinerja Utama",
    "SN-DIKTI": "Standar Nasional Pendidikan Tinggi",
}


def expand_indonesian_acronyms(text: str, glossary: Optional[Dict[str, str]] = None) -> str:
    """
    Annotates first occurrences of academic acronyms with <abbr title="Full Form">ACRONYM</abbr>.
    """
    if not text:
        return ""
    active_glossary = glossary or DEFAULT_ACADEMIC_GLOSSARY
    expanded_text = text
    for acronym, full_form in active_glossary.items():
        pattern = re.compile(rf'(?<![<"\'])\b({re.escape(acronym)})\b(?![>"\'])')
        expanded_text = pattern.sub(f'<abbr title="{full_form}">{acronym}</abbr>', expanded_text, count=1)
    return expanded_text


def normalize_markdown_code_blocks(text: str, default_lang: str = "text") -> str:
    """
    Normalizes Markdown fenced code blocks into semantic HTML <pre><code class="language-...">
    with language alias mapping and auto-detection fallback.
    """
    if not text:
        return ""
    import html

    LANG_ALIASES = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "sh": "bash",
        "golang": "go",
        "yml": "yaml",
        "cpp": "cpp",
        "c++": "cpp",
        "rs": "rust",
    }

    def detect_lang(code_snippet: str) -> str:
        snippet = code_snippet.strip()
        if re.search(r'^(import\s+|def\s+|from\s+\w+\s+import|class\s+\w+:)', snippet, re.MULTILINE):
            return "python"
        if re.search(r'^(const\s+|let\s+|function\s+|export\s+default)', snippet, re.MULTILINE):
            return "javascript"
        if re.search(r'^(#include\s+<|int\s+main\s*\()', snippet, re.MULTILINE):
            return "cpp"
        if re.search(r'^(SELECT\s+|INSERT\s+INTO\s+|UPDATE\s+)', snippet, re.IGNORECASE | re.MULTILINE):
            return "sql"
        return default_lang

    def replace_fenced_code(match):
        raw_lang = (match.group(1) or "").strip().lower()
        code_body = match.group(2)
        lang = LANG_ALIASES.get(raw_lang, raw_lang) if raw_lang else detect_lang(code_body)
        escaped_code = html.escape(code_body.rstrip("\n"))
        return f'<pre class="tu-code-block"><code class="language-{lang}">{escaped_code}</code></pre>'

    fenced_pattern = re.compile(r'```([a-zA-Z0-9_\-+]*)\n([\s\S]*?)```', re.MULTILINE)
    return fenced_pattern.sub(replace_fenced_code, text)


def extract_paragraph_transitions(text: str) -> List[Dict[str, Any]]:
    """
    Extracts topic sentences (first sentence) and concluding/transitional sentences
    (last sentence) of each paragraph for structural discourse analysis.
    """
    if not text:
        return []
    cleaned = re.sub(r'</p>\s*<p[^>]*>', '\n\n', text)
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    raw_paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]

    results: List[Dict[str, Any]] = []
    for idx, p in enumerate(raw_paragraphs, 1):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', p) if s.strip()]
        if not sentences:
            continue
        topic = sentences[0]
        conclusion = sentences[-1] if len(sentences) > 1 else topic
        results.append({
            "paragraph_index": idx,
            "topic_sentence": topic,
            "concluding_sentence": conclusion,
            "sentence_count": len(sentences),
            "word_count": len(p.split()),
        })
    return results


def normalize_academic_degrees(text: str) -> str:
    """
    Normalizes academic titles and degrees with standardized dots and non-breaking spaces.
    Examples: 'S Kom' -> 'S.Kom.', 'M Kom' -> 'M.Kom.', 'Ph D' -> 'Ph.D.'
    """
    if not text:
        return ""

    degree_patterns = [
        (r'\bS[\.\s]*Kom\b\.?', 'S.Kom.'),
        (r'\bM[\.\s]*Kom\b\.?', 'M.Kom.'),
        (r'\bS[\.\s]*T\b\.?', 'S.T.'),
        (r'\bM[\.\s]*T\b\.?', 'M.T.'),
        (r'\bS[\.\s]*Si\b\.?', 'S.Si.'),
        (r'\bM[\.\s]*Si\b\.?', 'M.Si.'),
        (r'\bPh[\.\s]*D\b\.?', 'Ph.D.'),
        (r'\bM[\.\s]*Sc\b\.?', 'M.Sc.'),
        (r'\bB[\.\s]*Sc\b\.?', 'B.Sc.'),
        (r'\bProf\b\.?', 'Prof.'),
        (r'\bDr\b\.?', 'Dr.'),
        (r'\bIr\b\.?', 'Ir.'),
    ]

    res = text
    for pattern, repl in degree_patterns:
        res = re.sub(pattern, repl, res)

    return res


def parse_course_curriculum_codes(text: str) -> List[Dict[str, Any]]:
    """
    Extracts university curriculum course codes (e.g. IF2143, TIF101, CSI402)
    and resolves department prefix and semester level.
    """
    if not text:
        return []

    pattern = re.compile(r'\b([A-Z]{2,4})\s*([1-8])(\d{2,3})\b')
    results = []
    seen = set()

    for match in pattern.finditer(text):
        full_code = f"{match.group(1)}{match.group(2)}{match.group(3)}"
        if full_code in seen:
            continue
        seen.add(full_code)

        dept_prefix = match.group(1)
        level_digit = int(match.group(2))
        sub_number = match.group(3)

        results.append({
            "code": full_code,
            "department_prefix": dept_prefix,
            "level": level_digit,
            "course_number": sub_number,
        })

    return results


def balance_and_clean_quotes(text: str) -> str:
    """
    Normalizes straight quotes into Indonesian smart quotes and fixes unclosed quotation pairs.
    """
    if not text:
        return ""

    res = re.sub(r'(^|[\s\(\[\{])"', r'\1“', text)
    res = re.sub(r'"($|[\s\,\.\!\?\:\;\)\]\}])', r'”\1', res)
    res = res.replace('"', '”')

    open_count = res.count('“')
    close_count = res.count('”')
    if open_count > close_count:
        res += '”' * (open_count - close_count)

    return res


def italicize_academic_latin_terms(text: str) -> str:
    """
    Auto-italicizes standard academic Latin terms (et al., ibid., de facto, ad hoc, vice versa, a priori)
    outside of existing HTML tags or code blocks.
    """
    if not text:
        return ""

    latin_terms = [
        r'\bet\s+al\.(?!\<\/em\>)',
        r'\bibid\.(?!\<\/em\>)',
        r'\bde\s+facto(?!\<\/em\>)',
        r'\bad\s+hoc(?!\<\/em\>)',
        r'\bvice\s+versa(?!\<\/em\>)',
        r'\ba\s+priori(?!\<\/em\>)',
        r'\bpassim(?!\<\/em\>)',
    ]

    pattern = re.compile(r'(' + '|'.join(latin_terms) + r')', re.IGNORECASE)

    tokens = re.split(r'(<[^>]+>)', text)
    processed = []
    in_code = False

    for token in tokens:
        if token.startswith("<"):
            if "<code" in token or "<pre" in token:
                in_code = True
            elif "</code" in token or "</pre" in token:
                in_code = False
            processed.append(token)
        else:
            if not in_code:
                token = pattern.sub(r'<em>\1</em>', token)
            processed.append(token)

    return "".join(processed)


def wrap_glossary_terms(text: str, glossary: Dict[str, str]) -> str:
    """
    Wraps known academic glossary terms outside of HTML tags and code blocks with <dfn title="..."> tags.
    """
    if not text or not glossary:
        return text or ""

    sorted_terms = sorted(glossary.keys(), key=len, reverse=True)
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted_terms) + r')\b', re.IGNORECASE)

    tokens = re.split(r'(<[^>]+>)', text)
    processed = []
    in_code = False
    in_link = False

    for token in tokens:
        if token.startswith("<"):
            lower = token.lower()
            if "<code" in lower or "<pre" in lower:
                in_code = True
            elif "</code" in lower or "</pre" in lower:
                in_code = False
            elif "<a" in lower:
                in_link = True
            elif "</a" in lower:
                in_link = False
            processed.append(token)
        else:
            if not in_code and not in_link:
                def replace_term(m):
                    matched = m.group(1)
                    meaning = glossary.get(matched) or glossary.get(matched.lower()) or glossary.get(matched.upper())
                    if not meaning:
                        for k, v in glossary.items():
                            if k.lower() == matched.lower():
                                meaning = v
                                break
                    if meaning:
                        return f'<dfn title="{meaning}">{matched}</dfn>'
                    return matched

                token = pattern.sub(replace_term, token)
            processed.append(token)

    return "".join(processed)


def parse_indonesian_formal_date(date_str: str) -> Optional[Dict[str, Any]]:
    """
    Parses formal Indonesian date string (e.g., 'Senin, 14 Oktober 2024 15:30 WIB'
    or '25 Desember 2024') into structured date fields and ISO format.
    """
    if not date_str:
        return None

    months_map = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12"
    }

    pattern = re.compile(
        r'(?:(Senin|Selasa|Rabu|Kamis|Jumat|Jum\'at|Sabtu|Minggu),\s*)?'
        r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})'
        r'(?:\s+(\d{1,2}:\d{2})(?:\s*(WIB|WITA|WIT))?)?',
        re.IGNORECASE
    )

    match = pattern.search(date_str.strip())
    if not match:
        return None

    day_name = match.group(1).capitalize() if match.group(1) else None
    day_num = int(match.group(2))
    month_name = match.group(3).lower()
    year_num = int(match.group(4))
    time_str = match.group(5)
    tz_str = match.group(6)

    month_code = months_map.get(month_name)
    if not month_code or not (1 <= day_num <= 31):
        return None

    iso_date = f"{year_num:04d}-{month_code}-{day_num:02d}"
    iso_str = f"{iso_date}T{time_str}:00" if time_str else iso_date

    return {
        "day_name": day_name,
        "day": day_num,
        "month_name": match.group(3).capitalize(),
        "month": int(month_code),
        "year": year_num,
        "time": time_str,
        "timezone": tz_str.upper() if tz_str else None,
        "iso_date": iso_str
    }


def extract_research_cluster_tags(text: str) -> List[str]:
    """
    Extracts faculty research cluster tags based on Telkom Purwokerto Informatics clusters.
    """
    if not text:
        return []

    clusters = {
        "Artificial Intelligence & Data Science": [
            r"\b(machine\s+learning|deep\s+learning|kecerdasan\s+buatan|nlp|computer\s+vision|data\s+science|neural\s+network|llm|generative\s+ai)\b"
        ],
        "Cybersecurity & Networks": [
            r"\b(cybersecurity|keamanan\s+siber|jaringan|penetration\s+testing|cryptography|kriptografi|firewall|infosec|network\s+security)\b"
        ],
        "Software Engineering & Cloud Computing": [
            r"\b(software\s+engineering|rekayasa\s+perangkat\s+lunak|cloud\s+computing|microservices|devops|ci/cd|kubernetes|docker|rest\s+api)\b"
        ],
        "Internet of Things & Embedded Systems": [
            r"\b(internet\s+of\s+things|iot|embedded\s+system|sistem\s+tertanam|sensor|microcontroller|arduino|esp32|raspberry\s+pi)\b"
        ],
    }

    matched_clusters = []
    clean_text = re.sub(r'<[^>]+>', ' ', text).lower()

    for cluster_name, patterns in clusters.items():
        for pat in patterns:
            if re.search(pat, clean_text, re.IGNORECASE):
                matched_clusters.append(cluster_name)
                break

    return matched_clusters


def normalize_nested_list_indentation(markdown_text: str) -> str:
    """
    Normalizes markdown list indentation to standard 2-space increments for nested lists.
    """
    if not markdown_text:
        return ""

    lines = markdown_text.splitlines()
    normalized_lines = []

    list_item_re = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.*)$')

    for line in lines:
        m = list_item_re.match(line)
        if m:
            raw_indent = m.group(1).replace('\t', '  ')
            bullet = m.group(2)
            content = m.group(3)
            indent_level = len(raw_indent) // 2
            norm_indent = '  ' * indent_level
            normalized_lines.append(f"{norm_indent}{bullet} {content}")
        else:
            normalized_lines.append(line)

    return "\n".join(normalized_lines)


def calculate_total_sks_credits(text: str) -> Dict[str, Any]:
    """
    Parses mentions of SKS (Sistem Kredit Semester) in curriculum descriptions
    and computes total credits across theoretical and practical courses.
    """
    if not text:
        return {"total_sks": 0, "theory_sks": 0, "practical_sks": 0, "mentions_count": 0}

    pattern = re.compile(r'(\d+)\s*(?:SKS|sks)(?:\s*(teori|praktikum|lapangan|workshop))?', re.IGNORECASE)

    total_sks = 0
    theory_sks = 0
    practical_sks = 0
    mentions_count = 0

    for match in pattern.finditer(text):
        val = int(match.group(1))
        modality = (match.group(2) or "").lower()
        mentions_count += 1
        total_sks += val

        if modality in ("praktikum", "lapangan", "workshop"):
            practical_sks += val
        elif modality == "teori":
            theory_sks += val
        else:
            theory_sks += val

    return {
        "total_sks": total_sks,
        "theory_sks": theory_sks,
        "practical_sks": practical_sks,
        "mentions_count": mentions_count
    }


def validate_academic_advisor_credentials(text: str) -> List[Dict[str, Any]]:
    """
    Extracts names of academic supervisors or thesis examiners with their credentials/degrees
    and validates postgraduate credential qualifications.
    """
    if not text:
        return []

    pattern = re.compile(
        r'^[ \t]*(Pembimbing(?:\s+[12I|II])?|Penguji(?:\s+[123I|II|III])?|Dosen\s+Wali|Promotor)\s*:\s*'
        r'([^\n\r]+)',
        re.MULTILINE
    )

    results = []
    for match in pattern.finditer(text):
        role = match.group(1).strip()
        full_name_with_degrees = match.group(2).strip()

        has_doctorate = bool(re.search(r'(?:Dr\.|Ph\.D\.|Prof\.)', full_name_with_degrees))
        has_masters = bool(re.search(r'(?:M\.[A-Za-z.]+|M\.Sc\.|M\.T\.|M\.Kom\.)', full_name_with_degrees))

        results.append({
            "role": role,
            "raw_name": full_name_with_degrees,
            "has_doctorate": has_doctorate,
            "has_masters": has_masters,
            "is_qualified_for_defense": has_doctorate or has_masters
        })

    return results


def expand_academic_acronyms(text: str, custom_acronyms: Optional[Dict[str, str]] = None) -> str:
    """
    Expands common higher-education Indonesian academic acronyms into structured abbr tags.
    """
    if not text:
        return ""

    defaults = {
        "MBKM": "Merdeka Belajar Kampus Merdeka",
        "KRS": "Kartu Rencana Studi",
        "KHS": "Kartu Hasil Studi",
        "BAP": "Berita Acara Perkuliahan",
        "KKN": "Kuliah Kerja Nyata",
        "TA": "Tugas Akhir / Skripsi",
        "PKL": "Praktik Kerja Lapangan",
        "SKPI": "Surat Keterangan Pendamping Ijazah",
        "SKS": "Sistem Kredit Semester",
    }
    if custom_acronyms:
        defaults.update(custom_acronyms)

    sorted_keys = sorted(defaults.keys(), key=len, reverse=True)
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted_keys) + r')\b')

    tokens = re.split(r'(<[^>]+>)', text)
    processed = []
    in_code = False

    for token in tokens:
        if token.startswith("<"):
            lower = token.lower()
            if "<code" in lower or "<pre" in lower:
                in_code = True
            elif "</code" in lower or "</pre" in lower:
                in_code = False
            processed.append(token)
        else:
            if not in_code:
                def replace_acr(m):
                    term = m.group(1)
                    exp = defaults.get(term)
                    return f'<abbr title="{exp}">{term}</abbr>' if exp else term
                token = pattern.sub(replace_acr, token)
            processed.append(token)

    return "".join(processed)


def normalize_code_block_language_tags(markdown_text: str) -> str:
    """
    Normalizes markdown code fence language aliases to canonical identifiers.
    """
    if not markdown_text:
        return ""

    lang_aliases = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "sh": "bash",
        "shell": "bash",
        "yml": "yaml",
        "golang": "go",
        "rs": "rust",
        "rb": "ruby",
        "cs": "csharp",
        "cpp": "cpp",
        "c++": "cpp",
        "htm": "html"
    }

    def replace_fence(m):
        prefix = m.group(1)
        fence = m.group(2)
        raw_lang = m.group(3).lower()
        canon_lang = lang_aliases.get(raw_lang, raw_lang)
        return f"{prefix}{fence}{canon_lang}"

    return re.sub(r'(^|\n)(```|~~~)([a-zA-Z0-9_+-]+)(?=\s|$)', replace_fence, markdown_text)


def parse_curriculum_semester_plan(text_or_markdown: str) -> List[Dict[str, Any]]:
    """
    Parses curriculum semester study plans extracting semester numbers,
    courses, course codes, SKS credit weights, and elective flags.
    """
    if not text_or_markdown:
        return []

    sem_pattern = re.compile(r'(?:###?\s*|Semester\s+)(\d+)', re.IGNORECASE)
    course_pattern = re.compile(
        r'[-*]\s*([A-Z]{2,4}\d{3,4})?\s*([^(]+?)\s*\(\s*(\d+)\s*(?:SKS|sks)\s*\)(?:\s*\[(Wajib|Pilihan|Elective)\])?',
        re.IGNORECASE
    )

    results: List[Dict[str, Any]] = []
    current_sem: Optional[int] = None
    current_courses: List[Dict[str, Any]] = []

    for line in text_or_markdown.splitlines():
        line_str = line.strip()
        sem_match = sem_pattern.search(line_str)
        if sem_match and ("semester" in line_str.lower() or line_str.startswith("#")):
            if current_sem is not None:
                tot_credits = sum(c["credits"] for c in current_courses)
                results.append({
                    "semester": current_sem,
                    "courses": current_courses,
                    "total_credits": tot_credits
                })
            current_sem = int(sem_match.group(1))
            current_courses = []
            continue

        if current_sem is not None:
            c_match = course_pattern.search(line_str)
            if c_match:
                code = (c_match.group(1) or "").strip()
                name = c_match.group(2).strip()
                credits = int(c_match.group(3))
                flag = (c_match.group(4) or "").lower()
                is_elective = flag in ("pilihan", "elective")
                current_courses.append({
                    "code": code,
                    "name": name,
                    "credits": credits,
                    "is_elective": is_elective
                })

    if current_sem is not None:
        tot_credits = sum(c["credits"] for c in current_courses)
        results.append({
            "semester": current_sem,
            "courses": current_courses,
            "total_credits": tot_credits
        })

    return results


def parse_lab_safety_guidelines(content: str) -> List[Dict[str, str]]:
    """
    Parses laboratory safety instructions and emergency rules into categorized guideline entries.
    Categories include: APD (PPE), Bahaya Listrik/Alat (Equipment/Electrical),
    Tanggap Darurat (Emergency), and Tata Tertib (Protocol).
    """
    if not content:
        return []

    lines = content.splitlines()
    guidelines: List[Dict[str, str]] = []

    cat_map = {
        "apd": "Alat Pelindung Diri (APD)",
        "ppe": "Alat Pelindung Diri (APD)",
        "bahaya": "Pencegahan Bahaya",
        "hazard": "Pencegahan Bahaya",
        "darurat": "Tanggap Darurat",
        "emergency": "Tanggap Darurat",
        "tata tertib": "Tata Tertib Laboratorium",
        "protokol": "Tata Tertib Laboratorium",
    }

    current_cat = "Tata Tertib Laboratorium"

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        cat_match = re.search(r'(?:[#*]{1,3}\s*|\*\*)([A-Za-z\s/]+?)(?:\*\*|:|$)', line_clean)
        if cat_match:
            candidate = cat_match.group(1).strip().lower()
            for key, val in cat_map.items():
                if key in candidate:
                    current_cat = val
                    break
            continue

        item_match = re.match(r'^(?:[-*+]|\d+\.)\s+(.*)$', line_clean)
        if item_match:
            guidelines.append({
                "category": current_cat,
                "rule": item_match.group(1).strip()
            })

    return guidelines


def validate_and_format_bibliographic_ids(text: str) -> Dict[str, List[str]]:
    """
    Extracts, validates, and normalizes standard academic bibliographic identifiers
    (ISBN-10, ISBN-13, and ISSN) from citations and textbook bibliographies.
    """
    if not text:
        return {"isbn": [], "issn": []}

    isbn_pattern = re.compile(
        r'\b(?:ISBN(?:-1[03])?:?\s*)?((?:97[89][-\s]?)?\d{1,5}[-\s]?\d+[-\s]?\d+[-\s]?[0-9X])\b',
        re.IGNORECASE
    )
    issn_pattern = re.compile(
        r'\b(?:ISSN:?\s*)?(\d{4}[-\s]?\d{3}[0-9X])\b',
        re.IGNORECASE
    )

    found_isbns: List[str] = []
    found_issns: List[str] = []

    # Match ISSN first
    for m in issn_pattern.finditer(text):
        raw = m.group(1).replace("-", "").replace(" ", "").upper()
        if len(raw) == 8 and ("issn" in text[max(0, m.start()-10):m.end()+10].lower() or "-" in m.group(1)):
            formatted = f"{raw[:4]}-{raw[4:]}"
            if formatted not in found_issns:
                found_issns.append(formatted)

    # Match ISBN
    for m in isbn_pattern.finditer(text):
        raw = m.group(1).replace("-", "").replace(" ", "").upper()
        if len(raw) in (10, 13):
            if len(raw) == 13 and (raw.startswith("978") or raw.startswith("979")):
                formatted = f"{raw[:3]}-{raw[3:5]}-{raw[5:10]}-{raw[10:12]}-{raw[12]}"
                if formatted not in found_isbns:
                    found_isbns.append(formatted)
            elif len(raw) == 10:
                formatted = f"{raw[:2]}-{raw[2:6]}-{raw[6:9]}-{raw[9]}"
                if formatted not in found_isbns:
                    found_isbns.append(formatted)

    return {"isbn": found_isbns, "issn": found_issns}


def parse_academic_calendar_range(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses formal Indonesian academic calendar date ranges (single month or cross-month/year).
    Examples:
      - '12 - 24 Agustus 2026'
      - '28 Juli - 15 Agustus 2026'
      - '15 Desember 2026 - 10 Januari 2027'
    """
    if not text:
        return None

    from datetime import date

    months_map = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4,
        "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12
    }

    pattern_cross = re.compile(
        r'(\d{1,2})\s+([A-Za-z]+)(?:\s+(\d{4}))?\s*[-–—]\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',
        re.IGNORECASE
    )
    pattern_single = re.compile(
        r'(\d{1,2})\s*[-–—]\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',
        re.IGNORECASE
    )

    m_cross = pattern_cross.search(text.strip())
    if m_cross:
        d1 = int(m_cross.group(1))
        m1_name = m_cross.group(2).lower()
        y1 = int(m_cross.group(3)) if m_cross.group(3) else int(m_cross.group(6))
        d2 = int(m_cross.group(4))
        m2_name = m_cross.group(5).lower()
        y2 = int(m_cross.group(6))

        if m1_name in months_map and m2_name in months_map:
            mo1 = months_map[m1_name]
            mo2 = months_map[m2_name]
            try:
                dt1 = date(y1, mo1, d1)
                dt2 = date(y2, mo2, d2)
                span = (dt2 - dt1).days + 1
                return {
                    "start_day": d1, "start_month": mo1, "start_year": y1,
                    "end_day": d2, "end_month": mo2, "end_year": y2,
                    "start_iso": dt1.isoformat(),
                    "end_iso": dt2.isoformat(),
                    "days_span": span
                }
            except ValueError:
                pass

    m_single = pattern_single.search(text.strip())
    if m_single:
        d1 = int(m_single.group(1))
        d2 = int(m_single.group(2))
        m_name = m_single.group(3).lower()
        y = int(m_single.group(4))

        if m_name in months_map:
            mo = months_map[m_name]
            try:
                dt1 = date(y, mo, d1)
                dt2 = date(y, mo, d2)
                span = (dt2 - dt1).days + 1
                return {
                    "start_day": d1, "start_month": mo, "start_year": y,
                    "end_day": d2, "end_month": mo, "end_year": y,
                    "start_iso": dt1.isoformat(),
                    "end_iso": dt2.isoformat(),
                    "days_span": span
                }
            except ValueError:
                pass

    return None


def parse_lab_inventory_specs(text: str) -> List[Dict[str, Any]]:
    """
    Parses laboratory equipment inventory records from markdown tables or bulleted specifications.
    Extracts item name, category, quantity, condition/status, and hardware specifications.
    """
    if not text:
        return []

    results: List[Dict[str, Any]] = []

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]

    if len(table_lines) >= 3:
        for row_str in table_lines[2:]:
            cells = [c.strip() for c in row_str.split("|")[1:-1]]
            if len(cells) < 2:
                continue
            name = cells[0]
            cat = cells[1] if len(cells) > 1 else "Peralatan Umum"
            qty_str = cells[2] if len(cells) > 2 else "1"
            qty_match = re.search(r'\d+', qty_str)
            qty = int(qty_match.group(0)) if qty_match else 1
            cond = cells[3] if len(cells) > 3 else "Baik / Siap Pakai"
            specs = cells[4] if len(cells) > 4 else ""

            results.append({
                "name": name,
                "category": cat,
                "quantity": qty,
                "condition": cond,
                "specs": specs
            })
        if results:
            return results

    bullet_pattern = re.compile(
        r'[-*]\s*([^:\[(]+?)(?::\s*(\d+)\s*(?:unit|buah)?)?(?:\s*\[(?:Kondisi:\s*)?([^\]]+)\])?(?:\s*\(([^)]+)\))?$',
        re.MULTILINE
    )
    for m in bullet_pattern.finditer(text):
        name = m.group(1).strip()
        if not name or name.startswith("|"):
            continue
        qty = int(m.group(2)) if m.group(2) else 1
        cond = m.group(3).strip() if m.group(3) else "Baik / Siap Pakai"
        specs = m.group(4).strip() if m.group(4) else ""
        results.append({
            "name": name,
            "category": "Peralatan Laboratorium",
            "quantity": qty,
            "condition": cond,
            "specs": specs
        })

    return results


def parse_apa_journal_citations(text: str) -> List[Dict[str, Any]]:
    """
    Parses APA 7th edition journal article citations from reference lists.
    Extracts authors, publication year, article title, journal name, volume, issue, pages, and DOI.
    """
    if not text:
        return []

    pattern = re.compile(
        r'([A-Za-z\s,\.&-]+?)\s*\((19\d{2}|20\d{2})\)\.\s*'
        r'([^.]+?\??)\.\s*'
        r'([A-Za-z0-9\s,\.&-]+?),\s*'
        r'(\d+)(?:\((\d+)\))?,\s*'
        r'(\d+[-–]\d+)\.?'
        r'(?:\s*(https?://(?:dx\.)?doi\.org/[^\s]+|doi:[^\s]+))?',
        re.MULTILINE
    )

    results: List[Dict[str, Any]] = []
    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        m = pattern.search(line_clean)
        if m:
            authors_str = m.group(1).strip()
            year = int(m.group(2))
            title = m.group(3).strip()
            journal = m.group(4).strip()
            volume = m.group(5).strip()
            issue = m.group(6).strip() if m.group(6) else None
            pages = m.group(7).strip()
            doi = m.group(8).strip() if m.group(8) else None

            results.append({
                "authors": authors_str,
                "year": year,
                "title": title,
                "journal": journal,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "doi": doi
            })

    return results


def parse_defense_rubric_criteria(text: str) -> List[Dict[str, Any]]:
    """
    Parses capstone/thesis defense rubric evaluation components from markdown tables or lists.
    Extracts assessment criteria name, weight percentage, target CPL, and description.
    """
    if not text:
        return []

    results: List[Dict[str, Any]] = []

    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    if len(table_lines) >= 3:
        for row in table_lines[2:]:
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if len(cells) < 2:
                continue
            name = cells[0]
            pct_m = re.search(r'(\d+)\s*%', cells[1])
            weight = int(pct_m.group(1)) if pct_m else 0
            cpl = cells[2] if len(cells) > 2 else "CPL Umum"
            desc = cells[3] if len(cells) > 3 else ""
            results.append({
                "criteria": name,
                "weight_percentage": weight,
                "cpl_target": cpl,
                "description": desc
            })
        if results:
            return results

    list_pattern = re.compile(
        r'[-*]\s*([^(\[]+?)(?:\s*\(\s*(\d+)\s*%\s*\))?(?:\s*\[([^\]]+)\])?(?::\s*(.*))?$',
        re.MULTILINE
    )
    for m in list_pattern.finditer(text):
        name = m.group(1).strip()
        if not name or name.startswith("|"):
            continue
        weight = int(m.group(2)) if m.group(2) else 0
        cpl = m.group(3).strip() if m.group(3) else "CPL Umum"
        desc = m.group(4).strip() if m.group(4) else ""
        results.append({
            "criteria": name,
            "weight_percentage": weight,
            "cpl_target": cpl,
            "description": desc
        })

    return results


def convert_indonesian_grade_letter(letter_grade: str) -> Optional[Dict[str, Any]]:
    """
    Converts Indonesian higher education letter grade (A, AB, B, BC, C, D, E)
    to standard 4.0 numerical scale and qualitative predicate.
    """
    if not letter_grade:
        return None

    clean = letter_grade.strip().upper()
    grade_table = {
        "A": {"point": 4.0, "predicate": "Sangat Baik Sekali (Istimewa)", "passing": True},
        "AB": {"point": 3.5, "predicate": "Sangat Baik", "passing": True},
        "B": {"point": 3.0, "predicate": "Baik", "passing": True},
        "BC": {"point": 2.5, "predicate": "Cukup Baik", "passing": True},
        "C": {"point": 2.0, "predicate": "Cukup", "passing": True},
        "D": {"point": 1.0, "predicate": "Kurang", "passing": False},
        "E": {"point": 0.0, "predicate": "Gagal", "passing": False},
    }

    if clean not in grade_table:
        return None

    entry = grade_table[clean]
    return {
        "letter": clean,
        "gpa_point": entry["point"],
        "predicate": entry["predicate"],
        "is_passing": entry["passing"]
    }


def calculate_weighted_semester_gpa(courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates weighted Grade Point Average (IPK/IPS) from a list of courses with SKS credits and letter grades.
    """
    total_credits = 0
    total_points = 0.0

    for c in courses:
        credits = int(c.get("credits", 0))
        grade_str = str(c.get("grade", ""))
        grade_info = convert_indonesian_grade_letter(grade_str)
        if grade_info and credits > 0:
            total_credits += credits
            total_points += credits * grade_info["gpa_point"]

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    if gpa >= 3.51:
        standing = "Dengan Pujian (Cum Laude)"
    elif gpa >= 3.00:
        standing = "Sangat Memuaskan"
    elif gpa >= 2.50:
        standing = "Memuaskan"
    elif gpa >= 2.00:
        standing = "Cukup"
    else:
        standing = "Percobaan (Perlu Perbaikan)"

    return {
        "total_credits": total_credits,
        "total_grade_points": round(total_points, 2),
        "gpa": gpa,
        "academic_standing": standing
    }


def parse_ieee_journal_citation(citation_text: str) -> Optional[Dict[str, Any]]:
    """
    Parses IEEE journal transaction and conference proceedings citation string
    into a structured bibliographic dictionary.
    """
    if not citation_text:
        return None

    clean = citation_text.strip()
    title_match = re.search(r'["“]([^"”]+)["”]', clean)
    if not title_match:
        return None

    title = title_match.group(1).strip().rstrip(",")
    before_title = clean[:title_match.start()].strip().rstrip(",")
    after_title = clean[title_match.end():].strip().lstrip(",").strip()

    author_str = before_title
    authors = [a.strip() for a in re.split(r',?\s+(?:and|&)\s+|,\s+', author_str) if a.strip()]

    doi = ""
    doi_match = re.search(r'(?:doi:\s*|https?://doi\.org/)(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', after_title, re.IGNORECASE)
    if doi_match:
        doi = doi_match.group(1).rstrip(".")

    vol = ""
    vol_match = re.search(r'\bvol\.\s*(\d+)', after_title, re.IGNORECASE)
    if vol_match:
        vol = vol_match.group(1)

    issue = ""
    issue_match = re.search(r'\bno\.\s*(\d+)', after_title, re.IGNORECASE)
    if issue_match:
        issue = issue_match.group(1)

    pages = ""
    pages_match = re.search(r'\bpp?\.\s*([\d-]+)', after_title, re.IGNORECASE)
    if pages_match:
        pages = pages_match.group(1)

    year = 0
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', after_title)
    if year_match:
        year = int(year_match.group(1))

    journal_part = after_title
    for token in ["vol.", "no.", "pp.", "doi:"]:
        idx = journal_part.lower().find(token)
        if idx != -1:
            journal_part = journal_part[:idx]
    journal = journal_part.strip().rstrip(",").strip()

    return {
        "authors": authors,
        "title": title,
        "journal": journal,
        "volume": vol,
        "issue": issue,
        "pages": pages,
        "year": year,
        "doi": doi
    }


def parse_laboratory_sop(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses laboratory standard operating procedure (SOP / IK) text
    into a structured dictionary of metadata, hazard level, and numbered steps.
    """
    if not text:
        return None

    clean = text.strip()
    code_match = re.search(r'\b(SOP-[A-Z0-9-]+|IK-[A-Z0-9-]+)\b', clean, re.IGNORECASE)
    sop_code = code_match.group(1).upper() if code_match else "SOP-LAB-001"

    hazard = "Sedang"
    if re.search(r'\b(?:bahaya\s+tinggi|high\s+hazard|level\s+3)\b', clean, re.IGNORECASE):
        hazard = "Tinggi"
    elif re.search(r'\b(?:bahaya\s+rendah|low\s+hazard|level\s+1)\b', clean, re.IGNORECASE):
        hazard = "Rendah"

    title = ""
    title_match = re.search(r'(?:judul|prosedur|nama\s+sop)\s*:\s*([^\n\r]+)', clean, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        first_line = clean.splitlines()[0].strip()
        title = re.sub(r'^(?:SOP-[A-Z0-9-]+\s*[:\-]?\s*)', '', first_line).strip()

    step_pattern = re.compile(r'^\s*(\d+)[\.\)]\s+(.+)$', re.MULTILINE)
    steps = []
    for m in step_pattern.finditer(clean):
        num = int(m.group(1))
        desc = m.group(2).strip()
        has_warning = bool(re.search(r'\b(?:peringatan|perhatian|awas|hazard|danger)\b', desc, re.IGNORECASE))
        steps.append({
            "step_number": num,
            "instruction": desc,
            "has_safety_warning": has_warning
        })

    if not steps:
        return None

    return {
        "sop_code": sop_code,
        "title": title,
        "hazard_level": hazard,
        "total_steps": len(steps),
        "steps": steps
    }


def parse_scholarship_eligibility(criteria_text: str) -> Dict[str, Any]:
    """
    Parses scholarship call-for-application bullet points or free text
    into a structured qualification profile.
    """
    if not criteria_text:
        return {
            "min_gpa": 0.0,
            "target_semesters": [],
            "required_documents": [],
            "requires_interview": False,
            "is_full_coverage": False
        }

    clean = criteria_text.strip()

    gpa = 0.0
    gpa_match = re.search(r'(?:ipk|gpa)\s*(?:minimal|min|&gt;=|>=)?\s*([234]\.\d{1,2})', clean, re.IGNORECASE)
    if gpa_match:
        gpa = float(gpa_match.group(1))

    semesters = []
    sem_range_match = re.search(r'semester\s*([1-8])\s*[-–]\s*([1-8])', clean, re.IGNORECASE)
    if sem_range_match:
        s1 = int(sem_range_match.group(1))
        s2 = int(sem_range_match.group(2))
        semesters = list(range(s1, s2 + 1))
    else:
        for m in re.finditer(r'semester\s*([1-8])\b', clean, re.IGNORECASE):
            semesters.append(int(m.group(1)))
        semesters = sorted(list(set(semesters)))

    doc_keywords = {
        "KTM / Kartu Tanda Mahasiswa": ["ktm", "kartu tanda mahasiswa"],
        "Transkrip Nilai": ["transkrip", "khs", "transkrip nilai"],
        "Surat Rekomendasi Dosen": ["surat rekomendasi", "rekomendasi dosen", "rekomendasi kaprodi"],
        "Sertifikat Prestasi / Portofolio": ["sertifikat", "portofolio", "piagam"],
        "Surat Keterangan Tidak Mampu (SKTM)": ["sktm", "tidak mampu"],
        "Motivation Letter": ["motivation letter", "surat motivasi", "esai"]
    }
    required_docs = []
    for doc_name, kw_list in doc_keywords.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', clean, re.IGNORECASE) for kw in kw_list):
            required_docs.append(doc_name)

    requires_interview = bool(re.search(r'\b(?:wawancara|interview|tahap\s+wawancara)\b', clean, re.IGNORECASE))
    is_full = bool(re.search(r'\b(?:full\s+coverage|bebas\s+bpp\s+100%|penuh|beasiswa\s+penuh)\b', clean, re.IGNORECASE))

    return {
        "min_gpa": gpa,
        "target_semesters": semesters,
        "required_documents": required_docs,
        "requires_interview": requires_interview,
        "is_full_coverage": is_full
    }


def calculate_sks_to_ects(sks_credits: int, ects_ratio: float = 1.6) -> Dict[str, Any]:
    """
    Calculates Indonesian national credit system (SKS) to European Credit Transfer
    and Accumulation System (ECTS) conversion along with student workload hours.
    Standard ratio: 1 SKS ≈ 1.6 ECTS (based on Permendikbudristek learning workload standards).
    """
    sks = max(0, int(sks_credits))
    ratio = float(ects_ratio) if ects_ratio > 0 else 1.6
    ects = round(sks * ratio, 1)

    workload_hours = round(sks * 45.33, 1)

    return {
        "sks_credits": sks,
        "ects_ratio": ratio,
        "ects_credits": ects,
        "workload_hours_per_semester": workload_hours,
        "workload_hours_per_week": round((workload_hours / 16), 1) if sks > 0 else 0.0
    }


def parse_acm_citation(citation_str: str) -> Dict[str, Any]:
    """
    Parses ACM reference citations from academic publications into structured fields.
    Extracts author list, publication year, paper title, conference/journal name, pages, and DOI.
    """
    if not citation_str or not citation_str.strip():
        return {
            "authors": [],
            "year": None,
            "title": "",
            "publication": "",
            "pages": "",
            "doi": ""
        }

    clean = citation_str.strip()

    doi = ""
    doi_match = re.search(r'https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', clean)
    if doi_match:
        doi = doi_match.group(0)
        clean = clean.replace(doi_match.group(0), "").strip()

    year = None
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', clean)
    if year_match:
        year = int(year_match.group(1))

    authors: List[str] = []
    title = ""
    publication = ""
    pages = ""

    if year_match:
        y_start = year_match.start()
        y_end = year_match.end()
        raw_authors = clean[:y_start].rstrip(". ,")
        raw_rest = clean[y_end:].lstrip(". ,")

        raw_authors_list = [a.strip() for a in re.split(r'\band\b|,', raw_authors) if a.strip()]
        authors = raw_authors_list

        pages_match = re.search(r'\b(\d+[-–]\d+)\b', raw_rest)
        if pages_match:
            pages = pages_match.group(1).replace("–", "-")

        in_match = re.search(r'\bIn\s+', raw_rest, re.IGNORECASE)
        if in_match:
            title = raw_rest[:in_match.start()].rstrip(". ,")
            pub_part = raw_rest[in_match.end():]
            pub_match = re.split(r'\bACM\b|\b\d+[-–]\d+\b', pub_part)
            publication = pub_match[0].rstrip(". ,")
        else:
            parts = [p.strip() for p in raw_rest.split(".") if p.strip()]
            if parts:
                title = parts[0]
            if len(parts) > 1:
                publication = parts[1]

    return {
        "authors": authors,
        "year": year,
        "title": title.strip(),
        "publication": publication.strip(),
        "pages": pages.strip(),
        "doi": doi.strip()
    }


def calculate_defense_rubric_grade(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates weighted final numerical grade, Indonesian standard letter grade (A - E),
    grade point equivalence (4.00 - 0.00), and pass/fail accreditation status
    from thesis defense examination rubric assessment criteria.
    """
    if not scores:
        return {
            "total_score": 0.0,
            "letter_grade": "E",
            "grade_point": 0.0,
            "is_passed": False,
            "predicate": "Tidak Lulus",
            "criteria_breakdown": []
        }

    total_weight = 0.0
    weighted_sum = 0.0
    breakdown = []

    for item in scores:
        crit = str(item.get("criteria", "Komponen"))
        weight = float(item.get("weight_pct", 0.0))
        raw_score = float(item.get("score", 0.0))
        weighted_val = (weight / 100.0) * raw_score
        weighted_sum += weighted_val
        total_weight += weight
        breakdown.append({
            "criteria": crit,
            "weight_pct": weight,
            "raw_score": raw_score,
            "weighted_score": round(weighted_val, 2)
        })

    # Normalize if total weight is around 100
    final_score = round(weighted_sum, 2)
    if total_weight > 0 and abs(total_weight - 100.0) > 0.01:
        # Scale to 100% basis if weights do not sum to 100
        final_score = round((weighted_sum / total_weight) * 100.0, 2)

    if final_score >= 80.0:
        letter = "A"
        gp = 4.00
        predicate = "Lulus Sangat Memuaskan (Cumlaude)"
        passed = True
    elif final_score >= 75.0:
        letter = "AB"
        gp = 3.50
        predicate = "Lulus Memuaskan"
        passed = True
    elif final_score >= 70.0:
        letter = "B"
        gp = 3.00
        predicate = "Lulus Baik"
        passed = True
    elif final_score >= 65.0:
        letter = "BC"
        gp = 2.50
        predicate = "Lulus Cukup Baik"
        passed = True
    elif final_score >= 60.0:
        letter = "C"
        gp = 2.00
        predicate = "Lulus Cukup"
        passed = True
    elif final_score >= 50.0:
        letter = "D"
        gp = 1.00
        predicate = "Tidak Lulus (Wajib Mengulang)"
        passed = False
    else:
        letter = "E"
        gp = 0.00
        predicate = "Tidak Lulus (Gagal)"
        passed = False

    return {
        "total_score": final_score,
        "letter_grade": letter,
        "grade_point": gp,
        "is_passed": passed,
        "predicate": predicate,
        "criteria_breakdown": breakdown
    }


def parse_internship_weekly_logbook(logbook_markdown: str) -> List[Dict[str, Any]]:
    """
    Parses MBKM (Merdeka Belajar Kampus Merdeka) or industrial internship weekly logbook reports.
    Extracts week number, date range, activities, competencies acquired, and supervisor approval status.
    """
    if not logbook_markdown or not logbook_markdown.strip():
        return []

    entries: List[Dict[str, Any]] = []
    # Split by week header: e.g., '### Minggu 1' or '## Week 1' or 'Minggu 1:'
    sections = re.split(r'(?m)^#{2,4}\s*(?:Minggu|Week)\s*(\d+)', logbook_markdown.strip())

    if len(sections) > 1:
        # sections[0] is preamble before first week
        for i in range(1, len(sections), 2):
            w_num = int(sections[i])
            w_content = sections[i + 1] if i + 1 < len(sections) else ""

            # Extract date range from first line or parentheses
            date_range = ""
            date_match = re.search(r'\(([^)]+)\)', w_content.split("\n")[0])
            if date_match:
                date_range = date_match.group(1).strip()

            # Extract activities
            activities = ""
            act_match = re.search(r'(?:Aktivitas|Kegiatan|Activities):\s*([^\n]+)', w_content, re.IGNORECASE)
            if act_match:
                activities = act_match.group(1).strip()
            else:
                # Fallback to bullet points
                bullets = re.findall(r'^[*-]\s+(.+)$', w_content, re.MULTILINE)
                if bullets:
                    activities = "; ".join(b.strip() for b in bullets if not re.match(r'^(?:Kompetensi|Status):', b, re.IGNORECASE))

            # Extract competencies
            competencies = []
            comp_match = re.search(r'(?:Kompetensi|Skills?):\s*([^\n]+)', w_content, re.IGNORECASE)
            if comp_match:
                competencies = [c.strip() for c in comp_match.group(1).split(",") if c.strip()]

            # Extract approval status
            status = "Pending"
            is_approved = False
            stat_match = re.search(r'(?:Status|Approval):\s*([^\n]+)', w_content, re.IGNORECASE)
            if stat_match:
                raw_stat = stat_match.group(1).strip()
                status = raw_stat
                if re.search(r'\b(?:disetujui|approved|acc|valid)\b', raw_stat, re.IGNORECASE):
                    is_approved = True

            entries.append({
                "week_number": w_num,
                "date_range": date_range,
                "activities": activities,
                "competencies": competencies,
                "status": status,
                "is_approved": is_approved
            })

    return entries


def parse_lab_equipment_maintenance_log(log_text: str) -> Dict[str, Any]:
    """
    Parses laboratory equipment maintenance, repair, and calibration incident logs.
    Extracts equipment name, asset ID, maintenance date, technician, issue, resolution,
    calibration expiration date, and operational readiness status.
    """
    if not log_text or not log_text.strip():
        return {
            "equipment_name": "",
            "equipment_id": "",
            "maintenance_date": "",
            "technician": "",
            "issue": "",
            "resolution": "",
            "calibration_validity": "",
            "status": "Unknown",
            "is_operational": False
        }

    clean = log_text.strip()

    eq_match = re.search(r'(?:Equipment|Alat|Perangkat):\s*([^\n]+)', clean, re.IGNORECASE)
    raw_eq = eq_match.group(1).strip() if eq_match else ""
    eq_name = raw_eq
    eq_id = ""
    # Extract asset ID from parentheses or bracket
    id_m = re.search(r'\(([^)]+)\)|\[([^\]]+)\]', raw_eq)
    if id_m:
        eq_id = (id_m.group(1) or id_m.group(2)).strip()
        eq_name = re.sub(r'\s*\([^)]+\)|\s*\[[^\]]+\]', '', raw_eq).strip()

    date_match = re.search(r'(?:Date|Tanggal):\s*([^\n]+)', clean, re.IGNORECASE)
    m_date = date_match.group(1).strip() if date_match else ""

    tech_match = re.search(r'(?:Technician|Teknisi|Petugas):\s*([^\n]+)', clean, re.IGNORECASE)
    technician = tech_match.group(1).strip() if tech_match else ""

    issue_match = re.search(r'(?:Issue|Kerusakan|Kendala|Masalah):\s*([^\n]+)', clean, re.IGNORECASE)
    issue = issue_match.group(1).strip() if issue_match else ""

    res_match = re.search(r'(?:Resolution|Tindakan|Solusi|Perbaikan):\s*([^\n]+)', clean, re.IGNORECASE)
    resolution = res_match.group(1).strip() if res_match else ""

    cal_match = re.search(r'(?:Calibration Validity|Masa Kalibrasi|Valid Hingga):\s*([^\n]+)', clean, re.IGNORECASE)
    cal_valid = cal_match.group(1).strip() if cal_match else ""

    stat_match = re.search(r'(?:Status|Kondisi):\s*([^\n]+)', clean, re.IGNORECASE)
    status = stat_match.group(1).strip() if stat_match else "Normal"

    is_operational = bool(re.search(r'\b(?:operasional|siap|ready|baik|normal|passed)\b', status, re.IGNORECASE)) and not bool(re.search(r'\b(?:rusak|trouble|mati|kritis|unusable)\b', status, re.IGNORECASE))

    return {
        "equipment_name": eq_name,
        "equipment_id": eq_id,
        "maintenance_date": m_date,
        "technician": technician,
        "issue": issue,
        "resolution": resolution,
        "calibration_validity": cal_valid,
        "status": status,
        "is_operational": is_operational
    }


def parse_springer_citation(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses Springer LNCS / CCIS / IFIP academic conference and book chapter citations.
    Standard pattern: Authors: Title. In: Editors (eds.) BookTitle. LNCS, vol. N, pp. X-Y. Springer (Year). DOI
    """
    clean = text.strip()
    if not clean:
        return None

    doi_m = re.search(r'(?:https?://doi\.org/|doi:\s*)(10\.\d{4,9}/[^\s;,]+)', clean, re.IGNORECASE)
    doi = doi_m.group(1).rstrip('.') if doi_m else ""

    year_m = re.search(r'\((19\d{2}|20\d{2})\)', clean)
    year = int(year_m.group(1)) if year_m else None

    pages_m = re.search(r'(?:pp\.?|pages)\s*([0-9]+[\s–\-]+[0-9]+)', clean, re.IGNORECASE)
    pages = pages_m.group(1).replace("–", "-").replace(" ", "") if pages_m else ""

    vol_m = re.search(r'(?:vol\.?|volume)\s*([0-9]+)', clean, re.IGNORECASE)
    volume = int(vol_m.group(1)) if vol_m else None

    series_m = re.search(r'\b(LNCS|LNAI|LNBI|CCIS|IFIP AICT|AISC|Lecture Notes in [A-Za-z\s]+)\b', clean, re.IGNORECASE)
    series = series_m.group(1).strip() if series_m else ""

    in_idx = clean.lower().find(". in:")
    if in_idx != -1:
        before_in = clean[:in_idx].strip()
        after_in = clean[in_idx + 5:].strip()
    else:
        before_in = clean
        after_in = ""

    if ":" in before_in:
        parts = before_in.split(":", 1)
        authors = parts[0].strip()
        title = parts[1].strip().strip('.')
    elif "." in before_in:
        parts = before_in.split(".", 1)
        authors = parts[0].strip()
        title = parts[1].strip().strip('.')
    else:
        authors = before_in
        title = ""

    book_title = ""
    if after_in:
        book_match = re.search(r'^(?:[^.]+\(eds?\.\)\s*)?([^.]+)\.', after_in)
        if book_match:
            book_title = book_match.group(1).strip()
        else:
            book_title = after_in.split(".")[0].strip()

    return {
        "authors": authors,
        "title": title,
        "book_title": book_title,
        "series": series,
        "volume": volume,
        "pages": pages,
        "year": year,
        "doi": doi,
        "publisher": "Springer"
    }


def parse_proposal_defense_eligibility(
    checklist_text: str,
    earned_sks: int,
    ipk: float,
    toefl_score: int
) -> Dict[str, Any]:
    """
    Validates academic proposal defense (Seminar Proposal Tugas Akhir) eligibility against
    department graduation criteria (minimum 100 SKS, minimum IPK 2.75, minimum TOEFL/EPR 450,
    and administrative clearances).
    """
    clean_text = checklist_text.strip()
    sks_ok = earned_sks >= 100
    ipk_ok = ipk >= 2.75
    toefl_ok = toefl_score >= 450

    missing: List[str] = []
    if not sks_ok:
        missing.append(f"SKS belum mencukupi (diperoleh: {earned_sks}, minimal: 100)")
    if not ipk_ok:
        missing.append(f"IPK belum mencukupi (diperoleh: {ipk:.2f}, minimal: 2.75)")
    if not toefl_ok:
        missing.append(f"Skor TOEFL/EPR belum mencukupi (diperoleh: {toefl_score}, minimal: 450)")

    checks = {
        "krs_approved": bool(re.search(r'\b(?:krs\s*(?:disetujui|acc|valid|disahkan)|krs\s*ok)\b', clean_text, re.IGNORECASE)),
        "lab_clearance": bool(re.search(r'\b(?:bebas\s*lab|lab\s*(?:clearance|selesai|bebas))\b', clean_text, re.IGNORECASE)),
        "library_clearance": bool(re.search(r'\b(?:bebas\s*perpustakaan|bebas\s*perpus|library\s*clearance)\b', clean_text, re.IGNORECASE)),
        "advisory_sessions": bool(re.search(r'\b(?:bimbingan\s*(?:min(?:imal)?\s*8|selesai|acc|cukup)|kartu\s*bimbingan)\b', clean_text, re.IGNORECASE))
    }

    if not checks["krs_approved"]:
        missing.append("KRS Tugas Akhir belum disetujui dosen wali")
    if not checks["lab_clearance"]:
        missing.append("Surat bebas tanggungan laboratorium belum lengkap")
    if not checks["library_clearance"]:
        missing.append("Surat bebas perpustakaan belum lengkap")
    if not checks["advisory_sessions"]:
        missing.append("Log bimbingan minimal 8 kali belum terpenuhi")

    is_eligible = bool(sks_ok and ipk_ok and toefl_ok and all(checks.values()))

    return {
        "is_eligible": is_eligible,
        "earned_sks": int(earned_sks),
        "ipk": float(ipk),
        "toefl_score": int(toefl_score),
        "sks_passed": sks_ok,
        "ipk_passed": ipk_ok,
        "toefl_passed": toefl_ok,
        "administrative_checks": checks,
        "missing_requirements": missing
    }


def parse_community_service_log(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses community service (Pengabdian kepada Masyarakat - PKM) activity reports and logs,
    extracting title, partner organization, regency/district location, funding scheme,
    beneficiary counts, and Sustainable Development Goals (SDGs) category.
    """
    clean = text.strip()
    if not clean:
        return None

    title_m = re.search(r'(?:Judul|Title|Kegiatan):\s*([^\n]+)', clean, re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else clean.split('\n')[0].strip()

    partner_m = re.search(r'(?:Mitra|Partner|Sasaran):\s*([^\n]+)', clean, re.IGNORECASE)
    partner = partner_m.group(1).strip() if partner_m else ""

    loc_m = re.search(r'(?:Lokasi|Location|Tempat|Kabupaten|Desa):\s*([^\n]+)', clean, re.IGNORECASE)
    location = loc_m.group(1).strip() if loc_m else ""

    fund_m = re.search(r'(?:Sumber Dana|Funding|Skema Dana|Pendanaan):\s*([^\n]+)', clean, re.IGNORECASE)
    funding_source = fund_m.group(1).strip() if fund_m else "Internal Perguruan Tinggi"

    ben_m = re.search(r'(?:Jumlah Penerima|Penerima Manfaat|Peserta|Beneficiaries):\s*(\d+)', clean, re.IGNORECASE)
    beneficiaries = int(ben_m.group(1)) if ben_m else 0

    sdg_m = re.search(r'(?:SDGs?|Tujuan SDGs?):\s*([^\n]+)', clean, re.IGNORECASE)
    sdgs_label = sdg_m.group(1).strip() if sdg_m else ""
    if not sdgs_label:
        if re.search(r'\b(?:pendidikan|literasi|sekolah|guru|siswa|pelatihan coding)\b', clean, re.IGNORECASE):
            sdgs_label = "SDG 4 - Pendidikan Berkualitas"
        elif re.search(r'\b(?:teknologi|iot|digitalisasi|industri|inovasi|umkm digital)\b', clean, re.IGNORECASE):
            sdgs_label = "SDG 9 - Industri, Inovasi, dan Infrastruktur"
        elif re.search(r'\b(?:kesehatan|posyandu|stunting|medis|lansia)\b', clean, re.IGNORECASE):
            sdgs_label = "SDG 3 - Kehidupan Sehat dan Sejahtera"
        else:
            sdgs_label = "SDG 11 - Kota dan Komunitas Berkelanjutan"

    return {
        "title": title,
        "partner": partner,
        "location": location,
        "funding_source": funding_source,
        "beneficiaries_count": beneficiaries,
        "sdgs_theme": sdgs_label
    }


def parse_lab_safety_inspection(text: str) -> Dict[str, Any]:
    """
    Parses laboratory occupational safety & health (K3 Laboratorium) inspection checklists,
    evaluating fire extinguisher (APAR) readiness, emergency exit, first aid kit (P3K),
    electrical installations, ventilation, and overall compliance score.
    """
    clean = text.strip()

    lab_m = re.search(r'(?:Lab|Laboratorium):\s*([^\n]+)', clean, re.IGNORECASE)
    lab_name = lab_m.group(1).strip() if lab_m else "Laboratorium Komputer"

    inspector_m = re.search(r'(?:Inspektur|Pemeriksa|Auditor|Teknisi):\s*([^\n]+)', clean, re.IGNORECASE)
    inspector = inspector_m.group(1).strip() if inspector_m else "Petugas K3"

    date_m = re.search(r'(?:Tanggal|Date):\s*([^\n]+)', clean, re.IGNORECASE)
    inspection_date = date_m.group(1).strip() if date_m else ""

    apar_ok = bool(re.search(r'\b(?:apar|pemadam)\s*:\s*(?:siap|lengkap|aktif|layak|ok|passed)\b', clean, re.IGNORECASE)) or (
        "apar siap" in clean.lower() or "apar layak" in clean.lower()
    )
    first_aid_ok = bool(re.search(r'\b(?:p3k|first aid|kotak obat)\s*:\s*(?:lengkap|siap|tersedia|ok|passed)\b', clean, re.IGNORECASE)) or (
        "p3k lengkap" in clean.lower() or "p3k tersedia" in clean.lower()
    )
    exit_ok = bool(re.search(r'\b(?:jalur evakuasi|emergency exit|pintu darurat)\s*:\s*(?:bersih|bebas hambatan|terbuka|clear|ok|passed)\b', clean, re.IGNORECASE)) or (
        "jalur evakuasi bebas hambatan" in clean.lower() or "pintu darurat clear" in clean.lower()
    )
    elec_ok = bool(re.search(r'\b(?:kelistrikan|kabel|instalasi listrik|grounding)\s*:\s*(?:aman|standar|tertata|rapi|ok|passed)\b', clean, re.IGNORECASE)) or (
        "listrik aman" in clean.lower() or "instalasi listrik rapi" in clean.lower()
    )

    items = {
        "apar_ready": apar_ok,
        "first_aid_complete": first_aid_ok,
        "emergency_exit_clear": exit_ok,
        "electrical_safe": elec_ok
    }

    passed_count = sum(1 for v in items.values() if v)
    total_count = len(items)
    score_pct = round((passed_count / total_count) * 100, 1)
    is_passed = bool(score_pct >= 75.0 and apar_ok)

    return {
        "lab_name": lab_name,
        "inspector": inspector,
        "inspection_date": inspection_date,
        "checks": items,
        "compliance_score": score_pct,
        "is_passed": is_passed
    }


def parse_harvard_citation(citation: str) -> Optional[Dict[str, Any]]:
    """
    Parses academic citations formatted in Harvard referencing style:
    Author, A.A. (Year) 'Title of article', Publication/Journal Title, Volume(Issue), pp. pages. doi/url.
    """
    clean = citation.strip()
    if not clean:
        return None

    # Match Author (Year) pattern
    author_year_m = re.match(r'^([^()]+?)\s*\((19\d{2}|20\d{2})\)\s*[\'"]?([^\'",\.\n]+)[\'"]?\s*[\.,]?(.*)$', clean, re.DOTALL)
    if not author_year_m:
        return None

    raw_authors = author_year_m.group(1).strip()
    year = int(author_year_m.group(2))
    title = author_year_m.group(3).strip()
    remainder = author_year_m.group(4).strip()

    # Extract DOI or URL if present
    doi_or_url = ""
    doi_m = re.search(r'(?:https?://[^\s]+|doi:\s*10\.[^\s]+|10\.\d{4,9}/[^\s]+)', remainder, re.IGNORECASE)
    if doi_m:
        doi_or_url = doi_m.group(0).rstrip('.,')
        remainder = remainder.replace(doi_m.group(0), "").strip()

    # Extract pages (pp. 120-135 or p. 45)
    pages = ""
    pages_m = re.search(r'\bpp?\.\s*([0-9]+(?:\s*[-–]\s*[0-9]+)?)', remainder, re.IGNORECASE)
    if pages_m:
        pages = pages_m.group(1).replace(" ", "")
        remainder = re.sub(r'\bpp?\.\s*[0-9]+(?:\s*[-–]\s*[0-9]+)?', '', remainder, flags=re.IGNORECASE).strip()

    # Extract volume/issue e.g., 15(2) or 15
    volume_issue = ""
    vol_m = re.search(r'\b(\d+(?:\(\d+\))?)', remainder)
    if vol_m:
        volume_issue = vol_m.group(1)
        remainder = remainder.replace(vol_m.group(0), "").strip()

    # Publication / venue
    publication = remainder.strip(' ,.')

    # Parse authors into list
    authors = [a.strip() for a in re.split(r'\s+and\s+|;\s*|(?<=[A-Z]\.),\s*', raw_authors) if a.strip()]

    return {
        "authors": authors,
        "year": year,
        "title": title,
        "publication": publication,
        "volume_issue": volume_issue,
        "pages": pages,
        "doi_or_url": doi_or_url,
        "raw_citation": clean
    }


def validate_mbkm_credit_transfer(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates MBKM (Merdeka Belajar Kampus Merdeka) external course credit transfers,
    calculating total converted SKS, weighted grade point average, and verifying curriculum cap (max 20 SKS).
    """
    program_name = str(data.get("program_name", "")).strip()
    partner = str(data.get("partner_institution", "")).strip()
    student_name = str(data.get("student_name", "")).strip()
    nim = str(data.get("nim", "")).strip()
    semester = int(data.get("semester", 6))
    courses = data.get("courses_mapped", [])

    issues = []
    if not program_name:
        issues.append("Nama program MBKM tidak boleh kosong")
    if not student_name or not nim:
        issues.append("Identitas mahasiswa (nama dan NIM) wajib diisi")

    grade_point_map = {
        "A": 4.0, "AB": 3.5, "B": 3.0, "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0
    }

    total_sks = 0
    weighted_points = 0.0
    normalized_courses = []

    for c in courses:
        code = str(c.get("course_code", "")).strip()
        name = str(c.get("course_name", "")).strip()
        sks = int(c.get("sks", 0))
        letter = str(c.get("score_letter", "A")).strip().upper()

        if sks <= 0:
            issues.append(f"Mata kuliah {code or name} memiliki bobot SKS tidak valid ({sks})")
            continue

        num_val = grade_point_map.get(letter, float(c.get("score_num", 4.0)))
        total_sks += sks
        weighted_points += (sks * num_val)

        normalized_courses.append({
            "course_code": code,
            "course_name": name,
            "sks": sks,
            "score_letter": letter,
            "score_num": num_val
        })

    if total_sks > 20:
        issues.append(f"Total SKS transfer ({total_sks} SKS) melebihi batas regulasi MBKM (maksimal 20 SKS)")
    elif total_sks == 0:
        issues.append("Belum ada mata kuliah yang diekivalensikan")

    converted_gpa = round(weighted_points / total_sks, 2) if total_sks > 0 else 0.0
    is_approved = bool(len(issues) == 0 and total_sks > 0 and total_sks <= 20)

    return {
        "is_approved": is_approved,
        "program_name": program_name,
        "partner_institution": partner,
        "student_name": student_name,
        "nim": nim,
        "semester": semester,
        "total_sks": total_sks,
        "converted_gpa": converted_gpa,
        "courses": normalized_courses,
        "issues": issues
    }


def parse_lab_equipment_log(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses laboratory equipment asset inventory and calibration audit records,
    extracting equipment model, barcode ID, lab room, operating condition, and calibration validity.
    """
    clean = text.strip()
    if not clean:
        return None

    id_m = re.search(r'(?:ID(?:\s*Aset)?|Barcode|Kode(?:\s*Alat)?):\s*([A-Za-z0-9_-]+)', clean, re.IGNORECASE)
    asset_id = id_m.group(1).strip() if id_m else "EQ-GEN-001"

    name_m = re.search(r'(?:Nama(?:\s*Alat)?|Equipment|Perangkat):\s*([^\n]+)', clean, re.IGNORECASE)
    equipment_name = name_m.group(1).strip() if name_m else clean.split('\n')[0].strip()

    lab_m = re.search(r'(?:Lab(?:oratorium)?|Ruangan|Room):\s*([^\n]+)', clean, re.IGNORECASE)
    lab_name = lab_m.group(1).strip() if lab_m else "Laboratorium Telekomunikasi"

    brand_m = re.search(r'(?:Merk|Brand|Model|Tipe):\s*([^\n]+)', clean, re.IGNORECASE)
    brand_model = brand_m.group(1).strip() if brand_m else ""

    cal_m = re.search(r'(?:Tgl\s*Kalibrasi|Tanggal\s*Kalibrasi|Last\s*Calibrated):\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', clean, re.IGNORECASE)
    calibration_date = cal_m.group(1).strip() if cal_m else ""

    due_m = re.search(r'(?:Jatuh\s*Tempo|Due\s*Date|Exp(?:ired)?(?:\s*Date)?):\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', clean, re.IGNORECASE)
    due_date = due_m.group(1).strip() if due_m else ""

    cond_m = re.search(r'(?:Kondisi|Condition|Status(?:\s*Fisik)?):\s*([^\n]+)', clean, re.IGNORECASE)
    raw_cond = cond_m.group(1).strip().lower() if cond_m else "baik"
    if "rusak berat" in raw_cond or "broken" in raw_cond:
        operating_condition = "Rusak Berat"
    elif "rusak ringan" in raw_cond or "minor" in raw_cond:
        operating_condition = "Rusak Ringan"
    else:
        operating_condition = "Baik"

    pic_m = re.search(r'(?:PIC|Penanggung\s*Jawab|Laboran|Teknisi):\s*([^\n]+)', clean, re.IGNORECASE)
    pic = pic_m.group(1).strip() if pic_m else "Laboran"

    # Calibration status evaluation
    cal_status = "Not Calibrated"
    if calibration_date and due_date:
        import datetime
        today_str = datetime.date.today().isoformat()
        cal_status = "Valid" if due_date >= today_str else "Expired"
    elif calibration_date:
        cal_status = "Valid"

    return {
        "asset_id": asset_id,
        "equipment_name": equipment_name,
        "lab_name": lab_name,
        "brand_model": brand_model,
        "calibration_date": calibration_date,
        "calibration_due_date": due_date,
        "operating_condition": operating_condition,
        "calibration_status": cal_status,
        "pic": pic
    }


def validate_yudisium_clearance(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates student undergraduate graduation (Yudisium) clearance checklist:
    minimum 144 SKS, GPA >= 2.00, no E grades, D grades <= 6 SKS, TOEFL >= 450,
    extracurricular SKK points >= 40, and administrative clearances.
    """
    student_name = str(data.get("student_name", "")).strip()
    nim = str(data.get("nim", "")).strip()
    sks = int(data.get("earned_sks", 0))
    ipk = float(data.get("ipk", 0.0))
    sks_d = int(data.get("sks_d", 0))
    sks_e = int(data.get("sks_e", 0))
    toefl = int(data.get("toefl_score", 0))
    skk_points = int(data.get("skk_points", 0))

    admin_clearances = {
        "library_clearance": bool(data.get("library_clearance", False)),
        "lab_clearance": bool(data.get("lab_clearance", False)),
        "tuition_clearance": bool(data.get("tuition_clearance", False)),
        "thesis_repository_uploaded": bool(data.get("thesis_repository_uploaded", False))
    }

    issues = []
    if sks < 144:
        issues.append(f"Jumlah SKS kelulusan belum terpenuhi ({sks}/144 SKS)")
    if ipk < 2.00:
        issues.append(f"IPK kumulatif di bawah ambang batas minimal ({ipk:.2f}/2.00)")
    if sks_e > 0:
        issues.append(f"Terdapat nilai E sebanyak {sks_e} SKS yang belum diulang")
    if sks_d > 6:
        issues.append(f"Total nilai D ({sks_d} SKS) melebihi batas maksimal regulasi (6 SKS)")
    if toefl < 450:
        issues.append(f"Skor EPR/TOEFL belum memenuhi standar minimum prodi ({toefl}/450)")
    if skk_points < 40:
        issues.append(f"Poin SKK kegiatan kemahasiswaan belum mencukupi ({skk_points}/40 poin)")

    for check_key, passed in admin_clearances.items():
        if not passed:
            human_label = check_key.replace("_", " ").title()
            issues.append(f"Verifikasi berkas {human_label} belum disetujui")

    predicate = "Tidak Lulus"
    if ipk >= 3.51:
        predicate = "Dengan Pujian (Cum Laude)"
    elif ipk >= 3.01:
        predicate = "Sangat Memuaskan"
    elif ipk >= 2.76:
        predicate = "Memuaskan"
    elif ipk >= 2.00:
        predicate = "Cukup"

    is_eligible = bool(len(issues) == 0 and sks >= 144 and ipk >= 2.00)

    return {
        "is_eligible": is_eligible,
        "student_name": student_name,
        "nim": nim,
        "earned_sks": sks,
        "ipk": ipk,
        "graduation_predicate": predicate if is_eligible else "Belum Memenuhi Syarat",
        "administrative_clearances": admin_clearances,
        "issues": issues
    }


def parse_vancouver_citations(text: str) -> List[Dict[str, Any]]:
    """
    Parses Vancouver biomedical/clinical academic reference citations into structured elements.
    Format: [1] Author AA, Author BB. Article title. Abbr Journal Name. Year;Volume(Issue):Pages. doi:10.xxx
    """
    if not text:
        return []

    pattern = re.compile(
        r'^(?:\[?(\d+)\]?\.?\s*)?'
        r'([A-Za-z\s,\.\'-]+?)\.\s*'
        r'([^.]+?\??)\.\s*'
        r'([A-Za-z0-9\s,\.&-]+?)\.\s*'
        r'(19\d{2}|20\d{2});'
        r'(\d+)(?:\((\d+)\))?:'
        r'(\d+[-–]\d+)\.?'
        r'(?:\s*(?:doi:\s*|https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+))?',
        re.MULTILINE
    )

    results = []
    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        m = pattern.search(line_clean)
        if m:
            idx = int(m.group(1)) if m.group(1) else len(results) + 1
            raw_authors = m.group(2).strip()
            authors = [a.strip() for a in re.split(r',\s*', raw_authors) if a.strip()]
            title = m.group(3).strip()
            journal = m.group(4).strip()
            year = int(m.group(5))
            vol = m.group(6).strip()
            issue = m.group(7).strip() if m.group(7) else None
            pages = m.group(8).strip()
            doi = m.group(9).strip() if m.group(9) else None

            results.append({
                "citation_index": idx,
                "authors": authors,
                "title": title,
                "journal": journal,
                "year": year,
                "volume": vol,
                "issue": issue,
                "pages": pages,
                "doi": doi
            })

    return results


def audit_academic_probation_status(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits student semester standing and evaluates academic probation / warning status (Surat Peringatan SP).
    Evaluates against minimum credit benchmarks per semester (Semester 2: 24 SKS, Sem 4: 48 SKS, Sem 6: 72 SKS, Sem 8: 96 SKS)
    and GPA threshold (IPK >= 2.00, IPS >= 2.00).
    """
    name = student_data.get("student_name", "").strip()
    nim = student_data.get("nim", "").strip()
    sem = int(student_data.get("semester", 1))
    ipk = float(student_data.get("gpa_cumulative", 0.0))
    ips = float(student_data.get("gpa_semester", 0.0))
    sks = int(student_data.get("earned_credits", 0))
    prev_sp = int(student_data.get("sp_history", 0))

    reasons = []
    min_sks_threshold = 0

    if sem >= 8:
        min_sks_threshold = 96
    elif sem >= 6:
        min_sks_threshold = 72
    elif sem >= 4:
        min_sks_threshold = 48
    elif sem >= 2:
        min_sks_threshold = 24

    remedial_sks_needed = max(0, min_sks_threshold - sks)

    if remedial_sks_needed > 0:
        reasons.append(f"Perolehan SKS ({sks} SKS) belum mencapai batas minimum semester {sem} ({min_sks_threshold} SKS).")

    if ipk < 2.00:
        reasons.append(f"IPK kumulatif ({ipk:.2f}) di bawah batas kelulusan akademik 2.00.")

    if ips < 2.00:
        reasons.append(f"IPS semester berjalan ({ips:.2f}) di bawah standar performa 2.00.")

    if not reasons:
        status = "CLEAR"
        counseling_required = False
    elif prev_sp >= 2:
        status = "CRITICAL_DO"
        counseling_required = True
    elif prev_sp == 1:
        status = "WARNING_2"
        counseling_required = True
    elif ipk < 2.00 or remedial_sks_needed >= 12:
        status = "PROBATION"
        counseling_required = True
    else:
        status = "WARNING_1"
        counseling_required = True

    return {
        "student_name": name,
        "nim": nim,
        "semester": sem,
        "gpa_cumulative": ipk,
        "gpa_semester": ips,
        "earned_credits": sks,
        "min_credits_required": min_sks_threshold,
        "remedial_sks_needed": remedial_sks_needed,
        "status": status,
        "counseling_required": counseling_required,
        "reasons": reasons
    }


def evaluate_faculty_bkd_workload(faculty_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates faculty semester teaching and tridharma workload compliance under statutory BKD guidelines (Kemendikbudristek/LLDIKTI).
    Statutory criteria:
      - Total credits: 12.0 to 16.0 SKS
      - Pendidikan & Pengajaran: min 4.0 SKS
      - Penelitian: min 2.0 SKS
      - Pengabdian Masyarakat: min 0.5 SKS
      - Core Subtotal (Pendidikan + Penelitian): min 9.0 SKS
    """
    lecturer = faculty_data.get("lecturer_name", "").strip()
    nidn = faculty_data.get("nidn", "").strip()
    rank = faculty_data.get("academic_rank", "Asisten Ahli").strip()
    teaching = float(faculty_data.get("teaching_credits", 0.0))
    research = float(faculty_data.get("research_credits", 0.0))
    service = float(faculty_data.get("service_credits", 0.0))
    supporting = float(faculty_data.get("supporting_credits", 0.0))

    total = teaching + research + service + supporting
    core_subtotal = teaching + research

    issues = []
    if total < 12.0:
        issues.append(f"Total beban kerja ({total:.2f} SKS) kurang dari batas minimum perundangan (12.00 SKS).")
    elif total > 16.0:
        issues.append(f"Total beban kerja ({total:.2f} SKS) melebihi batas regulasi 16.00 SKS (kategori kelebihan beban).")

    if teaching < 4.0:
        issues.append(f"Beban Pengajaran ({teaching:.2f} SKS) di bawah batas minimal 4.00 SKS.")

    if research < 2.0:
        issues.append(f"Beban Penelitian ({research:.2f} SKS) di bawah batas minimal 2.00 SKS.")

    if service < 0.5:
        issues.append(f"Beban Pengabdian Masyarakat ({service:.2f} SKS) di bawah batas minimal 0.50 SKS.")

    if core_subtotal < 9.0:
        issues.append(f"Subtotal Tridharma Inti Pengajaran + Penelitian ({core_subtotal:.2f} SKS) di bawah minimal 9.00 SKS.")

    if total > 16.0:
        status = "LEBIH BEBAN"
        is_compliant = True
    elif len(issues) == 0:
        status = "MEMENUHI"
        is_compliant = True
    else:
        status = "TIDAK MEMENUHI"
        is_compliant = False

    return {
        "lecturer_name": lecturer,
        "nidn": nidn,
        "academic_rank": rank,
        "teaching_credits": teaching,
        "research_credits": research,
        "service_credits": service,
        "supporting_credits": supporting,
        "core_subtotal": core_subtotal,
        "total_sks": total,
        "is_compliant": is_compliant,
        "status": status,
        "issues": issues
    }


def parse_kkn_village_assignment(text: str) -> List[Dict[str, Any]]:
    """
    Parses student community engagement (KKN - Kuliah Kerja Nyata) assignment records from table or list format.
    Extracts group number/code, village, district, regency, faculty supervisor (DPL), student count, and theme.
    """
    if not text:
        return []

    results = []
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]

    if len(table_lines) >= 3:
        for row in table_lines[2:]:
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if len(cells) < 4:
                continue
            grp = cells[0]
            village = cells[1]
            district = cells[2]
            regency = cells[3]
            dpl = cells[4] if len(cells) > 4 else ""
            student_count_m = re.search(r'\d+', cells[5]) if len(cells) > 5 else None
            student_count = int(student_count_m.group(0)) if student_count_m else 10
            theme = cells[6] if len(cells) > 6 else "Pemberdayaan Masyarakat"

            results.append({
                "group_code": grp,
                "village_name": village,
                "district_name": district,
                "regency_name": regency,
                "supervisor_dpl": dpl,
                "student_count": student_count,
                "thematic_focus": theme
            })
        if results:
            return results

    bullet_re = re.compile(
        r'[-*]\s*(?:Kelompok\s+)?([A-Za-z0-9_-]+)\s*:\s*'
        r'Desa\s+([^,]+),\s*'
        r'Kec\.\s+([^,]+),\s*'
        r'Kab\.\s+([^|]+)'
        r'(?:\s*\|\s*DPL:\s*([^|]+))?'
        r'(?:\s*\|\s*(\d+)\s*(?:Mhs|Mahasiswa)?)?'
        r'(?:\s*\|\s*Tema:\s*(.*))?',
        re.IGNORECASE
    )

    for line in lines:
        m = bullet_re.search(line)
        if m:
            grp = m.group(1).strip()
            village = m.group(2).strip()
            district = m.group(3).strip()
            regency = m.group(4).strip()
            dpl = m.group(5).strip() if m.group(5) else ""
            student_count = int(m.group(6)) if m.group(6) else 10
            theme = m.group(7).strip() if m.group(7) else "Pemberdayaan Masyarakat"

            results.append({
                "group_code": grp,
                "village_name": village,
                "district_name": district,
                "regency_name": regency,
                "supervisor_dpl": dpl,
                "student_count": student_count,
                "thematic_focus": theme
            })

    return results


def normalize_ieee_doi(doi_or_url: str) -> Optional[Dict[str, Any]]:
    """
    Parses and normalizes a Digital Object Identifier (DOI), extracting prefix, suffix, and canonical URL.
    """
    if not doi_or_url or not isinstance(doi_or_url, str):
        return None

    cleaned = doi_or_url.strip()
    # Strip URL prefixes if present
    cleaned = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^doi:\s*', '', cleaned, flags=re.IGNORECASE).strip()

    doi_pattern = re.compile(r'^(10\.\d{4,9})/([-._;()/:A-Za-z0-9]+)$')
    match = doi_pattern.match(cleaned)
    if not match:
        return None

    prefix = match.group(1)
    suffix = match.group(2)
    canonical_doi = f"{prefix}/{suffix}"
    is_ieee = prefix.startswith("10.1109")

    return {
        "doi": canonical_doi,
        "prefix": prefix,
        "suffix": suffix,
        "canonical_url": f"https://doi.org/{canonical_doi}",
        "is_ieee": is_ieee
    }


def evaluate_bima_grant_proposal(
    scheme_name: str,
    requested_budget: float,
    lead_nidn: str,
    sinta_score_3yr: float,
    team_member_count: int
) -> Dict[str, Any]:
    """
    Evaluates research proposal compliance under Kemdikbud BIMA guidelines.
    """
    scheme = scheme_name.strip()
    norm_scheme = scheme.lower()

    scheme_limits = {
        "pdp": {"name": "Penelitian Dosen Pemula (PDP)", "max_budget": 25000000.0, "min_sinta": 50.0, "min_members": 1},
        "penelitian dosen pemula": {"name": "Penelitian Dosen Pemula (PDP)", "max_budget": 25000000.0, "min_sinta": 50.0, "min_members": 1},
        "penelitian terapan": {"name": "Penelitian Terapan (PT)", "max_budget": 150000000.0, "min_sinta": 150.0, "min_members": 1},
        "penelitian dasar": {"name": "Penelitian Dasar (PD)", "max_budget": 100000000.0, "min_sinta": 100.0, "min_members": 1},
        "penelitian kerjasama": {"name": "Penelitian Kerjasama Antar Perguruan Tinggi (PKPT)", "max_budget": 200000000.0, "min_sinta": 200.0, "min_members": 2},
        "penelitian pascasarjana": {"name": "Penelitian Tesis Magister (PTM)", "max_budget": 60000000.0, "min_sinta": 100.0, "min_members": 1}
    }

    config = None
    for k, v in scheme_limits.items():
        if k in norm_scheme:
            config = v
            break

    if not config:
        config = {"name": scheme, "max_budget": 100000000.0, "min_sinta": 100.0, "min_members": 1}

    max_budget = config["max_budget"]
    min_sinta = config["min_sinta"]
    min_members = config["min_members"]

    budget_compliant = float(requested_budget) <= max_budget
    sinta_compliant = float(sinta_score_3yr) >= min_sinta
    team_compliant = int(team_member_count) >= min_members
    is_eligible = budget_compliant and sinta_compliant and team_compliant

    remarks = []
    if not budget_compliant:
        remarks.append(f"Usulan anggaran Rp {requested_budget:,.0f} melebihi pagu maksimal skema (Rp {max_budget:,.0f}).")
    if not sinta_compliant:
        remarks.append(f"Skor SINTA 3 tahun ({sinta_score_3yr}) belum memenuhi ambang minimal skema ({min_sinta}).")
    if not team_compliant:
        remarks.append(f"Jumlah anggota tim ({team_member_count}) kurang dari ketentuan minimal ({min_members} anggota).")
    if is_eligible:
        remarks.append("Seluruh kriteria administratif dan substantif awal skema BIMA terpenuhi.")

    return {
        "scheme": config["name"],
        "is_eligible": is_eligible,
        "max_allowed_budget": max_budget,
        "requested_budget": float(requested_budget),
        "budget_compliant": budget_compliant,
        "sinta_compliant": sinta_compliant,
        "team_compliant": team_compliant,
        "remarks": remarks
    }


def evaluate_kerja_praktik_placement(
    company_name: str,
    duration_weeks: int,
    project_title: str,
    domain_keywords: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluates student Kerja Praktik (KP) internship company placement and project alignment.
    """
    company = company_name.strip()
    title = project_title.strip()
    title_lower = title.lower()

    standard_domains = [
        "jaringan", "network", "telekomunikasi", "telecom", "antenna", "antena",
        "fiber", "optik", "iot", "sensor", "wireless", "nirkabel", "5g", "4g",
        "rf", "cloud", "api", "software", "perangkat lunak", "ai", "machine learning",
        "keamanan", "security", "database", "data engineering", "devops", "server"
    ]
    check_keywords = domain_keywords if domain_keywords else standard_domains

    matched = [kw for kw in check_keywords if kw.lower() in title_lower]
    relevance_score = min(1.0, len(matched) * 0.35 + (0.3 if len(matched) > 0 else 0.0))

    duration_compliant = int(duration_weeks) >= 8
    domain_compliant = len(matched) > 0

    is_approved = duration_compliant and domain_compliant

    feedback = []
    if not duration_compliant:
        feedback.append(f"Durasi pelaksanaan KP ({duration_weeks} minggu) kurang dari standar minimal 8 minggu.")
    if not domain_compliant:
        feedback.append("Topik proyek belum mencerminkan kompetensi inti bidang teknik telekomunikasi / informatika.")
    if is_approved:
        feedback.append("Usulan tempat dan proyek Kerja Praktik memenuhi syarat kurikulum prodi.")

    return {
        "company_name": company,
        "project_title": title,
        "duration_weeks": int(duration_weeks),
        "duration_compliant": duration_compliant,
        "domain_compliant": domain_compliant,
        "relevance_score": round(relevance_score, 2),
        "matched_keywords": matched,
        "is_approved": is_approved,
        "feedback": " ".join(feedback)
    }


def parse_telecom_isr_frequency_allocation(text_or_markdown: str) -> List[Dict[str, Any]]:
    """
    Parses laboratory radio station license (ISR) and RF spectrum assignments.
    """
    if not text_or_markdown or not isinstance(text_or_markdown, str):
        return []

    results = []
    lines = [line.strip() for line in text_or_markdown.strip().splitlines() if line.strip()]

    def parse_freq_to_mhz(val_str: str) -> float:
        m = re.search(r'([\d.]+)\s*(ghz|mhz|khz)?', val_str, re.IGNORECASE)
        if not m:
            return 0.0
        val = float(m.group(1))
        unit = (m.group(2) or "mhz").lower()
        if unit == "ghz":
            return round(val * 1000.0, 2)
        elif unit == "khz":
            return round(val / 1000.0, 3)
        return round(val, 2)

    def parse_power_to_dbm(val_str: str) -> float:
        m = re.search(r'([\d.]+)\s*(dbm|w|mw)?', val_str, re.IGNORECASE)
        if not m:
            return 0.0
        val = float(m.group(1))
        unit = (m.group(2) or "dbm").lower()
        if unit == "w":
            import math
            return round(10 * math.log10(val * 1000.0), 1)
        elif unit == "mw":
            import math
            return round(10 * math.log10(val), 1)
        return round(val, 1)

    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    if len(table_lines) >= 3:
        for l in table_lines[2:]:
            cells = [c.strip() for c in l.split("|")[1:-1]]
            if len(cells) < 3:
                continue
            lab = cells[0]
            freq_mhz = parse_freq_to_mhz(cells[1])
            bw_mhz = parse_freq_to_mhz(cells[2]) if len(cells) > 2 else 20.0
            power_dbm = parse_power_to_dbm(cells[3]) if len(cells) > 3 else 20.0
            band = cells[4] if len(cells) > 4 else "Unspecified"
            status = cells[5] if len(cells) > 5 else "Aktif"

            results.append({
                "lab_name": lab,
                "center_freq_mhz": freq_mhz,
                "bandwidth_mhz": bw_mhz,
                "max_power_dbm": power_dbm,
                "band_designation": band,
                "status": status
            })
        if results:
            return results

    bullet_re = re.compile(
        r'[-*]\s*(?:\[([^\]]+)\]\s*)?([^:]+):\s*'
        r'([\d.]+\s*(?:GHz|MHz|kHz)?)\s*\|'
        r'(?:\s*(?:BW|Bandwidth):\s*([\d.]+\s*(?:MHz|kHz|GHz)?)\s*\|)?'
        r'(?:\s*(?:Power|Daya):\s*([\d.]+\s*(?:dBm|W|mW)?)\s*\|)?'
        r'(?:\s*(?:Band|Pita):\s*([^|]+)\s*\|)?'
        r'(?:\s*Status:\s*(.*))?',
        re.IGNORECASE
    )

    for line in lines:
        m = bullet_re.search(line)
        if m:
            lab = m.group(2).strip()
            freq_mhz = parse_freq_to_mhz(m.group(3))
            bw_mhz = parse_freq_to_mhz(m.group(4)) if m.group(4) else 20.0
            power_dbm = parse_power_to_dbm(m.group(5)) if m.group(5) else 20.0
            band = m.group(6).strip() if m.group(6) else "Unspecified"
            status = m.group(7).strip() if m.group(7) else "Aktif"

            results.append({
                "lab_name": lab,
                "center_freq_mhz": freq_mhz,
                "bandwidth_mhz": bw_mhz,
                "max_power_dbm": power_dbm,
                "band_designation": band,
                "status": status
            })

    return results


def parse_accreditation_status(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses study program accreditation status decrees from LAM INFOKOM or BAN-PT text.
    Extracts program name, accreditation agency, decree/SK number, rating, expiry date, and active status.
    """
    if not text:
        return None

    prog_m = re.search(r'(?:Program Studi|Prodi)\s*:\s*([^\n\r,;]+)', text, re.IGNORECASE)
    agency_m = re.search(r'(?:Lembaga Akreditasi|Badan Akreditasi|Akreditasi oleh)\s*:\s*(LAM-?INFOKOM|BAN-?PT)', text, re.IGNORECASE)
    if not agency_m:
        if "LAM-INFOKOM" in text.upper() or "LAM INFOKOM" in text.upper():
            agency = "LAM INFOKOM"
        elif "BAN-PT" in text.upper():
            agency = "BAN-PT"
        else:
            agency = "LAM INFOKOM"
    else:
        raw_ag = agency_m.group(1).upper()
        agency = "LAM INFOKOM" if "INFOKOM" in raw_ag else "BAN-PT"

    rating_m = re.search(r'(?:Peringkat|Status Akreditasi|Predikat)\s*:\s*(Unggul|Baik Sekali|Baik|Terakreditasi Sementara|A|B|C)\b', text, re.IGNORECASE)
    sk_m = re.search(r'(?:Nomor SK|No\.? SK|SK No\.?)\s*:\s*([A-Za-z0-9\/\.\-]+)', text, re.IGNORECASE)
    date_m = re.search(r'(?:Berlaku Hingga|Kedaluwarsa|Masa Berlaku|Berakhir)\s*:\s*(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE)

    if not rating_m and not sk_m:
        return None

    rating = rating_m.group(1).strip() if rating_m else "Unggul"
    sk_number = sk_m.group(1).strip() if sk_m else "N/A"
    program_name = prog_m.group(1).strip() if prog_m else "S1 Teknik Telekomunikasi"
    expiry_date = date_m.group(1).strip() if date_m else "2029-08-31"

    is_active = True
    if re.search(r'\b(?:kadaluwarsa|kedaluwarsa|expired|tidak aktif)\b', text, re.IGNORECASE):
        is_active = False

    return {
        "program_name": program_name,
        "agency": agency,
        "rating": rating,
        "sk_number": sk_number,
        "expiry_date": expiry_date,
        "is_active": is_active
    }


def parse_scholarship_allocation(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses student scholarship aid award allocation details.
    Extracts student name, NIM, scholarship scheme/type, sponsor name, amount, semester, and minimum GPA.
    """
    if not text:
        return None

    name_m = re.search(r'(?:Nama Mahasiswa|Penerima|Nama)\s*:\s*([^\n\r,;]+)', text, re.IGNORECASE)
    nim_m = re.search(r'(?:NIM|Nomor Induk Mahasiswa)\s*:\s*(\d{5,12})', text, re.IGNORECASE)
    scheme_m = re.search(r'(?:Skema Beasiswa|Jenis Beasiswa|Beasiswa)\s*:\s*([^\n\r,;]+)', text, re.IGNORECASE)
    sponsor_m = re.search(r'(?:Penyelenggara|Sponsor|Mitra)\s*:\s*([^\n\r,;]+)', text, re.IGNORECASE)
    amount_m = re.search(r'(?:Nominal|Besaran|Bantuan UKT|Dana)\s*:\s*(?:Rp\.?\s*)?([\d\.,]+)', text, re.IGNORECASE)
    sem_m = re.search(r'(?:Semester|Periode)\s*:\s*([^\n\r,;]+)', text, re.IGNORECASE)
    gpa_m = re.search(r'(?:IPK Minimal|IPK|Syarat IPK)\s*:\s*(\d+(?:[\.,]\d+)?)', text, re.IGNORECASE)

    if not nim_m and not scheme_m:
        return None

    amount = 0.0
    if amount_m:
        raw_amt = amount_m.group(1).replace('.', '').replace(',', '.')
        try:
            amount = float(raw_amt)
        except ValueError:
            amount = 0.0

    gpa = 3.0
    if gpa_m:
        raw_gpa = gpa_m.group(1).replace(',', '.')
        try:
            gpa = float(raw_gpa)
        except ValueError:
            gpa = 3.0

    return {
        "student_name": name_m.group(1).strip() if name_m else "Mahasiswa",
        "nim": nim_m.group(1).strip() if nim_m else "00000000",
        "scholarship_type": scheme_m.group(1).strip() if scheme_m else "Beasiswa Prestasi",
        "sponsor_name": sponsor_m.group(1).strip() if sponsor_m else "Yayasan Pendidikan Telkom",
        "amount_idr": amount,
        "semester": sem_m.group(1).strip() if sem_m else "Semester Ganjil 2026/2027",
        "minimum_gpa": gpa
    }


def calculate_optical_link_budget(
    fiber_length_km: float,
    attenuation_db_per_km: float = 0.25,
    num_splices: int = 2,
    splice_loss_db: float = 0.1,
    num_connectors: int = 2,
    connector_loss_db: float = 0.5,
    safety_margin_db: float = 3.0,
    tx_power_dbm: float = 0.0,
    rx_sensitivity_dbm: float = -28.0
) -> Dict[str, Any]:
    """
    Calculates telecommunication optical fiber transmission link budget and power margins.
    Computes total fiber attenuation, connector losses, splice losses, safety margin, and viability.
    """
    length = max(0.0, float(fiber_length_km))
    alpha = max(0.0, float(attenuation_db_per_km))
    n_splices = max(0, int(num_splices))
    loss_splice = max(0.0, float(splice_loss_db))
    n_conn = max(0, int(num_connectors))
    loss_conn = max(0.0, float(connector_loss_db))
    margin_safe = max(0.0, float(safety_margin_db))
    tx_pwr = float(tx_power_dbm)
    rx_sens = float(rx_sensitivity_dbm)

    total_fiber_loss = length * alpha
    total_splice_loss = n_splices * loss_splice
    total_connector_loss = n_conn * loss_conn
    total_loss_db = total_fiber_loss + total_splice_loss + total_connector_loss + margin_safe

    max_allowable_loss_db = tx_pwr - rx_sens
    power_margin_db = max_allowable_loss_db - total_loss_db
    is_viable = power_margin_db >= 0.0

    return {
        "fiber_length_km": round(length, 2),
        "total_fiber_loss_db": round(total_fiber_loss, 3),
        "total_splice_loss_db": round(total_splice_loss, 3),
        "total_connector_loss_db": round(total_connector_loss, 3),
        "safety_margin_db": round(margin_safe, 2),
        "total_attenuation_db": round(total_loss_db, 3),
        "allowed_optical_loss_db": round(max_allowable_loss_db, 2),
        "power_margin_db": round(power_margin_db, 3),
        "is_viable": is_viable
    }


def parse_djki_patent_grant(text: str) -> Optional[Dict[str, Any]]:
    """
    Parses Directorate General of Intellectual Property (DJKI) patent grant certificates and filings.
    Extracts patent title, registration/patent number, application number, filing date, grant date, inventors, and status.
    """
    if not text:
        return None

    title_m = re.search(r'(?:Judul Invensi|Judul Paten|Invensi)\s*:\s*([^\n\r;]+)', text, re.IGNORECASE)
    pat_num_m = re.search(r'(?:Nomor Paten|No\.? Paten|Paten No\.?)\s*:\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
    app_num_m = re.search(r'(?:Nomor Permohonan|No\.? Permohonan|Permohonan No\.?)\s*:\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
    filing_m = re.search(r'(?:Tanggal Penerimaan|Tanggal Permohonan|Filing Date)\s*:\s*(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE)
    grant_m = re.search(r'(?:Tanggal Pemberian|Tanggal Granted|Grant Date)\s*:\s*(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE)
    inv_m = re.search(r'(?:Inventor|Nama Inventor|Penemu)\s*:\s*([^\n\r;]+)', text, re.IGNORECASE)
    type_m = re.search(r'(?:Jenis Paten|Tipe Paten)\s*:\s*(Paten Biasa|Paten Sederhana)', text, re.IGNORECASE)
    status_m = re.search(r'(?:Status Paten|Status Permohonan|Status)\s*:\s*(Granted|Terdaftar|Pemeriksaan Substantif|Dalam Proses|Ditolak)\b', text, re.IGNORECASE)

    if not pat_num_m and not app_num_m and not title_m:
        return None

    inventors: List[str] = []
    if inv_m:
        raw_inv = inv_m.group(1).strip()
        if ";" in raw_inv:
            parts = [i.strip() for i in raw_inv.split(";") if i.strip()]
        elif re.search(r'\s+dan\s+', raw_inv, re.IGNORECASE):
            parts = [i.strip() for i in re.split(r'\s+dan\s+', raw_inv, flags=re.IGNORECASE) if i.strip()]
        else:
            parts = [raw_inv]
        inventors = [p.strip().rstrip(",") for p in parts if p.strip()]


    return {
        "patent_title": title_m.group(1).strip() if title_m else "Invensi Sistem IoT dan Telekomunikasi",
        "patent_number": pat_num_m.group(1).strip() if pat_num_m else None,
        "application_number": app_num_m.group(1).strip() if app_num_m else "P000000000",
        "filing_date": filing_m.group(1).strip() if filing_m else "2025-01-01",
        "grant_date": grant_m.group(1).strip() if grant_m else None,
        "inventors": inventors if inventors else ["Tim Peneliti"],
        "patent_type": type_m.group(1).strip() if type_m else "Paten Sederhana",
        "status": status_m.group(1).strip() if status_m else ("Granted" if pat_num_m else "Dalam Proses")
    }


def evaluate_cum_laude_predicate(
    ipk: float,
    study_duration_semesters: int,
    has_failing_grades: bool = False,
    has_disciplinary_violations: bool = False
) -> Dict[str, Any]:
    """
    Evaluates undergraduate graduation judiciary cum laude honor predicate based on
    Indonesian academic governance and university judiciary guidelines.
    Criteria:
    - Summa Cum Laude: IPK >= 3.90, study duration <= 8 semesters, no failing grades (C/D/E), no disciplinary violations.
    - Magna Cum Laude: IPK >= 3.75, study duration <= 8 semesters, no failing grades, no disciplinary violations.
    - Cum Laude: IPK >= 3.51, study duration <= 8 semesters, no failing grades, no disciplinary violations.
    - Sangat Memuaskan: IPK >= 3.00 (or if disqualified from Cum Laude due to duration or repeat courses).
    - Memuaskan: IPK >= 2.75.
    - Cukup: IPK >= 2.00.
    """
    ipk_val = round(float(ipk), 2)
    duration = int(study_duration_semesters)

    is_disqualified = has_failing_grades or has_disciplinary_violations or (duration > 8)

    disqualification_reasons = []
    if duration > 8:
        disqualification_reasons.append(f"Masa studi {duration} semester melampaui batas maksimal 8 semester")
    if has_failing_grades:
        disqualification_reasons.append("Memiliki rekam nilai mengulang atau di bawah ambang batas kelulusan")
    if has_disciplinary_violations:
        disqualification_reasons.append("Memiliki catatan pelanggaran kode etik / tata tertib akademik")

    if ipk_val >= 3.90 and not is_disqualified:
        predicate = "Summa Cum Laude"
        is_honor = True
    elif ipk_val >= 3.75 and not is_disqualified:
        predicate = "Magna Cum Laude"
        is_honor = True
    elif ipk_val >= 3.51 and not is_disqualified:
        predicate = "Dengan Pujian (Cum Laude)"
        is_honor = True
    elif ipk_val >= 3.00:
        predicate = "Sangat Memuaskan"
        is_honor = False
    elif ipk_val >= 2.75:
        predicate = "Memuaskan"
        is_honor = False
    elif ipk_val >= 2.00:
        predicate = "Cukup"
        is_honor = False
    else:
        predicate = "Tidak Lulus (IPK di bawah ambang batas kelulusan)"
        is_honor = False

    return {
        "ipk": ipk_val,
        "study_duration_semesters": duration,
        "predicate": predicate,
        "is_honor": is_honor,
        "is_disqualified": is_disqualified if ipk_val >= 3.51 else False,
        "disqualification_reasons": disqualification_reasons
    }


def calculate_friis_free_space_path_loss(
    frequency_mhz: float,
    distance_km: float,
    tx_gain_dbi: float = 0.0,
    rx_gain_dbi: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates Friis Free Space Path Loss (FSPL) and RF attenuation for cellular base station links.
    Standard equation:
      FSPL(dB) = 20 * log10(distance_km) + 20 * log10(frequency_mhz) + 32.44 - tx_gain_dbi - rx_gain_dbi
    """
    import math

    freq = max(1.0, float(frequency_mhz))
    dist = max(0.001, float(distance_km))
    gtx = float(tx_gain_dbi)
    grx = float(rx_gain_dbi)

    raw_fspl = 20 * math.log10(dist) + 20 * math.log10(freq) + 32.44
    net_path_loss = raw_fspl - gtx - grx
    wavelength_m = 300.0 / freq

    if net_path_loss < 80.0:
        link_quality = "Sangat Kuat (Line-of-Sight Dekat)"
    elif net_path_loss < 110.0:
        link_quality = "Baik (Cakupan Seluler Standar)"
    elif net_path_loss < 135.0:
        link_quality = "Batas Marjinal (Peredaman Tinggi)"
    else:
        link_quality = "Kritis (Memerlukan Penguat Sinyal / Repeater)"

    return {
        "frequency_mhz": freq,
        "distance_km": dist,
        "tx_gain_dbi": gtx,
        "rx_gain_dbi": grx,
        "wavelength_meters": round(wavelength_m, 4),
        "raw_fspl_db": round(raw_fspl, 2),
        "net_path_loss_db": round(net_path_loss, 2),
        "link_quality": link_quality
    }


def parse_kkn_thematic_evaluation(
    village_name: str,
    student_count: int,
    program_category: str,
    performance_score: float,
    community_impact_metric: str = ""
) -> Dict[str, Any]:
    """
    Evaluates student thematic community service (Kuliah Kerja Nyata / KKN) program performance,
    grade distribution, and regional community development index.
    Performance score range: 0.0 to 100.0.
    """
    score = round(max(0.0, min(100.0, float(performance_score))), 2)
    s_count = max(1, int(student_count))

    if score >= 85.0:
        grade = "A"
        grade_point = 4.0
        evaluation_status = "Sangat Berhasil (Program Unggulan)"
    elif score >= 75.0:
        grade = "AB"
        grade_point = 3.5
        evaluation_status = "Berhasil Baik"
    elif score >= 65.0:
        grade = "B"
        grade_point = 3.0
        evaluation_status = "Cukup Memadai"
    else:
        grade = "C"
        grade_point = 2.0
        evaluation_status = "Perlu Perbaikan / Monitoring Lanjutan"

    return {
        "village_name": village_name.strip(),
        "student_count": s_count,
        "program_category": program_category.strip(),
        "performance_score": score,
        "letter_grade": grade,
        "grade_point": grade_point,
        "evaluation_status": evaluation_status,
        "community_impact_metric": community_impact_metric.strip() if community_impact_metric else "Pengembangan Digitalisasi Desa",
        "is_passed": score >= 65.0
    }


def parse_tridharma_internal_grant_compliance(
    nidn: str,
    proposal_budget: float,
    publication_target: str,
    student_involvement_count: int = 0
) -> Dict[str, Any]:
    """
    Parses and evaluates lecturer internal tridharma research grant compliance
    based on university research guidelines (budget thresholds, student involvement, target journal).
    """
    clean_nidn = nidn.strip()
    is_valid_nidn = bool(re.match(r'^\d{10}$', clean_nidn))

    budget = float(proposal_budget)
    max_internal_budget = 50000000.0
    budget_compliant = (budget > 0 and budget <= max_internal_budget)

    students = max(0, int(student_involvement_count))
    students_compliant = (students >= 2)

    pub = publication_target.strip().lower()
    is_high_impact = bool(re.search(r'\b(?:scopus|wos|sinta\s*[12]|ieee)\b', pub))
    pub_compliant = bool(re.search(r'\b(?:scopus|wos|sinta|ieee|prosiding|jurnal)\b', pub))

    compliance_issues = []
    if not is_valid_nidn:
        compliance_issues.append(f"Format NIDN '{clean_nidn}' tidak valid (wajib 10 digit numerik)")
    if not budget_compliant:
        compliance_issues.append(f"Anggaran Rp {budget:,.0f} melebihi pagu internal maksimal Rp {max_internal_budget:,.0f}")
    if not students_compliant:
        compliance_issues.append(f"Keterlibatan mahasiswa ({students}) belum memenuhi syarat minimal 2 orang")
    if not pub_compliant:
        compliance_issues.append(f"Target luaran '{publication_target}' belum terakreditasi")

    is_compliant = is_valid_nidn and budget_compliant and students_compliant and pub_compliant

    return {
        "nidn": clean_nidn,
        "is_valid_nidn": is_valid_nidn,
        "proposal_budget": budget,
        "student_involvement_count": students,
        "publication_target": publication_target.strip(),
        "is_high_impact": is_high_impact,
        "is_compliant": is_compliant,
        "compliance_issues": compliance_issues
    }


def evaluate_fast_track_masters_eligibility(
    ipk: float,
    completed_sks: int,
    english_score: int,
    min_ipk: float = 3.50,
    min_sks: int = 120,
    min_toefl: int = 475
) -> Dict[str, Any]:
    """
    Evaluates undergraduate student eligibility for the Fast-Track accelerated Master's program (S1 + S2).
    Requires high academic standing (IPK >= 3.50), minimum 120 SKS credit completion, and certified English score.
    """
    c_ipk = max(0.0, min(4.0, float(ipk)))
    c_sks = max(0, int(completed_sks))
    c_eng = max(0, int(english_score))

    deficiencies: List[str] = []
    if c_ipk < min_ipk:
        deficiencies.append(f"IPK kumulatif {c_ipk:.2f} di bawah ambang batas minimal {min_ipk:.2f}")
    if c_sks < min_sks:
        deficiencies.append(f"Jumlah SKS lulus {c_sks} kurang dari syarat minimal {min_sks} SKS")
    if c_eng < min_toefl:
        deficiencies.append(f"Skor kemahiran bahasa Inggris {c_eng} di bawah syarat minimal {min_toefl}")

    is_eligible = len(deficiencies) == 0
    if is_eligible:
        tier = "Lolos Seleksi Utama"
    elif len(deficiencies) == 1 and c_eng < min_toefl and c_ipk >= min_ipk and c_sks >= min_sks:
        tier = "Lolos Bersyarat"
    else:
        tier = "Belum Memenuhi Syarat"

    recommendations: List[str] = []
    if is_eligible:
        recommendations.append("Dapat langsung memilih calon pembimbing tesis dan rencana studi Magister.")
    elif tier == "Lolos Bersyarat":
        recommendations.append("Diberikan kesempatan 1 semester untuk memenuhi sertifikasi TOEFL minimal.")
    else:
        recommendations.append("Fokus menuntaskan mata kuliah S1 dan perbaikan nilai untuk mencapai kriteria.")

    return {
        "ipk": c_ipk,
        "completed_sks": c_sks,
        "english_score": c_eng,
        "is_eligible": is_eligible,
        "eligibility_tier": tier,
        "deficiencies": deficiencies,
        "recommendations": recommendations
    }


def calculate_optical_snr_and_ber(
    signal_power_dbm: float,
    noise_power_dbm: float,
    bitrate_gbps: float = 10.0
) -> Dict[str, Any]:
    """
    Calculates Optical Signal-to-Noise Ratio (OSNR), Q-factor, and estimated Bit Error Rate (BER)
    for high-speed optical fiber transmission links (DWDM / metro optical networks).
    """
    import math

    sig_p = float(signal_power_dbm)
    noise_p = float(noise_power_dbm)
    rate = max(0.1, float(bitrate_gbps))

    osnr_db = sig_p - noise_p
    linear_snr = 10.0 ** (osnr_db / 10.0)

    q_factor = math.sqrt(max(0.001, linear_snr))
    q_factor_db = 20.0 * math.log10(max(0.001, q_factor))

    try:
        ber_est = 0.5 * math.erfc(q_factor / math.sqrt(2.0))
    except OverflowError:
        ber_est = 0.0

    if osnr_db >= 25.0:
        quality_status = "Excellent"
        assessment = "Kualitas sinyal optik sangat prima; transmisi bebas hambatan tanpa ketergantungan kritis pada FEC."
    elif osnr_db >= 18.0:
        quality_status = "Good"
        assessment = "Kualitas transmisi memenuhi standar link DWDM metro berkinerja stabil."
    elif osnr_db >= 14.0:
        quality_status = "Marginal"
        assessment = "Kualitas sinyal berada di batas toleransi; aktivasi Forward Error Correction (FEC) diwajibkan."
    else:
        quality_status = "Unacceptable"
        assessment = "Tingkat redaman atau derau terlalu tinggi; risiko bit error tinggi melampaui batas ambang."

    return {
        "signal_power_dbm": sig_p,
        "noise_power_dbm": noise_p,
        "bitrate_gbps": rate,
        "osnr_db": round(osnr_db, 2),
        "q_factor": round(q_factor, 2),
        "q_factor_db": round(q_factor_db, 2),
        "estimated_ber": float(f"{ber_est:.2e}"),
        "quality_status": quality_status,
        "assessment": assessment
    }


def parse_lab_equipment_calibration(
    equipment_name: str,
    serial_number: str,
    last_calibration_date: str,
    calibration_interval_months: int = 12,
    reference_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates laboratory telecommunication instrumentation calibration status (ISO/IEC 17025 standard).
    Calculates expiration deadline, remaining validity days, and operational compliance.
    """
    from datetime import datetime, timedelta

    eq_name = equipment_name.strip()
    sn = serial_number.strip().upper()
    interval_m = max(1, int(calibration_interval_months))

    try:
        last_dt = datetime.strptime(last_calibration_date.strip(), "%Y-%m-%d")
    except ValueError:
        return {
            "equipment_name": eq_name,
            "serial_number": sn,
            "error": f"Format tanggal kalibrasi '{last_calibration_date}' tidak valid (gunakan YYYY-MM-DD).",
            "is_operational_compliant": False
        }

    if reference_date:
        try:
            ref_dt = datetime.strptime(reference_date.strip(), "%Y-%m-%d")
        except ValueError:
            ref_dt = datetime.now()
    else:
        ref_dt = datetime.now()

    due_dt = last_dt + timedelta(days=int(interval_m * 30.4375))
    days_left = (due_dt.date() - ref_dt.date()).days

    if days_left < 0:
        status = "Expired"
        is_compliant = False
        recommendation = "Alat lab harus dihentikan dari praktikum / pengujian akreditasi dan segera dikalibrasi ulang di laboratorium kalibrasi terakreditasi KAN."
    elif days_left <= 30:
        status = "Due Soon"
        is_compliant = True
        recommendation = f"Masa kalibrasi tersisa {days_left} hari. Jadwalkan pengiriman kalibrasi sebelum tanggal jatuh tempo."
    else:
        status = "Valid"
        is_compliant = True
        recommendation = "Peralatan memenuhi standar kepatuhan pengujian ISO/IEC 17025 dan laik pakai untuk praktikum dan riset."

    return {
        "equipment_name": eq_name,
        "serial_number": sn,
        "last_calibration_date": last_dt.strftime("%Y-%m-%d"),
        "next_due_date": due_dt.strftime("%Y-%m-%d"),
        "interval_months": interval_m,
        "days_remaining": days_left,
        "status": status,
        "is_operational_compliant": is_compliant,
        "recommendation": recommendation
    }


def parse_lecturer_hki_copyright(
    work_title: str,
    creator_names: List[str],
    creation_type: str,
    application_number: str,
    registration_number: str,
    registration_date: str
) -> Dict[str, Any]:
    """
    Parses and evaluates lecturer intellectual property copyright certificates (HKI Hak Cipta DJKI Kemenkumham RI)
    for BKD (Beban Kerja Dosen) Tridharma compliance and SINTA score calculation.
    """
    clean_title = work_title.strip()
    clean_creators = [c.strip() for c in creator_names if c.strip()]
    c_type = creation_type.strip()
    app_num = application_number.strip().upper()
    reg_num = registration_number.strip()
    reg_date = registration_date.strip()

    type_lower = c_type.lower()
    if "program komputer" in type_lower or "software" in type_lower:
        rubric_points = 20.0
        standard_category = "Program Komputer"
    elif "buku" in type_lower or "monograf" in type_lower:
        rubric_points = 40.0
        standard_category = "Buku / Monograf"
    elif "modul" in type_lower or "panduan" in type_lower:
        rubric_points = 15.0
        standard_category = "Modul / Bahan Ajar"
    elif "karya" in type_lower or "ilmiah" in type_lower:
        rubric_points = 15.0
        standard_category = "Karya Tulis Ilmiah"
    else:
        rubric_points = 10.0
        standard_category = c_type

    is_valid_format = bool(re.match(r'^[A-Z0-9\-]+$', app_num)) and len(reg_num) >= 5
    has_creators = len(clean_creators) > 0
    is_valid_registration = is_valid_format and has_creators and bool(clean_title)

    primary_creator = clean_creators[0] if clean_creators else "Tidak Diketahui"

    return {
        "work_title": clean_title,
        "creators": clean_creators,
        "primary_creator": primary_creator,
        "creation_type": standard_category,
        "application_number": app_num,
        "registration_number": reg_num,
        "registration_date": reg_date,
        "is_valid_registration": is_valid_registration,
        "sinta_bkd_rubric_points": rubric_points,
        "legal_status": "Granted" if is_valid_registration else "Pending Verification"
    }


def calculate_fso_link_budget(
    tx_power_dbm: float,
    tx_beam_divergence_mrad: float,
    rx_aperture_diam_cm: float,
    link_distance_km: float,
    atmospheric_attenuation_db_km: float = 2.0,
    optical_rx_sensitivity_dbm: float = -38.0
) -> Dict[str, Any]:
    """
    Calculates Free Space Optics (FSO) laser telecommunications link budget.
    Computes geometric beam divergence loss, atmospheric extinction loss, received power, and link fade margin.
    """
    import math

    p_tx = float(tx_power_dbm)
    theta_mrad = max(0.01, float(tx_beam_divergence_mrad))
    d_rx_cm = max(0.1, float(rx_aperture_diam_cm))
    dist_km = max(0.001, float(link_distance_km))
    alpha_atm = max(0.0, float(atmospheric_attenuation_db_km))
    p_sens = float(optical_rx_sensitivity_dbm)

    # Beam footprint diameter at receiver in meters
    dist_m = dist_km * 1000.0
    beam_diam_m = dist_m * (theta_mrad * 1e-3)
    rx_diam_m = d_rx_cm * 1e-2

    # Geometric loss
    if beam_diam_m > rx_diam_m:
        geo_ratio = (rx_diam_m / beam_diam_m) ** 2
        l_geo = -10.0 * math.log10(geo_ratio)
    else:
        l_geo = 0.0

    # Atmospheric loss
    l_atm = alpha_atm * dist_km

    # Total path loss and received power
    total_loss = l_geo + l_atm
    p_rx = p_tx - total_loss
    margin = p_rx - p_sens

    if margin >= 15.0:
        status = "Robust"
        feasibility = "Sangat Layak (Mendukung transmisi laser pada segala kondisi cuaca umum)."
    elif margin >= 6.0:
        status = "Adequate"
        feasibility = "Layak (Margin memadai untuk kondisi kabut tipis dan hujan ringan)."
    elif margin >= 0.0:
        status = "Marginal"
        feasibility = "Kritis (Rentan terjadi link outage apabila terjadi kabut tebal)."
    else:
        status = "Link Outage"
        feasibility = "Tidak Layak (Daya terima di bawah ambang batas sensitivitas fotodetektor)."

    return {
        "tx_power_dbm": round(p_tx, 2),
        "link_distance_km": round(dist_km, 3),
        "beam_footprint_diam_m": round(beam_diam_m, 2),
        "geometric_loss_db": round(l_geo, 2),
        "atmospheric_loss_db": round(l_atm, 2),
        "total_path_loss_db": round(total_loss, 2),
        "received_power_dbm": round(p_rx, 2),
        "rx_sensitivity_dbm": round(p_sens, 2),
        "link_margin_db": round(margin, 2),
        "status": status,
        "is_link_feasible": margin >= 0.0,
        "feasibility_assessment": feasibility
    }


def evaluate_student_msib_internship(
    student_name: str,
    nim: str,
    industry_partner: str,
    internship_role: str,
    mentor_grade: float,
    duration_months: int = 5,
    partner_category: str = "BUMN/Multinasional"
) -> Dict[str, Any]:
    """
    Evaluates student Magang dan Studi Independen Bersertifikat (MSIB Kampus Merdeka) industrial internships.
    Converts mentor assessment score into university letter grade and maps 20 academic SKS curriculum course credits.
    """
    s_name = student_name.strip()
    s_nim = nim.strip()
    partner = industry_partner.strip()
    role = internship_role.strip()
    grade = max(0.0, min(100.0, float(mentor_grade)))
    dur = max(1, int(duration_months))
    category = partner_category.strip()

    if grade >= 80.0:
        letter_grade = "A"
        grade_point = 4.0
    elif grade >= 75.0:
        letter_grade = "AB"
        grade_point = 3.5
    elif grade >= 70.0:
        letter_grade = "B"
        grade_point = 3.0
    elif grade >= 65.0:
        letter_grade = "BC"
        grade_point = 2.5
    elif grade >= 60.0:
        letter_grade = "C"
        grade_point = 2.0
    else:
        letter_grade = "E"
        grade_point = 0.0

    is_passed = grade >= 60.0 and dur >= 4
    if not is_passed:
        converted_sks = 0
        conversion_status = "Tidak Lolos Konversi SKS"
    elif dur >= 5:
        converted_sks = 20
        conversion_status = "Konversi Penuh (20 SKS)"
    else:
        converted_sks = 16
        conversion_status = "Konversi Parsial (16 SKS)"

    curriculum_mappings = [
        {"course_code": "TT4012", "course_name": "Kerja Praktik", "sks": 2},
        {"course_code": "TT4024", "course_name": "Proyek Rekayasa Industri", "sks": 4},
        {"course_code": "TT4036", "course_name": "Praktik Sistem Telekomunikasi Lapangan", "sks": 6},
        {"course_code": "TT4044", "course_name": "Kapita Selekta Industri Telekomunikasi", "sks": 4},
        {"course_code": "TT4054", "course_name": "Komunikasi Profesional & Etika Rekayasa", "sks": 4 if converted_sks == 20 else 0}
    ]
    approved_courses = [c for c in curriculum_mappings if c["sks"] > 0] if is_passed else []

    return {
        "student_name": s_name,
        "nim": s_nim,
        "industry_partner": partner,
        "internship_role": role,
        "partner_category": category,
        "duration_months": dur,
        "mentor_grade": round(grade, 2),
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "is_conversion_approved": is_passed,
        "conversion_status": conversion_status,
        "converted_courses": approved_courses
    }


def calculate_antenna_polarization_loss(
    tx_polarization: str,
    rx_polarization: str,
    tilt_angle_deg: float = 0.0,
    axial_ratio_db: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates RF antenna Polarization Loss Factor (PLF), polarization efficiency, and axial ratio mismatch.
    Evaluates linear, circular (RHCP/LHCP), and elliptical antenna polarization alignments.
    """
    import math

    tx_pol = tx_polarization.strip().upper()
    rx_pol = rx_polarization.strip().upper()
    theta = abs(float(tilt_angle_deg)) % 180.0
    ar_db = max(0.0, float(axial_ratio_db))

    is_tx_linear = any(k in tx_pol for k in ("LIN", "VERT", "HORIZ", "SLANT"))
    is_rx_linear = any(k in rx_pol for k in ("LIN", "VERT", "HORIZ", "SLANT"))
    is_tx_circ = any(k in tx_pol for k in ("RHCP", "LHCP", "CIRC"))
    is_rx_circ = any(k in rx_pol for k in ("RHCP", "LHCP", "CIRC"))

    if is_tx_linear and is_rx_linear:
        # Tilt angle between linear polarization vectors
        rad = math.radians(theta)
        cos_val = math.cos(rad)
        plf_linear = cos_val ** 2
        # Avoid log of zero
        plf_linear = max(1e-4, plf_linear)
        plf_db = -10.0 * math.log10(plf_linear)
        alignment_note = f"Penyelarasan linear dengan beda sudut kemiringan {theta:.1f}°"
    elif (is_tx_circ and is_rx_linear) or (is_tx_linear and is_rx_circ):
        plf_linear = 0.50
        plf_db = 3.01
        alignment_note = "Kombinasi sirkuler dan linier menghasilkan rugi-rugi intrinsik tetap 3 dB."
    elif is_tx_circ and is_rx_circ:
        is_tx_rhcp = "RHCP" in tx_pol
        is_rx_rhcp = "RHCP" in rx_pol
        is_tx_lhcp = "LHCP" in tx_pol
        is_rx_lhcp = "LHCP" in rx_pol

        if (is_tx_rhcp and is_rx_rhcp) or (is_tx_lhcp and is_rx_lhcp):
            plf_linear = 1.0
            plf_db = 0.0
            alignment_note = "Penyelarasan sirkuler ko-polarisasi sempurna (RHCP-RHCP / LHCP-LHCP)."
        elif (is_tx_rhcp and is_rx_lhcp) or (is_tx_lhcp and is_rx_rhcp):
            plf_linear = 0.001
            plf_db = 30.0
            alignment_note = "Isolasi silang polarisasi sirkuler (Cross-Polarization Isolation RHCP vs LHCP)."
        else:
            plf_linear = 1.0
            plf_db = 0.0
            alignment_note = "Penyelarasan polarisasi sirkuler teridentifikasi."
    else:
        # Elliptical polarization model with axial ratio
        r = 10.0 ** (ar_db / 20.0) if ar_db > 0 else 1.0
        plf_linear = (2.0 * r) / (r ** 2 + 1.0)
        plf_linear = min(1.0, max(1e-4, plf_linear))
        plf_db = -10.0 * math.log10(plf_linear)
        alignment_note = f"Polarisasi elips dengan rasio aksial (Axial Ratio) {ar_db:.1f} dB"

    efficiency_pct = round(plf_linear * 100.0, 2)
    loss_db = round(plf_db, 2)

    if loss_db <= 0.5:
        status = "Optimal"
    elif loss_db <= 3.5:
        status = "Acceptable"
    elif loss_db <= 10.0:
        status = "Degraded"
    else:
        status = "High Loss / Mismatch"

    return {
        "tx_polarization": tx_pol,
        "rx_polarization": rx_pol,
        "tilt_angle_deg": round(theta, 1),
        "axial_ratio_db": round(ar_db, 2),
        "plf_factor": round(plf_linear, 4),
        "polarization_loss_db": loss_db,
        "polarization_efficiency_pct": efficiency_pct,
        "status": status,
        "alignment_note": alignment_note
    }


def parse_lecturer_pkm_grant(
    project_title: str,
    team_leader: str,
    nidn: str,
    partner_name: str,
    target_location: str,
    proposed_budget: float,
    fiscal_year: int,
    focus_area: str = "Pemberdayaan Teknologi Digital"
) -> Dict[str, Any]:
    """
    Parses and evaluates lecturer Tridharma Community Service (Pengabdian kepada Masyarakat - PKM) grant proposals.
    Verifies partner eligibility, NIDN registration, budget caps, and generates compliance deliverables.
    """
    clean_title = project_title.strip()
    clean_leader = team_leader.strip()
    clean_nidn = nidn.strip()
    partner = partner_name.strip()
    location = target_location.strip()
    budget = max(0.0, float(proposed_budget))
    year = int(fiscal_year)
    area = focus_area.strip()

    is_valid_nidn = bool(re.match(r'^\d{10}$', clean_nidn))
    is_strategic = "desa" in location.lower() or "binaan" in partner.lower()
    max_budget_cap = 25000000.0 if is_strategic else 15000000.0

    if not clean_title or not clean_leader or not partner:
        status = "Invalid Data"
        is_approved = False
        recom_budget = 0.0
        recommendation = "Proposal tidak lengkap; judul, ketua peneliti, dan nama mitra wajib diisi."
    elif not is_valid_nidn:
        status = "NIDN Invalid"
        is_approved = False
        recom_budget = 0.0
        recommendation = f"NIDN '{clean_nidn}' tidak valid (wajib 10 digit numerik)."
    elif budget > max_budget_cap:
        status = "Budget Cap Exceeded"
        is_approved = False
        recom_budget = max_budget_cap
        recommendation = f"Anggaran Rp {budget:,.0f} melebihi pagu maksimal (Rp {max_budget_cap:,.0f}). Ajukan revisi anggaran."
    else:
        status = "Approved"
        is_approved = True
        recom_budget = budget
        recommendation = "Proposal memenuhi kelayakan skema pengabdian masyarakat LPPM dan disetujui untuk pendanaan."

    deliverables = [
        "Laporan Kemajuan & Laporan Akhir Pelaksanaan PKM",
        "Publikasi Artikel di Jurnal Nasional Pengabdian Masyarakat Terakreditasi",
        "Publikasi Pemberitaan Kegiatan di Media Massa Online Nasional",
        "Video Dokumentasi Implementasi Solusi Teknologi di Kanal YouTube Prodi"
    ]

    return {
        "project_title": clean_title,
        "team_leader": clean_leader,
        "nidn": clean_nidn,
        "is_valid_nidn": is_valid_nidn,
        "partner_name": partner,
        "target_location": location,
        "proposed_budget": round(budget, 2),
        "approved_budget": round(recom_budget, 2),
        "fiscal_year": year,
        "focus_area": area,
        "is_strategic_partner": is_strategic,
        "status": status,
        "is_grant_approved": is_approved,
        "evaluation_recommendation": recommendation,
        "mandatory_deliverables": deliverables
    }


def calculate_satellite_link_budget(
    downlink_freq_ghz: float,
    slant_range_km: float,
    tx_eirp_dbw: float,
    rx_g_over_t_db_k: float,
    bandwidth_mhz: float,
    atmospheric_loss_db: float = 0.5
) -> Dict[str, Any]:
    """
    Computes satellite space-to-ground downlink link budget, free-space path loss,
    carrier-to-noise spectral density (C/No), and overall carrier-to-noise ratio (C/N).
    Based on ITU-R P.618 and standard DVB-S2/S2X telecommunication link parameters.
    """
    import math

    f_ghz = max(0.1, float(downlink_freq_ghz))
    d_km = max(100.0, float(slant_range_km))
    eirp = float(tx_eirp_dbw)
    g_over_t = float(rx_g_over_t_db_k)
    bw_mhz = max(0.1, float(bandwidth_mhz))
    l_atm = max(0.0, float(atmospheric_loss_db))

    # Free Space Path Loss (FSPL) in dB: 92.45 + 20*log10(f_GHz) + 20*log10(d_km)
    fspl_db = 92.45 + 20.0 * math.log10(f_ghz) + 20.0 * math.log10(d_km)

    # Boltzmann constant in dBW/K/Hz: -228.6 dBW/K/Hz
    k_boltzmann_dbw = -228.6

    # C/No = EIRP - FSPL - Latm + (G/T) - k
    c_over_n0_db_hz = eirp - fspl_db - l_atm + g_over_t - k_boltzmann_dbw

    # Noise Bandwidth in dBHz: 10 * log10(BW_MHz * 1e6)
    noise_bw_db_hz = 10.0 * math.log10(bw_mhz * 1e6)

    # Carrier-to-Noise Ratio (C/N) in dB: C/No - B_dBHz
    cnr_db = c_over_n0_db_hz - noise_bw_db_hz

    # Minimum threshold for DVB-S2 QPSK 3/4 is ~4.0 dB; 7.0 dB gives adequate fade margin
    min_cnr_threshold_db = 7.0
    link_margin_db = cnr_db - min_cnr_threshold_db
    is_viable = cnr_db >= min_cnr_threshold_db

    return {
        "downlink_freq_ghz": round(f_ghz, 3),
        "slant_range_km": round(d_km, 2),
        "tx_eirp_dbw": round(eirp, 2),
        "rx_g_over_t_db_k": round(g_over_t, 2),
        "bandwidth_mhz": round(bw_mhz, 2),
        "atmospheric_loss_db": round(l_atm, 2),
        "fspl_db": round(fspl_db, 2),
        "c_over_n0_db_hz": round(c_over_n0_db_hz, 2),
        "noise_bandwidth_db_hz": round(noise_bw_db_hz, 2),
        "cnr_db": round(cnr_db, 2),
        "link_margin_db": round(link_margin_db, 2),
        "min_cnr_threshold_db": min_cnr_threshold_db,
        "is_viable": is_viable,
        "modulation_recommendation": "DVB-S2 8PSK/16APSK" if cnr_db >= 10.0 else ("DVB-S2 QPSK" if is_viable else "Increase Antenna Aperture or EIRP")
    }


def calculate_rf_intermod_distortion(
    input_power_dbm: float,
    gain_db: float,
    iip3_dbm: float
) -> Dict[str, Any]:
    """
    Calculates RF front-end amplifier/mixer linearity metrics including Output IP3 (OIP3),
    third-order intermodulation distortion level (IMD3), and intermodulation rejection ratio (Delta IM3).
    Essential for RF receiver sensitivity and co-channel rejection analysis in telecommunication systems.
    """
    pin = float(input_power_dbm)
    gain = float(gain_db)
    iip3 = float(iip3_dbm)

    # Fundamental output power
    pout = pin + gain

    # Output Third-Order Intercept Point: OIP3 = IIP3 + Gain
    oip3 = iip3 + gain

    # Third-Order Intermodulation output level: P_IM3 = 3*Pout - 2*OIP3
    pim3_out = 3.0 * pout - 2.0 * oip3

    # Intermodulation Suppression Ratio (Delta IM3) in dBc: Pout - P_IM3 = 2*(OIP3 - Pout)
    imd3_suppression_dbc = 2.0 * (oip3 - pout)

    # Linearity Classification
    if imd3_suppression_dbc >= 50.0:
        linearity_status = "Excellent"
        operational_mode = "Highly Linear / Low Distortion"
    elif imd3_suppression_dbc >= 35.0:
        linearity_status = "Acceptable"
        operational_mode = "Linear Region"
    elif imd3_suppression_dbc >= 20.0:
        linearity_status = "Marginal"
        operational_mode = "Compression Impending"
    else:
        linearity_status = "Severe Distortion"
        operational_mode = "Nonlinear Saturation"

    return {
        "input_power_dbm": round(pin, 2),
        "gain_db": round(gain, 2),
        "iip3_dbm": round(iip3, 2),
        "fundamental_output_power_dbm": round(pout, 2),
        "oip3_dbm": round(oip3, 2),
        "third_order_intermod_power_dbm": round(pim3_out, 2),
        "imd3_suppression_dbc": round(imd3_suppression_dbc, 2),
        "linearity_status": linearity_status,
        "operational_mode": operational_mode,
        "is_linear": imd3_suppression_dbc >= 35.0
    }


def calculate_optical_fiber_dispersion(
    fiber_length_km: float,
    dispersion_coeff_ps_nm_km: float,
    spectral_width_nm: float,
    pmd_coeff_ps_sqrt_km: float,
    bit_rate_gbps: float
) -> Dict[str, Any]:
    """
    Calculates optical fiber pulse broadening caused by Chromatic Dispersion (CD)
    and Polarization Mode Dispersion (PMD), bit duration ratio, and optical power penalty.
    Crucial for high-speed single-mode fiber (G.652/G.655) DWDM transmission engineering.
    """
    import math

    length = max(0.1, float(fiber_length_km))
    d_cd = float(dispersion_coeff_ps_nm_km)
    delta_lambda = max(0.001, float(spectral_width_nm))
    d_pmd = max(0.0, float(pmd_coeff_ps_sqrt_km))
    bit_rate = max(0.1, float(bit_rate_gbps))

    # Chromatic dispersion delay in ps: Delta t_CD = |D| * L * Delta lambda
    delta_t_cd_ps = abs(d_cd) * length * delta_lambda

    # PMD differential group delay (DGD) in ps: Delta t_PMD = D_pmd * sqrt(L)
    delta_t_pmd_ps = d_pmd * math.sqrt(length)

    # Total dispersion delay in ps (root-sum-square): sqrt(t_CD^2 + t_PMD^2)
    delta_t_total_ps = math.sqrt(delta_t_cd_ps ** 2 + delta_t_pmd_ps ** 2)

    # Bit slot duration in ps: Tb = 1000 / bit_rate_gbps
    bit_duration_ps = 1000.0 / bit_rate

    # Pulse broadening ratio: rho = Delta t_total / Tb
    broadening_ratio = delta_t_total_ps / bit_duration_ps

    # Power penalty estimation in dB: ~ 5 * (rho)^2 for moderate broadening
    power_penalty_db = 5.0 * (broadening_ratio ** 2)

    if broadening_ratio <= 0.10:
        status = "Negligible Dispersion"
        recommendation = "Transmission within acceptable linear limits; no DCF required."
        is_viable = True
    elif broadening_ratio <= 0.25:
        status = "Moderate Dispersion"
        recommendation = "Minor eye-opening penalty; consider electronic dispersion compensation (EDC)."
        is_viable = True
    else:
        status = "Excessive Dispersion"
        recommendation = "Severe inter-symbol interference (ISI); deploy Dispersion Compensating Fiber (DCF) or coherent DSP."
        is_viable = False

    return {
        "fiber_length_km": round(length, 2),
        "dispersion_coeff_ps_nm_km": round(d_cd, 2),
        "spectral_width_nm": round(delta_lambda, 3),
        "pmd_coeff_ps_sqrt_km": round(d_pmd, 3),
        "bit_rate_gbps": round(bit_rate, 2),
        "cd_delay_ps": round(delta_t_cd_ps, 2),
        "pmd_delay_ps": round(delta_t_pmd_ps, 2),
        "total_delay_ps": round(delta_t_total_ps, 2),
        "bit_duration_ps": round(bit_duration_ps, 2),
        "broadening_ratio": round(broadening_ratio, 4),
        "power_penalty_db": round(power_penalty_db, 2),
        "status": status,
        "recommendation": recommendation,
        "is_viable": is_viable
    }


def parse_kampus_mengajar_evaluation(
    student_name: str,
    nim: str,
    target_school: str,
    school_level: str,
    teaching_hours: int,
    principal_grade: float,
    faculty_supervisor_grade: float,
    duration_months: int = 4
) -> Dict[str, Any]:
    """
    Evaluates MBKM Kampus Mengajar teaching assistantship program completion,
    calculates composite performance score, letter grade, and credit conversion (up to 20 SKS).
    """
    clean_name = student_name.strip()
    clean_nim = nim.strip()
    clean_school = target_school.strip()
    clean_level = school_level.strip()
    hours = max(0, int(teaching_hours))
    p_grade = min(100.0, max(0.0, float(principal_grade)))
    f_grade = min(100.0, max(0.0, float(faculty_supervisor_grade)))
    months = max(1, int(duration_months))

    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))

    # Composite grade: 50% Principal / School Mentor, 50% Faculty Field Supervisor (DPL)
    composite_score = round(0.50 * p_grade + 0.50 * f_grade, 2)

    # Letter Grade Conversion
    if composite_score >= 85.0:
        letter_grade = "A"
        grade_point = 4.0
    elif composite_score >= 80.0:
        letter_grade = "AB"
        grade_point = 3.5
    elif composite_score >= 70.0:
        letter_grade = "B"
        grade_point = 3.0
    elif composite_score >= 65.0:
        letter_grade = "BC"
        grade_point = 2.5
    elif composite_score >= 60.0:
        letter_grade = "C"
        grade_point = 2.0
    else:
        letter_grade = "D"
        grade_point = 1.0

    # Credit Conversion Calculation
    # Standard: 320 teaching/service hours over 4 months = 20 SKS
    if hours >= 320 and months >= 4 and composite_score >= 65.0:
        converted_sks = 20
        status = "Completed with Full Recognition"
        is_eligible = True
    elif hours >= 200 and composite_score >= 60.0:
        converted_sks = min(16, max(10, int(hours / 16.0)))
        status = "Partial Credit Recognition"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Ineligible for Credit Conversion"
        is_eligible = False

    course_equivalencies = [
        {"code": "TT-4101", "name": "Kuliah Kerja Nyata Tematik Pendidikan", "credits": 4},
        {"code": "TT-4102", "name": "Komunikasi Publik dan Kepemimpinan", "credits": 4},
        {"code": "TT-4103", "name": "Literasi Digital & Pembelajaran Komputasi", "credits": 4},
        {"code": "TT-4104", "name": "Pengembangan Karakter & Etika Profesi", "credits": 4},
        {"code": "TT-4105", "name": "Proyek Pengabdian Sekolah Mandiri", "credits": 4}
    ] if converted_sks == 20 else []

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "target_school": clean_school,
        "school_level": clean_level,
        "teaching_hours": hours,
        "duration_months": months,
        "principal_grade": p_grade,
        "faculty_supervisor_grade": f_grade,
        "composite_score": composite_score,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": course_equivalencies
    }


def calculate_radar_range_equation(
    peak_power_kw: float,
    antenna_gain_dbi: float,
    radar_cross_section_m2: float,
    freq_ghz: float,
    min_detectable_signal_dbm: float
) -> Dict[str, Any]:
    """
    Computes maximum monostatic radar detection range using the Radar Range Equation.
    Calculates wavelength, linear antenna gain, minimum detectable power, and round-trip delay.
    
    Formula: R_max = ((Pt * G^2 * lambda^2 * sigma) / ((4 * pi)^3 * S_min))^(1/4)
    """
    if peak_power_kw <= 0 or freq_ghz <= 0 or radar_cross_section_m2 <= 0:
        raise ValueError("Peak power, frequency, and radar cross-section must be strictly positive.")

    c = 299792458.0
    freq_hz = float(freq_ghz) * 1e9
    wavelength_m = c / freq_hz

    peak_power_w = float(peak_power_kw) * 1000.0
    gain_linear = 10.0 ** (float(antenna_gain_dbi) / 10.0)
    s_min_w = 10.0 ** ((float(min_detectable_signal_dbm) - 30.0) / 10.0)

    numerator = peak_power_w * (gain_linear ** 2) * (wavelength_m ** 2) * float(radar_cross_section_m2)
    denominator = ((4.0 * math.pi) ** 3) * s_min_w

    r_max_m = (numerator / denominator) ** 0.25
    r_max_km = r_max_m / 1000.0
    r_max_nmi = r_max_km / 1.852
    round_trip_delay_us = (2.0 * r_max_m / c) * 1e6

    return {
        "peak_power_kw": float(peak_power_kw),
        "peak_power_watts": round(peak_power_w, 2),
        "antenna_gain_dbi": float(antenna_gain_dbi),
        "antenna_gain_linear": round(gain_linear, 2),
        "radar_cross_section_m2": float(radar_cross_section_m2),
        "freq_ghz": float(freq_ghz),
        "wavelength_m": round(wavelength_m, 5),
        "min_detectable_signal_dbm": float(min_detectable_signal_dbm),
        "min_detectable_signal_watts": s_min_w,
        "max_range_m": round(r_max_m, 2),
        "max_range_km": round(r_max_km, 2),
        "max_range_nmi": round(r_max_nmi, 2),
        "round_trip_delay_us": round(round_trip_delay_us, 2),
        "is_valid": True
    }


def calculate_phase_noise_and_evm(
    carrier_freq_mhz: float,
    phase_jitter_ps: float = 0.0,
    integrated_phase_noise_dbc: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes phase noise in radians/degrees and estimates Error Vector Magnitude (EVM)
    constellation degradation from timing jitter or integrated single-sideband phase noise.
    
    Formula: phi_rms (rad) = 2 * pi * f_c * Delta_t_rms = sqrt(2 * 10^(dBc / 10))
    """
    if carrier_freq_mhz <= 0:
        raise ValueError("Carrier frequency must be strictly positive.")
    if phase_jitter_ps < 0:
        raise ValueError("Phase jitter cannot be negative.")

    fc_hz = float(carrier_freq_mhz) * 1e6

    if integrated_phase_noise_dbc is not None:
        phi_rad = math.sqrt(2.0 * (10.0 ** (float(integrated_phase_noise_dbc) / 10.0)))
        jitter_s = phi_rad / (2.0 * math.pi * fc_hz)
        jitter_ps = jitter_s * 1e12
        dbc_val = float(integrated_phase_noise_dbc)
    else:
        jitter_s = float(phase_jitter_ps) * 1e-12
        jitter_ps = float(phase_jitter_ps)
        phi_rad = 2.0 * math.pi * fc_hz * jitter_s
        dbc_val = 10.0 * math.log10(max((phi_rad ** 2) / 2.0, 1e-15))

    phi_deg = phi_rad * (180.0 / math.pi)
    evm_pct = phi_rad * 100.0
    evm_db = 20.0 * math.log10(phi_rad) if phi_rad > 0 else -100.0

    if evm_pct <= 2.0:
        modulation_support = "Excellent (High-Order 256/1024-QAM)"
        quality_rating = "Excellent"
    elif evm_pct <= 5.0:
        modulation_support = "Good (64-QAM / 16-QAM compatible)"
        quality_rating = "Good"
    elif evm_pct <= 8.0:
        modulation_support = "Marginal (QPSK / BPSK only)"
        quality_rating = "Marginal"
    else:
        modulation_support = "Degraded (Constellation closure risk)"
        quality_rating = "Degraded"

    return {
        "carrier_freq_mhz": float(carrier_freq_mhz),
        "phase_jitter_ps": round(jitter_ps, 3),
        "integrated_phase_noise_dbc": round(dbc_val, 2),
        "phase_noise_rad": round(phi_rad, 6),
        "phase_noise_deg": round(phi_deg, 4),
        "evm_percent": round(evm_pct, 3),
        "evm_db": round(evm_db, 2),
        "modulation_support": modulation_support,
        "quality_rating": quality_rating
    }


def calculate_edfa_amplifier_gain(
    input_power_dbm: float,
    pump_power_mw: float,
    small_signal_gain_db: float,
    saturation_output_power_dbm: float = 17.0
) -> Dict[str, Any]:
    """
    Simulates Erbium-Doped Fiber Amplifier (EDFA) optical gain saturation,
    noise figure (NF), and Amplified Spontaneous Emission (ASE) noise level.
    """
    if pump_power_mw <= 0:
        raise ValueError("Laser pump power must be strictly positive.")
    if small_signal_gain_db <= 0:
        raise ValueError("Small signal gain must be strictly positive.")

    # Pump efficiency threshold (~50 mW minimum for optimal inversion in C-band)
    pump_ratio = min(1.0, float(pump_power_mw) / 50.0)
    avail_g0_db = float(small_signal_gain_db) * pump_ratio
    g0_linear = 10.0 ** (avail_g0_db / 10.0)

    p_in_mw = 10.0 ** (float(input_power_dbm) / 10.0)
    p_sat_mw = 10.0 ** (float(saturation_output_power_dbm) / 10.0)

    # Gain saturation equation: G_sat = G_0 / (1 + P_in * G_0 / P_sat)
    gain_sat_linear = g0_linear / (1.0 + (p_in_mw * g0_linear / p_sat_mw))
    gain_actual_db = max(0.0, 10.0 * math.log10(max(gain_sat_linear, 1.0)))

    p_out_mw = p_in_mw * (10.0 ** (gain_actual_db / 10.0))
    p_out_dbm = 10.0 * math.log10(p_out_mw)

    # Noise Figure calculation based on inversion parameter
    inversion_ratio = min(1.0, float(pump_power_mw) / 120.0)
    nf_db = 3.2 + 2.5 * (1.0 - inversion_ratio)
    if gain_actual_db < 10.0:
        nf_db += 0.8

    # Operating regime
    regime = "Small-Signal Linear" if gain_actual_db >= (avail_g0_db - 0.5) else "Gain Saturation / Compressed"

    return {
        "input_power_dbm": float(input_power_dbm),
        "input_power_mw": round(p_in_mw, 5),
        "pump_power_mw": float(pump_power_mw),
        "small_signal_gain_db": float(small_signal_gain_db),
        "available_gain_db": round(avail_g0_db, 2),
        "actual_gain_db": round(gain_actual_db, 2),
        "saturation_output_power_dbm": float(saturation_output_power_dbm),
        "output_power_dbm": round(p_out_dbm, 2),
        "output_power_mw": round(p_out_mw, 3),
        "noise_figure_db": round(nf_db, 2),
        "operating_regime": regime
    }


def parse_wirausaha_merdeka_evaluation(
    student_name: str,
    nim: str,
    startup_name: str,
    business_sector: str,
    mentor_score: float,
    pitch_score: float,
    duration_months: int = 5
) -> Dict[str, Any]:
    """
    Evaluates MBKM Wirausaha Merdeka (WMK) startup acceleration program
    for engineering students, computing composite scoring and course SKS conversion.
    """
    clean_name = student_name.strip() if student_name else ""
    clean_nim = nim.strip() if nim else ""
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))

    clean_startup = startup_name.strip() if startup_name else "Inovasi Startup Mandiri"
    clean_sector = business_sector.strip() if business_sector else "Teknologi Informasi & Komunikasi"

    m_score = max(0.0, min(100.0, float(mentor_score)))
    p_score = max(0.0, min(100.0, float(pitch_score)))
    months = max(1, int(duration_months))

    composite_score = round((m_score * 0.60) + (p_score * 0.40), 2)

    if composite_score >= 80.0:
        letter_grade = "A"
        grade_point = 4.0
        converted_sks = 20
    elif composite_score >= 70.0:
        letter_grade = "AB"
        grade_point = 3.5
        converted_sks = 18
    elif composite_score >= 60.0:
        letter_grade = "B"
        grade_point = 3.0
        converted_sks = 16
    elif composite_score >= 50.0:
        letter_grade = "BC"
        grade_point = 2.5
        converted_sks = 12
    else:
        letter_grade = "C"
        grade_point = 2.0
        converted_sks = 10

    status = "Lolos Konversi Penuh (20 SKS)" if converted_sks == 20 else f"Konversi Parsial ({converted_sks} SKS)"
    is_eligible = bool(is_valid_nim and composite_score >= 60.0 and months >= 4)

    all_courses = [
        {"code": "TT-4106", "name": "Inovasi Bisnis Teknologi Telekomunikasi", "credits": 4},
        {"code": "TT-4107", "name": "Validasi Pasar & Traksi Produk Digital", "credits": 4},
        {"code": "TT-4108", "name": "Pengembangan Prototipe Hardware/IoT", "credits": 4},
        {"code": "TT-4109", "name": "Manajemen Keuangan & Valuasi Startup", "credits": 4},
        {"code": "TT-4110", "name": "Pitching & Komunikasi Investor", "credits": 4}
    ]

    # Select courses matching converted_sks
    equiv_courses = []
    accum_credits = 0
    for c in all_courses:
        if accum_credits + c["credits"] <= converted_sks:
            equiv_courses.append(c)
            accum_credits += c["credits"]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "startup_name": clean_startup,
        "business_sector": clean_sector,
        "mentor_score": m_score,
        "pitch_score": p_score,
        "composite_score": composite_score,
        "duration_months": months,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_otdr_fiber_events(
    fiber_length_km: float,
    total_loss_db: float,
    splice_loss_db: float = 0.05,
    num_splices: int = 4,
    connector_loss_db: float = 0.5,
    num_connectors: int = 2,
    wavelength_nm: int = 1550
) -> Dict[str, Any]:
    """
    Analyzes Optical Time Domain Reflectometer (OTDR) fiber trace events,
    deducting discrete passive event losses (fusion splices and optical connectors)
    to calculate the intrinsic fiber attenuation coefficient against ITU-T G.652 standards.
    """
    if fiber_length_km <= 0 or total_loss_db < 0:
        raise ValueError("Fiber length must be strictly positive and total loss cannot be negative.")

    total_splice_loss = max(0, int(num_splices)) * max(0.0, float(splice_loss_db))
    total_conn_loss = max(0, int(num_connectors)) * max(0.0, float(connector_loss_db))
    total_event_loss = total_splice_loss + total_conn_loss

    intrinsic_loss = max(0.0, float(total_loss_db) - total_event_loss)
    attenuation_per_km = intrinsic_loss / float(fiber_length_km)

    # Standard attenuation thresholds according to ITU-T G.652 standard
    itu_limit = 0.22 if wavelength_nm >= 1500 else 0.35
    is_compliant = attenuation_per_km <= itu_limit

    if attenuation_per_km <= itu_limit:
        quality_status = "Optimal / Sesuai Standar ITU-T G.652"
    elif attenuation_per_km <= (itu_limit * 1.25):
        quality_status = "Marginal / Perlu Pembersihan Konektor"
    else:
        quality_status = "Degradasi Berat / Indikasi Bending atau Micro-crack"

    return {
        "fiber_length_km": float(fiber_length_km),
        "total_loss_db": float(total_loss_db),
        "num_splices": int(num_splices),
        "splice_loss_db": float(splice_loss_db),
        "num_connectors": int(num_connectors),
        "connector_loss_db": float(connector_loss_db),
        "total_event_loss_db": round(total_event_loss, 3),
        "intrinsic_loss_db": round(intrinsic_loss, 3),
        "attenuation_db_per_km": round(attenuation_per_km, 4),
        "wavelength_nm": int(wavelength_nm),
        "itu_standard_limit_db_km": itu_limit,
        "is_compliant": is_compliant,
        "quality_status": quality_status
    }


def calculate_mimo_channel_capacity(
    bandwidth_mhz: float,
    snr_db: float,
    num_tx_antennas: int = 4,
    num_rx_antennas: int = 4
) -> Dict[str, Any]:
    """
    Computes Multiple-Input Multiple-Output (MIMO) spatial multiplexing channel capacity
    and Shannon spectral efficiency over uncorrelated Rayleigh fading wireless channels.
    """
    if bandwidth_mhz <= 0 or num_tx_antennas <= 0 or num_rx_antennas <= 0:
        raise ValueError("Bandwidth and antenna counts must be strictly positive.")

    n_tx = int(num_tx_antennas)
    n_rx = int(num_rx_antennas)
    mimo_rank = min(n_tx, n_rx)

    snr_linear = 10.0 ** (float(snr_db) / 10.0)

    # Shannon-Telatar MIMO capacity approximation: C = N_min * B * log2(1 + SNR / N_tx)
    spectral_eff = mimo_rank * math.log2(1.0 + (snr_linear / float(n_tx)))
    siso_spectral_eff = math.log2(1.0 + snr_linear)

    capacity_mbps = spectral_eff * float(bandwidth_mhz)
    capacity_gbps = capacity_mbps / 1000.0
    gain_factor = spectral_eff / max(siso_spectral_eff, 1e-9)

    if mimo_rank >= 4:
        multiplexing_status = f"High-Rank Spatial Multiplexing ({n_tx}x{n_rx} MIMO)"
    elif mimo_rank >= 2:
        multiplexing_status = f"Dual-Stream Spatial Multiplexing ({n_tx}x{n_rx} MIMO)"
    else:
        multiplexing_status = "Single Stream Transmission (SISO/SIMO/MISO)"

    return {
        "bandwidth_mhz": float(bandwidth_mhz),
        "snr_db": float(snr_db),
        "snr_linear": round(snr_linear, 2),
        "num_tx_antennas": n_tx,
        "num_rx_antennas": n_rx,
        "mimo_rank": mimo_rank,
        "spectral_efficiency_bps_hz": round(spectral_eff, 3),
        "siso_spectral_efficiency_bps_hz": round(siso_spectral_eff, 3),
        "capacity_mbps": round(capacity_mbps, 2),
        "capacity_gbps": round(capacity_gbps, 3),
        "capacity_gain_factor": round(gain_factor, 2),
        "spatial_multiplexing_status": multiplexing_status
    }


def calculate_lorawan_battery_lifetime(
    battery_capacity_mah: float,
    tx_current_ma: float,
    rx_current_ma: float,
    sleep_current_ua: float,
    uplink_interval_min: float,
    time_on_air_ms: float = 120.0,
    rx_window_ms: float = 50.0,
    battery_self_discharge_pct_year: float = 2.0
) -> Dict[str, Any]:
    """
    Estimates IoT LoRaWAN edge node operational battery longevity and hourly current profile
    considering transmit Time-on-Air (ToA), receive windows, deep-sleep current, and battery self-discharge.
    """
    if battery_capacity_mah <= 0 or uplink_interval_min <= 0:
        raise ValueError("Battery capacity and uplink interval must be strictly positive.")

    n_tx_per_hour = 60.0 / float(uplink_interval_min)
    t_tx_s = n_tx_per_hour * (float(time_on_air_ms) / 1000.0)
    t_rx_s = n_tx_per_hour * (float(rx_window_ms) / 1000.0)
    t_sleep_s = max(0.0, 3600.0 - t_tx_s - t_rx_s)

    q_tx_mah = (t_tx_s * float(tx_current_ma)) / 3600.0
    q_rx_mah = (t_rx_s * float(rx_current_ma)) / 3600.0
    q_sleep_mah = (t_sleep_s * (float(sleep_current_ua) / 1000.0)) / 3600.0
    q_total_per_hour = q_tx_mah + q_rx_mah + q_sleep_mah
    avg_current_ma = q_total_per_hour

    nominal_hours = float(battery_capacity_mah) / max(avg_current_ma, 1e-9)
    nominal_days = nominal_hours / 24.0
    nominal_years = nominal_days / 365.25

    # Self-discharge degradation adjustment
    discharge_factor = 1.0 + (max(0.0, float(battery_self_discharge_pct_year)) / 100.0)
    adjusted_years = nominal_years / discharge_factor
    adjusted_days = adjusted_years * 365.25

    duty_cycle_pct = (t_tx_s / 3600.0) * 100.0
    is_etsi_compliant = duty_cycle_pct <= 1.0

    return {
        "battery_capacity_mah": float(battery_capacity_mah),
        "uplink_interval_min": float(uplink_interval_min),
        "uplinks_per_day": round(n_tx_per_hour * 24.0, 1),
        "time_on_air_ms": float(time_on_air_ms),
        "duty_cycle_percent": round(duty_cycle_pct, 4),
        "is_etsi_compliant": is_etsi_compliant,
        "avg_current_ma": round(avg_current_ma, 4),
        "avg_current_ua": round(avg_current_ma * 1000.0, 2),
        "nominal_lifetime_days": round(nominal_days, 1),
        "nominal_lifetime_years": round(nominal_years, 2),
        "adjusted_lifetime_years": round(adjusted_years, 2),
        "adjusted_lifetime_days": round(adjusted_days, 1)
    }


def parse_iisma_evaluation(
    student_name: str,
    nim: str,
    host_university: str,
    country: str,
    gpa_host: float,
    credits_taken: int,
    duration_semesters: int = 1
) -> Dict[str, Any]:
    """
    Evaluates student participation in the Indonesian International Student Mobility Awards (IISMA)
    MBKM exchange program, calculating national grade equivalents and curriculum SKS credit recognition.
    """
    clean_name = student_name.strip() if student_name else ""
    clean_nim = nim.strip() if nim else ""
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))

    clean_host = host_university.strip() if host_university else "Partner University Overseas"
    clean_country = country.strip() if country else "International"

    gpa = max(0.0, min(4.0, float(gpa_host)))
    semesters = max(1, int(duration_semesters))
    credits_num = max(0, int(credits_taken))

    if gpa >= 3.67:
        letter_grade = "A"
        grade_point = 4.0
        converted_sks = 20
    elif gpa >= 3.33:
        letter_grade = "AB"
        grade_point = 3.5
        converted_sks = 18
    elif gpa >= 3.00:
        letter_grade = "B"
        grade_point = 3.0
        converted_sks = 16
    elif gpa >= 2.50:
        letter_grade = "BC"
        grade_point = 2.5
        converted_sks = 12
    else:
        letter_grade = "C"
        grade_point = 2.0
        converted_sks = 10

    is_eligible = bool(is_valid_nim and gpa >= 3.0 and credits_num >= 10)
    status = "Lolos Rekognisi Penuh (20 SKS)" if converted_sks == 20 else f"Rekognisi Parsial ({converted_sks} SKS)"

    all_courses = [
        {"code": "TT-4201", "name": "Global Telecommunication Engineering Seminar", "credits": 4},
        {"code": "TT-4202", "name": "Cross-Cultural Technical Communication & Leadership", "credits": 4},
        {"code": "TT-4203", "name": "International Technology Management & Innovation", "credits": 4},
        {"code": "TT-4204", "name": "Advanced Topic in Emerging Wireless Systems", "credits": 4},
        {"code": "TT-4205", "name": "Independent International Engineering Project", "credits": 4}
    ]

    equiv_courses = []
    accum_credits = 0
    for c in all_courses:
        if accum_credits + c["credits"] <= converted_sks:
            equiv_courses.append(c)
            accum_credits += c["credits"]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "host_university": clean_host,
        "country": clean_country,
        "gpa_host": gpa,
        "credits_taken": credits_num,
        "duration_semesters": semesters,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_fspl_and_link_budget(
    frequency_mhz: float,
    distance_km: float,
    tx_power_dbm: float = 20.0,
    tx_gain_dbi: float = 14.0,
    rx_gain_dbi: float = 14.0,
    misc_losses_db: float = 2.0,
    rx_sensitivity_dbm: float = -85.0
) -> Dict[str, Any]:
    """
    Calculates Free Space Path Loss (FSPL) and RF wireless link budget fade margin.
    Uses Friis transmission model:
      FSPL(dB) = 32.44 + 20*log10(d_km) + 20*log10(f_MHz)
      Prx(dBm) = Ptx + Gtx + Grx - FSPL - L_misc
      FadeMargin = Prx - Sensitivity
    """
    freq = max(0.1, float(frequency_mhz))
    dist = max(0.001, float(distance_km))
    p_tx = float(tx_power_dbm)
    g_tx = float(tx_gain_dbi)
    g_rx = float(rx_gain_dbi)
    l_misc = max(0.0, float(misc_losses_db))
    sens = float(rx_sensitivity_dbm)

    fspl = 32.44 + (20.0 * math.log10(dist)) + (20.0 * math.log10(freq))
    rx_power = p_tx + g_tx + g_rx - fspl - l_misc
    fade_margin = rx_power - sens
    wavelength_m = 300.0 / freq

    if fade_margin >= 15.0:
        status = "Sangat Andal (Excellent Link Margin)"
        is_viable = True
    elif fade_margin >= 10.0:
        status = "Andal (Good Link Margin)"
        is_viable = True
    elif fade_margin >= 0.0:
        status = "Marjinal (Borderline Fade Margin)"
        is_viable = True
    else:
        status = "Gagal (Link Outage / Infeasible)"
        is_viable = False

    return {
        "frequency_mhz": round(freq, 2),
        "distance_km": round(dist, 3),
        "wavelength_m": round(wavelength_m, 4),
        "fspl_db": round(fspl, 2),
        "tx_power_dbm": round(p_tx, 2),
        "tx_gain_dbi": round(g_tx, 2),
        "rx_gain_dbi": round(g_rx, 2),
        "misc_losses_db": round(l_misc, 2),
        "rx_power_dbm": round(rx_power, 2),
        "rx_sensitivity_dbm": round(sens, 2),
        "fade_margin_db": round(fade_margin, 2),
        "is_viable": is_viable,
        "status": status
    }


def calculate_optical_chromatic_dispersion(
    dispersion_param_ps_nm_km: float,
    spectral_width_nm: float,
    fiber_length_km: float,
    bit_rate_gbps: float = 10.0
) -> Dict[str, Any]:
    """
    Calculates optical fiber chromatic dispersion pulse broadening and maximum bit rate limit.
    Formula:
      delta_t (ps) = |D| * L_km * delta_lambda_nm
      Bit period Tb (ps) = 1000.0 / bit_rate_gbps
      Spreading ratio = delta_t / Tb
      Max bit rate B_max (Gbps) approx = 1000.0 / (4 * delta_t)
    """
    d_param = float(dispersion_param_ps_nm_km)
    delta_lambda = max(0.001, float(spectral_width_nm))
    length = max(0.001, float(fiber_length_km))
    bit_rate = max(0.1, float(bit_rate_gbps))

    pulse_broadening_ps = abs(d_param) * length * delta_lambda
    bit_period_ps = 1000.0 / bit_rate
    spreading_ratio = pulse_broadening_ps / bit_period_ps if bit_period_ps > 0 else 0.0

    max_bit_rate_gbps = 1000.0 / (4.0 * pulse_broadening_ps) if pulse_broadening_ps > 0 else 1000.0

    if spreading_ratio <= 0.25:
        severity = "Rendah (Negligible ISI)"
        requires_compensation = False
    elif spreading_ratio <= 0.50:
        severity = "Sedang (Moderate ISI - Kompensasi Dianjurkan)"
        requires_compensation = False
    else:
        severity = "Tinggi (Severe ISI - Butuh DCF/EDC)"
        requires_compensation = True

    return {
        "dispersion_param_ps_nm_km": round(d_param, 2),
        "spectral_width_nm": round(delta_lambda, 3),
        "fiber_length_km": round(length, 2),
        "bit_rate_gbps": round(bit_rate, 2),
        "pulse_broadening_ps": round(pulse_broadening_ps, 2),
        "bit_period_ps": round(bit_period_ps, 2),
        "spreading_ratio": round(spreading_ratio, 4),
        "max_bit_rate_gbps": round(max_bit_rate_gbps, 2),
        "severity": severity,
        "requires_compensation": requires_compensation
    }


def calculate_cellular_handover_hysteresis(
    rsrp_serving_dbm: float,
    rsrp_target_dbm: float,
    hysteresis_db: float = 3.0,
    a3_offset_db: float = 2.0,
    time_to_trigger_ms: int = 160
) -> Dict[str, Any]:
    """
    Analyzes 3GPP LTE/5G A3 event handover condition, hysteresis margin, and ping-pong risk.
    A3 condition:
      Mn (target) - Hys > Ms (serving) + Off
      => Mn - Ms > Off + Hys
    """
    rsrp_s = float(rsrp_serving_dbm)
    rsrp_t = float(rsrp_target_dbm)
    hys = max(0.0, float(hysteresis_db))
    off = float(a3_offset_db)
    ttt = max(0, int(time_to_trigger_ms))

    delta_rsrp = rsrp_t - rsrp_s
    threshold_margin = off + hys
    margin_diff = delta_rsrp - threshold_margin

    is_a3_triggered = delta_rsrp > threshold_margin

    if delta_rsrp <= 0:
        ping_pong_risk = "Nol (Target Lebih Lemah)"
        decision = "MAINTAIN_SERVING"
    elif delta_rsrp < threshold_margin:
        ping_pong_risk = "Tinggi jika dipaksa handover (Di bawah Hysteresis)"
        decision = "MAINTAIN_SERVING"
    elif margin_diff < 1.5 and ttt < 100:
        ping_pong_risk = "Tinggi (Margin Tipis & TTT Terlalu Cepat)"
        decision = "PENDING_TTT_EVALUATION"
    else:
        ping_pong_risk = "Rendah (Handover Stabil)"
        decision = "TRIGGER_HANDOVER"

    return {
        "rsrp_serving_dbm": round(rsrp_s, 2),
        "rsrp_target_dbm": round(rsrp_t, 2),
        "delta_rsrp_db": round(delta_rsrp, 2),
        "hysteresis_db": round(hys, 2),
        "a3_offset_db": round(off, 2),
        "time_to_trigger_ms": ttt,
        "is_a3_triggered": is_a3_triggered,
        "margin_diff_db": round(margin_diff, 2),
        "decision": decision,
        "ping_pong_risk": ping_pong_risk
    }


def parse_proyek_kemanusiaan_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student participation in MBKM Proyek Kemanusiaan (Disaster Relief / Community Action),
    calculates composite score from field and mentor assessments, and converts to 20 SKS curriculum credits.
    """
    raw_name = str(data.get("student_name", "")).strip()
    raw_nim = str(data.get("nim", "")).strip()
    raw_partner = str(data.get("partner_org", "")).strip()
    raw_location = str(data.get("location", "")).strip()

    clean_name = raw_name if raw_name else "Mahasiswa MBKM"
    clean_nim = raw_nim if raw_nim else "1201200000"
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))
    clean_partner = raw_partner if raw_partner else "BPBD / Relawan Kemanusiaan"
    clean_location = raw_location if raw_location else "Jawa Tengah"

    score_mentor = max(0.0, min(100.0, float(data.get("score_mentor", 0.0))))
    score_field = max(0.0, min(100.0, float(data.get("score_field", 0.0))))
    score_impact = max(0.0, min(100.0, float(data.get("score_impact", 0.0))))
    field_hours = max(0, int(data.get("field_hours", 0)))

    composite = round((0.40 * score_mentor) + (0.40 * score_field) + (0.20 * score_impact), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 75.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 65.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if field_hours >= 400 and composite >= 60.0:
        converted_sks = 20
        status = "Lulus Rekognisi Penuh (20 SKS)"
        is_eligible = True
    elif field_hours >= 200 and composite >= 50.0:
        converted_sks = 10
        status = "Lulus Rekognisi Sebagian (10 SKS)"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Syarat Minimal SKS Kemanusiaan"
        is_eligible = False

    equiv_courses = [
        {"code": "TT4201", "name": "Komunikasi Tanggap Darurat & Kebencanaan", "sks": 4},
        {"code": "TT4202", "name": "Jaringan Telekomunikasi Nirkabel Ad-Hoc Lapangan", "sks": 4},
        {"code": "TT4203", "name": "Etika Rekayasa & Pengabdian Masyarakat", "sks": 4},
        {"code": "TT4204", "name": "Kapita Selekta Mitigasi Bencana Digital", "sks": 4},
        {"code": "TT4205", "name": "Laporan Aksi Sosial & Dokumentasi Lapangan", "sks": 4}
    ]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "partner_org": clean_partner,
        "location": clean_location,
        "field_hours": field_hours,
        "score_mentor": score_mentor,
        "score_field": score_field,
        "score_impact": score_impact,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_polarization_mode_dispersion(
    pmd_coeff_ps_sqrt_km: float,
    fiber_length_km: float,
    bit_rate_gbps: float = 10.0
) -> Dict[str, Any]:
    """
    Calculates optical fiber Polarization Mode Dispersion (PMD), mean Differential Group Delay (DGD),
    and transmission outage risk according to ITU-T G.650.2 Maxwellian statistics.
    Formula:
      <DGD> (ps) = D_pmd * sqrt(L_km)
      Bit period Tb (ps) = 1000.0 / bit_rate_gbps
      Allowable DGD threshold approx 0.10 * Tb
      Max bit rate B_max (Gbps) approx = 100.0 / <DGD>
    """
    pmd_coeff = max(0.01, float(pmd_coeff_ps_sqrt_km))
    length = max(0.001, float(fiber_length_km))
    bit_rate = max(0.1, float(bit_rate_gbps))

    mean_dgd_ps = pmd_coeff * math.sqrt(length)
    bit_period_ps = 1000.0 / bit_rate
    dgd_ratio = mean_dgd_ps / bit_period_ps
    max_allowable_dgd_ps = 0.10 * bit_period_ps

    max_bit_rate_gbps = 100.0 / mean_dgd_ps if mean_dgd_ps > 0 else 1000.0

    if mean_dgd_ps <= max_allowable_dgd_ps:
        outage_risk = "Sangat Rendah (Aman/Robust)"
        is_compliant = True
    elif mean_dgd_ps <= 1.5 * max_allowable_dgd_ps:
        outage_risk = "Moderat (Kompensator PMD Dianjurkan)"
        is_compliant = True
    else:
        outage_risk = "Tinggi (Kritis / Butuh Adaptive Optical PMDC)"
        is_compliant = False

    return {
        "pmd_coeff_ps_sqrt_km": round(pmd_coeff, 3),
        "fiber_length_km": round(length, 2),
        "bit_rate_gbps": round(bit_rate, 2),
        "mean_dgd_ps": round(mean_dgd_ps, 3),
        "bit_period_ps": round(bit_period_ps, 2),
        "dgd_ratio": round(dgd_ratio, 4),
        "max_allowable_dgd_ps": round(max_allowable_dgd_ps, 2),
        "max_bit_rate_gbps": round(max_bit_rate_gbps, 2),
        "outage_risk": outage_risk,
        "is_compliant": is_compliant
    }


def calculate_cost231_hata_path_loss(
    frequency_mhz: float,
    base_station_height_m: float,
    mobile_height_m: float,
    distance_km: float,
    is_metropolitan: bool = False
) -> Dict[str, Any]:
    """
    Calculates cellular radio frequency path loss using the COST 231 Hata empirical propagation model
    for urban and suburban environments (1500 - 2000 MHz).
    Formula:
      PL (dB) = 46.3 + 33.9*log10(f) - 13.82*log10(hb) - a(hm) + (44.9 - 6.55*log10(hb))*log10(d) + Cm
      a(hm) = (1.1*log10(f) - 0.7)*hm - (1.56*log10(f) - 0.8)
      Cm = 3.0 dB if metropolitan center else 0.0 dB
    """
    f = max(150.0, float(frequency_mhz))
    hb = max(10.0, float(base_station_height_m))
    hm = max(1.0, float(mobile_height_m))
    d = max(0.1, float(distance_km))

    log_f = math.log10(f)
    log_hb = math.log10(hb)
    log_d = math.log10(d)

    a_hm = ((1.1 * log_f) - 0.7) * hm - ((1.56 * log_f) - 0.8)
    cm = 3.0 if is_metropolitan else 0.0

    path_loss_db = 46.3 + (33.9 * log_f) - (13.82 * log_hb) - a_hm + ((44.9 - (6.55 * log_hb)) * log_d) + cm

    if path_loss_db <= 120.0:
        coverage_quality = "Sangat Baik (Dense Urban Coverage)"
    elif path_loss_db <= 140.0:
        coverage_quality = "Baik (Standard Urban/Suburban Coverage)"
    elif path_loss_db <= 155.0:
        coverage_quality = "Marjinal (Cell Edge / Weak Signal)"
    else:
        coverage_quality = "Di Luar Jangkauan (Out of Cell Coverage)"

    return {
        "frequency_mhz": round(f, 2),
        "base_station_height_m": round(hb, 2),
        "mobile_height_m": round(hm, 2),
        "distance_km": round(d, 3),
        "is_metropolitan": is_metropolitan,
        "correction_factor_a_hm": round(a_hm, 3),
        "clutter_constant_cm": cm,
        "path_loss_db": round(path_loss_db, 2),
        "coverage_quality": coverage_quality
    }


def calculate_rain_attenuation_itu_r(
    frequency_ghz: float,
    path_length_km: float,
    rain_rate_mm_hr: float = 42.0,
    fade_margin_db: float = 30.0,
    polarization: str = "horizontal"
) -> Dict[str, Any]:
    """
    Calculates microwave terrestrial link rain attenuation and link availability
    according to ITU-R P.838 and ITU-R P.530 recommendations.
    Formula:
      gamma_R = k * (R ** alpha)  (dB/km)
      r = 1.0 / (1.0 + 0.045 * d_km) (path reduction factor)
      A_rain = gamma_R * d_km * r
      excess_margin = fade_margin_db - A_rain
    """
    freq = max(1.0, float(frequency_ghz))
    d = max(0.1, float(path_length_km))
    rain_rate = max(0.1, float(rain_rate_mm_hr))
    margin = float(fade_margin_db)
    pol = polarization.strip().lower()

    if pol == "vertical":
        k = 0.0000387 * (freq ** 2.4)
        alpha = 0.95 + (0.01 * freq)
    else:
        k = 0.000042 * (freq ** 2.45)
        alpha = 0.98 + (0.01 * freq)

    specific_attenuation_db_km = k * (rain_rate ** alpha)
    path_reduction_factor = 1.0 / (1.0 + (0.045 * d))
    effective_distance_km = d * path_reduction_factor
    total_rain_attenuation_db = specific_attenuation_db_km * effective_distance_km

    excess_margin_db = margin - total_rain_attenuation_db

    if excess_margin_db >= 10.0:
        availability_status = "Tinggi (Ketersediaan Link >= 99.999% Bebas Outage)"
        is_reliable = True
    elif excess_margin_db >= 0.0:
        availability_status = "Cukup (Ketersediaan Link >= 99.99% Standar)"
        is_reliable = True
    else:
        availability_status = "Rentan Putus (Rain Fade Outage / Margin Defisit)"
        is_reliable = False

    return {
        "frequency_ghz": round(freq, 2),
        "path_length_km": round(d, 2),
        "rain_rate_mm_hr": round(rain_rate, 1),
        "polarization": pol,
        "fade_margin_db": round(margin, 2),
        "k_coeff": round(k, 6),
        "alpha_coeff": round(alpha, 4),
        "specific_attenuation_db_km": round(specific_attenuation_db_km, 3),
        "path_reduction_factor": round(path_reduction_factor, 4),
        "effective_distance_km": round(effective_distance_km, 3),
        "total_rain_attenuation_db": round(total_rain_attenuation_db, 2),
        "excess_margin_db": round(excess_margin_db, 2),
        "availability_status": availability_status,
        "is_reliable": is_reliable
    }


def parse_studi_independen_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student participation in MBKM Studi / Riset Independen Bersertifikat (SIB),
    calculates composite score based on mentor assessment, technical milestone, and final capstone defense,
    and converts to 20 SKS curriculum credits.
    """
    raw_name = str(data.get("student_name", "")).strip()
    raw_nim = str(data.get("nim", "")).strip()
    raw_partner = str(data.get("partner_name", "")).strip()
    raw_track = str(data.get("track_name", "")).strip()

    clean_name = raw_name if raw_name else "Mahasiswa MBKM"
    clean_nim = raw_nim if raw_nim else "1201200000"
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))
    clean_partner = raw_partner if raw_partner else "Mitra Industri Teknologi"
    clean_track = raw_track if raw_track else "AI & Cloud Engineering"

    score_mentor = max(0.0, min(100.0, float(data.get("score_mentor", 0.0))))
    score_project = max(0.0, min(100.0, float(data.get("score_project", 0.0))))
    score_defense = max(0.0, min(100.0, float(data.get("score_defense", 0.0))))

    composite = round((0.35 * score_mentor) + (0.40 * score_project) + (0.25 * score_defense), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 75.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 65.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if composite >= 60.0:
        converted_sks = 20
        status = "Lulus Rekognisi Penuh SIB (20 SKS)"
        is_eligible = True
    elif composite >= 50.0:
        converted_sks = 10
        status = "Lulus Rekognisi Sebagian SIB (10 SKS)"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Ambang Batas Kelulusan SIB"
        is_eligible = False

    equiv_courses = [
        {"code": "TT4301", "name": "Riset Mandiri Teknologi Telekomunikasi", "sks": 4},
        {"code": "TT4302", "name": "Arsitektur Solusi Cloud & Platform Cerdas", "sks": 4},
        {"code": "TT4303", "name": "Proyek Rekayasa Sistem Lanjut", "sks": 4},
        {"code": "TT4304", "name": "Manajemen Produk & Inovasi Teknologi", "sks": 4},
        {"code": "TT4305", "name": "Diseminasi & Publikasi Ilmiah", "sks": 4}
    ]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "partner_name": clean_partner,
        "track_name": clean_track,
        "score_mentor": score_mentor,
        "score_project": score_project,
        "score_defense": score_defense,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_optical_four_wave_mixing(
    channel_spacing_ghz: float,
    fiber_length_km: float,
    chromatic_dispersion_ps_nm_km: float,
    dispersion_slope_ps_nm2_km: float = 0.08,
    attenuation_db_km: float = 0.2,
    channel_power_dbm: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates DWDM optical fiber Four-Wave Mixing (FWM) nonlinear phase mismatch,
    mixing efficiency eta, and generated crosstalk power according to ITU-T G.692 / Agrawal nonlinear optics.
    """
    spacing_ghz = max(12.5, float(channel_spacing_ghz))
    length_km = max(0.1, float(fiber_length_km))
    d_param = float(chromatic_dispersion_ps_nm_km)
    s_slope = float(dispersion_slope_ps_nm2_km)
    alpha_db = max(0.1, float(attenuation_db_km))
    p_in_dbm = float(channel_power_dbm)

    c_speed = 2.99792458e8  # m/s
    lambda_0 = 1550e-9      # m
    delta_f = spacing_ghz * 1e9  # Hz

    # Phase mismatch delta_beta in rad/m:
    # delta_beta = -(2 * pi * lambda_0^2 / c) * (delta_f)^2 * (D * 1e-6 + (lambda_0^2 / c) * delta_f * S * 1e-3)
    d_si = d_param * 1e-6  # s/m^2
    s_si = s_slope * 1e-3  # s/m^3
    beta_factor = (2.0 * math.pi * (lambda_0 ** 2)) / c_speed
    delta_beta_m = -beta_factor * (delta_f ** 2) * (d_si + ((lambda_0 ** 2) / c_speed) * delta_f * s_si)
    delta_beta_km = delta_beta_m * 1000.0  # rad/km

    # Attenuation coefficient alpha in 1/km:
    alpha_km = alpha_db / 4.3429448

    # Effective length:
    l_eff_km = (1.0 - math.exp(-alpha_km * length_km)) / alpha_km

    # FWM efficiency eta:
    denom = (alpha_km ** 2) + (delta_beta_km ** 2)
    phase_sin = math.sin(delta_beta_km * length_km / 2.0)
    numerator_ratio = 4.0 * math.exp(-alpha_km * length_km) * (phase_sin ** 2)
    denom_ratio = (1.0 - math.exp(-alpha_km * length_km)) ** 2
    fwm_efficiency = ((alpha_km ** 2) / denom) * (1.0 + (numerator_ratio / denom_ratio)) if denom > 0 and denom_ratio > 0 else 0.0
    fwm_efficiency = max(0.0, min(1.0, fwm_efficiency))

    # FWM crosstalk power estimation (relative to input power):
    gamma_nl = 1.3  # W^-1 * km^-1 typical SMF
    p_linear_w = (10.0 ** (p_in_dbm / 10.0)) * 1e-3
    p_fwm_linear_w = fwm_efficiency * (gamma_nl ** 2) * (p_linear_w ** 3) * (l_eff_km ** 2)
    p_fwm_dbm = 10.0 * math.log10(p_fwm_linear_w / 1e-3) if p_fwm_linear_w > 0 else -120.0
    crosstalk_suppression_dbc = p_in_dbm - p_fwm_dbm

    if fwm_efficiency < 0.05 and abs(d_param) >= 2.0:
        fwm_risk = "Sangat Rendah (Aman / Non-Zero Dispersion)"
        is_compliant = True
    elif fwm_efficiency < 0.25:
        fwm_risk = "Moderat (Waspada Kanal DWDM Rapat)"
        is_compliant = True
    else:
        fwm_risk = "Tinggi (Kritis / Jebakan Zero Dispersion)"
        is_compliant = False

    return {
        "channel_spacing_ghz": round(spacing_ghz, 2),
        "fiber_length_km": round(length_km, 2),
        "dispersion_ps_nm_km": round(d_param, 3),
        "dispersion_slope_ps_nm2_km": round(s_slope, 4),
        "attenuation_db_km": round(alpha_db, 3),
        "input_power_dbm": round(p_in_dbm, 2),
        "delta_beta_rad_km": round(delta_beta_km, 4),
        "effective_length_km": round(l_eff_km, 3),
        "fwm_efficiency": round(fwm_efficiency, 6),
        "fwm_efficiency_pct": round(fwm_efficiency * 100.0, 3),
        "fwm_power_dbm": round(p_fwm_dbm, 2),
        "crosstalk_suppression_dbc": round(crosstalk_suppression_dbc, 2),
        "fwm_risk": fwm_risk,
        "is_compliant": is_compliant
    }


def calculate_erlang_traffic_capacity(
    offered_traffic_erlangs: float,
    num_channels: int,
    avg_holding_time_sec: float = 120.0
) -> Dict[str, Any]:
    """
    Calculates cellular radio and telephone network trunking traffic metrics
    using Erlang-B (blocked calls cleared) and Erlang-C (blocked calls queued) models.
    """
    a = max(0.001, float(offered_traffic_erlangs))
    c = max(1, int(num_channels))
    h_sec = max(1.0, float(avg_holding_time_sec))

    # Erlang-B iterative computation (avoids factorial overflow)
    b = 1.0
    for k in range(1, c + 1):
        b = (a * b) / (k + (a * b))

    carried_traffic = a * (1.0 - b)
    blocking_pct = b * 100.0

    # Erlang-C queuing probability (valid when a < c)
    if a < c:
        erlang_c = (c * b) / (c - a + (a * b))
        erlang_c = max(0.0, min(1.0, erlang_c))
        avg_wait_sec = (erlang_c * h_sec) / (c - a)
    else:
        erlang_c = 1.0
        avg_wait_sec = float('inf')

    # Grade of Service evaluation (industry standard: GOS <= 2% or 0.02)
    if b <= 0.02:
        gos_status = "Sangat Baik (GoS <= 2%, Kapasitas Memadai)"
        is_acceptable = True
    elif b <= 0.05:
        gos_status = "Cukup (GoS <= 5%, Beban Sibuk Moderat)"
        is_acceptable = True
    else:
        gos_status = "Kelebihan Beban (GoS > 5%, Terjadi Kongesti Kanal)"
        is_acceptable = False

    return {
        "offered_traffic_erlangs": round(a, 3),
        "num_channels": c,
        "avg_holding_time_sec": round(h_sec, 1),
        "blocking_probability_erlang_b": round(b, 6),
        "blocking_pct": round(blocking_pct, 3),
        "carried_traffic_erlangs": round(carried_traffic, 3),
        "queuing_probability_erlang_c": round(erlang_c, 6) if erlang_c <= 1.0 else 1.0,
        "avg_queue_delay_sec": round(avg_wait_sec, 2) if avg_wait_sec != float('inf') else 99999.0,
        "grade_of_service_status": gos_status,
        "is_acceptable": is_acceptable
    }


def calculate_satellite_atmospheric_attenuation_itu_r(
    frequency_ghz: float,
    elevation_angle_deg: float,
    water_vapor_density_g_m3: float = 7.5
) -> Dict[str, Any]:
    """
    Calculates Earth-space satellite link gaseous atmospheric absorption (oxygen and water vapor)
    according to ITU-R P.676 recommendations for frequencies up to 55 GHz and elevation angles >= 5 deg.
    """
    f = max(1.0, min(55.0, float(frequency_ghz)))
    theta = max(5.0, min(90.0, float(elevation_angle_deg)))
    rho = max(0.1, min(30.0, float(water_vapor_density_g_m3)))

    # Oxygen specific attenuation gamma_o (dB/km)
    gamma_o = ((7.2 / ((f ** 2) + 0.36)) + (0.34 / (((f - 57.0) ** 2) + 2.1))) * (f ** 2) * 1e-3
    gamma_o = max(0.001, gamma_o)

    # Water vapor specific attenuation gamma_w (dB/km) with 22.235 GHz peak
    wv_resonance = 3.6 / (((f - 22.2) ** 2) + 8.5)
    gamma_w = (0.05 + (0.0021 * rho) + wv_resonance) * (f ** 2) * rho * 1e-4
    gamma_w = max(0.001, gamma_w)

    # Scale heights
    h_o = 6.0  # km for dry air
    h_w = 2.0  # km for water vapor

    zenith_o = gamma_o * h_o
    zenith_w = gamma_w * h_w
    zenith_total = zenith_o + zenith_w

    # Slant path cosecant mapping
    sin_theta = math.sin(math.radians(theta))
    slant_attenuation_db = zenith_total / sin_theta

    if slant_attenuation_db <= 0.5:
        band_status = "Sangat Rendah (Transmisi Satelit Sangat Jernih)"
        is_viable = True
    elif slant_attenuation_db <= 2.0:
        band_status = "Moderat (Standar Link Budget Ku/Ka-Band)"
        is_viable = True
    else:
        band_status = "Tinggi (Memerlukan Margin Daya Tambahan Uplink/Downlink)"
        is_viable = False

    return {
        "frequency_ghz": round(f, 2),
        "elevation_angle_deg": round(theta, 1),
        "water_vapor_density_g_m3": round(rho, 2),
        "oxygen_attenuation_db_km": round(gamma_o, 4),
        "water_vapor_attenuation_db_km": round(gamma_w, 4),
        "zenith_attenuation_db": round(zenith_total, 3),
        "slant_path_attenuation_db": round(slant_attenuation_db, 2),
        "transmission_band_status": band_status,
        "is_viable": is_viable
    }


def parse_pkm_mbkm_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student participation and achievement in Program Kreativitas Mahasiswa (PKM)
    and PIMNAS (Pekan Ilmiah Mahasiswa Nasional) for MBKM curriculum credit recognition.
    """
    raw_name = str(data.get("student_name", "")).strip()
    raw_nim = str(data.get("nim", "")).strip()
    raw_scheme = str(data.get("scheme", "")).strip()
    raw_title = str(data.get("proposal_title", "")).strip()
    qualified_pimnas = bool(data.get("qualified_pimnas", False))
    medal = str(data.get("medal", "")).strip()

    clean_name = raw_name if raw_name else "Mahasiswa Pengusul PKM"
    clean_nim = raw_nim if raw_nim else "1201200000"
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))
    clean_scheme = raw_scheme if raw_scheme else "PKM-KC (Karsa Cipta)"
    clean_title = raw_title if raw_title else "Inovasi Perangkat Nirkabel Cerdas"

    score_proposal = max(0.0, min(100.0, float(data.get("score_proposal", 0.0))))
    score_progress = max(0.0, min(100.0, float(data.get("score_progress", 0.0))))
    score_presentation = max(0.0, min(100.0, float(data.get("score_presentation", 0.0))))

    composite = round((0.30 * score_proposal) + (0.40 * score_progress) + (0.30 * score_presentation), 2)

    if qualified_pimnas or composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 78.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 68.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if qualified_pimnas:
        converted_sks = 20
        status = f"Lolos PIMNAS - Rekognisi Penuh 20 SKS ({medal or 'Finalis Nasional'})"
        is_eligible = True
    elif composite >= 75.0:
        converted_sks = 15
        status = "Didanai Kemdikbud Belmawa - Rekognisi 15 SKS"
        is_eligible = True
    elif composite >= 60.0:
        converted_sks = 10
        status = "Tingkat Universitas/Fakultas - Rekognisi 10 SKS"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Ambang Batas Rekognisi PKM"
        is_eligible = False

    equiv_courses = [
        {"code": "TT4401", "name": "Riset dan Inovasi Kreatif Mahasiswa", "sks": 4},
        {"code": "TT4402", "name": "Pengembangan Prototipe Rekayasa Telekomunikasi", "sks": 4},
        {"code": "TT4403", "name": "Kewirausahaan dan Alih Teknologi", "sks": 4},
        {"code": "TT4404", "name": "Komunikasi Ilmiah dan Presentasi Produk", "sks": 4},
        {"code": "TT4405", "name": "Karya Cipta Teknologi Tepat Guna", "sks": 4}
    ]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "scheme": clean_scheme,
        "proposal_title": clean_title,
        "qualified_pimnas": qualified_pimnas,
        "medal": medal,
        "score_proposal": score_proposal,
        "score_progress": score_progress,
        "score_presentation": score_presentation,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_optical_cross_phase_modulation(
    pump_power_mw: float,
    probe_power_mw: float,
    fiber_length_km: float,
    attenuation_db_km: float = 0.2,
    nonlinear_refractive_index_n2: float = 2.6e-20,
    effective_area_um2: float = 80.0,
    wavelength_nm: float = 1550.0
) -> Dict[str, Any]:
    """
    Calculates Cross-Phase Modulation (XPM) and Self-Phase Modulation (SPM) nonlinear phase shifts
    in wavelength-division multiplexing (WDM/DWDM) optical fiber transmission according to Agrawal nonlinear optics.
    """
    p_pump_mw = max(0.001, float(pump_power_mw))
    p_probe_mw = max(0.001, float(probe_power_mw))
    l_km = max(0.1, float(fiber_length_km))
    alpha_db = max(0.01, float(attenuation_db_km))
    n2 = max(1e-21, float(nonlinear_refractive_index_n2))
    a_eff_um2 = max(10.0, float(effective_area_um2))
    wl_nm = max(800.0, float(wavelength_nm))

    # Convert units to SI
    alpha_km = alpha_db / 4.3429448
    l_eff_km = (1.0 - math.exp(-alpha_km * l_km)) / alpha_km
    wl_m = wl_nm * 1e-9
    a_eff_m2 = a_eff_um2 * 1e-12

    # Nonlinear coefficient gamma in (W * km)^-1
    gamma_per_w_km = (2.0 * math.pi * n2 / (wl_m * a_eff_m2)) * 1000.0

    p_pump_w = p_pump_mw * 1e-3
    p_probe_w = p_probe_mw * 1e-3

    # Nonlinear phase shifts
    phi_spm_rad = gamma_per_w_km * p_probe_w * l_eff_km
    phi_xpm_rad = 2.0 * gamma_per_w_km * p_pump_w * l_eff_km
    phi_total_rad = phi_spm_rad + phi_xpm_rad

    phi_xpm_deg = phi_xpm_rad * (180.0 / math.pi)
    phi_spm_deg = phi_spm_rad * (180.0 / math.pi)

    if phi_xpm_rad <= 0.5:
        xpm_risk = "Rendah (Aman untuk Transmisi DWDM Standar)"
        is_acceptable = True
    elif phi_xpm_rad <= 1.0:
        xpm_risk = "Moderat (Perlu Monitoring Dispersion Mapping & Walk-Off)"
        is_acceptable = True
    else:
        xpm_risk = "Tinggi (Kritis / Distorsi Fase Nonlinier Signifikan)"
        is_acceptable = False

    return {
        "pump_power_mw": round(p_pump_mw, 3),
        "probe_power_mw": round(p_probe_mw, 3),
        "fiber_length_km": round(l_km, 2),
        "attenuation_db_km": round(alpha_db, 3),
        "effective_length_km": round(l_eff_km, 3),
        "gamma_per_w_km": round(gamma_per_w_km, 4),
        "phi_spm_rad": round(phi_spm_rad, 4),
        "phi_spm_deg": round(phi_spm_deg, 2),
        "phi_xpm_rad": round(phi_xpm_rad, 4),
        "phi_xpm_deg": round(phi_xpm_deg, 2),
        "phi_total_rad": round(phi_total_rad, 4),
        "xpm_risk": xpm_risk,
        "is_acceptable": is_acceptable
    }


def calculate_5g_nr_numerology_timing(
    numerology_mu: int,
    num_resource_blocks: int = 100,
    is_extended_cp: bool = False
) -> Dict[str, Any]:
    """
    Calculates 3GPP TS 38.211 5G NR physical layer numerology parameters,
    slot timing, symbol durations, and frame structures across FR1 and FR2 bands.
    """
    mu = max(0, min(4, int(numerology_mu)))
    n_rb = max(1, min(275, int(num_resource_blocks)))

    # Subcarrier spacing in kHz: 15 * 2^mu
    scs_khz = 15 * (2 ** mu)

    # Slot timing: 1 radio frame = 10 ms, 1 subframe = 1 ms
    slots_per_subframe = 2 ** mu
    slots_per_frame = 10 * slots_per_subframe
    slot_duration_ms = 1.0 / (2 ** mu)

    # Symbols per slot (extended CP is only standardized for mu=2 / 60 kHz)
    if is_extended_cp and mu == 2:
        symbols_per_slot = 12
        cp_type = "Extended Cyclic Prefix"
    else:
        symbols_per_slot = 14
        cp_type = "Normal Cyclic Prefix"

    total_symbols_per_subframe = symbols_per_slot * slots_per_subframe
    symbol_duration_us = (slot_duration_ms * 1000.0) / symbols_per_slot

    # Useful OFDM symbol duration Tu in microseconds: 1 / scs
    tu_us = 1000.0 / scs_khz
    cp_duration_us = symbol_duration_us - tu_us

    # Bandwidth occupied: N_RB * 12 subcarriers * SCS
    occupied_bw_mhz = (n_rb * 12 * scs_khz) / 1000.0

    if mu <= 2:
        frequency_range = "FR1 (Sub-6 GHz / Mid-band)"
        typical_deployment = "Macro / Micro Cellular Coverage (e.g. n78, n1, n3)"
    else:
        frequency_range = "FR2 (mmWave High-Band)"
        typical_deployment = "High Capacity Hotspot / FWA (e.g. n257, n258)"

    return {
        "numerology_mu": mu,
        "subcarrier_spacing_khz": scs_khz,
        "slots_per_subframe": slots_per_subframe,
        "slots_per_frame": slots_per_frame,
        "slot_duration_ms": round(slot_duration_ms, 4),
        "symbols_per_slot": symbols_per_slot,
        "total_symbols_per_subframe": total_symbols_per_subframe,
        "symbol_duration_us": round(symbol_duration_us, 3),
        "useful_symbol_duration_us": round(tu_us, 3),
        "cyclic_prefix_duration_us": round(cp_duration_us, 3),
        "cp_type": cp_type,
        "num_resource_blocks": n_rb,
        "occupied_bandwidth_mhz": round(occupied_bw_mhz, 2),
        "frequency_range": frequency_range,
        "typical_deployment": typical_deployment
    }


def calculate_satellite_scintillation_itu_r(
    frequency_ghz: float,
    elevation_angle_deg: float,
    antenna_diameter_m: float,
    percentage_p: float = 0.01,
    surface_temp_c: float = 25.0,
    relative_humidity_pct: float = 75.0,
    antenna_efficiency: float = 0.6
) -> Dict[str, Any]:
    """
    Calculates Earth-space satellite link tropospheric scintillation fading depth
    and amplitude variance according to ITU-R Recommendation P.618-13.
    """
    f = max(4.0, float(frequency_ghz))
    theta = max(5.0, min(90.0, float(elevation_angle_deg)))
    d_m = max(0.3, float(antenna_diameter_m))
    p = max(0.001, min(50.0, float(percentage_p)))
    temp_c = float(surface_temp_c)
    rh = max(1.0, min(100.0, float(relative_humidity_pct)))
    eta = max(0.3, min(0.9, float(antenna_efficiency)))

    temp_k = temp_c + 273.15

    # 1. Saturation water vapor pressure e_s (hPa)
    e_s = 6.1121 * math.exp((17.502 * temp_c) / (temp_c + 240.97))
    e = (rh * e_s) / 100.0

    # 2. Radio refractivity wet term N_wet
    n_wet = (373200.0 * e) / (temp_k ** 2)

    # 3. Standard deviation reference sigma_ref (dB)
    sigma_ref = 3.6e-3 + (1.0e-4 * n_wet)

    # 4. Effective turbulent path length L (m) with h_L = 1000 m
    sin_theta = math.sin(math.radians(theta))
    denom_l = math.sqrt((sin_theta ** 2) + 2.35e-4) + sin_theta
    turbulent_length_m = 2000.0 / denom_l

    # 5. Effective antenna diameter and wavelength
    d_eff = math.sqrt(eta) * d_m
    c_speed = 2.99792458e8
    wavelength_m = c_speed / (f * 1e9)

    # 6. Aperture averaging factor g(x)
    val_sqrt = math.sqrt(wavelength_m * turbulent_length_m)
    x = 0.572 * (d_eff / val_sqrt) if val_sqrt > 0 else 0.0
    # ITU-R P.618 empirical aperture averaging approximation
    g_x = 1.0 / math.sqrt(1.0 + 0.69 * (x ** (5.0 / 3.0)))

    # 7. Tropospheric scintillation standard deviation sigma (dB)
    sigma = sigma_ref * (f ** (7.0 / 12.0)) * (g_x / (sin_theta ** 1.2))

    # 8. Time percentage factor a(p)
    log_p = math.log10(p)
    a_p = -0.0615 * (log_p ** 3) + 0.0771 * (log_p ** 2) - 1.219 * log_p - 1.47

    fade_depth_db = max(0.01, a_p * sigma)

    if fade_depth_db <= 1.5:
        fading_risk = "Sangat Rendah (Scintillation Margin Aman)"
        is_viable = True
    elif fade_depth_db <= 3.0:
        fading_risk = "Moderat (Perlu Tambahan Margin Daya Ku/Ka-Band)"
        is_viable = True
    else:
        fading_risk = "Tinggi (Kritis / Potensi Deep Fading Troposfer)"
        is_viable = False

    return {
        "frequency_ghz": round(f, 2),
        "elevation_angle_deg": round(theta, 1),
        "antenna_diameter_m": round(d_m, 2),
        "percentage_p": round(p, 4),
        "surface_temp_c": round(temp_c, 1),
        "relative_humidity_pct": round(rh, 1),
        "n_wet": round(n_wet, 2),
        "sigma_ref_db": round(sigma_ref, 5),
        "sigma_db": round(sigma, 4),
        "aperture_averaging_factor": round(g_x, 4),
        "time_factor_a_p": round(a_p, 4),
        "scintillation_fade_depth_db": round(fade_depth_db, 2),
        "fading_risk": fading_risk,
        "is_viable": is_viable
    }


def parse_pmm_mbkm_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student participation, learning achievements, and credit conversions
    in the Pertukaran Mahasiswa Merdeka (PMM) Kemendikbudristek student exchange program.
    """
    raw_name = str(data.get("student_name", "")).strip()
    raw_nim = str(data.get("nim", "")).strip()
    raw_host = str(data.get("host_university", "")).strip()
    raw_home = str(data.get("home_university", "")).strip()

    clean_name = raw_name if raw_name else "Mahasiswa Peserta PMM"
    clean_nim = raw_nim if raw_nim else "1201200000"
    is_valid_nim = bool(re.match(r'^\d{8,12}$', clean_nim))
    clean_host = raw_host if raw_host else "Universitas Mitra Dalam Negeri"
    clean_home = raw_home if raw_home else "Telkom University Purwokerto"

    score_nusantara = max(0.0, min(100.0, float(data.get("nusantara_module_score", 85.0))))
    score_academic = max(0.0, min(100.0, float(data.get("academic_courses_score", 85.0))))
    score_mentor = max(0.0, min(100.0, float(data.get("host_mentor_score", 85.0))))

    # Composite: 30% Modul Nusantara, 50% Mata Kuliah Akademik Host, 20% Evaluasi Mentor Host
    composite = round((0.30 * score_nusantara) + (0.50 * score_academic) + (0.20 * score_mentor), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 78.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 68.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if composite >= 70.0:
        converted_sks = 20
        status = f"Lulus Penuh Program PMM - Rekognisi 20 SKS ({clean_host})"
        is_eligible = True
    elif composite >= 60.0:
        converted_sks = 15
        status = f"Lulus Bersyarat Program PMM - Rekognisi 15 SKS ({clean_host})"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Ambang Batas Kelulusan PMM"
        is_eligible = False

    equiv_courses = [
        {"code": "TT4501", "name": "Modul Nusantara: Kebinekaan, Inspirasi, & Refleksi", "sks": 4},
        {"code": "TT4502", "name": "Rekayasa Jaringan Telekomunikasi Lanjut", "sks": 4},
        {"code": "TT4503", "name": "Pemrosesan Sinyal Digital Terapan", "sks": 4},
        {"code": "TT4504", "name": "Sistem Komunikasi Nirkabel Modern", "sks": 4},
        {"code": "TT4505", "name": "Komunikasi Lintas Budaya & Kepemimpinan", "sks": 4}
    ]

    return {
        "student_name": clean_name,
        "nim": clean_nim,
        "is_valid_nim": is_valid_nim,
        "host_university": clean_host,
        "home_university": clean_home,
        "nusantara_module_score": score_nusantara,
        "academic_courses_score": score_academic,
        "host_mentor_score": score_mentor,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible,
        "course_equivalencies": equiv_courses
    }


def calculate_optical_srs_threshold(
    fiber_length_km: float,
    attenuation_db_km: float = 0.2,
    effective_area_um2: float = 80.0,
    raman_gain_coeff_m_w: float = 1.0e-13,
    input_power_mw: float = 100.0
) -> Dict[str, Any]:
    """
    Calculates the Stimulated Raman Scattering (SRS) critical threshold power
    and Raman depletion margin in single-mode optical fiber according to Stolen & Smith / Agrawal nonlinear optics.
    """
    l_km = max(0.1, float(fiber_length_km))
    alpha_db = max(0.01, float(attenuation_db_km))
    a_eff_um2 = max(10.0, float(effective_area_um2))
    g_r = max(1e-15, float(raman_gain_coeff_m_w))
    p_in_mw = max(0.1, float(input_power_mw))

    # Attenuation coefficient in 1/km and 1/m
    alpha_km = alpha_db / 4.3429448
    l_eff_km = (1.0 - math.exp(-alpha_km * l_km)) / alpha_km
    l_eff_m = l_eff_km * 1000.0

    a_eff_m2 = a_eff_um2 * 1e-12

    # Critical threshold power P_th = 16 * A_eff / (g_R * L_eff) (in Watts)
    p_th_w = (16.0 * a_eff_m2) / (g_r * l_eff_m)
    p_th_mw = p_th_w * 1000.0
    p_th_dbm = 10.0 * math.log10(p_th_mw)

    p_in_w = p_in_mw * 1e-3
    p_in_dbm = 10.0 * math.log10(p_in_mw)
    power_ratio = p_in_w / p_th_w
    margin_db = p_th_dbm - p_in_dbm

    if power_ratio <= 0.5:
        srs_risk = "Sangat Aman (Jauh di Bawah Ambang SRS)"
        is_safe = True
    elif power_ratio <= 1.0:
        srs_risk = "Moderat (Mendekati Ambang Depletion SRS)"
        is_safe = True
    else:
        srs_risk = "Kritis (Terjadi Depletion Daya dan Crosstalk Raman Parah)"
        is_safe = False

    return {
        "fiber_length_km": round(l_km, 2),
        "attenuation_db_km": round(alpha_db, 3),
        "effective_length_km": round(l_eff_km, 3),
        "effective_area_um2": round(a_eff_um2, 1),
        "input_power_mw": round(p_in_mw, 2),
        "input_power_dbm": round(p_in_dbm, 2),
        "threshold_power_mw": round(p_th_mw, 2),
        "threshold_power_dbm": round(p_th_dbm, 2),
        "power_to_threshold_ratio": round(power_ratio, 4),
        "srs_margin_db": round(margin_db, 2),
        "srs_risk": srs_risk,
        "is_safe": is_safe
    }


def calculate_5g_nr_eirp_psd(
    conducted_power_dbm: float,
    antenna_gain_dbi: float,
    cable_loss_db: float = 2.0,
    bandwidth_mhz: float = 20.0,
    is_macro_cell: bool = True
) -> Dict[str, Any]:
    """
    Calculates 3GPP TS 38.104 5G NR base station Equivalent Isotropically Radiated Power (EIRP)
    and Power Spectral Density (PSD) for spectrum emissions compliance.
    """
    p_tx_dbm = float(conducted_power_dbm)
    g_tx_dbi = float(antenna_gain_dbi)
    l_cable_db = max(0.0, float(cable_loss_db))
    bw_mhz = max(1.4, float(bandwidth_mhz))

    eirp_dbm = p_tx_dbm + g_tx_dbi - l_cable_db
    eirp_w = (10.0 ** ((eirp_dbm - 30.0) / 10.0))

    psd_conducted_dbm_mhz = p_tx_dbm - (10.0 * math.log10(bw_mhz))
    psd_eirp_dbm_mhz = eirp_dbm - (10.0 * math.log10(bw_mhz))

    max_limit_dbm = 65.0 if is_macro_cell else 43.0
    is_compliant = eirp_dbm <= max_limit_dbm

    if eirp_dbm <= (max_limit_dbm - 7.0):
        regulatory_status = "Optimal (Sesuai Standar Kominfo / 3GPP)"
    elif eirp_dbm <= max_limit_dbm:
        regulatory_status = "Batas Atas Regulasi (Mendekati Limit Emisi)"
    else:
        regulatory_status = "Melebihi Ambang Regulasi (Daya Terpancar Terlalu Tinggi)"

    return {
        "conducted_power_dbm": round(p_tx_dbm, 2),
        "antenna_gain_dbi": round(g_tx_dbi, 2),
        "cable_loss_db": round(l_cable_db, 2),
        "bandwidth_mhz": round(bw_mhz, 2),
        "eirp_dbm": round(eirp_dbm, 2),
        "eirp_watts": round(eirp_w, 2),
        "psd_conducted_dbm_mhz": round(psd_conducted_dbm_mhz, 2),
        "psd_eirp_dbm_mhz": round(psd_eirp_dbm_mhz, 2),
        "is_macro_cell": is_macro_cell,
        "max_limit_eirp_dbm": max_limit_dbm,
        "regulatory_status": regulatory_status,
        "is_compliant": is_compliant
    }


def calculate_satellite_faraday_rotation(
    frequency_ghz: float,
    total_electron_content_tecu: float = 30.0,
    geomagnetic_field_tesla: float = 4.5e-5
) -> Dict[str, Any]:
    """
    Calculates ionospheric Faraday rotation angle and polarization mismatch loss
    for Earth-space satellite links according to ITU-R Recommendation P.531.
    """
    f_ghz = max(0.1, float(frequency_ghz))
    tec = max(1.0, float(total_electron_content_tecu))
    b_avg = max(1e-6, float(geomagnetic_field_tesla))

    # Faraday rotation angle in radians: Omega = (2.36e4 * B * TEC * 1e16) / (f_Hz)^2
    omega_rad = (2.36e20 * b_avg * tec) / ((f_ghz * 1e9) ** 2)
    omega_deg = math.degrees(omega_rad)

    # Polarization mismatch loss for linear polarization: L_pol = -20 * log10(cos(omega))
    # Using modulo 90 degrees for effective polarization alignment
    eff_angle_deg = abs(omega_deg) % 90.0
    if eff_angle_deg > 45.0:
        eff_angle_deg = 90.0 - eff_angle_deg

    cos_val = math.cos(math.radians(eff_angle_deg))
    if cos_val > 1e-4:
        pol_mismatch_loss_db = -20.0 * math.log10(cos_val)
    else:
        pol_mismatch_loss_db = 40.0

    if eff_angle_deg <= 5.0:
        rotation_risk = "Sangat Rendah (Aman untuk Polarisasi Linier)"
        is_linear_viable = True
    elif eff_angle_deg <= 20.0:
        rotation_risk = "Moderat (Disarankan Kompensasi atau Polarisasi Sirkular)"
        is_linear_viable = True
    else:
        rotation_risk = "Tinggi (Kritis / Wajib Menggunakan Polarisasi Sirkular RHCP/LHCP)"
        is_linear_viable = False

    return {
        "frequency_ghz": round(f_ghz, 3),
        "total_electron_content_tecu": round(tec, 1),
        "geomagnetic_field_tesla": b_avg,
        "rotation_angle_rad": round(omega_rad, 4),
        "rotation_angle_deg": round(omega_deg, 2),
        "effective_angle_deg": round(eff_angle_deg, 2),
        "polarization_loss_db": round(pol_mismatch_loss_db, 2),
        "rotation_risk": rotation_risk,
        "is_linear_viable": is_linear_viable
    }


def parse_praktisi_mengajar_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates industry collaborative teaching and competency achievements in the
    Program Praktisi Mengajar Kemendikbudristek for telecommunication engineering courses.
    """
    course_name = str(data.get("course_name", "Rekayasa Jaringan Telekomunikasi")).strip()
    course_code = str(data.get("course_code", "TT3104")).strip()
    practitioner = str(data.get("practitioner_name", "Praktisi Industri")).strip()
    company = str(data.get("industry_company", "Industri Telekomunikasi")).strip()
    lecturer = str(data.get("lecturer_name", "Dosen Pengampu")).strip()
    teaching_hours = max(1, int(data.get("teaching_hours", 12)))

    score_case = max(0.0, min(100.0, float(data.get("case_study_score", 85.0))))
    score_practitioner = max(0.0, min(100.0, float(data.get("practitioner_assessment", 85.0))))
    score_student = max(0.0, min(100.0, float(data.get("student_evaluation", 85.0))))

    # Composite: 40% Studi Kasus Riil, 40% Penilaian Praktisi, 20% Evaluasi Mahasiswa
    composite = round((0.40 * score_case) + (0.40 * score_practitioner) + (0.20 * score_student), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 78.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 68.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if teaching_hours >= 12 and composite >= 70.0:
        converted_sks = 4
        status = f"Kolaborasi Industri Selesai Penuh - Rekognisi 4 SKS ({company})"
        is_eligible = True
    elif composite >= 60.0:
        converted_sks = 2
        status = f"Kolaborasi Selesai Parsial - Rekognisi 2 SKS ({company})"
        is_eligible = True
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Ambang Batas Praktisi Mengajar"
        is_eligible = False

    return {
        "course_name": course_name,
        "course_code": course_code,
        "practitioner_name": practitioner,
        "industry_company": company,
        "lecturer_name": lecturer,
        "teaching_hours": teaching_hours,
        "case_study_score": score_case,
        "practitioner_assessment": score_practitioner,
        "student_evaluation": score_student,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_eligible": is_eligible
    }


def calculate_optical_spm_broadening(
    fiber_length_km: float,
    peak_power_w: float,
    non_linear_coeff_gamma: float = 1.3,
    attenuation_db_km: float = 0.2,
    initial_pulse_width_ps: float = 20.0
) -> Dict[str, Any]:
    """
    Calculates optical Self-Phase Modulation (SPM) nonlinear phase shift, B-integral accumulation,
    and spectral broadening factor in single-mode optical fiber according to Agrawal Nonlinear Optics.
    """
    l_km = max(0.1, float(fiber_length_km))
    p0 = max(0.001, float(peak_power_w))
    gamma = max(0.1, float(non_linear_coeff_gamma))
    alpha_db = max(0.01, float(attenuation_db_km))
    t0_ps = max(0.1, float(initial_pulse_width_ps))

    # Attenuation coefficient in 1/km
    alpha_km = alpha_db / 4.3429448
    l_eff_km = (1.0 - math.exp(-alpha_km * l_km)) / alpha_km

    # Maximum nonlinear phase shift phi_max = gamma * P0 * L_eff
    phi_max_rad = gamma * p0 * l_eff_km
    phi_max_deg = math.degrees(phi_max_rad)

    # Approximate spectral broadening factor for Gaussian pulse: sqrt(1 + (4 / (3 * sqrt(3))) * phi_max^2)
    broadening_factor = math.sqrt(1.0 + (4.0 / (3.0 * math.sqrt(3.0))) * (phi_max_rad ** 2))

    # B-integral is equivalent to maximum accumulated nonlinear phase shift
    b_integral = phi_max_rad

    if b_integral < 1.0:
        spm_risk = "Rendah (Rezim Linier / Efek SPM Minimal)"
        is_acceptable = True
    elif b_integral <= 3.0:
        spm_risk = "Moderat (Terjadi Chirping, Dapat Dikompensasi Dispersi Kromatik)"
        is_acceptable = True
    else:
        spm_risk = "Kritis (Degradasi Spektral Parah & B-Integral Melampaui Batas)"
        is_acceptable = False

    return {
        "fiber_length_km": round(l_km, 2),
        "effective_length_km": round(l_eff_km, 3),
        "peak_power_w": round(p0, 3),
        "gamma_per_w_km": round(gamma, 2),
        "attenuation_db_km": round(alpha_db, 3),
        "initial_pulse_width_ps": round(t0_ps, 1),
        "phi_max_rad": round(phi_max_rad, 4),
        "phi_max_deg": round(phi_max_deg, 2),
        "b_integral": round(b_integral, 3),
        "broadening_factor": round(broadening_factor, 3),
        "spm_risk": spm_risk,
        "is_acceptable": is_acceptable
    }


def calculate_5g_nr_carrier_aggregation_throughput(
    component_carriers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculates 3GPP TS 38.306 aggregate multi-carrier peak data rate throughput for 5G NR Carrier Aggregation (CA).
    Evaluates individual Component Carriers (CC), MIMO layer efficiency, modulation coding, and total bandwidth aggregation.
    """
    if not component_carriers:
        return {
            "num_carriers": 0,
            "total_bandwidth_mhz": 0.0,
            "total_throughput_mbps": 0.0,
            "total_throughput_gbps": 0.0,
            "carriers": [],
            "spectral_efficiency_bps_hz": 0.0
        }

    # Bandwidth to PRB lookup table for numerology mu=1 (30 kHz SCS) in FR1
    prb_table_mu1 = {
        10: 24,
        15: 38,
        20: 51,
        40: 106,
        50: 133,
        60: 162,
        80: 217,
        90: 245,
        100: 273
    }

    # Modulation order Qm lookup
    qm_table = {
        "QPSK": 2,
        "16QAM": 4,
        "64QAM": 6,
        "256QAM": 8,
        "1024QAM": 10
    }

    r_max = 948.0 / 1024.0  # Max code rate ~0.92578
    total_bw = 0.0
    total_rate_mbps = 0.0
    carrier_details = []

    for idx, cc in enumerate(component_carriers, 1):
        name = str(cc.get("name", f"CC{idx}"))
        bw_mhz = int(cc.get("bandwidth_mhz", 100))
        mu = int(cc.get("numerology_mu", 1))
        mimo_layers = max(1, int(cc.get("mimo_layers", 4)))
        mod_str = str(cc.get("modulation", "256QAM")).upper().replace("-", "")
        qm = qm_table.get(mod_str, 8)
        scaling_factor = float(cc.get("scaling_factor", 1.0))
        overhead = float(cc.get("overhead", 0.14))  # FR1 DL standard overhead

        # Approximate PRBs
        prb = cc.get("prb")
        if not prb:
            prb = prb_table_mu1.get(bw_mhz, int(bw_mhz * 2.73))

        # Average symbol duration Ts^mu = 10^-3 / (14 * 2^mu)
        symbols_per_sec = 14 * (2 ** mu) * 1000.0

        # Throughput for this CC in Mbps: 10^-6 * (layers * Qm * f * Rmax * (PRB * 12 * symbols/sec) * (1 - OH))
        data_rate_bps = mimo_layers * qm * scaling_factor * r_max * (prb * 12 * symbols_per_sec) * (1.0 - overhead)
        rate_mbps = data_rate_bps * 1e-6

        total_bw += bw_mhz
        total_rate_mbps += rate_mbps

        carrier_details.append({
            "carrier": name,
            "bandwidth_mhz": bw_mhz,
            "numerology_mu": mu,
            "prb": prb,
            "mimo_layers": mimo_layers,
            "modulation": mod_str,
            "qm": qm,
            "data_rate_mbps": round(rate_mbps, 2)
        })

    spectral_eff = (total_rate_mbps * 1e6) / (total_bw * 1e6) if total_bw > 0 else 0.0

    return {
        "num_carriers": len(carrier_details),
        "total_bandwidth_mhz": round(total_bw, 1),
        "total_throughput_mbps": round(total_rate_mbps, 2),
        "total_throughput_gbps": round(total_rate_mbps / 1000.0, 3),
        "spectral_efficiency_bps_hz": round(spectral_eff, 2),
        "carriers": carrier_details
    }


def calculate_satellite_rain_attenuation_itu_r(
    frequency_ghz: float,
    elevation_angle_deg: float,
    rain_rate_001_mm_h: float = 95.0,
    earth_station_altitude_km: float = 0.05,
    latitude_deg: float = -7.4,
    percentage_p: float = 0.01
) -> Dict[str, Any]:
    """
    Calculates Earth-space satellite slant-path rain attenuation according to ITU-R P.618-13
    and specific rain attenuation coefficients according to ITU-R P.838-3.
    Particularly tuned for tropical high-intensity precipitation regimes (ITU Climate Zone P / Indonesia).
    """
    f_ghz = max(1.0, float(frequency_ghz))
    theta_deg = max(5.0, min(89.0, float(elevation_angle_deg)))
    r001 = max(0.1, float(rain_rate_001_mm_h))
    hs = max(0.0, float(earth_station_altitude_km))
    lat = abs(float(latitude_deg))
    p = max(0.001, min(1.0, float(percentage_p)))

    theta_rad = math.radians(theta_deg)

    # 1. Rain height h_R (km) based on 0 deg C isotherm height for tropical latitudes
    hr = 5.0 - (0.075 * (lat - 23.0)) if lat > 23.0 else 5.0
    hr = max(hs + 0.5, hr)

    # 2. Slant-path length L_s (km)
    ls = (hr - hs) / math.sin(theta_rad)

    # 3. Horizontal projection L_G (km)
    lg = ls * math.cos(theta_rad)

    # 4. Specific attenuation gamma_R = k * (R_001)^alpha (dB/km) ITU-R P.838
    # Accurate empirical interpolation for 4 GHz <= f <= 50 GHz
    if f_ghz < 10.0:
        k = 0.0001 * (f_ghz ** 2.2)
        alpha = 1.28
    elif f_ghz < 20.0:
        k = 0.018 * ((f_ghz / 12.0) ** 1.9)
        alpha = 1.15
    else:
        k = 0.075 * ((f_ghz / 20.0) ** 1.5)
        alpha = 1.05

    gamma_r = k * (r001 ** alpha)

    # 5. Horizontal path reduction factor r_001
    term_lg = math.sqrt(lg * gamma_r / f_ghz)
    r_denom = 1.0 + (0.78 * term_lg) - (0.38 * (1.0 - math.exp(-2.0 * lg)))
    r001_factor = 1.0 / max(0.1, r_denom)
    r001_factor = min(1.0, r001_factor)

    # 6. Vertical adjustment factor v_001
    zeta_rad = math.atan((hr - hs) / (lg * r001_factor))
    lr = (lg * r001_factor) / math.cos(theta_rad) if math.cos(theta_rad) > 0 else ls
    chi = 36.0 - lat if lat < 36.0 else 0.0
    v_denom = 1.0 + (math.sqrt(math.sin(theta_rad)) * ((31.0 * (1.0 - math.exp(-(theta_deg / (1.0 + chi))))) * (math.sqrt(lr * gamma_r) / (f_ghz ** 2))))
    v001_factor = 1.0 / max(0.1, v_denom)

    # Effective path length L_E (km)
    l_eff = lr * v001_factor

    # Rain attenuation at 0.01% outage A_0.01 (dB)
    a_001 = gamma_r * l_eff

    # 7. Extrapolate to percentage p
    if abs(p - 0.01) < 1e-6:
        a_p = a_001
    else:
        beta = 0.0 if p >= 1.0 or theta_deg >= 36.0 else (-0.005 * (theta_deg - 36.0)) if lat >= 36.0 else (-0.005 * (theta_deg - 36.0) + 1.8 - 4.25 * math.sin(math.radians(lat)))
        a_p = a_001 * 0.12 * (p ** (-(0.546 + 0.043 * math.log10(p))))

    a_p = max(0.1, a_p)

    if a_p <= 3.0:
        attenuation_risk = "Rendah (Margin Fading Standar Cukupi)"
        is_link_viable = True
    elif a_p <= 10.0:
        attenuation_risk = "Sedang (Memerlukan Adaptive Coding & Modulation ACM)"
        is_link_viable = True
    elif a_p <= 20.0:
        attenuation_risk = "Tinggi (Memerlukan Uplink Power Control & Site Diversity)"
        is_link_viable = True
    else:
        attenuation_risk = "Kritis (Potensi Terputusnya Sinyal Akibat Hujan Lebat)"
        is_link_viable = False

    return {
        "frequency_ghz": round(f_ghz, 2),
        "elevation_angle_deg": round(theta_deg, 2),
        "rain_rate_mm_h": round(r001, 1),
        "specific_attenuation_db_km": round(gamma_r, 3),
        "slant_path_length_km": round(ls, 2),
        "effective_path_length_km": round(l_eff, 2),
        "attenuation_001_db": round(a_001, 2),
        "outage_percentage": round(p, 4),
        "predicted_attenuation_db": round(a_p, 2),
        "attenuation_risk": attenuation_risk,
        "is_link_viable": is_link_viable
    }


def parse_p2mw_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student technology entrepreneurship milestones in the Program Pembinaan Mahasiswa
    Wirausaha (P2MW) Kemendikbudristek for academic SKS credit recognition and startup incubation.
    """
    student_name = str(data.get("student_name", "Mahasiswa")).strip()
    nim = str(data.get("nim", "")).strip()
    business_name = str(data.get("business_name", "Startup Telekomunikasi")).strip()
    business_stage = str(data.get("business_stage", "Tahap Awal")).strip()
    category = str(data.get("business_category", "Teknologi Terapan & IoT")).strip()

    score_pitch = max(0.0, min(100.0, float(data.get("pitch_bmc_score", 85.0))))
    score_proto = max(0.0, min(100.0, float(data.get("prototype_progress_score", 85.0))))
    score_finance = max(0.0, min(100.0, float(data.get("financial_governance_score", 85.0))))

    # Composite: 35% Business Model Canvas & Pitch, 35% Progress Prototipe/Traksi, 30% Akuntabilitas Keuangan
    composite = round((0.35 * score_pitch) + (0.35 * score_proto) + (0.30 * score_finance), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 78.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 68.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    is_growth = "tumbuh" in business_stage.lower()

    if is_growth and composite >= 80.0:
        converted_sks = 6
        status = f"Lolos Pendanaan & Inkubasi P2MW Tahap Bertumbuh - Rekognisi 6 SKS ({business_name})"
        is_funded = True
    elif composite >= 70.0:
        converted_sks = 4
        status = f"Lolos Pendanaan P2MW Tahap Awal - Rekognisi 4 SKS ({business_name})"
        is_funded = True
    elif composite >= 60.0:
        converted_sks = 2
        status = f"Penyelesaian Parsial Inkubasi P2MW - Rekognisi 2 SKS ({business_name})"
        is_funded = False
    else:
        converted_sks = 0
        status = "Tidak Memenuhi Standar Kelulusan P2MW"
        is_funded = False

    return {
        "student_name": student_name,
        "nim": nim,
        "business_name": business_name,
        "business_stage": business_stage,
        "business_category": category,
        "pitch_bmc_score": score_pitch,
        "prototype_progress_score": score_proto,
        "financial_governance_score": score_finance,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "converted_sks": converted_sks,
        "status": status,
        "is_funded": is_funded
    }


def calculate_optical_xpm_phase_shift(
    fiber_length_km: float,
    pump_power_w: float,
    probe_power_w: float = 0.001,
    wavelength_spacing_nm: float = 0.8,
    chromatic_dispersion_ps_nm_km: float = 17.0,
    non_linear_coeff_gamma: float = 1.3,
    attenuation_db_km: float = 0.2,
    pulse_width_ps: float = 50.0
) -> Dict[str, Any]:
    """
    Calculates optical Cross-Phase Modulation (XPM) induced phase shift, walk-off parameter,
    and suppression factor in WDM/DWDM single-mode optical fiber systems (Agrawal Nonlinear Fiber Optics).
    """
    l_km = max(0.1, float(fiber_length_km))
    p_pump = max(0.0001, float(pump_power_w))
    p_probe = max(0.0001, float(probe_power_w))
    delta_lambda = max(0.01, float(wavelength_spacing_nm))
    d_coeff = max(0.1, float(chromatic_dispersion_ps_nm_km))
    gamma = max(0.1, float(non_linear_coeff_gamma))
    alpha_db = max(0.01, float(attenuation_db_km))
    t0_ps = max(0.1, float(pulse_width_ps))

    alpha_km = alpha_db / 4.3429448
    l_eff_km = (1.0 - math.exp(-alpha_km * l_km)) / alpha_km

    # Walk-off parameter d_12 = D * delta_lambda (ps/km)
    d12_ps_km = d_coeff * delta_lambda

    # Walk-off length L_w = T0 / |d_12| (km)
    l_w_km = t0_ps / d12_ps_km if d12_ps_km > 0 else 1000.0

    # Maximum XPM phase shift (factor of 2 compared to SPM)
    phi_xpm_max_rad = 2.0 * gamma * p_pump * l_eff_km
    phi_xpm_max_deg = math.degrees(phi_xpm_max_rad)

    # Walk-off suppression factor eta_xpm = 1 / sqrt(1 + (L_eff / L_w)^2)
    eta_xpm = 1.0 / math.sqrt(1.0 + ((l_eff_km / l_w_km) ** 2))

    # Effective accumulated XPM phase shift
    phi_xpm_eff_rad = phi_xpm_max_rad * eta_xpm
    phi_xpm_eff_deg = math.degrees(phi_xpm_eff_rad)

    if phi_xpm_eff_rad < 0.5:
        xpm_risk = "Rendah (Penalti Crosstalk Nonlinier XPM Minimal)"
        is_acceptable = True
    elif phi_xpm_eff_rad <= 1.5:
        xpm_risk = "Moderat (Interferensi Kanal Terkelola Berkat Walk-off Dispersion)"
        is_acceptable = True
    else:
        xpm_risk = "Tinggi (Distorsi Spektral & Penalti Asimetri XPM Parah)"
        is_acceptable = False

    return {
        "fiber_length_km": round(l_km, 2),
        "effective_length_km": round(l_eff_km, 3),
        "pump_power_w": round(p_pump, 3),
        "probe_power_w": round(p_probe, 4),
        "wavelength_spacing_nm": round(delta_lambda, 2),
        "dispersion_ps_nm_km": round(d_coeff, 2),
        "walk_off_parameter_ps_km": round(d12_ps_km, 2),
        "walk_off_length_km": round(l_w_km, 2),
        "suppression_factor_eta": round(eta_xpm, 4),
        "phi_xpm_max_rad": round(phi_xpm_max_rad, 4),
        "phi_xpm_effective_rad": round(phi_xpm_eff_rad, 4),
        "phi_xpm_effective_deg": round(phi_xpm_eff_deg, 2),
        "xpm_risk": xpm_risk,
        "is_acceptable": is_acceptable
    }


def calculate_5g_nr_massive_mimo_gain(
    num_rows: int = 8,
    num_cols: int = 8,
    polarization_layers: int = 2,
    element_gain_dbi: float = 6.0,
    carrier_freq_ghz: float = 3.5,
    conducted_power_dbm: float = 43.0
) -> Dict[str, Any]:
    """
    Calculates 3GPP TS 38.211 / TR 38.901 Massive MIMO planar antenna array gain,
    beamwidth (HPBW), Equivalent Isotropically Radiated Power (EIRP), and spatial multiplexing capacity.
    """
    m_rows = max(1, int(num_rows))
    n_cols = max(1, int(num_cols))
    p_layers = max(1, int(polarization_layers))
    elem_gain = float(element_gain_dbi)
    freq_ghz = max(0.4, float(carrier_freq_ghz))
    p_conducted = float(conducted_power_dbm)

    # Total physical antenna elements
    total_elements = m_rows * n_cols * p_layers

    # Planar array coherent beamforming gain: 10 * log10(M * N)
    array_gain_db = 10.0 * math.log10(m_rows * n_cols)
    total_antenna_gain_dbi = elem_gain + array_gain_db

    # Half-Power Beamwidth (HPBW) approximations for uniform rectangular array (deg)
    # HPBW_az ~ 102 deg / N_cols, HPBW_el ~ 102 deg / M_rows
    hpbw_azimuth_deg = 102.0 / n_cols
    hpbw_elevation_deg = 102.0 / m_rows

    # Total Radiated Power / EIRP
    eirp_dbm = p_conducted + total_antenna_gain_dbi
    eirp_watts = 10.0 ** ((eirp_dbm - 30.0) / 10.0)

    # Maximum supported simultaneous spatial layers (rank) in 3GPP Rel-16/17 (up to 16 for gNB)
    max_spatial_layers = min(16, total_elements // 2)

    return {
        "num_rows": m_rows,
        "num_cols": n_cols,
        "polarization_layers": p_layers,
        "total_elements": total_elements,
        "element_gain_dbi": round(elem_gain, 2),
        "array_gain_dbi": round(array_gain_db, 2),
        "total_gain_dbi": round(total_antenna_gain_dbi, 2),
        "hpbw_azimuth_deg": round(hpbw_azimuth_deg, 2),
        "hpbw_elevation_deg": round(hpbw_elevation_deg, 2),
        "carrier_freq_ghz": round(freq_ghz, 2),
        "conducted_power_dbm": round(p_conducted, 2),
        "eirp_dbm": round(eirp_dbm, 2),
        "eirp_watts": round(eirp_watts, 2),
        "max_spatial_layers": max_spatial_layers,
        "is_massive_mimo": total_elements >= 32
    }


def calculate_satellite_gaseous_attenuation_itu_r_p676(
    frequency_ghz: float,
    elevation_angle_deg: float,
    surface_temp_c: float = 27.0,
    surface_pressure_hpa: float = 1013.25,
    water_vapor_density_g_m3: float = 18.0
) -> Dict[str, Any]:
    """
    Calculates Earth-space satellite slant-path atmospheric gaseous attenuation according to ITU-R P.676-12.
    Evaluates dry air (oxygen O2) and water vapor (H2O) absorption up to 350 GHz for tropical climates.
    """
    f_ghz = max(1.0, min(350.0, float(frequency_ghz)))
    theta_deg = max(5.0, min(90.0, float(elevation_angle_deg)))
    t_c = float(surface_temp_c)
    p_hpa = max(800.0, min(1050.0, float(surface_pressure_hpa)))
    rho = max(0.1, min(50.0, float(water_vapor_density_g_m3)))

    theta_rad = math.radians(theta_deg)
    t_k = t_c + 273.15
    theta_param = 300.0 / t_k
    p_ratio = p_hpa / 1013.0

    # 1. Oxygen / dry air specific attenuation gamma_o (dB/km)
    # ITU-R P.676 model for dry air absorption
    if f_ghz <= 54.0:
        gamma_o = (0.0072 * (p_ratio ** 2) * (theta_param ** 2) + (0.326 * (p_ratio ** 2) * (theta_param ** 1.5)) / (((f_ghz - 60.0) ** 2) + 1.0)) * ((f_ghz / 30.0) ** 1.2) * 0.1
    elif f_ghz <= 66.0:
        # 60 GHz oxygen absorption peak (~15 dB/km)
        gamma_o = 15.0 - (0.8 * abs(f_ghz - 60.0))
    else:
        gamma_o = 0.05 + (0.15 * ((f_ghz - 66.0) / 100.0))

    # 2. Water vapor specific attenuation gamma_w (dB/km)
    # ITU-R P.676 model for 22.235 GHz resonance and continuum
    term_22 = (0.05 * rho * (theta_param ** 2.5)) / (((f_ghz - 22.235) ** 2) + 9.0)
    term_continuum = 1.5e-5 * rho * (f_ghz ** 1.6) * p_ratio * (theta_param ** 1.5)
    gamma_w = term_22 + term_continuum

    gamma_o = max(0.001, gamma_o)
    gamma_w = max(0.001, gamma_w)

    # 3. Equivalent scale heights (km)
    h_o = 6.0
    h_w = 1.6 + (0.02 * rho)

    # 4. Zenith attenuation (dB)
    a_zenith_oxygen = gamma_o * h_o
    a_zenith_vapor = gamma_w * h_w
    a_zenith_total = a_zenith_oxygen + a_zenith_vapor

    # 5. Slant path gaseous attenuation (dB)
    sin_theta = math.sin(theta_rad)
    a_slant_total = a_zenith_total / sin_theta

    if a_slant_total <= 0.5:
        risk = "Sangat Rendah (Redaman Atmosferik Transparan)"
    elif a_slant_total <= 2.0:
        risk = "Rendah (Dapat Diatasi Margin Daya Standar)"
    elif a_slant_total <= 5.0:
        risk = "Moderat (Perlu Alokasi Fading Margin Ku/Ka-Band)"
    else:
        risk = "Tinggi (Resonansi Molekular Atmosfer Signifikan)"

    return {
        "frequency_ghz": round(f_ghz, 2),
        "elevation_angle_deg": round(theta_deg, 2),
        "surface_temp_c": round(t_c, 1),
        "surface_pressure_hpa": round(p_hpa, 1),
        "water_vapor_density_g_m3": round(rho, 1),
        "gamma_oxygen_db_km": round(gamma_o, 4),
        "gamma_vapor_db_km": round(gamma_w, 4),
        "zenith_attenuation_db": round(a_zenith_total, 3),
        "slant_attenuation_db": round(a_slant_total, 3),
        "risk_level": risk,
        "is_link_viable": a_slant_total < 8.0
    }


def parse_pkm_proposal_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student proposal assessment in Program Kreativitas Mahasiswa (PKM) Simbelmawa Kemendikbudristek
    for research/innovation milestone tracking, Belmawa funding qualification, and SKS credit conversion.
    """
    student_name = str(data.get("student_name", "Mahasiswa")).strip()
    nim = str(data.get("nim", "")).strip()
    title = str(data.get("proposal_title", "Proposal Rekayasa")).strip()
    scheme = str(data.get("scheme", "PKM-KC")).strip().upper()

    score_creat = max(0.0, min(100.0, float(data.get("creativity_score", 85.0))))
    score_method = max(0.0, min(100.0, float(data.get("methodology_score", 85.0))))
    score_output = max(0.0, min(100.0, float(data.get("output_potential_score", 85.0))))
    score_budget = max(0.0, min(100.0, float(data.get("budget_feasibility_score", 85.0))))

    # Composite: 30% Orisinalitas/Kreativitas, 35% Metodologi Rekayasa, 20% Potensi Luaran/Paten, 15% Kelayakan Tim & RAB
    composite = round((0.30 * score_creat) + (0.35 * score_method) + (0.20 * score_output) + (0.15 * score_budget), 2)

    if composite >= 85.0:
        letter_grade = "A"
        grade_point = 4.00
    elif composite >= 78.0:
        letter_grade = "AB"
        grade_point = 3.50
    elif composite >= 68.0:
        letter_grade = "B"
        grade_point = 3.00
    elif composite >= 60.0:
        letter_grade = "BC"
        grade_point = 2.50
    elif composite >= 50.0:
        letter_grade = "C"
        grade_point = 2.00
    else:
        letter_grade = "D"
        grade_point = 1.00

    if composite >= 82.0:
        funding_status = f"Didanai Belmawa & Lolos Nominasi PIMNAS ({scheme})"
        converted_sks = 4
        is_funded = True
    elif composite >= 72.0:
        funding_status = f"Lolos Pendanaan Hibah Simbelmawa ({scheme})"
        converted_sks = 3
        is_funded = True
    elif composite >= 60.0:
        funding_status = f"Insentif Internal Hibah Riset Prodi ({scheme})"
        converted_sks = 2
        is_funded = False
    else:
        funding_status = "Belum Memenuhi Ambang Batas Pendanaan"
        converted_sks = 0
        is_funded = False

    return {
        "student_name": student_name,
        "nim": nim,
        "proposal_title": title,
        "scheme": scheme,
        "creativity_score": score_creat,
        "methodology_score": score_method,
        "output_potential_score": score_output,
        "budget_feasibility_score": score_budget,
        "composite_score": composite,
        "letter_grade": letter_grade,
        "grade_point": grade_point,
        "funding_status": funding_status,
        "converted_sks": converted_sks,
        "is_funded": is_funded
    }


def calculate_optical_fwm_phase_matching(
    fiber_length_km: float,
    channel_spacing_ghz: float = 100.0,
    chromatic_dispersion_ps_nm_km: float = 17.0,
    center_wavelength_nm: float = 1550.0,
    attenuation_db_km: float = 0.2,
    non_linear_coeff_gamma: float = 1.3,
    channel_power_mw: float = 10.0
) -> Dict[str, Any]:
    """
    Calculates optical Four-Wave Mixing (FWM) phase-mismatch, coherence length,
    and efficiency factor in DWDM dense optical transmission (Agrawal Nonlinear Fiber Optics).
    """
    l_km = max(0.1, float(fiber_length_km))
    delta_f_ghz = max(1.0, float(channel_spacing_ghz))
    d_coeff = float(chromatic_dispersion_ps_nm_km)
    lambda_nm = max(1200.0, float(center_wavelength_nm))
    alpha_db = max(0.01, float(attenuation_db_km))
    gamma = max(0.1, float(non_linear_coeff_gamma))
    p_ch_mw = max(0.01, float(channel_power_mw))

    c_light = 299792458.0  # m/s
    lambda_m = lambda_nm * 1e-9
    delta_f_hz = delta_f_ghz * 1e9

    # Group velocity dispersion parameter beta2 (ps^2/km)
    # beta2 = - (lambda^2 / (2 * pi * c)) * D
    # With D in ps/(nm*km), beta2_ps2_km = - (lambda_nm^2 * 1e-18 / (2 * pi * c)) * (D * 1e-3 * 1e9 * 1e-12 / 1e-3)
    # Standard formula: beta2 (ps^2/km) = - (lambda_nm^2 / (2 * pi * c_nm_ps)) * D
    # At 1550nm and D=17 ps/nm/km: beta2 ~ -21.7 ps^2/km
    beta2_ps2_km = - ((lambda_nm ** 2) / (2.0 * math.pi * 0.299792458)) * d_coeff * 1e-3

    # Phase mismatch delta_beta = beta2 * (2 * pi * delta_f)^2 (in 1/km)
    omega_rad_ps = 2.0 * math.pi * (delta_f_ghz * 1e-3)  # rad/ps
    delta_beta_per_km = abs(beta2_ps2_km * (omega_rad_ps ** 2))

    # Attenuation coefficient in 1/km
    alpha_km = alpha_db / 4.3429448
    l_eff_km = (1.0 - math.exp(-alpha_km * l_km)) / alpha_km

    # Coherence length L_c = 2*pi / |delta_beta| (km)
    coherence_length_km = (2.0 * math.pi) / delta_beta_per_km if delta_beta_per_km > 1e-6 else 1000.0

    # FWM efficiency factor eta
    denom = (alpha_km ** 2) + (delta_beta_per_km ** 2)
    bracket = 1.0 + (4.0 * math.exp(-alpha_km * l_km) * (math.sin(delta_beta_per_km * l_km / 2.0) ** 2)) / ((1.0 - math.exp(-alpha_km * l_km)) ** 2)
    fwm_efficiency = ((alpha_km ** 2) / denom) * bracket
    fwm_efficiency = min(1.0, max(0.0001, fwm_efficiency))

    # Approximate generated FWM cross-talk power in dBm
    p_w = p_ch_mw * 1e-3
    p_fwm_w = fwm_efficiency * (gamma ** 2) * (p_w ** 3) * (l_eff_km ** 2) * math.exp(-alpha_km * l_km)
    p_fwm_dbm = 10.0 * math.log10(p_fwm_w * 1e3) if p_fwm_w > 0 else -100.0

    if fwm_efficiency < 0.01:
        fwm_risk = "Sangat Rendah (Dispersi Kromatik Menekan Efisiensi FWM)"
        is_acceptable = True
    elif fwm_efficiency <= 0.15:
        fwm_risk = "Moderat (Interferensi Kanal Terkendali Grid DWDM)"
        is_acceptable = True
    else:
        fwm_risk = "Tinggi (Phase-Matching Terjadi, Efisiensi FWM Signifikan)"
        is_acceptable = False

    return {
        "fiber_length_km": round(l_km, 2),
        "channel_spacing_ghz": round(delta_f_ghz, 1),
        "chromatic_dispersion_ps_nm_km": round(d_coeff, 2),
        "beta2_ps2_km": round(beta2_ps2_km, 3),
        "phase_mismatch_per_km": round(delta_beta_per_km, 4),
        "coherence_length_km": round(coherence_length_km, 2),
        "fwm_efficiency": round(fwm_efficiency, 5),
        "fwm_efficiency_percent": round(fwm_efficiency * 100.0, 3),
        "fwm_power_dbm": round(p_fwm_dbm, 2),
        "fwm_risk": fwm_risk,
        "is_acceptable": is_acceptable
    }


def calculate_5g_nr_comp_joint_transmission(
    serving_cell_rsrp_dbm: float = -85.0,
    coord_cells_rsrp_dbm: Optional[List[float]] = None,
    interference_noise_dbm: float = -95.0,
    coordination_efficiency: float = 0.85,
    bandwidth_mhz: float = 20.0
) -> Dict[str, Any]:
    """
    Calculates 3GPP Coordinated Multi-Point (CoMP) Joint Transmission (JT) SINR improvement,
    cell-edge spectral efficiency boost, and aggregate data rate according to 3GPP TS 36.819 / TS 38.300.
    """
    p_serving_dbm = float(serving_cell_rsrp_dbm)
    p_noise_dbm = float(interference_noise_dbm)
    eta_comp = max(0.1, min(1.0, float(coordination_efficiency)))
    bw_mhz = max(1.4, float(bandwidth_mhz))

    coords = coord_cells_rsrp_dbm if coord_cells_rsrp_dbm is not None else [-88.0, -92.0]
    coords = [float(p) for p in coords]

    # Convert dBm to mW: P(mW) = 10^(P_dBm / 10)
    p_serv_mw = 10.0 ** (p_serving_dbm / 10.0)
    noise_mw = 10.0 ** (p_noise_dbm / 10.0)
    coord_powers_mw = [10.0 ** (p / 10.0) for p in coords]
    sum_coord_mw = sum(coord_powers_mw)

    # 1. Non-CoMP Baseline: Neighbor cells act as strong co-channel interferers
    sinr_non_comp_linear = p_serv_mw / (sum_coord_mw + noise_mw)
    sinr_non_comp_db = 10.0 * math.log10(sinr_non_comp_linear)
    shannon_eff_non_comp = math.log2(1.0 + sinr_non_comp_linear)
    throughput_non_comp_mbps = bw_mhz * shannon_eff_non_comp * 0.75  # Practical implementation efficiency

    # 2. CoMP Joint Transmission: Coordinated cells transmit constructively, converting interference to signal
    p_sig_comp_mw = p_serv_mw + (eta_comp * sum_coord_mw)
    residual_interf_mw = (1.0 - eta_comp) * sum_coord_mw
    sinr_comp_linear = p_sig_comp_mw / (residual_interf_mw + noise_mw)
    sinr_comp_db = 10.0 * math.log10(sinr_comp_linear)
    shannon_eff_comp = math.log2(1.0 + sinr_comp_linear)
    throughput_comp_mbps = bw_mhz * shannon_eff_comp * 0.75

    sinr_gain_db = sinr_comp_db - sinr_non_comp_db
    throughput_gain_percent = ((throughput_comp_mbps - throughput_non_comp_mbps) / throughput_non_comp_mbps) * 100.0 if throughput_non_comp_mbps > 0 else 0.0

    return {
        "serving_cell_rsrp_dbm": round(p_serving_dbm, 2),
        "coordinating_cells_count": len(coords),
        "coordinating_cells_rsrp_dbm": coords,
        "coordination_efficiency": round(eta_comp, 2),
        "bandwidth_mhz": round(bw_mhz, 1),
        "sinr_non_comp_db": round(sinr_non_comp_db, 2),
        "sinr_comp_db": round(sinr_comp_db, 2),
        "sinr_gain_db": round(sinr_gain_db, 2),
        "spectral_efficiency_non_comp_bps_hz": round(shannon_eff_non_comp, 2),
        "spectral_efficiency_comp_bps_hz": round(shannon_eff_comp, 2),
        "throughput_non_comp_mbps": round(throughput_non_comp_mbps, 2),
        "throughput_comp_mbps": round(throughput_comp_mbps, 2),
        "throughput_gain_percent": round(throughput_gain_percent, 2),
        "is_comp_beneficial": sinr_gain_db >= 2.0
    }










































































