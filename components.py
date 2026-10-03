from typing import List, Dict, Tuple, Any

class EditorialComponents:
    """
    Modular HTML/CSS component generator adhering to Telkom University Purwokerto visual standards.
    """

    PRIMARY_COLOR = "#c53030"
    SECONDARY_COLOR = "#dd6b20"
    DARK_BG = "#0f172a"
    LIGHT_TEXT = "#f1f5f9"
    SOFT_BG = "#fff5f5"

    @classmethod
    def get_scoped_css(cls) -> str:
        return f"""
    .tu-editorial-container {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      line-height: 1.75;
      font-size: 16px;
      max-width: 820px;
      margin: 0 auto;
      padding: 24px 16px;
    }}
    .tu-editorial-container * {{ box-sizing: border-box; }}
    .tu-hero-header {{
      border-left: 4px solid {cls.PRIMARY_COLOR};
      padding: 0 0 0 20px;
      margin-bottom: 28px;
    }}
    .tu-badge-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 12px;
    }}
    .tu-badge {{
      display: inline-block;
      background-color: {cls.SOFT_BG};
      color: {cls.PRIMARY_COLOR};
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 4px;
      border: 1px solid rgba(197, 48, 48, 0.2);
    }}
    .tu-meta-info {{
      font-size: 13px;
      color: #64748b;
      font-weight: 500;
    }}
    .tu-article-title {{
      font-size: 28px;
      line-height: 1.3;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 16px 0;
    }}
    .tu-lead-paragraph {{
      font-size: 18px;
      line-height: 1.7;
      color: #334155;
      font-weight: 500;
      margin: 0;
    }}
    .tu-figure {{ margin: 28px 0; }}
    .tu-figure img {{
      width: 100%;
      height: auto;
      max-height: 440px;
      object-fit: cover;
      border-radius: 8px;
      display: block;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
    }}
    .tu-figcaption {{
      font-size: 13px;
      color: #64748b;
      text-align: center;
      margin-top: 10px;
      font-style: italic;
    }}
    .tu-editorial-container h2 {{
      font-size: 22px;
      line-height: 1.35;
      color: #0f172a;
      font-weight: 700;
      margin: 36px 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid #e2e8f0;
    }}
    .tu-editorial-container p {{ margin: 0 0 18px 0; color: #334155; }}
    .tu-editorial-container a {{
      color: {cls.PRIMARY_COLOR};
      text-decoration: underline;
      font-weight: 600;
      transition: color 0.2s ease;
    }}
    .tu-editorial-container a:hover {{ color: {cls.SECONDARY_COLOR}; }}
    .tu-comparison-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin: 28px 0;
    }}
    @media (max-width: 640px) {{
      .tu-comparison-grid {{ grid-template-columns: 1fr; }}
    }}
    .tu-card-col {{
      border-radius: 8px;
      padding: 20px;
      border: 1px solid #e2e8f0;
      background-color: #ffffff;
    }}
    .tu-card-col.legacy {{
      border-top: 4px solid #64748b;
      background-color: #f8fafc;
    }}
    .tu-card-col.modern {{
      border-top: 4px solid {cls.PRIMARY_COLOR};
      background-color: {cls.SOFT_BG};
    }}
    .tu-card-col h3 {{
      font-size: 16px;
      font-weight: 700;
      margin: 0 0 14px 0;
      color: #0f172a;
    }}
    .tu-card-col ul {{ margin: 0; padding-left: 18px; color: #334155; font-size: 14px; }}
    .tu-card-col li {{ margin-bottom: 8px; line-height: 1.5; }}
    .tu-highlight-card {{
      background-color: #f8fafc;
      border-left: 4px solid {cls.SECONDARY_COLOR};
      border-radius: 0 8px 8px 0;
      padding: 18px 20px;
      margin: 28px 0;
    }}
    .tu-highlight-card h3 {{
      font-size: 16px;
      color: {cls.SECONDARY_COLOR};
      font-weight: 700;
      margin: 0 0 8px 0;
    }}
    .tu-highlight-card p {{ font-size: 14px; margin: 0; color: #334155; line-height: 1.6; }}
    .tu-footer-box {{
      background-color: {cls.DARK_BG};
      color: {cls.LIGHT_TEXT};
      border-radius: 8px;
      padding: 24px;
      margin-top: 36px;
      border: 1px solid #1e293b;
    }}
    .tu-footer-box h3 {{ font-size: 18px; font-weight: 700; color: #f8fafc; margin: 0 0 12px 0; }}
    .tu-footer-box p {{ color: #cbd5e1; font-size: 14px; line-height: 1.65; margin: 0 0 12px 0; }}
    .tu-footer-box p:last-child {{ margin-bottom: 0; }}
    .tu-footer-meta {{
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid #334155;
      padding-top: 12px;
      margin-top: 12px;
    }}
    .tu-takeaways-card {{
      background-color: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-left: 4px solid #16a34a;
      border-radius: 8px;
      padding: 20px;
      margin: 28px 0;
    }}
    .tu-takeaways-card h3 {{
      font-size: 16px;
      font-weight: 700;
      color: #15803d;
      margin: 0 0 12px 0;
    }}
    .tu-takeaways-card ul {{
      margin: 0;
      padding-left: 20px;
      color: #166534;
    }}
    .tu-takeaways-card li {{ margin-bottom: 6px; }}
    .tu-author-card {{
      display: flex;
      gap: 16px;
      align-items: center;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px 20px;
      margin: 28px 0;
    }}
    .tu-faq-wrap {{
      margin: 28px 0;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      background: #ffffff;
    }}
    .tu-faq-item {{
      border-bottom: 1px solid #e2e8f0;
    }}
    .tu-faq-item:last-child {{
      border-bottom: none;
    }}
    .tu-faq-question {{
      padding: 14px 18px;
      font-size: 15px;
      font-weight: 600;
      color: #0f172a;
      cursor: pointer;
      background: #f8fafc;
    }}
    .tu-faq-answer {{
      padding: 14px 18px;
      font-size: 14px;
      color: #334155;
      line-height: 1.65;
      background: #ffffff;
    }}
    .tu-stat-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin: 28px 0;
    }}
    .tu-stat-card {{
      background: {cls.SOFT_BG};
      border: 1px solid rgba(197, 48, 48, 0.2);
      border-radius: 8px;
      padding: 20px;
      text-align: center;
    }}
    .tu-stat-number {{
      font-size: 32px;
      font-weight: 800;
      color: {cls.PRIMARY_COLOR};
      line-height: 1.2;
      margin-bottom: 6px;
    }}
    .tu-stat-label {{
      font-size: 13px;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .tu-references-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px 24px;
      margin: 32px 0;
    }}
    .tu-references-box h3 {{
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 12px 0;
    }}
    .tu-references-list {{
      margin: 0;
      padding-left: 20px;
      font-size: 13px;
      color: #475569;
      line-height: 1.6;
    }}
    .tu-references-list li {{
      margin-bottom: 8px;
    }}
    .tu-code-container {{
      position: relative;
      margin: 28px 0;
      border-radius: 8px;
      overflow: hidden;
      background: #0f172a;
      border: 1px solid #1e293b;
    }}
    .tu-code-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 16px;
      background: #1e293b;
      font-size: 12px;
      color: #94a3b8;
      font-family: monospace;
    }}
    .tu-code-badge {{
      text-transform: uppercase;
      font-weight: 700;
      color: {cls.SECONDARY_COLOR};
    }}
    .tu-code-body {{
      margin: 0;
      padding: 16px;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13.5px;
      line-height: 1.6;
      color: #f8fafc;
    }}
    .tu-table-responsive {{
      overflow-x: auto;
      margin: 28px 0;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }}
    .tu-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 14px;
    }}
    .tu-table th {{
      background: #f8fafc;
      color: #0f172a;
      font-weight: 700;
      padding: 12px 16px;
      border-bottom: 2px solid #e2e8f0;
    }}
    .tu-table td {{
      padding: 12px 16px;
      border-bottom: 1px solid #e2e8f0;
      color: #334155;
    }}
    .tu-table tr:last-child td {{
      border-bottom: none;
    }}
"""

    @classmethod
    def render_hero(cls, category: str, date_str: str, read_time: str, title: str, lead_html: str) -> str:
        return f"""    <header class="tu-hero-header">
      <div class="tu-badge-wrap">
        <span class="tu-badge">{category}</span>
        <span class="tu-meta-info">{date_str} &bull; {read_time}</span>
      </div>
      <h1 class="tu-article-title">{title}</h1>
      <p class="tu-lead-paragraph">{lead_html}</p>
    </header>"""

    @classmethod
    def render_figure(cls, img_url: str, alt_text: str, caption: str) -> str:
        return f"""    <figure class="tu-figure">
      <img src="{img_url}" alt="{alt_text}" loading="lazy" />
      <figcaption class="tu-figcaption">{caption}</figcaption>
    </figure>"""

    @classmethod
    def render_comparison_grid(cls, legacy_title: str, legacy_items: List[str], modern_title: str, modern_items: List[str]) -> str:
        legacy_li = "\n".join(f"          <li>{item}</li>" for item in legacy_items)
        modern_li = "\n".join(f"          <li>{item}</li>" for item in modern_items)
        return f"""    <div class="tu-comparison-grid">
      <div class="tu-card-col legacy">
        <h3>{legacy_title}</h3>
        <ul>
{legacy_li}
        </ul>
      </div>
      <div class="tu-card-col modern">
        <h3>{modern_title}</h3>
        <ul>
{modern_li}
        </ul>
      </div>
    </div>"""

    @classmethod
    def render_callout(cls, title: str, body_text: str) -> str:
        return f"""    <div class="tu-highlight-card">
      <h3>{title}</h3>
      <p>{body_text}</p>
    </div>"""

    @classmethod
    def render_key_takeaways(cls, items: List[str], heading: str = "Poin-Poin Kunci") -> str:
        li_elements = "\n".join(f"        <li>{item}</li>" for item in items)
        return f"""    <div class="tu-takeaways-card">
      <h3>{heading}</h3>
      <ul>
{li_elements}
      </ul>
    </div>"""

    @classmethod
    def render_author_card(cls, author_name: str, author_role: str, bio_text: str = "") -> str:
        bio_html = f"\n        <p class=\"tu-author-bio\">{bio_text}</p>" if bio_text else ""
        return f"""    <div class="tu-author-card">
      <div class="tu-author-info">
        <h4>{author_name}</h4>
        <p class="tu-author-role">{author_role}</p>{bio_html}
      </div>
    </div>"""

    @classmethod
    def render_footer(cls, title: str, summary_text: str) -> str:
        return f"""    <footer class="tu-footer-box">
      <h3>{title}</h3>
      <p>{summary_text}</p>
      <div class="tu-footer-meta">
        Dipublikasikan oleh Tim Editorial &amp; Riset S1 Teknik Informatika Telkom University Purwokerto.
      </div>
    </footer>"""

    @classmethod
    def render_faq_accordion(cls, items: List[Tuple[str, str]], section_title: str = "Pertanyaan Umum (FAQ)") -> str:
        entries = []
        for q, a in items:
            entries.append(
                f"""      <details class="tu-faq-item">
        <summary class="tu-faq-question">{q}</summary>
        <div class="tu-faq-answer">{a}</div>
      </details>"""
            )
        items_html = "\n".join(entries)
        heading_html = f"    <h2>{section_title}</h2>\n" if section_title else ""
        return f"""{heading_html}    <div class="tu-faq-wrap">
{items_html}
    </div>"""

    @classmethod
    def render_stat_grid(cls, stats: List[Dict[str, str]]) -> str:
        cards = []
        for s in stats:
            num = s.get("value", "")
            lbl = s.get("label", "")
            cards.append(
                f"""      <div class="tu-stat-card">
        <div class="tu-stat-number">{num}</div>
        <div class="tu-stat-label">{lbl}</div>
      </div>"""
            )
        cards_html = "\n".join(cards)
        return f"""    <div class="tu-stat-grid">
{cards_html}
    </div>"""

    @classmethod
    def render_references_block(cls, references: List[str], heading: str = "Referensi & Publikasi Terkait") -> str:
        items = "\n".join(f"        <li>{ref}</li>" for ref in references)
        return f"""    <section class="tu-references-box">
      <h3>{heading}</h3>
      <ol class="tu-references-list">
{items}
      </ol>
    </section>"""

    @classmethod
    def render_code_block(cls, code: str, language: str = "text", filename: str = "") -> str:
        escaped_code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        header_title = filename if filename else language.upper()
        return f"""    <div class="tu-code-container">
      <div class="tu-code-header">
        <span>{header_title}</span>
        <span class="tu-code-badge">{language}</span>
      </div>
      <pre class="tu-code-body"><code>{escaped_code}</code></pre>
    </div>"""

    @classmethod
    def render_timeline_component(cls, events: List[Dict[str, str]]) -> str:
        """
        Renders a responsive academic and event roadmap timeline.
        """
        nodes = []
        for ev in events:
            date = ev.get("date", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            title = ev.get("title", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            desc = ev.get("description", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            nodes.append(
                f"""      <div class="tu-timeline-item">
        <div class="tu-timeline-badge"></div>
        <div class="tu-timeline-content">
          <span class="tu-timeline-date">{date}</span>
          <h4 class="tu-timeline-title">{title}</h4>
          <p class="tu-timeline-desc">{desc}</p>
        </div>
      </div>"""
            )
        timeline_html = "\n".join(nodes)
        return f"""    <div class="tu-timeline">
{timeline_html}
    </div>"""

    @classmethod
    def render_alumni_quote_card(cls, name: str, batch: str, role: str, company: str, quote: str, avatar_url: str = "") -> str:
        """
        Renders an alumni testimonial card for student career showcase.
        """
        from xml.sax.saxutils import escape
        safe_name = escape(name)
        safe_batch = escape(batch)
        safe_role = escape(role)
        safe_company = escape(company)
        safe_quote = escape(quote)
        avatar_img = f'<img src="{escape(avatar_url)}" alt="{safe_name}" class="tu-alumni-avatar" loading="lazy" decoding="async" />' if avatar_url else '<div class="tu-alumni-avatar-placeholder"></div>'

        return f"""    <div class="tu-alumni-card">
      <div class="tu-alumni-quote">"{safe_quote}"</div>
      <div class="tu-alumni-meta">
        {avatar_img}
        <div class="tu-alumni-info">
          <div class="tu-alumni-name">{safe_name} <span class="tu-alumni-batch">({safe_batch})</span></div>
          <div class="tu-alumni-role">{safe_role} di <strong>{safe_company}</strong></div>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_feature_matrix(cls, columns: List[str], rows: List[Dict[str, Any]]) -> str:
        """
        Renders a curriculum/feature comparison matrix with checkmarks and highlight badges.
        """
        from xml.sax.saxutils import escape
        th_cells = "\n".join(f"          <th>{escape(col)}</th>" for col in columns)

        row_trs = []
        for r in rows:
            feat_name = escape(str(r.get("feature", "")))
            td_cells = [f"          <td class=\"tu-matrix-feature\"><strong>{feat_name}</strong></td>"]
            for val in r.get("values", []):
                if isinstance(val, bool):
                    icon = '<span class="tu-matrix-check">&#10003;</span>' if val else '<span class="tu-matrix-cross">&#10007;</span>'
                    td_cells.append(f"          <td class=\"tu-matrix-val tu-matrix-bool\">{icon}</td>")
                else:
                    td_cells.append(f"          <td class=\"tu-matrix-val\">{escape(str(val))}</td>")
            row_trs.append("        <tr>\n" + "\n".join(td_cells) + "\n        </tr>")

        body_html = "\n".join(row_trs)
        return f"""    <div class="tu-table-responsive tu-feature-matrix-wrap">
      <table class="tu-table tu-feature-matrix">
        <thead>
        <tr>
{th_cells}
        </tr>
        </thead>
        <tbody>
{body_html}
        </tbody>
      </table>
    </div>"""

    @classmethod
    def render_table_of_contents(cls, headings: List[Dict[str, str]], title: str = "Daftar Isi Artikel") -> str:
        """
        Renders a structured, accessible Table of Contents component with slugified anchor links.
        """
        if not headings:
            return ""

        from xml.sax.saxutils import escape
        import re

        items = []
        for h in headings:
            tag = h.get("tag", "h2").lower()
            text = h.get("text", "")
            slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
            slug = re.sub(r"[-\s]+", "-", slug)
            indent_class = "tu-toc-sub" if tag == "h3" else "tu-toc-item"
            items.append(f'      <li class="{indent_class}"><a href="#{slug}">{escape(text)}</a></li>')

        list_html = "\n".join(items)
        return f"""    <nav class="tu-toc-card" aria-label="{escape(title)}">
      <div class="tu-toc-header">
        <span class="tu-toc-icon">&#128203;</span>
        <h4 class="tu-toc-title">{escape(title)}</h4>
      </div>
      <ul class="tu-toc-list">
{list_html}
      </ul>
    </nav>"""







