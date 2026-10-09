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

        cat_match = re.match(r'^(?:[#*]{1,3}\s*|\*\*)([A-Za-z\s/]+)(?:\*\*|:)?$', line_clean)
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










