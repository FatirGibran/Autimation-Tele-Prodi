import re
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




































