from typing import List, Dict, Tuple, Any, Optional

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

    @classmethod
    def render_author_team(cls, members: List[Dict[str, str]], title: str = "Tim Penulis & Peneliti") -> str:
        """
        Renders an editorial author team and faculty researcher profile grid.
        """
        if not members:
            return ""

        from xml.sax.saxutils import escape

        cards = []
        for m in members:
            name = escape(m.get("name", ""))
            role = escape(m.get("role", ""))
            lab = escape(m.get("lab", ""))
            avatar = m.get("avatar_url", "")
            img_html = f'<img src="{escape(avatar)}" alt="{name}" class="tu-team-avatar" loading="lazy" decoding="async" />' if avatar else '<div class="tu-team-avatar-placeholder"></div>'
            cards.append(f"""        <div class="tu-team-card">
          {img_html}
          <div class="tu-team-info">
            <h5 class="tu-team-name">{name}</h5>
            <span class="tu-team-role">{role}</span>
            {f'<span class="tu-team-lab">{lab}</span>' if lab else ''}
          </div>
        </div>""")

        grid_html = "\n".join(cards)
        return f"""    <section class="tu-team-section">
      <h4 class="tu-team-title">{escape(title)}</h4>
      <div class="tu-team-grid">
{grid_html}
      </div>
    </section>"""

    @classmethod
    def render_download_card(cls, title: str, description: str, file_type: str, file_size: str, download_url: str) -> str:
        """
        Renders an academic resource download card (syllabus, RPS, lab guide, dataset).
        """
        from xml.sax.saxutils import escape

        safe_title = escape(title)
        safe_desc = escape(description)
        safe_type = escape(file_type.upper())
        safe_size = escape(file_size)
        safe_url = escape(download_url)

        return f"""    <div class="tu-download-card">
      <div class="tu-download-icon-box">
        <span class="tu-download-badge">{safe_type}</span>
      </div>
      <div class="tu-download-content">
        <h5 class="tu-download-title">{safe_title}</h5>
        <p class="tu-download-desc">{safe_desc}</p>
        <span class="tu-download-size">Ukuran Berkas: {safe_size}</span>
      </div>
      <div class="tu-download-action">
        <a href="{safe_url}" class="tu-download-btn" target="_blank" rel="noopener noreferrer">&#11015; Unduh Berkas</a>
      </div>
    </div>"""

    @classmethod
    def render_video_embed(cls, embed_url: str, title: str, caption: str = "") -> str:
        """
        Renders a responsive 16:9 aspect-ratio video player embed for lectures and webinars.
        """
        from xml.sax.saxutils import escape

        safe_url = escape(embed_url)
        safe_title = escape(title)
        safe_caption = escape(caption)

        caption_html = f'\n      <figcaption class="tu-video-caption">{safe_caption}</figcaption>' if caption else ""
        return f"""    <figure class="tu-video-figure">
      <div class="tu-video-responsive">
        <iframe src="{safe_url}" title="{safe_title}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy" sandbox="allow-scripts allow-same-origin allow-presentation"></iframe>
      </div>{caption_html}
    </figure>"""

    @classmethod
    def render_admission_cta(
        cls,
        headline: str = "Bergabung dengan S1 Teknik Informatika Telkom University Purwokerto",
        description: str = "",
        cta_url: str = "https://bif-pwt.telkomuniversity.ac.id/pmb",
        button_text: str = "Daftar Sekarang"
    ) -> str:
        """
        Renders a branded institutional call-to-action banner for academic admission and prospective students.
        """
        from xml.sax.saxutils import escape

        safe_headline = escape(headline)
        safe_desc = escape(description or "Wujudkan karir masa depan di bidang kecerdasan buatan, komputasi awan, dan rekayasa perangkat lunak bersama kami.")
        safe_url = escape(cta_url)
        safe_btn = escape(button_text)

        return f"""    <div class="tu-cta-banner">
      <div class="tu-cta-content">
        <h4 class="tu-cta-title">{safe_headline}</h4>
        <p class="tu-cta-desc">{safe_desc}</p>
      </div>
      <div class="tu-cta-action">
        <a href="{safe_url}" class="tu-cta-btn" target="_blank" rel="noopener noreferrer">{safe_btn} &rarr;</a>
      </div>
    </div>"""

    @classmethod
    def render_metric_callout(cls, metric: str, label: str, context: str = "") -> str:
        """
        Renders a focused highlight callout box showcasing a key metric or performance KPI.
        """
        from xml.sax.saxutils import escape

        safe_metric = escape(metric)
        safe_label = escape(label)
        safe_context = escape(context)

        context_html = f'\n      <p class="tu-metric-context">{safe_context}</p>' if context else ""
        return f"""    <div class="tu-metric-card">
      <div class="tu-metric-value">{safe_metric}</div>
      <div class="tu-metric-label">{safe_label}</div>{context_html}
    </div>"""

    @classmethod
    def render_pull_quote(cls, quote: str, author: str, source: str = "", citation_url: str = "") -> str:
        """
        Renders a distinguished editorial pull quote with attribution and academic source citation.
        """
        from xml.sax.saxutils import escape

        safe_quote = escape(quote)
        safe_author = escape(author)
        safe_source = escape(source)
        source_html = f', <cite><a href="{escape(citation_url)}" target="_blank" rel="noopener noreferrer">{safe_source}</a></cite>' if (source and citation_url) else (f', <cite>{safe_source}</cite>' if source else "")

        return f"""    <figure class="tu-pull-quote">
      <blockquote>
        <p>&ldquo;{safe_quote}&rdquo;</p>
      </blockquote>
      <figcaption>&mdash; {safe_author}{source_html}</figcaption>
    </figure>"""

    @classmethod
    def render_lab_affiliation_banner(cls, lab_name: str, focus_area: str, coordinator: str, lab_url: str = "") -> str:
        """
        Renders an official research laboratory affiliation banner for academic publications.
        """
        from xml.sax.saxutils import escape

        safe_name = escape(lab_name)
        safe_area = escape(focus_area)
        safe_coord = escape(coordinator)
        btn_html = f'<a href="{escape(lab_url)}" class="tu-lab-btn" target="_blank" rel="noopener noreferrer">Profil Lab &rarr;</a>' if lab_url else ""

        return f"""    <aside class="tu-lab-banner">
      <div class="tu-lab-badge">Laboratorium Riset Resmi</div>
      <h5 class="tu-lab-name">{safe_name}</h5>
      <p class="tu-lab-focus">Fokus Riset: <strong>{safe_area}</strong></p>
      <span class="tu-lab-coordinator">Koordinator: {safe_coord}</span>
      {btn_html}
    </aside>"""

    @classmethod
    def render_prerequisite_tree(cls, course_code: str, course_name: str, prerequisites: List[str], semester: str = "") -> str:
        """
        Renders an academic prerequisite relationship card showing required preparatory courses.
        """
        from xml.sax.saxutils import escape

        safe_code = escape(course_code)
        safe_name = escape(course_name)
        sem_html = f'<span class="tu-prereq-sem">{escape(semester)}</span>' if semester else ""

        if prerequisites:
            prereq_items = "\n".join(f'        <li>&rarr; {escape(p)}</li>' for p in prerequisites)
            prereq_list_html = f'<ul class="tu-prereq-list">\n{prereq_items}\n      </ul>'
        else:
            prereq_list_html = '<p class="tu-prereq-none">Tidak ada prasyarat mata kuliah (Terbuka).</p>'

        return f"""    <div class="tu-prereq-card">
      <div class="tu-prereq-header">
        <span class="tu-prereq-code">{safe_code}</span>
        {sem_html}
        <h5 class="tu-prereq-title">{safe_name}</h5>
      </div>
      <div class="tu-prereq-body">
        <span class="tu-prereq-label">Prasyarat Mata Kuliah:</span>
        {prereq_list_html}
      </div>
    </div>"""

    @classmethod
    def render_event_box(cls, event_name: str, date_time: str, speaker: str, location: str, rsvp_url: str = "") -> str:
        """
        Renders an academic seminar, workshop, or guest lecture announcement card.
        """
        from xml.sax.saxutils import escape

        safe_name = escape(event_name)
        safe_dt = escape(date_time)
        safe_spk = escape(speaker)
        safe_loc = escape(location)
        rsvp_html = f'<div class="tu-event-action"><a href="{escape(rsvp_url)}" class="tu-event-btn" target="_blank" rel="noopener noreferrer">Daftar Seminar &rarr;</a></div>' if rsvp_url else ""

        return f"""    <div class="tu-event-box">
      <div class="tu-event-badge">Agenda Seminar & Kuliah Tamu</div>
      <h5 class="tu-event-title">{safe_name}</h5>
      <ul class="tu-event-details">
        <li><strong>Waktu:</strong> {safe_dt}</li>
        <li><strong>Narasumber:</strong> {safe_spk}</li>
        <li><strong>Lokasi:</strong> {safe_loc}</li>
      </ul>
      {rsvp_html}
    </div>"""

    @classmethod
    def render_code_repo_card(cls, repo_name: str, github_url: str, stars: str = "", language: str = "Python", description: str = "") -> str:
        """
        Renders an open-source research dataset or software repository badge card.
        """
        from xml.sax.saxutils import escape

        safe_name = escape(repo_name)
        safe_url = escape(github_url)
        safe_lang = escape(language)
        safe_desc = escape(description)
        stars_html = f'<span class="tu-repo-stars">&#9733; {escape(stars)}</span>' if stars else ""
        desc_html = f'\n      <p class="tu-repo-desc">{safe_desc}</p>' if description else ""

        return f"""    <div class="tu-repo-card">
      <div class="tu-repo-header">
        <span class="tu-repo-icon">&#128187;</span>
        <a href="{safe_url}" class="tu-repo-link" target="_blank" rel="noopener noreferrer">{safe_name}</a>
        <span class="tu-repo-lang">{safe_lang}</span>
        {stars_html}
      </div>{desc_html}
    </div>"""

    @classmethod
    def render_faculty_profile_card(
        cls,
        name: str,
        academic_title: str,
        nidn: str,
        expertise: str,
        scholar_url: str = "",
        email: str = ""
    ) -> str:
        """
        Renders a faculty member academic profile card with NIDN and Google Scholar links.
        """
        from xml.sax.saxutils import escape

        safe_name = escape(name)
        safe_title = escape(academic_title)
        safe_nidn = escape(nidn)
        safe_exp = escape(expertise)

        scholar_html = f'<a href="{escape(scholar_url)}" class="tu-faculty-link" target="_blank" rel="noopener noreferrer">Google Scholar &rarr;</a>' if scholar_url else ""
        email_html = f'<span class="tu-faculty-email">&#9993; {escape(email)}</span>' if email else ""

        return f"""    <div class="tu-faculty-card">
      <div class="tu-faculty-badge">Profil Dosen & Peneliti</div>
      <h4 class="tu-faculty-name">{safe_name}</h4>
      <p class="tu-faculty-title">{safe_title}</p>
      <div class="tu-faculty-meta">
        <span class="tu-faculty-nidn"><strong>NIDN:</strong> {safe_nidn}</span>
        <span class="tu-faculty-expertise"><strong>Bidang Keahlian:</strong> {safe_exp}</span>
      </div>
      <div class="tu-faculty-footer">
        {email_html}
        {scholar_html}
      </div>
    </div>"""

    @classmethod
    def render_capstone_showcase_card(
        cls,
        project_title: str,
        student_names: List[str],
        supervisor: str,
        abstract: str,
        demo_url: str = "",
        github_url: str = ""
    ) -> str:
        """
        Renders a student capstone / final project showcase card with abstract and links.
        """
        from xml.sax.saxutils import escape

        safe_title = escape(project_title)
        safe_students = ", ".join(escape(s) for s in student_names)
        safe_sup = escape(supervisor)
        safe_abs = escape(abstract)

        demo_html = f'<a href="{escape(demo_url)}" class="tu-capstone-btn" target="_blank" rel="noopener noreferrer">Live Demo &rarr;</a>' if demo_url else ""
        repo_html = f'<a href="{escape(github_url)}" class="tu-capstone-link" target="_blank" rel="noopener noreferrer">Source Code</a>' if github_url else ""

        return f"""    <div class="tu-capstone-card">
      <div class="tu-capstone-badge">Showcase Tugas Akhir / Capstone</div>
      <h4 class="tu-capstone-title">{safe_title}</h4>
      <div class="tu-capstone-meta">
        <p><strong>Pengembang:</strong> {safe_students}</p>
        <p><strong>Dosen Pembimbing:</strong> {safe_sup}</p>
      </div>
      <p class="tu-capstone-abstract">{safe_abs}</p>
      <div class="tu-capstone-actions">
        {demo_html}
        {repo_html}
      </div>
    </div>"""

    @classmethod
    def render_certification_grid(cls, certifications: List[Dict[str, str]]) -> str:
        """
        Renders an industry and international certification badge grid (e.g. Cisco, AWS, Red Hat).
        """
        from xml.sax.saxutils import escape

        cards = []
        for cert in certifications:
            name = escape(cert.get("name", ""))
            issuer = escape(cert.get("issuer", ""))
            level = escape(cert.get("level", "Professional"))
            badge_icon = escape(cert.get("icon", "🏅"))
            cards.append(f"""        <div class="tu-cert-card">
          <div class="tu-cert-icon">{badge_icon}</div>
          <h5 class="tu-cert-name">{name}</h5>
          <p class="tu-cert-issuer">{issuer}</p>
          <span class="tu-cert-level">{level}</span>
        </div>""")

        items_html = "\n".join(cards)
        return f"""    <div class="tu-cert-section">
      <div class="tu-cert-header">Sertifikasi Internasional & Industri</div>
      <div class="tu-cert-grid">
{items_html}
      </div>
    </div>"""

    @classmethod
    def render_academic_calendar_card(cls, semester_title: str, events: List[Dict[str, str]]) -> str:
        """
        Renders an academic semester milestone card (e.g. Registrasi, UTS, UAS, Yudisium).
        """
        from xml.sax.saxutils import escape

        safe_title = escape(semester_title)
        event_rows = []
        for ev in events:
            date_range = escape(ev.get("date", ""))
            activity = escape(ev.get("activity", ""))
            status = escape(ev.get("status", "Mendatang"))
            event_rows.append(f"""        <div class="tu-calendar-item">
          <span class="tu-calendar-date">{date_range}</span>
          <span class="tu-calendar-activity">{activity}</span>
          <span class="tu-calendar-status">{status}</span>
        </div>""")

        rows_html = "\n".join(event_rows)
        return f"""    <div class="tu-calendar-card">
      <div class="tu-calendar-badge">Kalender Akademik</div>
      <h4 class="tu-calendar-title">{safe_title}</h4>
      <div class="tu-calendar-list">
{rows_html}
      </div>
    </div>"""

    @classmethod
    def render_industry_partner_banner(cls, banner_title: str, partners: List[Dict[str, str]]) -> str:
        """
        Renders an industry partnership and internship sponsor banner with company badges.
        """
        from xml.sax.saxutils import escape

        safe_title = escape(banner_title)
        badges = []
        for p in partners:
            name = escape(p.get("name", ""))
            category = escape(p.get("category", "Industri Teknologi"))
            badges.append(f"""        <div class="tu-partner-badge">
          <span class="tu-partner-name">{name}</span>
          <span class="tu-partner-category">{category}</span>
        </div>""")

        badges_html = "\n".join(badges)
        return f"""    <div class="tu-partner-banner">
      <h5 class="tu-partner-title">{safe_title}</h5>
      <div class="tu-partner-track">
{badges_html}
      </div>
    </div>"""

    @classmethod
    def render_accreditation_badge(cls, agency: str, grade: str, decree_no: str, valid_until: str) -> str:
        """
        Renders an official academic accreditation rating card (e.g. LAM INFOKOM / BAN-PT).
        """
        from xml.sax.saxutils import escape
        s_agency = escape(agency)
        s_grade = escape(grade)
        s_decree = escape(decree_no)
        s_valid = escape(valid_until)

        return f"""    <div class="tu-accreditation-card">
      <div class="tu-accreditation-header">
        <span class="tu-accreditation-agency">{s_agency}</span>
        <span class="tu-accreditation-grade">{s_grade}</span>
      </div>
      <div class="tu-accreditation-body">
        <p class="tu-accreditation-decree">SK: {s_decree}</p>
        <p class="tu-accreditation-validity">Berlaku Hingga: {s_valid}</p>
      </div>
    </div>"""

    @classmethod
    def render_lab_equipment_card(cls, lab_name: str, equipment_list: List[Dict[str, str]]) -> str:
        """
        Renders a research computing laboratory equipment specification card.
        """
        from xml.sax.saxutils import escape
        s_lab = escape(lab_name)
        items = []
        for eq in equipment_list:
            item_name = escape(eq.get("name", ""))
            item_specs = escape(eq.get("specs", ""))
            item_qty = escape(str(eq.get("quantity", "1")))
            items.append(f"""        <li class="tu-equip-item">
          <strong class="tu-equip-name">{item_name}</strong> ({item_qty} unit)
          <span class="tu-equip-specs">{item_specs}</span>
        </li>""")

        items_html = "\n".join(items)
        return f"""    <div class="tu-lab-equipment-card">
      <h4 class="tu-lab-name">Fasilitas Laboratorium: {s_lab}</h4>
      <ul class="tu-lab-equipment-list">
{items_html}
      </ul>
    </div>"""

    @classmethod
    def render_award_podium_card(cls, competition_name: str, achievements: List[Dict[str, str]]) -> str:
        """
        Renders an academic/hackathon competition award showcase card.
        """
        from xml.sax.saxutils import escape
        s_comp = escape(competition_name)
        podium_entries = []
        for ach in achievements:
            medal = escape(ach.get("medal", "Juara"))
            team = escape(ach.get("team", ""))
            project = escape(ach.get("project", ""))
            podium_entries.append(f"""        <div class="tu-award-item">
          <span class="tu-award-medal">{medal}</span>
          <span class="tu-award-team">{team}</span>
          <span class="tu-award-project">{project}</span>
        </div>""")

        podium_html = "\n".join(podium_entries)
        return f"""    <div class="tu-award-podium-card">
      <div class="tu-award-header">
        <span class="tu-award-badge">Prestasi Mahasiswa</span>
        <h4 class="tu-award-comp">{s_comp}</h4>
      </div>
      <div class="tu-award-list">
{podium_html}
      </div>
    </div>"""

    @classmethod
    def render_exchange_program_showcase(cls, program_title: str, universities: List[Dict[str, str]]) -> str:
        """
        Renders an international student exchange and credit transfer partner showcase.
        """
        from xml.sax.saxutils import escape
        s_title = escape(program_title)
        univ_cards = []
        for u in universities:
            name = escape(u.get("name", ""))
            country = escape(u.get("country", ""))
            quota = escape(str(u.get("quota", "Tersedia")))
            univ_cards.append(f"""        <div class="tu-exchange-card">
          <h5 class="tu-exchange-univ">{name}</h5>
          <span class="tu-exchange-country">{country}</span>
          <span class="tu-exchange-quota">Kuota: {quota}</span>
        </div>""")

        univs_html = "\n".join(univ_cards)
        return f"""    <div class="tu-exchange-showcase">
      <h4 class="tu-exchange-title">{s_title}</h4>
      <div class="tu-exchange-grid">
{univs_html}
      </div>
    </div>"""

    @classmethod
    def render_career_placement_card(cls, stat_title: str, metrics: List[Dict[str, str]]) -> str:
        """
        Renders graduate career placement and salary outcome statistics card.
        """
        from xml.sax.saxutils import escape
        s_title = escape(stat_title)
        metric_items = []
        for m in metrics:
            label = escape(m.get("label", ""))
            value = escape(str(m.get("value", "")))
            detail = escape(m.get("detail", ""))
            metric_items.append(f"""        <div class="tu-career-metric">
          <span class="tu-career-val">{value}</span>
          <span class="tu-career-lbl">{label}</span>
          <span class="tu-career-desc">{detail}</span>
        </div>""")

        metrics_html = "\n".join(metric_items)
        return f"""    <div class="tu-career-placement-card">
      <div class="tu-career-badge">Tracer Study & Karir Alumni</div>
      <h4 class="tu-career-title">{s_title}</h4>
      <div class="tu-career-grid">
{metrics_html}
      </div>
    </div>"""

    @classmethod
    def render_journal_publication_card(
        cls,
        title: str,
        authors: List[str],
        journal_name: str,
        doi_url: str,
        quartile: str = "Q1"
    ) -> str:
        """
        Renders an academic journal publication highlight card with DOI link and quartile badge.
        """
        from xml.sax.saxutils import escape
        s_title = escape(title)
        s_authors = escape(", ".join(authors))
        s_journal = escape(journal_name)
        s_doi = escape(doi_url)
        s_quartile = escape(quartile)

        return f"""    <div class="tu-journal-card">
      <div class="tu-journal-header">
        <span class="tu-journal-badge">{s_quartile}</span>
        <span class="tu-journal-venue">{s_journal}</span>
      </div>
      <h4 class="tu-journal-title">{s_title}</h4>
      <p class="tu-journal-authors">Penulis: {s_authors}</p>
      <div class="tu-journal-footer">
        <a href="{s_doi}" target="_blank" rel="noopener noreferrer" class="tu-journal-doi-link">DOI: {s_doi}</a>
      </div>
    </div>"""

    @classmethod
    def render_student_club_card(
        cls,
        club_name: str,
        focus_area: str,
        leader: str,
        meet_schedule: str,
        member_count: int
    ) -> str:
        """
        Renders a student study group and coding club showcase component.
        """
        from xml.sax.saxutils import escape
        s_club = escape(club_name)
        s_focus = escape(focus_area)
        s_leader = escape(leader)
        s_sched = escape(meet_schedule)

        return f"""    <div class="tu-club-card">
      <div class="tu-club-header">
        <h4 class="tu-club-name">{s_club}</h4>
        <span class="tu-club-badge">{s_focus}</span>
      </div>
      <div class="tu-club-meta">
        <span class="tu-club-leader">Koordinator: {s_leader}</span>
        <span class="tu-club-sched">Jadwal: {s_sched}</span>
        <span class="tu-club-count">Total Anggota: {member_count} Mahasiswa</span>
      </div>
    </div>"""

    @classmethod
    def render_research_grant_banner(
        cls,
        grant_name: str,
        scheme: str,
        funding_agency: str,
        amount: str,
        lead_researcher: str
    ) -> str:
        """
        Renders a research grant and funding announcement banner component.
        """
        from xml.sax.saxutils import escape
        s_grant = escape(grant_name)
        s_scheme = escape(scheme)
        s_agency = escape(funding_agency)
        s_amount = escape(amount)
        s_lead = escape(lead_researcher)

        return f"""    <div class="tu-grant-banner">
      <div class="tu-grant-header">
        <span class="tu-grant-tag">Hibah Riset & Pendanaan</span>
        <span class="tu-grant-scheme">{s_scheme}</span>
      </div>
      <h3 class="tu-grant-title">{s_grant}</h3>
      <div class="tu-grant-details">
        <span class="tu-grant-agency">Sumber: {s_agency}</span>
        <span class="tu-grant-amount">Total: {s_amount}</span>
        <span class="tu-grant-lead">Ketua Peneliti: {s_lead}</span>
      </div>
    </div>"""

    @classmethod
    def render_specialization_track_card(
        cls,
        track_name: str,
        description: str,
        core_courses: List[str],
        career_roles: List[str]
    ) -> str:
        """
        Renders a curriculum elective track specialization card component.
        """
        from xml.sax.saxutils import escape
        s_track = escape(track_name)
        s_desc = escape(description)
        courses_html = "".join(f"<li>{escape(c)}</li>" for c in core_courses)
        roles_html = "".join(f'<span class="tu-role-tag">{escape(r)}</span>' for r in career_roles)

        return f"""    <div class="tu-track-card">
      <h4 class="tu-track-title">{s_track}</h4>
      <p class="tu-track-desc">{s_desc}</p>
      <div class="tu-track-courses">
        <strong>Mata Kuliah Pilihan Utama:</strong>
        <ul>{courses_html}</ul>
      </div>
      <div class="tu-track-roles">
        <strong>Prospek Profesi:</strong>
        <div class="tu-role-tags">{roles_html}</div>
      </div>
    </div>"""

    @classmethod
    def render_data_center_facility_card(
        cls,
        facility_name: str,
        specs: List[Dict[str, str]],
        status: str = "Operasional"
    ) -> str:
        """
        Renders a campus tech facility and data center specification card.
        """
        from xml.sax.saxutils import escape
        s_name = escape(facility_name)
        s_status = escape(status)
        specs_rows = "".join(
            f'<tr><td class="tu-spec-key">{escape(item.get("key", ""))}</td><td class="tu-spec-val">{escape(item.get("value", ""))}</td></tr>'
            for item in specs
        )

        return f"""    <div class="tu-facility-card">
      <div class="tu-facility-header">
        <h4 class="tu-facility-name">{s_name}</h4>
        <span class="tu-facility-status">{s_status}</span>
      </div>
      <table class="tu-facility-specs">
        <tbody>
          {specs_rows}
        </tbody>
      </table>
    </div>"""

    @classmethod
    def render_capstone_project_card(
        cls,
        title: str,
        students: List[str],
        advisor: str,
        repo_url: str,
        demo_url: str,
        tags: List[str]
    ) -> str:
        """
        Renders a student capstone project showcase card with repository and demo links.
        """
        from xml.sax.saxutils import escape
        s_title = escape(title)
        s_students = escape(", ".join(students))
        s_advisor = escape(advisor)
        s_repo = escape(repo_url)
        s_demo = escape(demo_url)
        tag_spans = "".join(f'<span class="tu-capstone-tag">{escape(t)}</span>' for t in tags)

        return f"""    <div class="tu-capstone-card">
      <div class="tu-capstone-header">
        <span class="tu-capstone-badge">Tugas Akhir Unggulan</span>
        <div class="tu-capstone-tags">{tag_spans}</div>
      </div>
      <h4 class="tu-capstone-title">{s_title}</h4>
      <p class="tu-capstone-team">Tim Pengembang: {s_students}</p>
      <p class="tu-capstone-advisor">Dosen Pembimbing: {s_advisor}</p>
      <div class="tu-capstone-links">
        <a href="{s_repo}" target="_blank" rel="noopener noreferrer" class="tu-btn-code">Kode Sumber</a>
        <a href="{s_demo}" target="_blank" rel="noopener noreferrer" class="tu-btn-demo">Live Demo</a>
      </div>
    </div>"""

    @classmethod
    def render_certification_badge_card(
        cls,
        cert_name: str,
        issuer: str,
        validity_period: str,
        credential_url: str
    ) -> str:
        """
        Renders an international industry certification badge showcase card.
        """
        from xml.sax.saxutils import escape
        s_cert = escape(cert_name)
        s_issuer = escape(issuer)
        s_val = escape(validity_period)
        s_url = escape(credential_url)

        return f"""    <div class="tu-cert-card">
      <div class="tu-cert-header">
        <span class="tu-cert-badge">Sertifikasi Internasional</span>
        <span class="tu-cert-issuer">{s_issuer}</span>
      </div>
      <h4 class="tu-cert-title">{s_cert}</h4>
      <p class="tu-cert-validity">Masa Berlaku: {s_val}</p>
      <div class="tu-cert-footer">
        <a href="{s_url}" target="_blank" rel="noopener noreferrer" class="tu-cert-verify">Verifikasi Kredensial</a>
      </div>
    </div>"""

    @classmethod
    def render_academic_calendar_banner(
        cls,
        semester_name: str,
        academic_year: str,
        milestones: List[Dict[str, str]]
    ) -> str:
        """
        Renders an academic calendar semester milestone schedule banner.
        """
        from xml.sax.saxutils import escape
        s_sem = escape(semester_name)
        s_year = escape(academic_year)
        items = []
        for m in milestones:
            d = escape(m.get("date", ""))
            event = escape(m.get("event", ""))
            items.append(f"""        <div class="tu-calendar-item">
          <span class="tu-calendar-date">{d}</span>
          <span class="tu-calendar-event">{event}</span>
        </div>""")

        items_html = "\n".join(items)
        return f"""    <div class="tu-calendar-banner">
      <div class="tu-calendar-header">
        <span class="tu-calendar-badge">Kalender Akademik</span>
        <h4 class="tu-calendar-title">{s_sem} Tahun Akademik {s_year}</h4>
      </div>
      <div class="tu-calendar-milestones">
{items_html}
      </div>
    </div>"""

    @classmethod
    def render_lab_reservation_card(
        cls,
        lab_name: str,
        equipment_name: str,
        supervisor: str,
        booking_status: str,
        schedule_slots: List[str]
    ) -> str:
        """
        Renders a research laboratory equipment booking and availability card.
        """
        from xml.sax.saxutils import escape
        s_lab = escape(lab_name)
        s_equip = escape(equipment_name)
        s_super = escape(supervisor)
        s_stat = escape(booking_status)
        slots_html = "".join(f'<span class="tu-slot-pill">{escape(s)}</span>' for s in schedule_slots)

        return f"""    <div class="tu-reservation-card">
      <div class="tu-reservation-header">
        <h4 class="tu-reservation-title">{s_equip}</h4>
        <span class="tu-reservation-status">{s_stat}</span>
      </div>
      <p class="tu-reservation-lab">Laboratorium: {s_lab}</p>
      <p class="tu-reservation-supervisor">Penanggung Jawab: {s_super}</p>
      <div class="tu-reservation-slots">
        <strong>Slot Tersedia:</strong>
        <div class="tu-slots-container">{slots_html}</div>
      </div>
    </div>"""

    @classmethod
    def render_exchange_testimonial_card(
        cls,
        student_name: str,
        host_university: str,
        country: str,
        courses_transferred: List[str],
        testimonial: str
    ) -> str:
        """
        Renders an international student exchange testimonial and credit transfer showcase card.
        """
        from xml.sax.saxutils import escape
        s_student = escape(student_name)
        s_host = escape(host_university)
        s_country = escape(country)
        s_testi = escape(testimonial)
        courses_html = "".join(f"<li>{escape(c)}</li>" for c in courses_transferred)

        return f"""    <div class="tu-exchange-testi-card">
      <div class="tu-exchange-testi-header">
        <span class="tu-exchange-badge">Testimoni IISMA & Exchange</span>
        <h4 class="tu-exchange-student">{s_student}</h4>
        <span class="tu-exchange-dest">{s_host}, {s_country}</span>
      </div>
      <blockquote class="tu-exchange-quote">"{s_testi}"</blockquote>
      <div class="tu-exchange-transfer">
        <strong>Mata Kuliah Konversi:</strong>
        <ul>{courses_html}</ul>
      </div>
    </div>"""

    @classmethod
    def render_cpl_curriculum_card(
        cls,
        cpl_code: str,
        title: str,
        domain: str,
        descriptions: List[str]
    ) -> str:
        """
        Renders an academic curriculum learning outcomes (CPL / Capaian Pembelajaran Lulusan) card.
        """
        from xml.sax.saxutils import escape
        s_code = escape(cpl_code)
        s_title = escape(title)
        s_domain = escape(domain)
        items_html = "".join(f"<li>{escape(d)}</li>" for d in descriptions)

        return f"""    <div class="tu-cpl-card">
      <div class="tu-cpl-header">
        <span class="tu-cpl-code">{s_code}</span>
        <span class="tu-cpl-domain">{s_domain}</span>
      </div>
      <h4 class="tu-cpl-title">{s_title}</h4>
      <div class="tu-cpl-body">
        <strong>Deskripsi Capaian:</strong>
        <ul class="tu-cpl-list">{items_html}</ul>
      </div>
    </div>"""

    @classmethod
    def render_internship_partner_card(
        cls,
        company_name: str,
        industry: str,
        city: str,
        quota: int,
        roles: List[str],
        logo_url: str = ""
    ) -> str:
        """
        Renders an industry internship partner company profile card for student internship opportunities.
        """
        from xml.sax.saxutils import escape
        s_comp = escape(company_name)
        s_ind = escape(industry)
        s_city = escape(city)
        logo_html = f'<img src="{escape(logo_url)}" alt="{s_comp} Logo" class="tu-partner-logo" loading="lazy" />' if logo_url else ""
        roles_html = "".join(f'<span class="tu-partner-role">{escape(r)}</span>' for r in roles)

        return f"""    <div class="tu-intern-partner-card">
      <div class="tu-intern-header">
        {logo_html}
        <div class="tu-intern-info">
          <h4 class="tu-intern-company">{s_comp}</h4>
          <span class="tu-intern-industry">{s_ind} &bull; {s_city}</span>
        </div>
        <span class="tu-intern-quota">Kuota: {quota} Posisi</span>
      </div>
      <div class="tu-intern-roles">
        <strong>Posisi Magang:</strong>
        <div class="tu-intern-roles-list">{roles_html}</div>
      </div>
    </div>"""

    @classmethod
    def render_grant_expenditure_card(
        cls,
        grant_title: str,
        scheme: str,
        budget_idr: int,
        progress_pct: int,
        milestones: List[Dict[str, Any]]
    ) -> str:
        """
        Renders a research grant expenditure progress and milestone timeline card.
        """
        from xml.sax.saxutils import escape
        s_title = escape(grant_title)
        s_scheme = escape(scheme)
        formatted_budget = f"Rp {budget_idr:,.0f}".replace(",", ".")
        pct = max(0, min(100, progress_pct))

        milestone_rows = []
        for m in milestones:
            m_name = escape(m.get("milestone", ""))
            m_status = escape(m.get("status", "pending"))
            m_cost = m.get("spent_idr", 0)
            cost_str = f"Rp {m_cost:,.0f}".replace(",", ".")
            badge_cls = "tu-status-done" if m_status.lower() in ("selesai", "completed", "done") else "tu-status-wait"
            milestone_rows.append(
                f"""        <div class="tu-grant-row">
          <span class="tu-grant-ms-name">{m_name}</span>
          <span class="tu-grant-ms-cost">{cost_str}</span>
          <span class="tu-grant-ms-badge {badge_cls}">{m_status}</span>
        </div>"""
            )

        rows_html = "\n".join(milestone_rows)
        return f"""    <div class="tu-grant-exp-card">
      <div class="tu-grant-exp-header">
        <h4 class="tu-grant-exp-title">{s_title}</h4>
        <span class="tu-grant-exp-scheme">{s_scheme}</span>
      </div>
      <div class="tu-grant-budget-bar">
        <div class="tu-grant-budget-meta">
          <span>Total Anggaran: <strong>{formatted_budget}</strong></span>
          <span>Realisasi: <strong>{pct}%</strong></span>
        </div>
        <div class="tu-progress-track">
          <div class="tu-progress-fill" style="width: {pct}%;"></div>
        </div>
      </div>
      <div class="tu-grant-milestones">
{rows_html}
      </div>
    </div>"""

    @classmethod
    def render_course_reserve_book_card(
        cls,
        title: str,
        author: str,
        call_number: str,
        course_code: str,
        available_copies: int
    ) -> str:
        """
        Renders a university library course reserve textbook availability card.
        """
        from xml.sax.saxutils import escape
        s_title = escape(title)
        s_author = escape(author)
        s_call = escape(call_number)
        s_course = escape(course_code)
        status_label = f"{available_copies} Eksemplar Tersedia" if available_copies > 0 else "Sedang Dipinjam Semua"
        badge_cls = "tu-reserve-avail" if available_copies > 0 else "tu-reserve-empty"

        return f"""    <div class="tu-reserve-card">
      <div class="tu-reserve-header">
        <span class="tu-reserve-badge">Buku Teks Wajib</span>
        <span class="tu-reserve-course">{s_course}</span>
      </div>
      <h4 class="tu-reserve-title">{s_title}</h4>
      <p class="tu-reserve-author">Penulis: {s_author}</p>
      <div class="tu-reserve-meta">
        <span class="tu-reserve-call">Nomor Panggil: <code>{s_call}</code></span>
        <span class="tu-reserve-status {badge_cls}">{status_label}</span>
      </div>
    </div>"""

    @classmethod
    def render_alumni_tracer_stat_card(
        cls,
        cohort_year: int,
        response_rate: float,
        avg_wait_months: float,
        top_industries: List[Dict[str, Any]]
    ) -> str:
        """
        Renders a graduate tracer study statistical summary card for alumni career tracking.
        """
        from xml.sax.saxutils import escape
        resp_pct = f"{response_rate:.1f}%"
        wait_str = f"{avg_wait_months:.1f} Bulan"

        industry_items = []
        for ind in top_industries:
            name = escape(ind.get("industry", ""))
            pct = ind.get("percentage", 0)
            industry_items.append(
                f"""        <div class="tu-tracer-ind-item">
          <span class="tu-tracer-ind-name">{name}</span>
          <span class="tu-tracer-ind-bar-wrap">
            <span class="tu-tracer-ind-bar" style="width: {pct}%;"></span>
          </span>
          <span class="tu-tracer-ind-pct">{pct}%</span>
        </div>"""
            )

        ind_html = "\n".join(industry_items)
        return f"""    <div class="tu-tracer-card">
      <div class="tu-tracer-header">
        <h4 class="tu-tracer-title">Tracer Study Lulusan Angkatan {cohort_year}</h4>
        <span class="tu-tracer-badge">Karier Alumni</span>
      </div>
      <div class="tu-tracer-kpis">
        <div class="tu-tracer-kpi">
          <span class="tu-tracer-kpi-val">{resp_pct}</span>
          <span class="tu-tracer-kpi-lbl">Tingkat Respon</span>
        </div>
        <div class="tu-tracer-kpi">
          <span class="tu-tracer-kpi-val">{wait_str}</span>
          <span class="tu-tracer-kpi-lbl">Rata-rata Masa Tunggu Kerja</span>
        </div>
      </div>
      <div class="tu-tracer-industries">
        <strong>Distribusi Bidang Industri:</strong>
{ind_html}
      </div>
    </div>"""

    @classmethod
    def render_curriculum_prerequisite_flow(
        cls,
        course_code: str,
        course_name: str,
        direct_prereqs: List[str],
        unlocks_courses: List[str],
        min_credits_required: int = 0
    ) -> str:
        """
        Renders an academic curriculum prerequisite pathway flow card
        showing course requirements and forward course unlocking chains.
        """
        from xml.sax.saxutils import escape

        code_esc = escape(course_code.strip())
        name_esc = escape(course_name.strip())

        prereq_lis = "".join(f"<li>{escape(p.strip())}</li>" for p in direct_prereqs) if direct_prereqs else "<li><em>Tidak ada prasyarat mata kuliah langsung</em></li>"
        unlock_lis = "".join(f"<li>{escape(u.strip())}</li>" for u in unlocks_courses) if unlocks_courses else "<li><em>Mata kuliah terminal / tingkat akhir</em></li>"

        sks_note = f'<div class="tu-prereq-credits-req">&#9888; Syarat minimal kelulusan: <strong>{min_credits_required} SKS</strong></div>' if min_credits_required > 0 else ""

        return f"""    <div class="tu-prereq-flow-card">
      <div class="tu-prereq-header">
        <span class="tu-prereq-badge">{code_esc}</span>
        <h4 class="tu-prereq-title">{name_esc}</h4>
      </div>
      {sks_note}
      <div class="tu-prereq-columns">
        <div class="tu-prereq-col">
          <span class="tu-prereq-col-label">&#9664; Prasyarat Sebelumnya:</span>
          <ul class="tu-prereq-list">
            {prereq_lis}
          </ul>
        </div>
        <div class="tu-prereq-col">
          <span class="tu-prereq-col-label">&#9654; Membuka Mata Kuliah:</span>
          <ul class="tu-prereq-list">
            {unlock_lis}
          </ul>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_lab_safety_equipment_card(
        cls,
        lab_name: str,
        ppe_items: List[Dict[str, str]],
        emergency_contacts: List[Dict[str, str]]
    ) -> str:
        """
        Renders a laboratory safety protocol and PPE requirement checklist card
        for compliance with campus OHS (K3) and ISO standards.
        """
        from xml.sax.saxutils import escape

        lab_esc = escape(lab_name.strip())

        ppe_rows = []
        for p in ppe_items:
            item = escape(str(p.get("item", "")))
            req = escape(str(p.get("required", "Wajib")))
            std = escape(str(p.get("standard", "-")))
            ppe_rows.append(f"""          <tr>
            <td><strong>{item}</strong></td>
            <td><span class="tu-safety-req-badge">{req}</span></td>
            <td><code>{std}</code></td>
          </tr>""")
        ppe_tbody = "\n".join(ppe_rows) if ppe_rows else "          <tr><td colspan='3'><em>Tidak ada daftar APD khusus.</em></td></tr>"

        contact_items = []
        for c in emergency_contacts:
            name = escape(str(c.get("name", "")))
            phone = escape(str(c.get("phone", "")))
            contact_items.append(f'<li><strong>{name}:</strong> <a href="tel:{phone}">{phone}</a></li>')
        contacts_html = "\n            ".join(contact_items) if contact_items else "<li><em>Kontak darurat belum diset.</em></li>"

        return f"""    <div class="tu-lab-safety-card">
      <div class="tu-safety-header">
        <span class="tu-safety-icon">&#9888;</span>
        <h4 class="tu-safety-title">Protokol Keselamatan Laboratorium: {lab_esc}</h4>
      </div>
      <table class="tu-safety-table">
        <thead>
          <tr>
            <th>Alat Pelindung Diri (APD)</th>
            <th>Status</th>
            <th>Standar / Spesifikasi</th>
          </tr>
        </thead>
        <tbody>
{ppe_tbody}
        </tbody>
      </table>
      <div class="tu-safety-emergency">
        <strong>Kontak Darurat Tanggap Cepat:</strong>
        <ul class="tu-safety-contacts">
            {contacts_html}
        </ul>
      </div>
    </div>"""

    @classmethod
    def render_exchange_quota_table(
        cls,
        program_name: str,
        partners: List[Dict[str, Any]],
        academic_year: str
    ) -> str:
        """
        Renders an international student exchange and study abroad partner quota table.
        """
        from xml.sax.saxutils import escape

        prog_esc = escape(program_name.strip())
        year_esc = escape(academic_year.strip())

        rows = []
        for p in partners:
            univ = escape(str(p.get("university", "")))
            country = escape(str(p.get("country", "")))
            quota = p.get("quota", 0)
            min_gpa = f"{float(p.get('min_gpa', 3.0)):.2f}"
            lang = escape(str(p.get("language_requirement", "-")))
            rows.append(f"""          <tr>
            <td><strong>{univ}</strong></td>
            <td>{country}</td>
            <td><span class="tu-quota-badge">{quota} Mahasiswa</span></td>
            <td><code>IPK &ge; {min_gpa}</code></td>
            <td>{lang}</td>
          </tr>""")

        tbody = "\n".join(rows) if rows else "          <tr><td colspan='5'><em>Belum ada mitra pertukaran terdaftar.</em></td></tr>"

        return f"""    <div class="tu-exchange-quota-container">
      <div class="tu-exchange-header">
        <h4 class="tu-exchange-title">Program Pertukaran Mahasiswa: {prog_esc}</h4>
        <span class="tu-exchange-year">Tahun Akademik {year_esc}</span>
      </div>
      <table class="tu-exchange-quota-table">
        <thead>
          <tr>
            <th>Universitas Mitra</th>
            <th>Negara</th>
            <th>Kuota</th>
            <th>Syarat IPK</th>
            <th>Syarat Bahasa</th>
          </tr>
        </thead>
        <tbody>
{tbody}
        </tbody>
      </table>
    </div>"""

    @classmethod
    def render_grant_funding_milestone_card(
        cls,
        project_title: str,
        grant_agency: str,
        budget_idr: int,
        milestones: List[Dict[str, Any]]
    ) -> str:
        """
        Renders a faculty research grant milestone progress tracker card
        with IDR budget localization and status indicators.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(project_title.strip())
        agency_esc = escape(grant_agency.strip())
        # Format IDR currency with thousand dot separators
        budget_str = f"Rp {budget_idr:,.0f}".replace(",", ".")

        milestone_items = []
        for idx, m in enumerate(milestones, 1):
            phase = escape(str(m.get("phase", f"Tahap {idx}")))
            status = escape(str(m.get("status", "Pending")))
            desc = escape(str(m.get("description", "")))
            pct = int(m.get("progress_pct", 0))
            milestone_items.append(f"""        <div class="tu-grant-milestone-item">
          <div class="tu-grant-ms-meta">
            <span class="tu-grant-ms-phase">{phase}</span>
            <span class="tu-grant-ms-status">{status} ({pct}%)</span>
          </div>
          <p class="tu-grant-ms-desc">{desc}</p>
          <div class="tu-grant-ms-bar-wrap">
            <div class="tu-grant-ms-bar" style="width: {pct}%;"></div>
          </div>
        </div>""")

        ms_html = "\n".join(milestone_items) if milestone_items else "        <p><em>Belum ada rincian tahapan capaian riset.</em></p>"

        return f"""    <div class="tu-grant-card">
      <div class="tu-grant-header">
        <span class="tu-grant-agency-badge">{agency_esc}</span>
        <h4 class="tu-grant-title">{title_esc}</h4>
      </div>
      <div class="tu-grant-meta">
        <span class="tu-grant-budget-lbl">Total Dana Hibah:</span>
        <strong class="tu-grant-budget-val">{budget_str}</strong>
      </div>
      <div class="tu-grant-milestones">
        <strong>Tahapan Capaian Luaran:</strong>
{ms_html}
      </div>
    </div>"""

    @classmethod
    def render_tracer_salary_histogram(
        cls,
        cohort_year: int,
        salary_brackets: List[Dict[str, Any]],
        median_salary_idr: int
    ) -> str:
        """
        Renders a graduate tracer study salary distribution bar histogram
        with Indonesian median wage indicator.
        """
        from xml.sax.saxutils import escape

        median_str = f"Rp {median_salary_idr:,.0f}".replace(",", ".")

        bar_items = []
        for b in salary_brackets:
            label = escape(str(b.get("bracket", "")))
            pct = float(b.get("percentage", 0.0))
            count = b.get("count", 0)
            bar_items.append(f"""        <div class="tu-salary-bar-item">
          <div class="tu-salary-bar-meta">
            <span class="tu-salary-bracket-label">{label}</span>
            <span class="tu-salary-bracket-pct">{pct:.1f}% ({count} orang)</span>
          </div>
          <div class="tu-salary-bar-track">
            <div class="tu-salary-bar-fill" style="width: {pct}%;"></div>
          </div>
        </div>""")

        bars_html = "\n".join(bar_items) if bar_items else "        <p><em>Data distribusi gaji belum tersedia.</em></p>"

        return f"""    <div class="tu-salary-histogram-card">
      <div class="tu-salary-hist-header">
        <h4 class="tu-salary-hist-title">Distribusi Gaji Pertama Lulusan (Angkatan {cohort_year})</h4>
        <div class="tu-salary-median-badge">
          <span>Median Gaji:</span>
          <strong>{median_str}</strong>
        </div>
      </div>
      <div class="tu-salary-bars-wrap">
{bars_html}
      </div>
    </div>"""

    @classmethod
    def render_bloom_taxonomy_level_card(
        cls,
        course_code: str,
        course_name: str,
        bloom_levels: List[Dict[str, Any]]
    ) -> str:
        """
        Renders a curriculum learning outcome card mapping course competencies
        across Bloom's cognitive taxonomy levels (C1 - C6) for academic accreditation.
        """
        from xml.sax.saxutils import escape

        code_esc = escape(course_code.strip())
        name_esc = escape(course_name.strip())

        items = []
        for b in bloom_levels:
            lvl = escape(str(b.get("level", "C1")))
            cpl = escape(str(b.get("cpl_code", "")))
            desc = escape(str(b.get("description", "")))
            weight = int(b.get("weight_pct", 0))
            items.append(f"""        <div class="tu-bloom-item">
          <div class="tu-bloom-meta">
            <span class="tu-bloom-badge">{lvl}</span>
            {f'<span class="tu-bloom-cpl">{cpl}</span>' if cpl else ''}
            <span class="tu-bloom-weight">Bobot: {weight}%</span>
          </div>
          <p class="tu-bloom-desc">{desc}</p>
        </div>""")

        items_html = "\n".join(items) if items else "<p><em>Belum ada pemetaan taksonomi Bloom.</em></p>"

        return f"""    <div class="tu-bloom-card">
      <div class="tu-bloom-header">
        <span class="tu-bloom-course-code">{code_esc}</span>
        <h4 class="tu-bloom-title">{name_esc} - Pemetaan Taksonomi Bloom</h4>
      </div>
      <div class="tu-bloom-list">
{items_html}
      </div>
    </div>"""

    @classmethod
    def render_hazardous_waste_protocol_card(
        cls,
        lab_name: str,
        waste_categories: List[Dict[str, str]],
        disposal_schedule: str
    ) -> str:
        """
        Renders a laboratory chemical and hazardous waste (B3) management protocol card
        for lab safety compliance and environmental health accreditation.
        """
        from xml.sax.saxutils import escape

        lab_esc = escape(lab_name.strip())
        sched_esc = escape(disposal_schedule.strip())

        rows = []
        for w in waste_categories:
            cat = escape(str(w.get("category", "")))
            cont = escape(str(w.get("container_type", "")))
            loc = escape(str(w.get("storage_location", "")))
            notes = escape(str(w.get("safety_notes", "")))
            rows.append(f"""          <tr>
            <td><strong>{cat}</strong></td>
            <td>{cont}</td>
            <td>{loc}</td>
            <td>{notes}</td>
          </tr>""")

        tbody_html = "\n".join(rows) if rows else "          <tr><td colspan=\"4\"><em>Tidak ada kategori limbah terdaftar.</em></td></tr>"

        return f"""    <div class="tu-waste-protocol-card">
      <div class="tu-waste-header">
        <span class="tu-waste-badge">Protokol Pengelolaan Limbah B3</span>
        <h4 class="tu-waste-lab-name">{lab_esc}</h4>
      </div>
      <div class="tu-waste-schedule">
        <strong>Jadwal Pengangkutan / Disposal:</strong> {sched_esc}
      </div>
      <table class="tu-waste-table">
        <thead>
          <tr>
            <th>Kategori Limbah</th>
            <th>Wadah / Kontainer</th>
            <th>Lokasi Simpan</th>
            <th>Catatan K3</th>
          </tr>
        </thead>
        <tbody>
{tbody_html}
        </tbody>
      </table>
    </div>"""

    @classmethod
    def render_credit_transfer_matrix(
        cls,
        host_university: str,
        course_mappings: List[Dict[str, Any]]
    ) -> str:
        """
        Renders an academic credit transfer matrix card mapping study abroad/exchange
        host university courses to home curriculum courses and recognized SKS credits.
        """
        from xml.sax.saxutils import escape

        univ_esc = escape(host_university.strip())

        rows = []
        for m in course_mappings:
            h_code = escape(str(m.get("host_course_code", "")))
            h_name = escape(str(m.get("host_course_name", "")))
            h_cred = escape(str(m.get("host_credits", "")))
            d_code = escape(str(m.get("home_course_code", "")))
            d_name = escape(str(m.get("home_course_name", "")))
            d_sks = int(m.get("home_sks", 0))
            stat = escape(str(m.get("status", "Disetujui")))

            rows.append(f"""          <tr>
            <td><strong>{h_code}</strong> {h_name}</td>
            <td>{h_cred}</td>
            <td><strong>{d_code}</strong> {d_name}</td>
            <td>{d_sks} SKS</td>
            <td><span class="tu-credit-status">{stat}</span></td>
          </tr>""")

        tbody_html = "\n".join(rows) if rows else "          <tr><td colspan=\"5\"><em>Tidak ada mata kuliah terpetakan.</em></td></tr>"

        return f"""    <div class="tu-credit-transfer-card">
      <div class="tu-credit-transfer-header">
        <span class="tu-credit-badge">Matriks Transfer Kredit</span>
        <h4 class="tu-credit-host-univ">{univ_esc}</h4>
      </div>
      <table class="tu-credit-table">
        <thead>
          <tr>
            <th>Mata Kuliah Mitra</th>
            <th>Kredit Mitra</th>
            <th>Mata Kuliah Diakui</th>
            <th>SKS Diakui</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
{tbody_html}
        </tbody>
      </table>
    </div>"""

    @classmethod
    def render_patent_grant_card(
        cls,
        patent_title: str,
        patent_number: str,
        inventors: List[str],
        filing_date: str,
        status: str,
        abstract: str = ""
    ) -> str:
        """
        Renders a faculty research intellectual property right (IPR/Paten) grant showcase card
        highlighting patent number, inventors, filing timeline, and legal registration status.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(patent_title.strip())
        num_esc = escape(patent_number.strip())
        date_esc = escape(filing_date.strip())
        stat_esc = escape(status.strip())
        invs_esc = escape(", ".join(inv.strip() for inv in inventors if inv.strip()))

        abstract_html = f'\n      <p class="tu-patent-abstract">{escape(abstract.strip())}</p>' if abstract.strip() else ""

        return f"""    <div class="tu-patent-card">
      <div class="tu-patent-badge">Paten &amp; Hak Kekayaan Intelektual</div>
      <h4 class="tu-patent-title">{title_esc}</h4>
      <div class="tu-patent-meta">
        <span class="tu-patent-number">No: <strong>{num_esc}</strong></span>
        <span class="tu-patent-status">Status: <strong>{stat_esc}</strong></span>
        <span class="tu-patent-date">Tanggal: <strong>{date_esc}</strong></span>
      </div>
      <div class="tu-patent-inventors">
        <span>Inventor:</span> <strong>{invs_esc}</strong>
      </div>{abstract_html}
    </div>"""

    @classmethod
    def render_industry_partner_testimonial(
        cls,
        company_name: str,
        representative_name: str,
        position: str,
        quote: str,
        partner_logo_url: str = "",
        hired_alumni_count: int = 0
    ) -> str:
        """
        Renders an industry employer testimonial card for graduate tracer studies,
        showcasing corporate feedback and total alumni absorbed into the workforce.
        """
        from xml.sax.saxutils import escape

        comp_esc = escape(company_name.strip())
        rep_esc = escape(representative_name.strip())
        pos_esc = escape(position.strip())
        quote_esc = escape(quote.strip())

        logo_html = f'<img src="{escape(partner_logo_url)}" alt="{comp_esc}" class="tu-partner-logo" loading="lazy" />\n        ' if partner_logo_url.strip() else ""
        hired_html = f'\n      <div class="tu-partner-hired-badge">Telah merekrut <strong>{hired_alumni_count} alumni</strong></div>' if hired_alumni_count > 0 else ""

        return f"""    <div class="tu-partner-testimonial-card">
      <div class="tu-partner-header">
        {logo_html}<div class="tu-partner-info">
          <h4 class="tu-partner-company">{comp_esc}</h4>
          <span class="tu-partner-rep">{rep_esc}, {pos_esc}</span>
        </div>
      </div>
      <blockquote class="tu-partner-quote">&ldquo;{quote_esc}&rdquo;</blockquote>{hired_html}
    </div>"""

    @classmethod
    def render_capstone_milestone_stepper(
        cls,
        project_title: str,
        milestones: List[Dict[str, Any]],
        current_step_index: int = 1
    ) -> str:
        """
        Renders a sequential milestone stepper card for undergraduate final year capstone/thesis projects,
        tracking stages from proposal seminar to manuscript publication and degree conferral.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(project_title.strip())

        steps = []
        for idx, m in enumerate(milestones, 1):
            s_num = int(m.get("step_number", idx))
            s_title = escape(str(m.get("title", "")))
            s_date = escape(str(m.get("due_date", "")))
            s_stat = escape(str(m.get("status", "Menunggu")))

            is_active = (s_num == current_step_index)
            is_completed = (s_num < current_step_index) or ("selesai" in s_stat.lower())
            cls_state = "tu-step-completed" if is_completed else ("tu-step-active" if is_active else "tu-step-pending")

            steps.append(f"""        <div class="tu-step-item {cls_state}">
          <div class="tu-step-circle">{s_num}</div>
          <div class="tu-step-content">
            <h5 class="tu-step-name">{s_title}</h5>
            <span class="tu-step-date">{s_date}</span>
            <span class="tu-step-status">{s_stat}</span>
          </div>
        </div>""")

        steps_html = "\n".join(steps) if steps else "        <p><em>Belum ada tahapan milestone terdefinisi.</em></p>"

        return f"""    <div class="tu-capstone-stepper-card">
      <div class="tu-stepper-header">
        <span class="tu-stepper-badge">Alur Milestone Tugas Akhir</span>
        <h4 class="tu-stepper-title">{title_esc}</h4>
      </div>
      <div class="tu-stepper-track">
{steps_html}
      </div>
    </div>"""

    @classmethod
    def render_lab_workshop_banner(
        cls,
        workshop_title: str,
        speaker_name: str,
        speaker_affiliation: str,
        date_time: str,
        venue: str,
        registration_url: str,
        quota_left: int = 0
    ) -> str:
        """
        Renders an open house hands-on workshop registration banner for academic research laboratories.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(workshop_title.strip())
        spk_esc = escape(speaker_name.strip())
        aff_esc = escape(speaker_affiliation.strip())
        dt_esc = escape(date_time.strip())
        ven_esc = escape(venue.strip())
        reg_esc = escape(registration_url.strip())

        quota_html = f'<span>Sisa Kuota: <strong>{quota_left} Kursi</strong></span>' if quota_left > 0 else '<span>Sisa Kuota: <strong>Terbuka Umum</strong></span>'

        return f"""    <div class="tu-workshop-card">
      <div class="tu-workshop-badge">Workshop Riset &amp; Pelatihan Lab</div>
      <h4 class="tu-workshop-title">{title_esc}</h4>
      <div class="tu-workshop-speaker">
        <strong>Narasumber:</strong> {spk_esc} ({aff_esc})
      </div>
      <div class="tu-workshop-meta">
        <span>Waktu: <strong>{dt_esc}</strong></span>
        <span>Lokasi: <strong>{ven_esc}</strong></span>
        {quota_html}
      </div>
      <a href="{reg_esc}" class="tu-workshop-btn" target="_blank" rel="noopener noreferrer">Daftar Workshop &rarr;</a>
    </div>"""

    @classmethod
    def render_internship_experience_card(
        cls,
        student_name: str,
        company_name: str,
        role: str,
        period: str,
        project_summary: str,
        mentor_name: str = ""
    ) -> str:
        """
        Renders an MBKM certified student industrial internship (MSIB) experience card,
        highlighting company placement, technical role, duration, project impact, and industry mentor.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(student_name.strip())
        comp_esc = escape(company_name.strip())
        role_esc = escape(role.strip())
        per_esc = escape(period.strip())
        sum_esc = escape(project_summary.strip())

        mentor_html = f'<span>Mentor Industri: <strong>{escape(mentor_name.strip())}</strong></span>' if mentor_name.strip() else ""

        return f"""    <div class="tu-internship-card">
      <div class="tu-internship-badge">Pengalaman Magang Bersertifikat (MSIB)</div>
      <h4 class="tu-internship-company">{comp_esc} &mdash; {role_esc}</h4>
      <div class="tu-internship-meta">
        <span>Mahasiswa: <strong>{name_esc}</strong></span>
        <span>Periode: <strong>{per_esc}</strong></span>
        {mentor_html}
      </div>
      <p class="tu-internship-summary">{sum_esc}</p>
    </div>"""

    @classmethod
    def render_monograph_showcase_card(
        cls,
        book_title: str,
        authors: List[str],
        publisher: str,
        isbn: str,
        year: int,
        synopsis: str,
        purchase_url: str = ""
    ) -> str:
        """
        Renders a scholarly monograph and university academic textbook publication showcase card.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(book_title.strip())
        authors_esc = escape(", ".join(a.strip() for a in authors if a.strip()))
        pub_esc = escape(publisher.strip())
        isbn_esc = escape(isbn.strip())
        syn_esc = escape(synopsis.strip())

        btn_html = f'\n      <a href="{escape(purchase_url.strip())}" class="tu-monograph-btn" target="_blank" rel="noopener noreferrer">Informasi / Akses Buku &rarr;</a>' if purchase_url.strip() else ""

        return f"""    <div class="tu-monograph-card">
      <div class="tu-monograph-badge">Monograf &amp; Buku Ajar Akademik</div>
      <h4 class="tu-monograph-title">{title_esc}</h4>
      <div class="tu-monograph-meta">
        <span>Penulis: <strong>{authors_esc}</strong></span>
        <span>Penerbit: <strong>{pub_esc} ({year})</strong></span>
        <span>ISBN: <strong>{isbn_esc}</strong></span>
      </div>
      <p class="tu-monograph-synopsis">{syn_esc}</p>{btn_html}
    </div>"""

    @classmethod
    def render_partner_university_profile_card(
        cls,
        univ_name: str,
        country: str,
        world_ranking: str,
        agreement_type: str,
        logo_url: str = "",
        contact_person: str = ""
    ) -> str:
        """
        Renders a global academic partner university profile card for international mobility and dual degree programs.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(univ_name.strip())
        c_esc = escape(country.strip())
        rank_esc = escape(world_ranking.strip())
        agree_esc = escape(agreement_type.strip())

        logo_html = f'<img src="{escape(logo_url.strip())}" alt="{name_esc}" class="tu-partner-univ-logo" loading="lazy" />\n        ' if logo_url.strip() else ""
        contact_html = f'<span>Kontak Person: <strong>{escape(contact_person.strip())}</strong></span>' if contact_person.strip() else ""

        return f"""    <div class="tu-partner-univ-card">
      <div class="tu-partner-univ-header">
        {logo_html}<div class="tu-partner-univ-info">
          <span class="tu-partner-univ-country">{c_esc}</span>
          <h4 class="tu-partner-univ-name">{name_esc}</h4>
        </div>
      </div>
      <div class="tu-partner-univ-meta">
        <span>Peringkat Dunia: <strong>{rank_esc}</strong></span>
        <span>Skema Kerja Sama: <strong>{agree_esc}</strong></span>
        {contact_html}
      </div>
    </div>"""

    @classmethod
    def render_community_service_card(
        cls,
        title: str,
        partner: str,
        location: str,
        grant_source: str,
        beneficiaries: int,
        sdgs_label: str
    ) -> str:
        """
        Renders a community service (Pengabdian kepada Masyarakat / PKM) showcase card for social impact reporting.
        """
        from xml.sax.saxutils import escape

        t_esc = escape(title.strip())
        p_esc = escape(partner.strip())
        loc_esc = escape(location.strip())
        grant_esc = escape(grant_source.strip())
        sdg_esc = escape(sdgs_label.strip())

        return f"""    <div class="tu-pkm-card">
      <div class="tu-pkm-badge">{sdg_esc}</div>
      <h4 class="tu-pkm-title">{t_esc}</h4>
      <div class="tu-pkm-meta">
        <span>Mitra Komunitas: <strong>{p_esc}</strong></span>
        <span>Lokasi: <strong>{loc_esc}</strong></span>
        <span>Penerima Manfaat: <strong>{beneficiaries} Orang</strong></span>
        <span>Sumber Dana: <strong>{grant_esc}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_competition_achievement_card(
        cls,
        competition_name: str,
        award_rank: str,
        team_name: str,
        team_members: List[str],
        supervisor: str,
        year: int
    ) -> str:
        """
        Renders a student innovation and technology competition achievement showcase card.
        """
        from xml.sax.saxutils import escape

        comp_esc = escape(competition_name.strip())
        award_esc = escape(award_rank.strip())
        team_esc = escape(team_name.strip())
        spv_esc = escape(supervisor.strip())
        members_html = "".join(f"<li>{escape(m.strip())}</li>" for m in team_members if m.strip())

        return f"""    <div class="tu-competition-card">
      <div class="tu-competition-badge">Prestasi Kompetisi {year}</div>
      <h4 class="tu-competition-award">{award_esc}</h4>
      <div class="tu-competition-name">{comp_esc}</div>
      <div class="tu-competition-team">
        <span>Tim: <strong>{team_esc}</strong></span>
        <span>Pembimbing: <strong>{spv_esc}</strong></span>
      </div>
      <ul class="tu-competition-members">{members_html}</ul>
    </div>"""

    @classmethod
    def render_journal_badge_card(
        cls,
        journal_name: str,
        sinta_rank: int,
        issn: str,
        publisher: str,
        focus_scope: str,
        archive_url: str = ""
    ) -> str:
        """
        Renders an academic journal profile card with official SINTA accreditation rank badge and ISSN.
        """
        from xml.sax.saxutils import escape

        j_esc = escape(journal_name.strip())
        issn_esc = escape(issn.strip())
        pub_esc = escape(publisher.strip())
        scope_esc = escape(focus_scope.strip())
        btn_html = f'\n      <a href="{escape(archive_url.strip())}" class="tu-journal-link" target="_blank" rel="noopener noreferrer">Kunjungi OJS Portal</a>' if archive_url.strip() else ""

        return f"""    <div class="tu-journal-card">
      <div class="tu-journal-header">
        <span class="tu-sinta-badge sinta-{sinta_rank}">SINTA {sinta_rank}</span>
        <span class="tu-journal-issn">E-ISSN: {issn_esc}</span>
      </div>
      <h4 class="tu-journal-title">{j_esc}</h4>
      <div class="tu-journal-meta">
        <span>Penerbit: <strong>{pub_esc}</strong></span>
        <span>Fokus &amp; Ruang Lingkup: <strong>{scope_esc}</strong></span>
      </div>{btn_html}
    </div>"""

    @classmethod
    def render_teaching_assistant_recruitment_card(
        cls,
        course_name: str,
        lab_name: str,
        semester: str,
        min_grade: str,
        deadline: str,
        registration_url: str
    ) -> str:
        """
        Renders a laboratory teaching assistant (Asisten Praktikum / Asprak) recruitment announcement card.
        """
        from xml.sax.saxutils import escape

        course_esc = escape(course_name.strip())
        lab_esc = escape(lab_name.strip())
        sem_esc = escape(semester.strip())
        grade_esc = escape(min_grade.strip())
        dl_esc = escape(deadline.strip())
        url_esc = escape(registration_url.strip())

        return f"""    <div class="tu-ta-recruitment-card">
      <div class="tu-ta-badge">Open Recruitment Asisten Praktikum</div>
      <h4 class="tu-ta-course">{course_esc}</h4>
      <div class="tu-ta-lab">{lab_esc} ({sem_esc})</div>
      <div class="tu-ta-requirements">
        <span>Nilai Minimal Mata Kuliah: <strong>{grade_esc}</strong></span>
        <span>Batas Akhir Pendaftaran: <strong>{dl_esc}</strong></span>
      </div>
      <a href="{url_esc}" class="tu-ta-cta-btn" target="_blank" rel="noopener noreferrer">Daftar Asisten Sekarang</a>
    </div>"""

    @classmethod
    def render_lab_safety_guideline_card(
        cls,
        lab_name: str,
        pic_technician: str,
        safety_rules: List[str],
        emergency_call: str
    ) -> str:
        """
        Renders a laboratory safety standard operating procedure and emergency hotline contact card.
        """
        from xml.sax.saxutils import escape

        lab_esc = escape(lab_name.strip())
        pic_esc = escape(pic_technician.strip())
        call_esc = escape(emergency_call.strip())
        rules_html = "".join(f"<li>{escape(r.strip())}</li>" for r in safety_rules if r.strip())

        return f"""    <div class="tu-lab-safety-card">
      <div class="tu-lab-safety-badge">Standar Keselamatan Kerja Lab (K3)</div>
      <h4 class="tu-lab-safety-title">{lab_esc}</h4>
      <div class="tu-lab-safety-pic">Penanggung Jawab Teknis: <strong>{pic_esc}</strong></div>
      <div class="tu-lab-safety-body">
        <strong>Aturan Keselamatan Wajib:</strong>
        <ul class="tu-lab-safety-rules">{rules_html}</ul>
      </div>
      <div class="tu-lab-emergency-hotline">
        <span>Kontak Darurat / APAR Center: <strong>{call_esc}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_mbkm_credit_transfer_card(
        cls,
        program_name: str,
        partner: str,
        student_name: str,
        nim: str,
        courses: List[Dict[str, Any]],
        total_sks: int,
        converted_gpa: float,
        sk_number: str = ""
    ) -> str:
        """
        Renders an MBKM course credit transfer equivalence card showing student identity,
        partner program, mapped curriculum courses, and accredited GPA conversion.
        """
        from xml.sax.saxutils import escape

        prog_esc = escape(program_name.strip())
        partner_esc = escape(partner.strip())
        name_esc = escape(student_name.strip())
        nim_esc = escape(nim.strip())
        sk_esc = escape(sk_number.strip())

        rows_html = "".join(
            f"<tr><td>{escape(str(c.get('course_code', '')))}</td>"
            f"<td>{escape(str(c.get('course_name', '')))}</td>"
            f"<td style='text-align:center;'>{escape(str(c.get('sks', '')))}</td>"
            f"<td style='text-align:center;'><strong>{escape(str(c.get('score_letter', 'A')))}</strong></td></tr>"
            for c in courses
        )

        sk_badge = f"<div class='tu-mbkm-sk'>SK Dekan: <strong>{sk_esc}</strong></div>" if sk_esc else ""

        return f"""    <div class="tu-mbkm-transfer-card">
      <div class="tu-mbkm-header">
        <span class="tu-mbkm-badge">Ekivalensi Nilai MBKM</span>
        <h4 class="tu-mbkm-program">{prog_esc} - {partner_esc}</h4>
        <div class="tu-mbkm-student">{name_esc} (NIM: {nim_esc})</div>
        {sk_badge}
      </div>
      <div class="tu-table-responsive">
        <table class="tu-table tu-mbkm-table">
          <thead>
            <tr><th>Kode</th><th>Mata Kuliah Prodi</th><th>SKS</th><th>Nilai</th></tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
      <div class="tu-mbkm-summary">
        <span>Total Konversi: <strong>{total_sks} SKS</strong></span>
        <span>IPK Ekivalensi: <strong>{converted_gpa:.2f}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_yudisium_clearance_card(
        cls,
        student_name: str,
        nim: str,
        thesis_title: str,
        ipk: float,
        predicate: str,
        yudisium_date: str,
        verification_code: str = ""
    ) -> str:
        """
        Renders an official graduation (Yudisium) clearance and degree conferral credential card.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(student_name.strip())
        nim_esc = escape(nim.strip())
        thesis_esc = escape(thesis_title.strip())
        pred_esc = escape(predicate.strip())
        date_esc = escape(yudisium_date.strip())
        code_esc = escape(verification_code.strip())

        code_badge = f"<span class='tu-yudisium-code'>No. Verifikasi: <strong>{code_esc}</strong></span>" if code_esc else ""

        return f"""    <div class="tu-yudisium-card">
      <div class="tu-yudisium-header">
        <span class="tu-yudisium-badge">Surat Keputusan Yudisium Sarjana</span>
        <h4 class="tu-yudisium-name">{name_esc}</h4>
        <div class="tu-yudisium-nim">NIM: <strong>{nim_esc}</strong></div>
      </div>
      <div class="tu-yudisium-body">
        <div class="tu-yudisium-thesis">
          <span>Judul Tugas Akhir / Skripsi:</span>
          <p>"{thesis_esc}"</p>
        </div>
        <div class="tu-yudisium-meta">
          <span>Indeks Prestasi Kumulatif (IPK): <strong>{ipk:.2f}</strong></span>
          <span>Predikat Kelulusan: <strong class="tu-yudisium-predicate">{pred_esc}</strong></span>
          <span>Tanggal Yudisium: <strong>{date_esc}</strong></span>
        </div>
      </div>
      <div class="tu-yudisium-footer">
        {code_badge}
        <span class="tu-yudisium-status">Status: Lulus Sidang Yudisium S1</span>
      </div>
    </div>"""

    @classmethod
    def render_scopus_paper_showcase_card(
        cls,
        title: str,
        authors: List[str],
        journal_name: str,
        quartile: str,
        sjr_score: float,
        doi: str,
        citation_count: int = 0
    ) -> str:
        """
        Renders a scientific research paper showcase card for Scopus Q1-Q4 indexed publications.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(title.strip())
        journal_esc = escape(journal_name.strip())
        q_esc = escape(quartile.strip().upper())
        doi_esc = escape(doi.strip())
        authors_html = ", ".join(escape(a.strip()) for a in authors if a.strip())

        doi_link = f"<a href='https://doi.org/{doi_esc}' class='tu-scopus-doi' target='_blank' rel='noopener noreferrer'>DOI: {doi_esc}</a>" if doi_esc else ""

        return f"""    <div class="tu-scopus-paper-card">
      <div class="tu-scopus-header">
        <span class="tu-scopus-quartile-badge tu-quartile-{q_esc.lower()}">Scopus {q_esc}</span>
        <span class="tu-scopus-sjr">SJR: <strong>{sjr_score:.2f}</strong></span>
      </div>
      <h4 class="tu-scopus-title">{title_esc}</h4>
      <div class="tu-scopus-authors">Penulis: <strong>{authors_html}</strong></div>
      <div class="tu-scopus-journal">Jurnal: <em>{journal_esc}</em></div>
      <div class="tu-scopus-footer">
        <span class="tu-scopus-citations">Sitasi: <strong>{citation_count}</strong></span>
        {doi_link}
      </div>
    </div>"""

    @classmethod
    def render_lab_equipment_status_card(
        cls,
        asset_id: str,
        equipment_name: str,
        lab_name: str,
        condition: str,
        cal_status: str,
        next_due_date: str,
        pic: str
    ) -> str:
        """
        Renders a laboratory equipment calibration schedule, physical operating condition,
        and asset inventory badge card.
        """
        from xml.sax.saxutils import escape

        id_esc = escape(asset_id.strip())
        name_esc = escape(equipment_name.strip())
        lab_esc = escape(lab_name.strip())
        cond_esc = escape(condition.strip())
        status_esc = escape(cal_status.strip())
        due_esc = escape(next_due_date.strip())
        pic_esc = escape(pic.strip())

        status_class = "tu-cal-valid" if status_esc.lower() == "valid" else "tu-cal-expired"

        return f"""    <div class="tu-lab-equipment-card">
      <div class="tu-lab-equipment-header">
        <span class="tu-equipment-badge">Inventaris Alat Lab</span>
        <span class="tu-cal-status {status_class}">Kalibrasi: {status_esc}</span>
      </div>
      <h4 class="tu-equipment-name">{name_esc}</h4>
      <div class="tu-equipment-meta">
        <span>Kode Aset: <strong>{id_esc}</strong></span>
        <span>Ruang Lab: <strong>{lab_esc}</strong></span>
        <span>Kondisi Fisik: <strong>{cond_esc}</strong></span>
        <span>Jatuh Tempo Kalibrasi: <strong>{due_esc}</strong></span>
        <span>Penanggung Jawab: <strong>{pic_esc}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_visiting_professor_card(
        cls,
        name: str,
        title_role: str,
        home_university: str,
        country: str,
        lecture_topic: str,
        date_time: str,
        registration_url: str = ""
    ) -> str:
        """
        Renders an international visiting professor or guest lecturer public lecture profile card.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(name.strip())
        role_esc = escape(title_role.strip())
        univ_esc = escape(home_university.strip())
        country_esc = escape(country.strip())
        topic_esc = escape(lecture_topic.strip())
        dt_esc = escape(date_time.strip())
        url_esc = escape(registration_url.strip())

        reg_btn = f"<a href='{url_esc}' class='tu-guest-reg-btn' target='_blank' rel='noopener noreferrer'>Registrasi Kuliah Umum</a>" if url_esc else ""

        return f"""    <div class="tu-visiting-prof-card">
      <div class="tu-visiting-prof-header">
        <span class="tu-prof-badge">International Visiting Professor</span>
        <h4 class="tu-prof-name">{name_esc}</h4>
        <div class="tu-prof-role">{role_esc}</div>
        <div class="tu-prof-origin">{univ_esc}, {country_esc}</div>
      </div>
      <div class="tu-visiting-prof-body">
        <div class="tu-prof-topic">
          <span>Topik Kuliah Umum:</span>
          <strong>"{topic_esc}"</strong>
        </div>
        <div class="tu-prof-schedule">Jadwal: <strong>{dt_esc}</strong></div>
      </div>
      <div class="tu-visiting-prof-footer">
        {reg_btn}
      </div>
    </div>"""

    @classmethod
    def render_kkn_village_profile_card(
        cls,
        group_code: str,
        village_name: str,
        district: str,
        regency: str,
        supervisor_dpl: str,
        student_count: int,
        thematic_focus: str,
        flagship_program: str
    ) -> str:
        """
        Renders a student community service (KKN Thematic) partner village profile card.
        """
        from xml.sax.saxutils import escape

        grp_esc = escape(group_code.strip())
        vil_esc = escape(village_name.strip())
        dist_esc = escape(district.strip())
        reg_esc = escape(regency.strip())
        dpl_esc = escape(supervisor_dpl.strip())
        theme_esc = escape(thematic_focus.strip())
        prog_esc = escape(flagship_program.strip())

        return f"""    <div class="tu-kkn-village-card">
      <div class="tu-kkn-header">
        <span class="tu-kkn-badge">KKN Tematik Mahasiswa</span>
        <span class="tu-kkn-group">{grp_esc}</span>
      </div>
      <h4 class="tu-kkn-village">Desa {vil_esc}</h4>
      <div class="tu-kkn-location">Kec. {dist_esc}, Kab. {reg_esc}</div>
      <div class="tu-kkn-body">
        <div class="tu-kkn-theme">Tema: <strong>{theme_esc}</strong></div>
        <div class="tu-kkn-program">Program Unggulan: <em>{prog_esc}</em></div>
      </div>
      <div class="tu-kkn-footer">
        <span>DPL: <strong>{dpl_esc}</strong></span>
        <span>Peserta: <strong>{student_count} Mahasiswa</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_faculty_bkd_compliance_card(
        cls,
        lecturer_name: str,
        nidn: str,
        academic_rank: str,
        semester: str,
        total_sks: float,
        is_compliant: bool,
        breakdown: Dict[str, float]
    ) -> str:
        """
        Renders a faculty semester BKD workload compliance status card.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(lecturer_name.strip())
        nidn_esc = escape(nidn.strip())
        rank_esc = escape(academic_rank.strip())
        sem_esc = escape(semester.strip())

        status_label = "MEMENUHI KETENTUAN" if is_compliant else "BELUM MEMENUHI"
        badge_cls = "tu-bkd-compliant" if is_compliant else "tu-bkd-warning"

        pendidikan = breakdown.get("pendidikan", 0.0)
        penelitian = breakdown.get("penelitian", 0.0)
        pengabdian = breakdown.get("pengabdian", 0.0)
        penunjang = breakdown.get("penunjang", 0.0)

        return f"""    <div class="tu-faculty-bkd-card">
      <div class="tu-bkd-header">
        <span class="tu-bkd-badge">Laporan Beban Kerja Dosen (BKD)</span>
        <span class="tu-bkd-status {badge_cls}">{status_label}</span>
      </div>
      <h4 class="tu-bkd-lecturer">{name_esc}</h4>
      <div class="tu-bkd-meta">
        <span>NIDN: <strong>{nidn_esc}</strong></span>
        <span>Jabatan: <strong>{rank_esc}</strong></span>
        <span>Semester: <strong>{sem_esc}</strong></span>
      </div>
      <div class="tu-bkd-breakdown">
        <div class="tu-bkd-item">Pendidikan: <strong>{pendidikan:.2f} SKS</strong></div>
        <div class="tu-bkd-item">Penelitian: <strong>{penelitian:.2f} SKS</strong></div>
        <div class="tu-bkd-item">Pengabdian: <strong>{pengabdian:.2f} SKS</strong></div>
        <div class="tu-bkd-item">Penunjang: <strong>{penunjang:.2f} SKS</strong></div>
      </div>
      <div class="tu-bkd-footer">
        <span>Total Beban Tridharma: <strong>{total_sks:.2f} SKS</strong> (Rentang Wajib: 12.00 - 16.00 SKS)</span>
      </div>
    </div>"""

    @classmethod
    def render_core_conference_showcase_card(
        cls,
        paper_title: str,
        authors: List[str],
        conference_name: str,
        acronym: str,
        core_tier: str,
        publisher: str,
        year: int,
        presentation_city: str
    ) -> str:
        """
        Renders an international research paper conference presentation card with CORE ranking tier.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(paper_title.strip())
        conf_esc = escape(conference_name.strip())
        acr_esc = escape(acronym.strip().upper())
        tier_esc = escape(core_tier.strip().upper())
        pub_esc = escape(publisher.strip())
        city_esc = escape(presentation_city.strip())
        authors_html = ", ".join(escape(a.strip()) for a in authors if a.strip())

        tier_class = f"tu-core-{tier_esc.lower().replace('*', 'star')}"

        return f"""    <div class="tu-core-conf-card">
      <div class="tu-core-conf-header">
        <span class="tu-core-tier-badge {tier_class}">CORE Rank {tier_esc}</span>
        <span class="tu-core-conf-acronym">{acr_esc} {year}</span>
      </div>
      <h4 class="tu-core-conf-title">{title_esc}</h4>
      <div class="tu-core-conf-authors">Penulis: <strong>{authors_html}</strong></div>
      <div class="tu-core-conf-name">Konferensi: <em>{conf_esc}</em></div>
      <div class="tu-core-conf-footer">
        <span>Kota: <strong>{city_esc}</strong></span>
        <span>Prosiding: <strong>{pub_esc}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_academic_warning_counseling_card(
        cls,
        student_name: str,
        nim: str,
        warning_level: str,
        cumulative_gpa: float,
        earned_credits: int,
        remedial_target_sks: int,
        advisor_name: str,
        counseling_deadline: str
    ) -> str:
        """
        Renders an academic warning counseling and remedial action plan card.
        """
        from xml.sax.saxutils import escape

        name_esc = escape(student_name.strip())
        nim_esc = escape(nim.strip())
        warn_esc = escape(warning_level.strip().upper())
        advisor_esc = escape(advisor_name.strip())
        deadline_esc = escape(counseling_deadline.strip())

        return f"""    <div class="tu-academic-warning-card">
      <div class="tu-warning-header">
        <span class="tu-warning-badge">Peringatan Akademik ({warn_esc})</span>
        <span class="tu-warning-nim">{nim_esc}</span>
      </div>
      <h4 class="tu-warning-student">{name_esc}</h4>
      <div class="tu-warning-stats">
        <span>IPK Kumulatif: <strong>{cumulative_gpa:.2f}</strong></span>
        <span>SKS Diperoleh: <strong>{earned_credits} SKS</strong></span>
        <span>Target Remedial: <strong>{remedial_target_sks} SKS</strong></span>
      </div>
      <div class="tu-warning-footer">
        <span>Dosen Wali: <strong>{advisor_esc}</strong></span>
        <span>Batas Konseling: <strong>{deadline_esc}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_biomedical_telemetry_showcase_card(
        cls,
        innovation_title: str,
        clinical_partner: str,
        telemetry_protocol: str,
        sensor_nodes: List[str],
        impact_summary: str,
        demo_video_url: str = ""
    ) -> str:
        """
        Renders a biomedical telemetry and digital healthcare research innovation showcase card.
        """
        from xml.sax.saxutils import escape

        title_esc = escape(innovation_title.strip())
        partner_esc = escape(clinical_partner.strip())
        proto_esc = escape(telemetry_protocol.strip())
        impact_esc = escape(impact_summary.strip())
        sensors_html = ", ".join(escape(s.strip()) for s in sensor_nodes if s.strip())

        video_btn = f"<a href='{escape(demo_video_url.strip())}' class='tu-biomed-video-link' target='_blank' rel='noopener noreferrer'>Video Demo Uji Klinis</a>" if demo_video_url else ""

        return f"""    <div class="tu-biomedical-telemetry-card">
      <div class="tu-biomed-header">
        <span class="tu-biomed-badge">Telemetri Biomedis &amp; e-Health</span>
        <span class="tu-biomed-protocol">{proto_esc}</span>
      </div>
      <h4 class="tu-biomed-title">{title_esc}</h4>
      <div class="tu-biomed-partner">Mitra Klinis: <strong>{partner_esc}</strong></div>
      <div class="tu-biomed-sensors">Sensor Terintegrasi: <em>{sensors_html}</em></div>
      <p class="tu-biomed-impact">{impact_esc}</p>
      <div class="tu-biomed-footer">
        {video_btn}
      </div>
    </div>"""

    @classmethod
    def render_bima_grant_award_card(
        cls,
        project_title: str,
        lead_researcher: str,
        scheme_name: str,
        funding_amount: float,
        fiscal_year: int,
        key_deliverables: List[str],
        grant_contract_no: str = ""
    ) -> str:
        """
        Renders an Elementor showcase card for Kemdikbud BIMA funded research grant projects.
        """
        from xml.sax.saxutils import escape

        t_esc = escape(project_title.strip())
        lead_esc = escape(lead_researcher.strip())
        scheme_esc = escape(scheme_name.strip())
        contract_esc = escape(grant_contract_no.strip())
        budget_str = f"Rp {funding_amount:,.0f}"

        deliverables_html = "".join(f"<li>{escape(d.strip())}</li>" for d in key_deliverables if d.strip())
        contract_badge = f"<span class='tu-bima-contract'>Kontrak: {contract_esc}</span>" if contract_esc else ""

        return f"""    <div class="tu-bima-grant-card">
      <div class="tu-bima-header">
        <span class="tu-bima-badge">Hibah Riset Kemdikbud BIMA</span>
        <span class="tu-bima-year">Tahun Anggaran {fiscal_year}</span>
      </div>
      <h4 class="tu-bima-title">{t_esc}</h4>
      <div class="tu-bima-meta">
        <p class="tu-bima-lead">Ketua Peneliti: <strong>{lead_esc}</strong></p>
        <p class="tu-bima-scheme">Skema: <em>{scheme_esc}</em></p>
        <p class="tu-bima-funding">Pagu Dana Disetujui: <strong class="tu-bima-amount">{budget_str}</strong></p>
      </div>
      <div class="tu-bima-deliverables">
        <strong>Target Luaran Wajib:</strong>
        <ul>{deliverables_html}</ul>
      </div>
      <div class="tu-bima-footer">
        {contract_badge}
      </div>
    </div>"""

    @classmethod
    def render_kerja_praktik_report_card(
        cls,
        student_name: str,
        nim: str,
        company_name: str,
        industry_sector: str,
        duration_weeks: int,
        project_title: str,
        technical_stack: List[str],
        company_mentor: str = ""
    ) -> str:
        """
        Renders an Elementor report card showcasing student Kerja Praktik (KP) industry placement and technical achievements.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        s_comp = escape(company_name.strip())
        s_sector = escape(industry_sector.strip())
        s_title = escape(project_title.strip())
        s_mentor = escape(company_mentor.strip())

        stack_html = " ".join(f'<span class="tu-kp-tech-pill">{escape(t.strip())}</span>' for t in technical_stack if t.strip())
        mentor_html = f'<p class="tu-kp-mentor">Pembimbing Lapangan: <strong>{s_mentor}</strong></p>' if s_mentor else ""

        return f"""    <div class="tu-kerja-praktik-card">
      <div class="tu-kp-header">
        <span class="tu-kp-badge">Laporan Kerja Praktik (KP)</span>
        <span class="tu-kp-duration">{duration_weeks} Minggu</span>
      </div>
      <h4 class="tu-kp-project-title">{s_title}</h4>
      <div class="tu-kp-company-info">
        <span class="tu-kp-company-name">{s_comp}</span>
        <span class="tu-kp-sector">({s_sector})</span>
      </div>
      <div class="tu-kp-student-meta">
        <p class="tu-kp-student">Praktikan: <strong>{s_name}</strong> (NIM: <code>{s_nim}</code>)</p>
        {mentor_html}
      </div>
      <div class="tu-kp-tech-stack">
        <strong>Teknologi Terapan:</strong>
        <div class="tu-kp-tech-container">{stack_html}</div>
      </div>
    </div>"""

    @classmethod
    def render_lab_spectrum_isr_card(
        cls,
        lab_name: str,
        center_frequency: str,
        bandwidth: str,
        transmit_power: str,
        band_name: str,
        license_number: str,
        valid_until: str,
        is_active: bool = True
    ) -> str:
        """
        Renders an Elementor card showing telecommunications laboratory radio frequency spectrum allocation and SDPPI ISR permit.
        """
        from xml.sax.saxutils import escape

        s_lab = escape(lab_name.strip())
        s_freq = escape(center_frequency.strip())
        s_bw = escape(bandwidth.strip())
        s_pwr = escape(transmit_power.strip())
        s_band = escape(band_name.strip())
        s_lic = escape(license_number.strip())
        s_valid = escape(valid_until.strip())

        status_class = "tu-status-active" if is_active else "tu-status-inactive"
        status_label = "Izin Aktif (SDPPI)" if is_active else "Masa Berlaku Habis"

        return f"""    <div class="tu-lab-spectrum-card">
      <div class="tu-spectrum-header">
        <span class="tu-spectrum-badge">Alokasi Frekuensi Lab &amp; ISR</span>
        <span class="tu-spectrum-status {status_class}">{status_label}</span>
      </div>
      <h4 class="tu-spectrum-lab">{s_lab}</h4>
      <div class="tu-spectrum-specs">
        <div class="tu-spec-item"><strong>Frekuensi Tengah:</strong> {s_freq}</div>
        <div class="tu-spec-item"><strong>Bandwidth Kanal:</strong> {s_bw}</div>
        <div class="tu-spec-item"><strong>Daya Pancar Maks:</strong> {s_pwr}</div>
        <div class="tu-spec-item"><strong>Pita / Band:</strong> <code>{s_band}</code></div>
      </div>
      <div class="tu-spectrum-footer">
        <span class="tu-spectrum-lic">No. ISR: {s_lic}</span>
        <span class="tu-spectrum-validity">Berlaku s.d: {s_valid}</span>
      </div>
    </div>"""

    @classmethod
    def render_faculty_sinta_profile_card(
        cls,
        lecturer_name: str,
        nidn: str,
        academic_rank: str,
        sinta_id: str,
        sinta_score_overall: float,
        sinta_score_3yr: float,
        scopus_h_index: int,
        top_expertise_areas: List[str],
        profile_url: str = ""
    ) -> str:
        """
        Renders an Elementor card highlighting faculty SINTA profile, bibliometric scores, and research expertise.
        """
        from xml.sax.saxutils import escape

        s_name = escape(lecturer_name.strip())
        s_nidn = escape(nidn.strip())
        s_rank = escape(academic_rank.strip())
        s_id = escape(str(sinta_id).strip())
        url_dest = profile_url.strip() if profile_url.strip() else f"https://sinta.kemdikbud.go.id/authors/profile/{s_id}"

        expertise_html = " ".join(f'<span class="tu-sinta-tag">{escape(e.strip())}</span>' for e in top_expertise_areas if e.strip())

        return f"""    <div class="tu-faculty-sinta-card">
      <div class="tu-sinta-card-header">
        <span class="tu-sinta-badge">Profil Riset Dosen SINTA</span>
        <span class="tu-sinta-rank">{s_rank}</span>
      </div>
      <h4 class="tu-sinta-name">{s_name}</h4>
      <p class="tu-sinta-nidn">NIDN: <code>{s_nidn}</code> | SINTA ID: <code>{s_id}</code></p>
      <div class="tu-sinta-metrics">
        <div class="tu-sinta-metric-box">
          <span class="tu-metric-val">{sinta_score_overall:,.0f}</span>
          <span class="tu-metric-lbl">SINTA Overall</span>
        </div>
        <div class="tu-sinta-metric-box">
          <span class="tu-metric-val">{sinta_score_3yr:,.0f}</span>
          <span class="tu-metric-lbl">SINTA 3Yr</span>
        </div>
        <div class="tu-sinta-metric-box">
          <span class="tu-metric-val">{scopus_h_index}</span>
          <span class="tu-metric-lbl">Scopus h-index</span>
        </div>
      </div>
      <div class="tu-sinta-expertise">
        <strong>Bidang Keahlian:</strong>
        <div class="tu-sinta-tags-container">{expertise_html}</div>
      </div>
      <div class="tu-sinta-footer">
        <a href="{escape(url_dest)}" class="tu-sinta-link" target="_blank" rel="noopener noreferrer">Buka Profil SINTA Kemdikbud</a>
      </div>
    </div>"""

    @classmethod
    def render_campus_fiber_backbone_card(
        cls,
        segment_name: str,
        origin_building: str,
        destination_building: str,
        core_count: int,
        fiber_type: str,
        total_attenuation_db: float,
        bandwidth_capacity_gbps: int,
        operating_status: str = "Aktif"
    ) -> str:
        """
        Renders an Elementor card showcasing campus optical fiber transmission network backbone topology and metrics.
        """
        from xml.sax.saxutils import escape

        s_seg = escape(segment_name.strip())
        s_orig = escape(origin_building.strip())
        s_dest = escape(destination_building.strip())
        s_type = escape(fiber_type.strip())
        s_stat = escape(operating_status.strip())

        return f"""    <div class="tu-fiber-backbone-card">
      <div class="tu-fiber-header">
        <span class="tu-fiber-badge">Transmisi Fiber Optik Kampus</span>
        <span class="tu-fiber-status">{s_stat}</span>
      </div>
      <h4 class="tu-fiber-segment">{s_seg}</h4>
      <div class="tu-fiber-route">
        <span class="tu-route-node">{s_orig}</span>
        <span class="tu-route-arrow">&rarr;</span>
        <span class="tu-route-node">{s_dest}</span>
      </div>
      <div class="tu-fiber-metrics-grid">
        <div class="tu-fiber-metric">
          <span class="tu-val">{core_count} Core</span>
          <span class="tu-lbl">Kapasitas Core</span>
        </div>
        <div class="tu-fiber-metric">
          <span class="tu-val">{s_type}</span>
          <span class="tu-lbl">Tipe Serat</span>
        </div>
        <div class="tu-fiber-metric">
          <span class="tu-val">{total_attenuation_db:.2f} dB</span>
          <span class="tu-lbl">Redaman Total</span>
        </div>
        <div class="tu-fiber-metric">
          <span class="tu-val">{bandwidth_capacity_gbps} Gbps</span>
          <span class="tu-lbl">Throughput</span>
        </div>
      </div>
    </div>"""

    @staticmethod
    def render_accreditation_status_card(
        program_name: str,
        agency: str,
        rating: str,
        sk_number: str,
        expiry_date: str,
        is_active: bool = True
    ) -> str:
        """
        Renders a responsive study program accreditation status showcase card
        displaying LAM INFOKOM / BAN-PT decree credentials and validity period.
        """
        from xml.sax.saxutils import escape

        s_prog = escape(program_name.strip())
        s_agency = escape(agency.strip())
        s_rating = escape(rating.strip())
        s_sk = escape(sk_number.strip())
        s_expiry = escape(expiry_date.strip())

        status_class = "tu-status-active" if is_active else "tu-status-expired"
        status_text = "Status Aktif Terakreditasi" if is_active else "Masa Berlaku Berakhir"

        return f"""    <div class="tu-accreditation-card">
      <div class="tu-accreditation-header">
        <span class="tu-accreditation-agency">{s_agency}</span>
        <span class="tu-accreditation-status {status_class}">{status_text}</span>
      </div>
      <h4 class="tu-accreditation-program">{s_prog}</h4>
      <div class="tu-accreditation-badge">
        <span class="tu-rating-lbl">Peringkat Akreditasi:</span>
        <strong class="tu-rating-val">{s_rating}</strong>
      </div>
      <div class="tu-accreditation-meta">
        <div class="tu-meta-item">
          <span class="tu-meta-lbl">Nomor SK:</span>
          <span class="tu-meta-val">{s_sk}</span>
        </div>
        <div class="tu-meta-item">
          <span class="tu-meta-lbl">Masa Berlaku Hingga:</span>
          <span class="tu-meta-val">{s_expiry}</span>
        </div>
      </div>
    </div>"""

    @staticmethod
    def render_scholarship_award_card(
        student_name: str,
        nim: str,
        scholarship_type: str,
        sponsor_name: str,
        amount_idr: float,
        semester: str,
        minimum_gpa: float = 3.0
    ) -> str:
        """
        Renders a student scholarship aid award showcase card
        with localized IDR currency formatting and eligibility indicators.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        s_type = escape(scholarship_type.strip())
        s_sponsor = escape(sponsor_name.strip())
        s_sem = escape(semester.strip())
        amount_fmt = f"Rp {amount_idr:,.0f}".replace(",", ".")

        return f"""    <div class="tu-scholarship-card">
      <div class="tu-scholarship-header">
        <span class="tu-scholarship-sponsor">{s_sponsor}</span>
        <span class="tu-scholarship-type">{s_type}</span>
      </div>
      <h4 class="tu-scholarship-recipient">{s_name} ({s_nim})</h4>
      <div class="tu-scholarship-amount-box">
        <span class="tu-amount-lbl">Bantuan UKT / Biaya Hidup:</span>
        <strong class="tu-amount-val">{amount_fmt}</strong>
      </div>
      <div class="tu-scholarship-meta">
        <div class="tu-meta-item">
          <span class="tu-meta-lbl">Periode:</span>
          <span class="tu-meta-val">{s_sem}</span>
        </div>
        <div class="tu-meta-item">
          <span class="tu-meta-lbl">Standar IPK:</span>
          <span class="tu-meta-val">&ge; {minimum_gpa:.2f}</span>
        </div>
      </div>
    </div>"""

    @staticmethod
    def render_optical_link_budget_card(
        fiber_length_km: float,
        total_attenuation_db: float,
        allowed_loss_db: float,
        power_margin_db: float,
        is_viable: bool
    ) -> str:
        """
        Renders a telecommunication optical fiber transmission link budget calculation card
        with attenuation metrics, power margin indicators, and viability status badges.
        """
        viable_class = "tu-viable-pass" if is_viable else "tu-viable-fail"
        viable_text = "Memenuhi Standar Margin Daya" if is_viable else "Margin Daya Tidak Cukup"

        return f"""    <div class="tu-optical-budget-card">
      <div class="tu-budget-header">
        <span class="tu-budget-title">Kalkulasi Link Budget Transmisi Optik</span>
        <span class="tu-budget-status {viable_class}">{viable_text}</span>
      </div>
      <div class="tu-budget-metrics-grid">
        <div class="tu-budget-metric">
          <span class="tu-metric-val">{fiber_length_km:.2f} km</span>
          <span class="tu-metric-lbl">Panjang Serat</span>
        </div>
        <div class="tu-budget-metric">
          <span class="tu-metric-val">{total_attenuation_db:.2f} dB</span>
          <span class="tu-metric-lbl">Redaman Total</span>
        </div>
        <div class="tu-budget-metric">
          <span class="tu-metric-val">{allowed_loss_db:.2f} dB</span>
          <span class="tu-metric-lbl">Redaman Maksimum</span>
        </div>
        <div class="tu-budget-metric">
          <span class="tu-metric-val">{power_margin_db:+.2f} dB</span>
          <span class="tu-metric-lbl">Margin Daya</span>
        </div>
      </div>
    </div>"""

    @staticmethod
    def render_djki_patent_certificate_card(
        patent_title: str,
        patent_number: Optional[str],
        application_number: str,
        filing_date: str,
        grant_date: Optional[str],
        inventors: List[str],
        patent_type: str = "Paten Sederhana",
        status: str = "Granted"
    ) -> str:
        """
        Renders a Directorate General of Intellectual Property (DJKI) patent grant showcase card
        displaying invention title, patent registration number, inventor team, and legal grant status.
        """
        from xml.sax.saxutils import escape

        s_title = escape(patent_title.strip())
        s_pat_num = escape(patent_number.strip()) if patent_number else "Dalam Proses Registrasi"
        s_app_num = escape(application_number.strip())
        s_filing = escape(filing_date.strip())
        s_grant = escape(grant_date.strip()) if grant_date else "Menunggu SK Menteri"
        s_type = escape(patent_type.strip())
        s_status = escape(status.strip())

        inv_items = "".join(f'<span class="tu-patent-inventor">{escape(i.strip())}</span>' for i in inventors)

        return f"""    <div class="tu-patent-grant-card">
      <div class="tu-patent-header">
        <span class="tu-patent-type-badge">{s_type}</span>
        <span class="tu-patent-status-badge">{s_status}</span>
      </div>
      <h4 class="tu-patent-title">{s_title}</h4>
      <div class="tu-patent-numbers">
        <div class="tu-pat-num-item">
          <span class="tu-lbl">Nomor Paten:</span>
          <strong class="tu-val">{s_pat_num}</strong>
        </div>
        <div class="tu-pat-num-item">
          <span class="tu-lbl">Nomor Permohonan:</span>
          <span class="tu-val">{s_app_num}</span>
        </div>
      </div>
      <div class="tu-patent-inventors-box">
        <span class="tu-inv-lbl">Tim Inventor:</span>
        <div class="tu-inv-list">
          {inv_items}
        </div>
      </div>
      <div class="tu-patent-dates">
        <span class="tu-date-item">Penerimaan: {s_filing}</span>
        <span class="tu-date-item">Pemberian: {s_grant}</span>
      </div>
    </div>"""

    @staticmethod
    def render_bnsp_certification_card(
        student_name: str,
        nim: str,
        scheme_name: str,
        assessor_name: str,
        cert_number: str,
        issue_date: str,
        valid_until: str,
        is_competent: bool = True
    ) -> str:
        """
        Renders a National Professional Certification Board (BNSP) student competency showcase card
        with occupational scheme details, assessor verification, and competency badge.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        s_scheme = escape(scheme_name.strip())
        s_assessor = escape(assessor_name.strip())
        s_cert = escape(cert_number.strip())
        s_issue = escape(issue_date.strip())
        s_valid = escape(valid_until.strip())

        comp_class = "tu-competent-pass" if is_competent else "tu-competent-pending"
        comp_text = "Kompeten (K)" if is_competent else "Belum Kompeten (BK)"

        return f"""    <div class="tu-bnsp-cert-card">
      <div class="tu-bnsp-header">
        <span class="tu-bnsp-badge">LSP Telekomunikasi / BNSP</span>
        <span class="tu-bnsp-status {comp_class}">{comp_text}</span>
      </div>
      <h4 class="tu-bnsp-scheme">{s_scheme}</h4>
      <div class="tu-bnsp-student">
        <span class="tu-bnsp-name">{s_name}</span>
        <span class="tu-bnsp-nim">NIM: {s_nim}</span>
      </div>
      <div class="tu-bnsp-meta">
        <div class="tu-bnsp-meta-item">
          <span class="tu-lbl">Nomor Sertifikat:</span>
          <strong class="tu-val">{s_cert}</strong>
        </div>
        <div class="tu-bnsp-meta-item">
          <span class="tu-lbl">Asesor Penguji:</span>
          <span class="tu-val">{s_assessor}</span>
        </div>
        <div class="tu-bnsp-meta-item">
          <span class="tu-lbl">Masa Berlaku:</span>
          <span class="tu-val">{s_issue} s.d. {s_valid}</span>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_cum_laude_honor_card(
        cls,
        student_name: str,
        nim: str,
        ipk: float,
        honor_predicate: str,
        thesis_title: str,
        study_duration_semesters: int = 8
    ) -> str:
        """
        Renders a student graduation judiciary Cum Laude / Summa Cum Laude honor showcase card.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        s_pred = escape(honor_predicate.strip())
        s_thesis = escape(thesis_title.strip())
        ipk_val = f"{float(ipk):.2f}"
        duration = int(study_duration_semesters)

        badge_class = "tu-honor-gold" if "summa" in s_pred.lower() else "tu-honor-silver"

        return f"""    <div class="tu-cum-laude-card">
      <div class="tu-cum-laude-header">
        <span class="tu-cum-laude-badge {badge_class}">{s_pred}</span>
        <span class="tu-cum-laude-duration">{duration} Semester</span>
      </div>
      <h3 class="tu-cum-laude-student">{s_name}</h3>
      <div class="tu-cum-laude-meta">
        <span class="tu-cum-laude-nim">NIM: <strong>{s_nim}</strong></span>
        <span class="tu-cum-laude-gpa">IPK: <strong>{ipk_val}</strong></span>
      </div>
      <div class="tu-cum-laude-thesis">
        <span class="tu-lbl">Tugas Akhir:</span>
        <p class="tu-cum-laude-thesis-title">&ldquo;{s_thesis}&rdquo;</p>
      </div>
    </div>"""

    @classmethod
    def render_friis_path_loss_card(
        cls,
        frequency_mhz: float,
        distance_km: float,
        path_loss_db: float,
        tx_power_dbm: float,
        rx_power_dbm: float
    ) -> str:
        """
        Renders a cellular base station Friis path loss and RF attenuation calculation card.
        """
        from xml.sax.saxutils import escape

        f_val = f"{float(frequency_mhz):.1f} MHz"
        d_val = f"{float(distance_km):.2f} km"
        loss_val = f"{float(path_loss_db):.2f} dB"
        tx_val = f"{float(tx_power_dbm):.1f} dBm"
        rx_val = f"{float(rx_power_dbm):.1f} dBm"

        return f"""    <div class="tu-friis-calc-card">
      <div class="tu-friis-header">
        <span class="tu-friis-badge">Transmisi Propagasi RF</span>
        <h4 class="tu-friis-title">Kalkulasi Friis Free Space Path Loss (FSPL)</h4>
      </div>
      <div class="tu-friis-grid">
        <div class="tu-friis-item">
          <span class="tu-lbl">Frekuensi Kerja:</span>
          <strong class="tu-val">{f_val}</strong>
        </div>
        <div class="tu-friis-item">
          <span class="tu-lbl">Jarak Transmisi (d):</span>
          <strong class="tu-val">{d_val}</strong>
        </div>
        <div class="tu-friis-item">
          <span class="tu-lbl">Daya Pancar Tx:</span>
          <span class="tu-val">{tx_val}</span>
        </div>
        <div class="tu-friis-item">
          <span class="tu-lbl">Level Daya Rx:</span>
          <span class="tu-val">{rx_val}</span>
        </div>
      </div>
      <div class="tu-friis-total">
        <span class="tu-friis-total-lbl">Total Redaman Path Loss:</span>
        <span class="tu-friis-total-val">{loss_val}</span>
      </div>
    </div>"""

    @classmethod
    def render_kkn_thematic_showcase_card(
        cls,
        village_name: str,
        regency: str,
        flagship_program: str,
        supervisor: str,
        student_count: int,
        impact_summary: str
    ) -> str:
        """
        Renders a student thematic community service (KKN Tematik) regional showcase card.
        """
        from xml.sax.saxutils import escape

        s_vil = escape(village_name.strip())
        s_reg = escape(regency.strip())
        s_prog = escape(flagship_program.strip())
        s_dpl = escape(supervisor.strip())
        s_imp = escape(impact_summary.strip())
        count = max(1, int(student_count))

        return f"""    <div class="tu-kkn-showcase-card">
      <div class="tu-kkn-header">
        <span class="tu-kkn-badge">KKN Tematik Perdesaan</span>
        <span class="tu-kkn-region">{s_vil}, {s_reg}</span>
      </div>
      <h4 class="tu-kkn-flagship">{s_prog}</h4>
      <div class="tu-kkn-meta">
        <span>Dosen Pembimbing (DPL): <strong>{s_dpl}</strong></span>
        <span>Peserta: <strong>{count} Mahasiswa</strong></span>
      </div>
      <p class="tu-kkn-impact">{s_imp}</p>
    </div>"""

    @classmethod
    def render_tridharma_grant_award_card(
        cls,
        lecturer_name: str,
        nidn: str,
        project_title: str,
        grant_amount: float,
        fiscal_year: int,
        publication_target: str
    ) -> str:
        """
        Renders a lecturer internal Tridharma research grant funding award card.
        """
        from xml.sax.saxutils import escape

        s_name = escape(lecturer_name.strip())
        s_nidn = escape(nidn.strip())
        s_title = escape(project_title.strip())
        s_pub = escape(publication_target.strip())
        amount_str = f"Rp {float(grant_amount):,.0f}".replace(",", ".")
        year = int(fiscal_year)

        return f"""    <div class="tu-tridharma-grant-card">
      <div class="tu-tridharma-header">
        <span class="tu-tridharma-badge">Hibah Riset Internal LPPM</span>
        <span class="tu-tridharma-year">T.A. {year}</span>
      </div>
      <h4 class="tu-tridharma-title">{s_title}</h4>
      <div class="tu-tridharma-lead">
        <span>Ketua Peneliti: <strong>{s_name}</strong></span>
        <span>NIDN: <code>{s_nidn}</code></span>
      </div>
      <div class="tu-tridharma-meta">
        <div class="tu-tridharma-meta-item">
          <span class="tu-lbl">Pagu Dana Riset:</span>
          <strong class="tu-val">{amount_str}</strong>
        </div>
        <div class="tu-tridharma-meta-item">
          <span class="tu-lbl">Target Luaran:</span>
          <span class="tu-val">{s_pub}</span>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_iot_sensor_telemetry_gauge_card(
        cls,
        sensor_node_id: str,
        sensor_type: str,
        current_value: float,
        unit: str,
        min_val: float,
        max_val: float,
        status: str = "normal"
    ) -> str:
        """
        Renders a laboratory IoT sensor telemetry gauge card with semantic meter and output tags.
        """
        from xml.sax.saxutils import escape

        s_node = escape(sensor_node_id.strip())
        s_type = escape(sensor_type.strip())
        s_unit = escape(unit.strip())
        s_status = escape(status.strip().lower())
        c_val = float(current_value)
        m_min = float(min_val)
        m_max = float(max_val)

        return f"""    <div class="tu-iot-sensor-card status-{s_status}">
      <div class="tu-sensor-header">
        <span class="tu-sensor-node">Node: <code>{s_node}</code></span>
        <span class="tu-sensor-status-badge">{s_status.upper()}</span>
      </div>
      <h4 class="tu-sensor-type">{s_type} Telemetry</h4>
      <div class="tu-sensor-reading">
        <span class="tu-sensor-val">{c_val:.2f}</span>
        <span class="tu-sensor-unit">{s_unit}</span>
      </div>
      <div class="tu-sensor-gauge-wrapper">
        <meter class="tu-sensor-meter" min="{m_min:.2f}" max="{m_max:.2f}" value="{c_val:.2f}"></meter>
        <div class="tu-gauge-range">
          <span>Min: {m_min:.1f} {s_unit}</span>
          <span>Max: {m_max:.1f} {s_unit}</span>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_fast_track_program_card(
        cls,
        student_name: str,
        nim: str,
        ipk: float,
        completed_sks: int,
        toefl_score: int,
        masters_specialization: str
    ) -> str:
        """
        Renders an accelerated Fast-Track Master's program (S1 + S2) student recognition card.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        s_spec = escape(masters_specialization.strip())
        c_ipk = f"{float(ipk):.2f}"
        sks = int(completed_sks)
        toefl = int(toefl_score)

        return f"""    <div class="tu-fast-track-card">
      <div class="tu-fast-track-header">
        <span class="tu-fast-track-badge">Program Akselerasi S1 + S2 (Fast-Track)</span>
        <span class="tu-fast-track-sks">{sks} SKS Lulus</span>
      </div>
      <h3 class="tu-fast-track-student">{s_name}</h3>
      <div class="tu-fast-track-meta">
        <span>NIM: <strong>{s_nim}</strong></span>
        <span>IPK: <strong>{c_ipk}</strong></span>
        <span>TOEFL: <strong>{toefl}</strong></span>
      </div>
      <div class="tu-fast-track-specialization">
        <span class="tu-lbl">Peminatan Magister:</span>
        <strong class="tu-val">{s_spec}</strong>
      </div>
    </div>"""

    @classmethod
    def render_optical_osnr_ber_card(
        cls,
        signal_power_dbm: float,
        noise_power_dbm: float,
        bitrate_gbps: float,
        osnr_db: float,
        q_factor: float,
        estimated_ber: float,
        quality_status: str = "Good"
    ) -> str:
        """
        Renders an optical fiber link Optical Signal-to-Noise Ratio (OSNR) and Bit Error Rate (BER) evaluation card.
        """
        from xml.sax.saxutils import escape

        status_clean = escape(quality_status.strip())
        sig_str = f"{float(signal_power_dbm):.1f} dBm"
        noise_str = f"{float(noise_power_dbm):.1f} dBm"
        rate_str = f"{float(bitrate_gbps):.1f} Gbps"
        osnr_str = f"{float(osnr_db):.2f} dB"
        q_str = f"{float(q_factor):.2f}"
        ber_str = f"{float(estimated_ber):.2e}"

        status_class = "tu-status-good" if quality_status.lower() in ("excellent", "good") else "tu-status-warning"

        return f"""    <div class="tu-optical-calc-card">
      <div class="tu-optical-header">
        <span class="tu-optical-badge">Transmisi Serat Optik DWDM</span>
        <span class="tu-optical-status {status_class}">{status_clean}</span>
      </div>
      <h4 class="tu-optical-title">Kalkulasi OSNR &amp; Bit Error Rate (BER)</h4>
      <div class="tu-optical-grid">
        <div class="tu-optical-item">
          <span class="tu-lbl">Daya Sinyal:</span>
          <strong class="tu-val">{sig_str}</strong>
        </div>
        <div class="tu-optical-item">
          <span class="tu-lbl">Tingkat Derau:</span>
          <strong class="tu-val">{noise_str}</strong>
        </div>
        <div class="tu-optical-item">
          <span class="tu-lbl">Laju Data:</span>
          <span class="tu-val">{rate_str}</span>
        </div>
        <div class="tu-optical-item">
          <span class="tu-lbl">Q-Factor:</span>
          <span class="tu-val">{q_str}</span>
        </div>
      </div>
      <div class="tu-optical-results">
        <div class="tu-res-block">
          <span class="tu-lbl">Optical SNR:</span>
          <span class="tu-osnr-val">{osnr_str}</span>
        </div>
        <div class="tu-res-block">
          <span class="tu-lbl">Estimasi BER:</span>
          <code class="tu-ber-val">{ber_str}</code>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_lab_equipment_calibration_card(
        cls,
        equipment_name: str,
        serial_number: str,
        lab_room: str,
        last_calibration: str,
        next_due: str,
        status: str,
        cert_number: str
    ) -> str:
        """
        Renders an RF & Telecommunications laboratory equipment calibration certificate compliance card.
        """
        from xml.sax.saxutils import escape

        eq_clean = escape(equipment_name.strip())
        sn_clean = escape(serial_number.strip())
        room_clean = escape(lab_room.strip())
        last_clean = escape(last_calibration.strip())
        due_clean = escape(next_due.strip())
        status_clean = escape(status.strip())
        cert_clean = escape(cert_number.strip())

        status_class = "tu-status-valid" if status.lower() in ("valid", "terkalibrasi", "calibrated", "ok") else "tu-status-expired"

        return f"""    <div class="tu-calib-cert-card">
      <div class="tu-calib-header">
        <span class="tu-calib-badge">Sertifikasi Kalibrasi Alat Lab</span>
        <span class="tu-calib-status {status_class}">{status_clean}</span>
      </div>
      <h4 class="tu-calib-title">{eq_clean}</h4>
      <div class="tu-calib-grid">
        <div class="tu-calib-item">
          <span class="tu-lbl">Nomor Seri:</span>
          <code class="tu-sn">{sn_clean}</code>
        </div>
        <div class="tu-calib-item">
          <span class="tu-lbl">Laboratorium:</span>
          <span class="tu-val">{room_clean}</span>
        </div>
        <div class="tu-calib-item">
          <span class="tu-lbl">No. Sertifikat:</span>
          <span class="tu-val">{cert_clean}</span>
        </div>
        <div class="tu-calib-item">
          <span class="tu-lbl">Terakhir Dikalibrasi:</span>
          <span class="tu-val">{last_clean}</span>
        </div>
        <div class="tu-calib-item">
          <span class="tu-lbl">Jatuh Tempo Kalibrasi:</span>
          <strong class="tu-due">{due_clean}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_hki_copyright_certificate_card(
        cls,
        work_title: str,
        creators: List[str],
        creation_type: str,
        registration_number: str,
        registration_date: str
    ) -> str:
        """
        Renders a Ministry of Law and Human Rights (DJKI Kemenkumham) Intellectual Property / HKI copyright showcase card.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(work_title.strip())
        type_clean = escape(creation_type.strip())
        reg_clean = escape(registration_number.strip())
        date_clean = escape(registration_date.strip())
        creators_list = "".join(f"<li>{escape(c.strip())}</li>" for c in creators if c.strip())

        return f"""    <div class="tu-hki-cert-card">
      <div class="tu-hki-header">
        <span class="tu-hki-badge">Hak Cipta Terdaftar (DJKI)</span>
        <span class="tu-hki-type">{type_clean}</span>
      </div>
      <h4 class="tu-hki-title">{title_clean}</h4>
      <div class="tu-hki-body">
        <div class="tu-hki-meta">
          <span class="tu-lbl">Nomor Permohonan / Pencatatan:</span>
          <code class="tu-hki-reg">{reg_clean}</code>
        </div>
        <div class="tu-hki-meta">
          <span class="tu-lbl">Tanggal Pencatatan:</span>
          <span class="tu-val">{date_clean}</span>
        </div>
        <div class="tu-hki-creators-section">
          <span class="tu-lbl">Pencipta / Penemu:</span>
          <ul class="tu-hki-creators-list">
            {creators_list}
          </ul>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_accessible_disclosure_card(
        cls,
        title: str,
        summary_heading: str,
        details_html: str,
        category_badge: str = "Informasi Akademik"
    ) -> str:
        """
        Renders a WCAG 2.1 accessible HTML5 details/summary interactive disclosure card.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(title.strip())
        summary_clean = escape(summary_heading.strip())
        badge_clean = escape(category_badge.strip())

        return f"""    <div class="tu-disclosure-card">
      <div class="tu-disclosure-header">
        <span class="tu-disclosure-badge">{badge_clean}</span>
        <h4 class="tu-disclosure-title">{title_clean}</h4>
      </div>
      <details class="tu-disclosure-element">
        <summary class="tu-disclosure-summary">
          <span class="tu-summary-text">{summary_clean}</span>
          <span class="tu-summary-chevron" aria-hidden="true">&#9662;</span>
        </summary>
        <div class="tu-disclosure-content">
          {details_html}
        </div>
      </details>
    </div>"""

    @classmethod
    def render_fso_link_budget_card(
        cls,
        link_name: str,
        distance_km: float,
        tx_power_dbm: float,
        rx_power_dbm: float,
        link_margin_db: float,
        link_status: str = "Robust"
    ) -> str:
        """
        Renders a Free Space Optical (FSO) laser telecommunications link budget and fade margin card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(link_name.strip())
        status_clean = escape(link_status.strip())
        dist_str = f"{float(distance_km):.2f} km"
        tx_str = f"{float(tx_power_dbm):.1f} dBm"
        rx_str = f"{float(rx_power_dbm):.2f} dBm"
        margin_str = f"{float(link_margin_db):.2f} dB"

        status_class = "tu-status-good" if link_status.lower() in ("robust", "adequate") else "tu-status-warning"

        return f"""    <div class="tu-fso-budget-card">
      <div class="tu-fso-header">
        <span class="tu-fso-badge">Komunikasi Optik Ruang Bebas (FSO)</span>
        <span class="tu-fso-status {status_class}">{status_clean}</span>
      </div>
      <h4 class="tu-fso-title">{name_clean}</h4>
      <div class="tu-fso-grid">
        <div class="tu-fso-item">
          <span class="tu-lbl">Jarak Tautan:</span>
          <strong class="tu-val">{dist_str}</strong>
        </div>
        <div class="tu-fso-item">
          <span class="tu-lbl">Daya Pancar Tx:</span>
          <span class="tu-val">{tx_str}</span>
        </div>
        <div class="tu-fso-item">
          <span class="tu-lbl">Daya Terima Rx:</span>
          <span class="tu-val">{rx_str}</span>
        </div>
        <div class="tu-fso-item">
          <span class="tu-lbl">Fade Margin:</span>
          <strong class="tu-margin">{margin_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_msib_internship_card(
        cls,
        student_name: str,
        nim: str,
        industry_partner: str,
        internship_role: str,
        converted_sks: int,
        final_grade: str
    ) -> str:
        """
        Renders a certified Kampus Merdeka MSIB industrial internship credit conversion card.
        """
        from xml.sax.saxutils import escape

        s_name = escape(student_name.strip())
        s_nim = escape(nim.strip())
        partner_clean = escape(industry_partner.strip())
        role_clean = escape(internship_role.strip())
        grade_clean = escape(final_grade.strip())
        sks = int(converted_sks)

        return f"""    <div class="tu-msib-card">
      <div class="tu-msib-header">
        <span class="tu-msib-badge">Magang Bersertifikat Kampus Merdeka (MSIB)</span>
        <span class="tu-msib-sks">{sks} SKS Terkonversi</span>
      </div>
      <h3 class="tu-msib-student">{s_name}</h3>
      <div class="tu-msib-meta">
        <span>NIM: <strong>{s_nim}</strong></span>
        <span>Nilai Akhir: <strong class="tu-grade">{grade_clean}</strong></span>
      </div>
      <div class="tu-msib-body">
        <div class="tu-msib-row">
          <span class="tu-lbl">Mitra Industri:</span>
          <strong class="tu-val">{partner_clean}</strong>
        </div>
        <div class="tu-msib-row">
          <span class="tu-lbl">Posisi Magang:</span>
          <span class="tu-val">{role_clean}</span>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_antenna_polarization_card(
        cls,
        tx_pol: str,
        rx_pol: str,
        plf_db: float,
        efficiency_percent: float,
        status: str = "Optimal"
    ) -> str:
        """
        Renders an RF antenna Polarization Loss Factor (PLF) and efficiency evaluation card.
        """
        from xml.sax.saxutils import escape

        tx_clean = escape(tx_pol.strip())
        rx_clean = escape(rx_pol.strip())
        status_clean = escape(status.strip())
        loss_str = f"{float(plf_db):.2f} dB"
        eff_str = f"{float(efficiency_percent):.1f}%"

        status_class = "tu-status-good" if status.lower() in ("optimal", "acceptable") else "tu-status-warning"

        return f"""    <div class="tu-polarization-card">
      <div class="tu-pol-header">
        <span class="tu-pol-badge">Kesesuaian Polarisasi Antena RF</span>
        <span class="tu-pol-status {status_class}">{status_clean}</span>
      </div>
      <h4 class="tu-pol-title">Polarization Loss Factor (PLF)</h4>
      <div class="tu-pol-grid">
        <div class="tu-pol-item">
          <span class="tu-lbl">Polarisasi Tx:</span>
          <strong class="tu-val">{tx_clean}</strong>
        </div>
        <div class="tu-pol-item">
          <span class="tu-lbl">Polarisasi Rx:</span>
          <strong class="tu-val">{rx_clean}</strong>
        </div>
        <div class="tu-pol-item">
          <span class="tu-lbl">Rugi Polarisasi:</span>
          <span class="tu-val">{loss_str}</span>
        </div>
        <div class="tu-pol-item">
          <span class="tu-lbl">Efisiensi Transfer Daya:</span>
          <strong class="tu-eff">{eff_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_pkm_grant_project_card(
        cls,
        project_title: str,
        team_leader: str,
        nidn: str,
        partner_name: str,
        location: str,
        budget_amount: float,
        fiscal_year: int
    ) -> str:
        """
        Renders a lecturer Tridharma Community Service (PKM) internal grant award project card.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(project_title.strip())
        leader_clean = escape(team_leader.strip())
        nidn_clean = escape(nidn.strip())
        partner_clean = escape(partner_name.strip())
        loc_clean = escape(location.strip())
        budget_str = f"Rp {float(budget_amount):,.0f}".replace(",", ".")
        year_str = str(int(fiscal_year))

        return f"""    <div class="tu-pkm-grant-card">
      <div class="tu-pkm-header">
        <span class="tu-pkm-badge">Hibah Pengabdian Masyarakat (PKM)</span>
        <span class="tu-pkm-year">T.A. {year_str}</span>
      </div>
      <h4 class="tu-pkm-title">{title_clean}</h4>
      <div class="tu-pkm-body">
        <div class="tu-pkm-leader">
          <span class="tu-lbl">Ketua Pengabdi:</span>
          <strong>{leader_clean}</strong> (NIDN: <code>{nidn_clean}</code>)
        </div>
        <div class="tu-pkm-partner">
          <span class="tu-lbl">Mitra Sasaran:</span>
          <span>{partner_clean} ({loc_clean})</span>
        </div>
        <div class="tu-pkm-budget">
          <span class="tu-lbl">Dana Disetujui LPPM:</span>
          <strong class="tu-amount">{budget_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_canvas_waveform_container_card(
        cls,
        title: str,
        canvas_id: str,
        width: int = 600,
        height: int = 300,
        signal_type: str = "OFDM Subcarrier Spectrum",
        caption: str = "Tampilan Gelombang Domain Waktu"
    ) -> str:
        """
        Renders a responsive oscilloscope / signal spectrum waveform HTML5 canvas container component.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(title.strip())
        c_id = escape(canvas_id.strip())
        sig_clean = escape(signal_type.strip())
        cap_clean = escape(caption.strip())
        w = max(100, int(width))
        h = max(50, int(height))

        return f"""    <div class="tu-canvas-waveform-card">
      <div class="tu-waveform-header">
        <span class="tu-waveform-badge">Visualisasi Sinyal &amp; Spektrum</span>
        <span class="tu-waveform-type">{sig_clean}</span>
      </div>
      <h4 class="tu-waveform-title">{title_clean}</h4>
      <div class="tu-canvas-wrap">
        <canvas id="{c_id}" width="{w}" height="{h}" class="tu-waveform-canvas">
          <p class="tu-canvas-fallback">Browser Anda tidak mendukung rendering visualisasi HTML5 canvas.</p>
        </canvas>
      </div>
      <p class="tu-waveform-caption">{cap_clean}</p>
    </div>"""

    @classmethod
    def render_satellite_link_budget_card(
        cls,
        satellite_name: str,
        downlink_freq_ghz: float,
        tx_eirp_dbw: float,
        rx_g_over_t_db_k: float,
        cnr_db: float,
        link_margin_db: float,
        is_viable: bool
    ) -> str:
        """
        Renders a satellite telecommunication downlink budget calculation card.
        """
        from xml.sax.saxutils import escape

        sat_clean = escape(satellite_name.strip())
        freq_str = f"{float(downlink_freq_ghz):.2f} GHz"
        eirp_str = f"{float(tx_eirp_dbw):.1f} dBW"
        g_t_str = f"{float(rx_g_over_t_db_k):.1f} dB/K"
        cnr_str = f"{float(cnr_db):.2f} dB"
        margin_str = f"{float(link_margin_db):+.2f} dB"
        status_cls = "tu-sat-viable" if is_viable else "tu-sat-unviable"
        status_lbl = "Link Feasible / Optimal" if is_viable else "Link Margin Deficient"

        return f"""    <div class="tu-satellite-budget-card">
      <div class="tu-sat-header">
        <span class="tu-sat-badge">Komunikasi Satelit &amp; Stasiun Bumi</span>
        <span class="tu-sat-status {status_cls}">{status_lbl}</span>
      </div>
      <h4 class="tu-sat-title">Link Budget Downlink: {sat_clean}</h4>
      <div class="tu-sat-grid">
        <div class="tu-sat-param">
          <span class="tu-lbl">Frekuensi Downlink:</span>
          <strong>{freq_str}</strong>
        </div>
        <div class="tu-sat-param">
          <span class="tu-lbl">Satelit EIRP:</span>
          <strong>{eirp_str}</strong>
        </div>
        <div class="tu-sat-param">
          <span class="tu-lbl">Antena G/T:</span>
          <strong>{g_t_str}</strong>
        </div>
        <div class="tu-sat-param">
          <span class="tu-lbl">Carrier-to-Noise (C/N):</span>
          <strong class="tu-cnr">{cnr_str}</strong>
        </div>
        <div class="tu-sat-param">
          <span class="tu-lbl">Fade Link Margin:</span>
          <strong class="tu-margin">{margin_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_rf_intermod_distortion_card(
        cls,
        component_name: str,
        input_power_dbm: float,
        gain_db: float,
        iip3_dbm: float,
        imd3_suppression_dbc: float,
        linearity_status: str
    ) -> str:
        """
        Renders an RF front-end mixer / amplifier linearity and IMD3 intermodulation distortion card.
        """
        from xml.sax.saxutils import escape

        comp_clean = escape(component_name.strip())
        pin_str = f"{float(input_power_dbm):.1f} dBm"
        gain_str = f"{float(gain_db):.1f} dB"
        iip3_str = f"{float(iip3_dbm):.1f} dBm"
        imd3_str = f"{float(imd3_suppression_dbc):.1f} dBc"
        stat_clean = escape(linearity_status.strip())

        return f"""    <div class="tu-rf-intermod-card">
      <div class="tu-rf-header">
        <span class="tu-rf-badge">RF Linearitas &amp; Intermodulasi (IMD3)</span>
        <span class="tu-rf-status">{stat_clean}</span>
      </div>
      <h4 class="tu-rf-title">Linearitas RF: {comp_clean}</h4>
      <div class="tu-rf-specs">
        <div class="tu-rf-spec">
          <span class="tu-lbl">Daya Input (Pin):</span>
          <strong>{pin_str}</strong>
        </div>
        <div class="tu-rf-spec">
          <span class="tu-lbl">Penguatan (Gain):</span>
          <strong>{gain_str}</strong>
        </div>
        <div class="tu-rf-spec">
          <span class="tu-lbl">Input IP3 (IIP3):</span>
          <strong>{iip3_str}</strong>
        </div>
        <div class="tu-rf-spec">
          <span class="tu-lbl">Supresi IMD3:</span>
          <strong class="tu-imd3">{imd3_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_optical_fiber_dispersion_card(
        cls,
        link_title: str,
        fiber_length_km: float,
        bit_rate_gbps: float,
        cd_delay_ps: float,
        pmd_delay_ps: float,
        total_delay_ps: float,
        power_penalty_db: float,
        status: str
    ) -> str:
        """
        Renders an optical fiber chromatic and polarization mode dispersion (PMD) penalty analysis card.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(link_title.strip())
        len_str = f"{float(fiber_length_km):.1f} km"
        rate_str = f"{float(bit_rate_gbps):.1f} Gbps"
        cd_str = f"{float(cd_delay_ps):.1f} ps"
        pmd_str = f"{float(pmd_delay_ps):.2f} ps"
        tot_str = f"{float(total_delay_ps):.1f} ps"
        penalty_str = f"{float(power_penalty_db):.2f} dB"
        stat_clean = escape(status.strip())

        return f"""    <div class="tu-fiber-dispersion-card">
      <div class="tu-disp-header">
        <span class="tu-disp-badge">Dispersi Serat Optik DWDM</span>
        <span class="tu-disp-status">{stat_clean}</span>
      </div>
      <h4 class="tu-disp-title">{title_clean}</h4>
      <div class="tu-disp-specs">
        <div class="tu-disp-item">
          <span class="tu-lbl">Panjang Fiber:</span>
          <strong>{len_str}</strong>
        </div>
        <div class="tu-disp-item">
          <span class="tu-lbl">Laju Data Transmisi:</span>
          <strong>{rate_str}</strong>
        </div>
        <div class="tu-disp-item">
          <span class="tu-lbl">Delay Dispersi Kromatik (CD):</span>
          <strong>{cd_str}</strong>
        </div>
        <div class="tu-disp-item">
          <span class="tu-lbl">Delay PMD (DGD):</span>
          <strong>{pmd_str}</strong>
        </div>
        <div class="tu-disp-item">
          <span class="tu-lbl">Total Pelebaran Pulsa:</span>
          <strong class="tu-delay">{tot_str}</strong>
        </div>
        <div class="tu-disp-item">
          <span class="tu-lbl">Optical Power Penalty:</span>
          <strong class="tu-penalty">{penalty_str}</strong>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_kampus_mengajar_recognition_card(
        cls,
        student_name: str,
        nim: str,
        target_school: str,
        converted_sks: int,
        letter_grade: str,
        status: str
    ) -> str:
        """
        Renders a student Kampus Mengajar teaching assistantship completion and credit conversion recognition card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(student_name.strip())
        nim_clean = escape(nim.strip())
        school_clean = escape(target_school.strip())
        sks_str = f"{int(converted_sks)} SKS"
        grade_clean = escape(letter_grade.strip())
        status_clean = escape(status.strip())

        return f"""    <div class="tu-mengajar-card">
      <div class="tu-km-header">
        <span class="tu-km-badge">Program Kampus Mengajar MBKM</span>
        <span class="tu-km-sks">{sks_str} Diakui</span>
      </div>
      <h4 class="tu-km-name">{name_clean}</h4>
      <div class="tu-km-meta">
        <span class="tu-km-nim">NIM: <code>{nim_clean}</code></span>
        <span class="tu-km-school">Sekolah Penugasan: <strong>{school_clean}</strong></span>
      </div>
      <div class="tu-km-footer">
        <span class="tu-km-grade">Nilai Mutu: <strong>{grade_clean}</strong></span>
        <span class="tu-km-status">{status_clean}</span>
      </div>
    </div>"""

    @classmethod
    def render_spectral_power_density_card(
        cls,
        title: str,
        center_freq_mhz: float,
        span_mhz: float,
        rbw_khz: float,
        noise_floor_dbm: float,
        peak_power_dbm: float,
        svg_points: Optional[str] = None
    ) -> str:
        """
        Renders an RF spectrum analyzer power spectral density (PSD) visualization component card with inline SVG.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(title.strip())
        fc_str = f"{float(center_freq_mhz):.2f} MHz"
        span_str = f"{float(span_mhz):.1f} MHz"
        rbw_str = f"{float(rbw_khz):.1f} kHz"
        noise_str = f"{float(noise_floor_dbm):.1f} dBm"
        peak_str = f"{float(peak_power_dbm):.1f} dBm"
        points = svg_points.strip() if svg_points else "20,120 60,118 100,119 140,70 150,20 160,70 200,119 240,118 280,120"

        return f"""    <div class="tu-spectral-psd-card">
      <div class="tu-psd-header">
        <span class="tu-psd-badge">Kerapatan Daya Spektral (PSD)</span>
        <span class="tu-psd-rbw">RBW: {rbw_str}</span>
      </div>
      <h4 class="tu-psd-title">{title_clean}</h4>
      <div class="tu-psd-display">
        <svg viewBox="0 0 300 140" class="tu-psd-svg" aria-label="Grafik Spektrum RF">
          <line x1="20" y1="20" x2="280" y2="20" stroke="#334155" stroke-dasharray="2,2" />
          <line x1="20" y1="70" x2="280" y2="70" stroke="#334155" stroke-dasharray="2,2" />
          <line x1="20" y1="120" x2="280" y2="120" stroke="#475569" />
          <polyline points="{points}" fill="none" stroke="#0284c7" stroke-width="2" />
        </svg>
      </div>
      <div class="tu-psd-footer">
        <span class="tu-psd-fc">Fc: <strong>{fc_str}</strong> (Span: {span_str})</span>
        <span class="tu-psd-peak">Puncak: <strong>{peak_str}</strong> (Noise Floor: {noise_str})</span>
      </div>
    </div>"""

    @classmethod
    def render_radar_detection_card(
        cls,
        peak_power_kw: float,
        antenna_gain_dbi: float,
        rcs_m2: float,
        freq_ghz: float,
        max_range_km: float,
        round_trip_delay_us: float
    ) -> str:
        """
        Renders a radar detection telemetry card displaying transmit parameters,
        target cross section, and calculated maximum detection range and propagation delay.
        """
        return f"""    <div class="tu-radar-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #f8fafc;">
      <div class="tu-radar-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0284c7; padding-bottom: 8px; margin-bottom: 12px;">
        <span class="tu-radar-badge" style="font-weight: 700; color: #0284c7; font-size: 13px; text-transform: uppercase;">Radar Range Telemetry</span>
        <span style="font-size: 12px; color: #64748b;">Carrier: {freq_ghz:.2f} GHz</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Jangkauan Deteksi Target Monostatik</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Peak Power</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{peak_power_kw:.1f} kW</div>
        </div>
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Gain Antena</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{antenna_gain_dbi:.1f} dBi</div>
        </div>
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Target RCS (\u03c3)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{rcs_m2:.2f} m\u00b2</div>
        </div>
      </div>
      <div style="background: #e0f2fe; padding: 12px; border-radius: 6px; border-left: 4px solid #0284c7; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 12px; color: #0369a1; font-weight: 600;">Jangkauan Maksimum (R_max):</span>
          <div style="font-size: 18px; font-weight: 800; color: #0c4a6e;">{max_range_km:.2f} km</div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; color: #0369a1;">Waktu Tempuh Pulsa:</span>
          <div style="font-size: 14px; font-weight: 700; color: #0c4a6e;">{round_trip_delay_us:.1f} \u03bcs</div>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_phase_noise_evm_card(
        cls,
        carrier_freq_mhz: float,
        phase_jitter_ps: float,
        phase_noise_rad: float,
        evm_percent: float,
        quality_rating: str
    ) -> str:
        """
        Renders an RF phase noise and EVM constellation degradation card.
        """
        color_map = {
            "Excellent": "#16a34a",
            "Good": "#2563eb",
            "Marginal": "#d97706",
            "Degraded": "#dc2626"
        }
        status_color = color_map.get(quality_rating, "#475569")
        phase_noise_mrad = phase_noise_rad * 1000.0

        return f"""    <div class="tu-evm-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #fdfdfd;">
      <div class="tu-evm-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid {status_color}; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: {status_color}; font-size: 13px; text-transform: uppercase;">Analisis Derau Fasa &amp; EVM</span>
        <span style="font-size: 12px; color: #64748b;">Carrier: {carrier_freq_mhz:.1f} MHz</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Integritas Konstelasi Modulasi Digital</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Jitter Fasa (RMS)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{phase_jitter_ps:.2f} ps</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Phase Error (\u03c6_rms)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{phase_noise_mrad:.2f} mrad</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Kualitas Modulasi</div>
          <div style="font-size: 14px; font-weight: 700; color: {status_color};">{quality_rating}</div>
        </div>
      </div>
      <div style="background: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 4px solid {status_color}; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 13px; color: #334155; font-weight: 600;">Error Vector Magnitude (EVM):</span>
        <span style="font-size: 18px; font-weight: 800; color: {status_color};">{evm_percent:.2f}%</span>
      </div>
    </div>"""

    @classmethod
    def render_edfa_amplifier_card(
        cls,
        input_power_dbm: float,
        pump_power_mw: float,
        gain_db: float,
        output_power_dbm: float,
        noise_figure_db: float,
        operating_regime: str
    ) -> str:
        """
        Renders an optical EDFA amplifier gain and noise figure status card.
        """
        is_linear = "Linear" in operating_regime
        regime_badge_bg = "#ecfdf5" if is_linear else "#fef3c7"
        regime_badge_color = "#047857" if is_linear else "#b45309"

        return f"""    <div class="tu-edfa-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #fafafa;">
      <div class="tu-edfa-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #059669; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #059669; font-size: 13px; text-transform: uppercase;">Penguat Optik EDFA C-Band</span>
        <span style="font-size: 11px; background: {regime_badge_bg}; color: {regime_badge_color}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{operating_regime}</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Karakteristik Penguatan &amp; Derau Spontan (ASE)</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Daya Masukan</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{input_power_dbm:.1f} dBm</div>
        </div>
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Daya Pompa (Pump)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{pump_power_mw:.0f} mW</div>
        </div>
        <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Noise Figure (NF)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{noise_figure_db:.2f} dB</div>
        </div>
      </div>
      <div style="background: #ecfdf5; padding: 12px; border-radius: 6px; border-left: 4px solid #059669; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 12px; color: #047857; font-weight: 600;">Net Optical Gain:</span>
          <div style="font-size: 18px; font-weight: 800; color: #064e3b;">+{gain_db:.2f} dB</div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; color: #047857;">Daya Keluaran (Output):</span>
          <div style="font-size: 16px; font-weight: 700; color: #064e3b;">{output_power_dbm:.2f} dBm</div>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_wirausaha_merdeka_card(
        cls,
        student_name: str,
        nim: str,
        startup_name: str,
        sector: str,
        composite_score: float,
        converted_sks: int,
        status: str
    ) -> str:
        """
        Renders a Wirausaha Merdeka (WMK) startup incubation progress card
        showing entrepreneurship milestones and academic SKS equivalency.
        """
        is_full = converted_sks >= 20
        badge_bg = "#eff6ff" if is_full else "#fff7ed"
        badge_color = "#1d4ed8" if is_full else "#c2410c"

        return f"""    <div class="tu-wmk-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #ffffff;">
      <div class="tu-wmk-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ea580c; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #ea580c; font-size: 13px; text-transform: uppercase;">MBKM Wirausaha Merdeka</span>
        <span style="font-size: 11px; background: {badge_bg}; color: {badge_color}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status}</span>
      </div>
      <h4 style="margin: 0 0 6px 0; color: #0f172a; font-size: 16px;">{startup_name}</h4>
      <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Sektor: <strong>{sector}</strong> | Mahasiswa: {student_name} ({nim})</div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #fff7ed; padding: 10px; border-radius: 6px; border: 1px solid #ffedd5;">
          <div style="font-size: 11px; color: #9a3412;">Nilai Komposit</div>
          <div style="font-size: 18px; font-weight: 800; color: #c2410c;">{composite_score:.1f} / 100</div>
        </div>
        <div style="background: #eff6ff; padding: 10px; border-radius: 6px; border: 1px solid #dbeafe;">
          <div style="font-size: 11px; color: #1e40af;">Konversi SKS</div>
          <div style="font-size: 18px; font-weight: 800; color: #1d4ed8;">{converted_sks} SKS</div>
        </div>
      </div>
      <div style="font-size: 12px; color: #475569; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
        Program akselerasi inkubasi startup teknologi telekomunikasi terakreditasi Kemendikbudristek.
      </div>
    </div>"""

    @classmethod
    def render_iq_constellation_diagram_card(
        cls,
        modulation_format: str,
        num_points: int,
        evm_pct: float,
        snr_db: float
    ) -> str:
        """
        Renders a responsive In-Phase / Quadrature (I/Q) constellation diagram SVG card
        for visual verification of digital modulation schemes and symbol dispersion.
        """
        format_clean = modulation_format.strip() if modulation_format else "QPSK"
        pts = max(4, min(64, int(num_points)))

        # Generate sample points in IQ space
        svg_points = []
        if pts == 4:
            # QPSK 4 points
            coords = [(60, 60), (140, 60), (60, 140), (140, 140)]
        elif pts == 16:
            # 16-QAM grid
            coords = [(40 + 40 * x, 40 + 40 * y) for x in range(4) for y in range(4)]
        else:
            # Generic 8/64 or fallback
            coords = [(50 + 33 * (i % 4), 50 + 33 * (i // 4)) for i in range(min(pts, 16))]

        for cx, cy in coords:
            svg_points.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#0284c7" opacity="0.85" />')
        points_markup = "\n          ".join(svg_points)

        return f"""    <div class="tu-iq-constellation-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #0f172a; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #38bdf8; font-size: 13px; text-transform: uppercase;">Diagram Konstelasi I/Q ({format_clean})</span>
        <span style="font-size: 12px; color: #94a3b8;">SNR: {snr_db:.1f} dB</span>
      </div>
      <div style="display: flex; justify-content: center; margin: 10px 0;">
        <svg viewBox="0 0 200 200" width="200" height="200" style="background: #1e293b; border-radius: 6px; border: 1px solid #475569;" aria-label="Diagram I/Q">
          <!-- Crosshair axes -->
          <line x1="100" y1="10" x2="100" y2="190" stroke="#64748b" stroke-dasharray="2,2" />
          <line x1="10" y1="100" x2="190" y2="100" stroke="#64748b" stroke-dasharray="2,2" />
          <!-- Constellation symbol points -->
          {points_markup}
        </svg>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: #94a3b8;">
        <span>Format: <strong>{format_clean} ({pts}-pt)</strong></span>
        <span>EVM: <strong style="color: #38bdf8;">{evm_pct:.2f}%</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_otdr_fiber_loss_card(
        cls,
        fiber_length_km: float,
        total_loss_db: float,
        attenuation_db_km: float,
        event_loss_db: float,
        wavelength_nm: int,
        status: str
    ) -> str:
        """
        Renders an Optical Time Domain Reflectometer (OTDR) fiber trace summary card
        comparing intrinsic attenuation against ITU-T G.652 standards.
        """
        is_opt = "Optimal" in status or "Sesuai" in status
        badge_bg = "#ecfdf5" if is_opt else "#fef2f2"
        badge_color = "#047857" if is_opt else "#b91c1c"

        return f"""    <div class="tu-otdr-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #ffffff;">
      <div class="tu-otdr-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0284c7; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #0284c7; font-size: 13px; text-transform: uppercase;">Audit Redaman Serat Optik OTDR</span>
        <span style="font-size: 11px; background: {badge_bg}; color: {badge_color}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status}</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Karakteristik Kabel Serat Optik ({wavelength_nm} nm)</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Panjang Kabel</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{fiber_length_km:.2f} km</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Rugi Event Pasif</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{event_loss_db:.2f} dB</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Total Link Loss</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{total_loss_db:.2f} dB</div>
        </div>
      </div>
      <div style="background: #e0f2fe; padding: 12px; border-radius: 6px; border-left: 4px solid #0284c7; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 13px; color: #0369a1; font-weight: 600;">Koefisien Redaman Intrinsik (\u03b1):</span>
        <span style="font-size: 18px; font-weight: 800; color: #0c4a6e;">{attenuation_db_km:.4f} dB/km</span>
      </div>
    </div>"""

    @classmethod
    def render_mimo_capacity_card(
        cls,
        bandwidth_mhz: float,
        snr_db: float,
        num_tx: int,
        num_rx: int,
        spectral_eff: float,
        capacity_gbps: float,
        gain_factor: float,
        status: str
    ) -> str:
        """
        Renders a MIMO channel capacity and spatial multiplexing spectral efficiency card.
        """
        return f"""    <div class="tu-mimo-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #ffffff;">
      <div class="tu-mimo-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #7c3aed; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #7c3aed; font-size: 13px; text-transform: uppercase;">Kapasitas Kanal Nirkabel {num_tx}x{num_rx} MIMO</span>
        <span style="font-size: 11px; background: #f5f3ff; color: #6d28d9; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status}</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Efisiensi Spektral Spatial Multiplexing Shannon-Telatar</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Lebar Pita (B)</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{bandwidth_mhz:.1f} MHz</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">SNR Kanal</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{snr_db:.1f} dB</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Gain vs SISO</div>
          <div style="font-size: 14px; font-weight: 700; color: #7c3aed;">{gain_factor:.2f}x Lipat</div>
        </div>
      </div>
      <div style="background: #f5f3ff; padding: 12px; border-radius: 6px; border-left: 4px solid #7c3aed; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 12px; color: #6d28d9; font-weight: 600;">Efisiensi Spektral (\u03b7):</span>
          <div style="font-size: 16px; font-weight: 800; color: #4c1d95;">{spectral_eff:.2f} bps/Hz</div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; color: #6d28d9;">Throughput Maksimum:</span>
          <div style="font-size: 18px; font-weight: 800; color: #4c1d95;">{capacity_gbps:.3f} Gbps</div>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_lorawan_battery_card(
        cls,
        battery_mah: float,
        interval_min: float,
        avg_current_ua: float,
        lifetime_years: float,
        duty_cycle_pct: float,
        is_compliant: bool
    ) -> str:
        """
        Renders an IoT LoRaWAN edge sensor node battery longevity and energy profiling card.
        """
        reg_status = "ETSI/AS923 Compliant" if is_compliant else "Duty Cycle Exceeded"
        badge_bg = "#ecfdf5" if is_compliant else "#fef2f2"
        badge_color = "#047857" if is_compliant else "#b91c1c"

        return f"""    <div class="tu-lorawan-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #ffffff;">
      <div class="tu-lora-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #059669; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #059669; font-size: 13px; text-transform: uppercase;">Profil Energi Node Sensor LoRaWAN</span>
        <span style="font-size: 11px; background: {badge_bg}; color: {badge_color}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{reg_status}</span>
      </div>
      <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">Estimasi Masa Pakai Baterai Mandiri</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Kapasitas Sel</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{battery_mah:.0f} mAh</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Interval Uplink</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{interval_min:.0f} menit</div>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
          <div style="font-size: 11px; color: #64748b;">Arus Rerata</div>
          <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{avg_current_ua:.1f} \u03bcA</div>
        </div>
      </div>
      <div style="background: #ecfdf5; padding: 12px; border-radius: 6px; border-left: 4px solid #059669; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 12px; color: #047857; font-weight: 600;">Estimasi Masa Aktif:</span>
          <div style="font-size: 18px; font-weight: 800; color: #064e3b;">~{lifetime_years:.1f} Tahun</div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 11px; color: #047857;">Duty Cycle TX:</span>
          <div style="font-size: 14px; font-weight: 700; color: #064e3b;">{duty_cycle_pct:.3f}%</div>
        </div>
      </div>
    </div>"""

    @classmethod
    def render_iisma_exchange_card(
        cls,
        student_name: str,
        nim: str,
        host_university: str,
        country: str,
        gpa_host: float,
        converted_sks: int,
        status: str
    ) -> str:
        """
        Renders an IISMA international student exchange recognition card.
        """
        is_full = converted_sks >= 20
        badge_bg = "#eff6ff" if is_full else "#fff7ed"
        badge_color = "#1d4ed8" if is_full else "#c2410c"

        return f"""    <div class="tu-iisma-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #ffffff;">
      <div class="tu-iisma-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2563eb; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #2563eb; font-size: 13px; text-transform: uppercase;">MBKM Indonesian International Student Mobility Awards (IISMA)</span>
        <span style="font-size: 11px; background: {badge_bg}; color: {badge_color}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status}</span>
      </div>
      <h4 style="margin: 0 0 6px 0; color: #0f172a; font-size: 16px;">{host_university} ({country})</h4>
      <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Mahasiswa Awardee: <strong>{student_name}</strong> (`{nim}`)</div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
        <div style="background: #eff6ff; padding: 10px; border-radius: 6px; border: 1px solid #dbeafe;">
          <div style="font-size: 11px; color: #1e40af;">IPK Luar Negeri</div>
          <div style="font-size: 18px; font-weight: 800; color: #1d4ed8;">{gpa_host:.2f} / 4.00</div>
        </div>
        <div style="background: #f0fdf4; padding: 10px; border-radius: 6px; border: 1px solid #dcfce7;">
          <div style="font-size: 11px; color: #166534;">Rekognisi SKS</div>
          <div style="font-size: 18px; font-weight: 800; color: #15803d;">{converted_sks} SKS Diakui</div>
        </div>
      </div>
      <div style="font-size: 12px; color: #475569; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
        Program mobilitas internasional bereputasi global Kemendikbudristek untuk penguatan kompetensi telekomunikasi global.
      </div>
    </div>"""

    @classmethod
    def render_beamforming_pattern_card(
        cls,
        array_elements: int,
        main_lobe_deg: float,
        half_power_beamwidth_deg: float,
        side_lobe_level_db: float,
        directivity_dbi: float
    ) -> str:
        """
        Renders an adaptive antenna array beamforming radiation pattern SVG card
        showing phased array main lobe steering, half-power beamwidth (HPBW), and sidelobe suppression.
        """
        return f"""    <div class="tu-beamforming-card" style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; background: #0f172a; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px;">
        <span style="font-weight: 700; color: #38bdf8; font-size: 13px; text-transform: uppercase;">Pola Radiasi Beamforming Phased Array ({array_elements} Elemen)</span>
        <span style="font-size: 12px; color: #94a3b8;">Direktivitas: {directivity_dbi:.1f} dBi</span>
      </div>
      <div style="display: flex; justify-content: center; margin: 10px 0;">
        <svg viewBox="0 0 240 130" width="240" height="130" style="background: #1e293b; border-radius: 6px; border: 1px solid #475569;" aria-label="Diagram Beamforming">
          <!-- Concentric angle grid -->
          <circle cx="120" cy="110" r="90" fill="none" stroke="#334155" stroke-dasharray="2,2" />
          <circle cx="120" cy="110" r="50" fill="none" stroke="#334155" stroke-dasharray="2,2" />
          <line x1="30" y1="110" x2="210" y2="110" stroke="#475569" />
          <!-- Main beam lobe -->
          <path d="M 120 110 C 95 60, 105 20, 120 15 C 135 20, 145 60, 120 110 Z" fill="#0284c7" opacity="0.8" />
          <!-- Side lobes -->
          <path d="M 120 110 C 80 90, 70 80, 80 75 C 90 75, 105 95, 120 110 Z" fill="#38bdf8" opacity="0.4" />
          <path d="M 120 110 C 135 95, 150 75, 160 75 C 170 80, 160 90, 120 110 Z" fill="#38bdf8" opacity="0.4" />
        </svg>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: #94a3b8;">
        <span>Sudut Kemudi (Steering): <strong>{main_lobe_deg:.1f}\u00b0</strong></span>
        <span>HPBW: <strong>{half_power_beamwidth_deg:.1f}\u00b0</strong></span>
        <span>SLL: <strong style="color: #38bdf8;">{side_lobe_level_db:.1f} dB</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_fspl_link_budget_card(
        cls,
        link_name: str,
        freq_mhz: float,
        distance_km: float,
        fspl_db: float,
        rx_power_dbm: float,
        fade_margin_db: float,
        is_viable: bool
    ) -> str:
        """
        Renders an RF free space path loss (FSPL) and wireless link budget fade margin card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(link_name.strip())
        status_color = "#10b981" if is_viable else "#ef4444"
        status_badge = "Link Layak (Viable)" if is_viable else "Link Putus (Outage)"

        return f"""    <div class="tu-fspl-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Link Budget & FSPL</span>
        <span style="background: {status_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status_badge}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Frekuensi: <strong>{freq_mhz:.1f} MHz</strong></div>
        <div>Jarak Bentang: <strong>{distance_km:.2f} km</strong></div>
        <div>Path Loss (FSPL): <strong style="color: #f59e0b;">{fspl_db:.2f} dB</strong></div>
        <div>Daya Terima (Prx): <strong style="color: #38bdf8;">{rx_power_dbm:.2f} dBm</strong></div>
      </div>
      <div style="border-top: 1px solid #334155; padding-top: 10px; font-size: 13px; display: flex; justify-content: space-between;">
        <span>Fade Margin:</span>
        <strong style="color: {status_color}; font-size: 15px;">{fade_margin_db:+.2f} dB</strong>
      </div>
    </div>"""

    @classmethod
    def render_chromatic_dispersion_card(
        cls,
        fiber_name: str,
        length_km: float,
        dispersion_param: float,
        pulse_broadening_ps: float,
        max_bit_rate_gbps: float,
        severity: str
    ) -> str:
        """
        Renders an optical fiber chromatic dispersion and pulse widening telemetry card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(fiber_name.strip())
        severity_clean = escape(severity.strip())

        return f"""    <div class="tu-dispersion-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #a855f7; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Dispersi Kromatik Serat</span>
        <span style="background: #334155; color: #cbd5e1; font-size: 11px; padding: 3px 8px; border-radius: 4px;">{severity_clean}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Panjang Serat: <strong>{length_km:.2f} km</strong></div>
        <div>Parameter D: <strong>{dispersion_param:.2f} ps/(nm\u00b7km)</strong></div>
        <div>Pelebaran Pulsa (\u0394t): <strong style="color: #f59e0b;">{pulse_broadening_ps:.2f} ps</strong></div>
        <div>Batas Laju Bit Maks: <strong style="color: #38bdf8;">{max_bit_rate_gbps:.2f} Gbps</strong></div>
      </div>
    </div>"""

    @classmethod
    def render_cellular_handover_card(
        cls,
        serving_cell: str,
        target_cell: str,
        rsrp_serving_dbm: float,
        rsrp_target_dbm: float,
        hysteresis_db: float,
        decision: str
    ) -> str:
        """
        Renders a cellular LTE/5G A3 handover telemetry and decision status card.
        """
        from xml.sax.saxutils import escape

        s_clean = escape(serving_cell.strip())
        t_clean = escape(target_cell.strip())
        dec_clean = escape(decision.strip())
        dec_color = "#10b981" if "TRIGGER" in decision else ("#f59e0b" if "PENDING" in decision else "#64748b")

        return f"""    <div class="tu-handover-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Cellular Handover A3</span>
        <span style="background: {dec_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{dec_clean}</span>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>Serving: <strong>{s_clean}</strong> ({rsrp_serving_dbm:.1f} dBm)</div>
        <div style="color: #64748b;">\u27a1</div>
        <div>Target: <strong>{t_clean}</strong> ({rsrp_target_dbm:.1f} dBm)</div>
      </div>
      <div style="font-size: 12px; color: #94a3b8; border-top: 1px solid #334155; padding-top: 8px;">
        <span>Margin Histeresis: <strong>{hysteresis_db:.1f} dB</strong> | Delta RSRP: <strong>{(rsrp_target_dbm - rsrp_serving_dbm):+.1f} dB</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_proyek_kemanusiaan_card(
        cls,
        student_name: str,
        nim: str,
        partner_org: str,
        converted_sks: int,
        composite_score: float,
        letter_grade: str,
        status: str
    ) -> str:
        """
        Renders a student MBKM Proyek Kemanusiaan completion and credit recognition card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(student_name.strip())
        nim_clean = escape(nim.strip())
        org_clean = escape(partner_org.strip())
        grade_clean = escape(letter_grade.strip())
        status_clean = escape(status.strip())

        return f"""    <div class="tu-kemanusiaan-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #f43f5e; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Proyek Kemanusiaan MBKM</span>
        <span style="background: #0284c7; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{converted_sks} SKS Diakui</span>
      </div>
      <h4 style="margin: 0 0 6px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="font-size: 13px; color: #94a3b8; margin-bottom: 12px;">
        NIM: <code style="color: #38bdf8;">{nim_clean}</code> | Mitra: <strong>{org_clean}</strong>
      </div>
      <div style="border-top: 1px solid #334155; padding-top: 10px; display: flex; justify-content: space-between; font-size: 13px;">
        <span>Skor Komposit: <strong>{composite_score:.2f}</strong> (Mutu: <strong style="color: #10b981;">{grade_clean}</strong>)</span>
        <span style="color: #cbd5e1;">{status_clean}</span>
      </div>
    </div>"""

    @classmethod
    def render_optical_eye_diagram_svg_card(
        cls,
        title: str,
        data_rate_gbps: float,
        eye_height_mv: float,
        eye_width_ps: float,
        jitter_rms_ps: float,
        q_factor: float
    ) -> str:
        """
        Renders an optical high-speed transmission eye diagram (diagram mata sinyal) visualization card with responsive inline SVG.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(title.strip())

        return f"""    <div class="tu-eye-diagram-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Diagram Mata Optik (Eye Diagram)</span>
        <span style="font-size: 12px; color: #94a3b8;">Laju: {data_rate_gbps:.1f} Gbps</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{title_clean}</h4>
      <div style="display: flex; justify-content: center; margin: 12px 0;">
        <svg viewBox="0 0 260 120" width="260" height="120" style="background: #020617; border-radius: 6px; border: 1px solid #334155;" aria-label="Diagram Mata Sinyal">
          <!-- Crosshair and thresholds -->
          <line x1="20" y1="60" x2="240" y2="60" stroke="#334155" stroke-dasharray="2,2" />
          <line x1="130" y1="15" x2="130" y2="105" stroke="#334155" stroke-dasharray="2,2" />
          <!-- Eye pattern transitions -->
          <path d="M 20 25 C 80 25, 90 95, 130 95 C 170 95, 180 25, 240 25" fill="none" stroke="#0ea5e9" stroke-width="2" opacity="0.8" />
          <path d="M 20 95 C 80 95, 90 25, 130 25 C 170 25, 180 95, 240 95" fill="none" stroke="#0ea5e9" stroke-width="2" opacity="0.8" />
          <path d="M 20 25 L 240 25" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.6" />
          <path d="M 20 95 L 240 95" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.6" />
          <!-- Eye opening opening area -->
          <ellipse cx="130" cy="60" rx="35" ry="22" fill="#0369a1" opacity="0.15" />
        </svg>
      </div>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 12px; color: #94a3b8; border-top: 1px solid #334155; padding-top: 10px;">
        <span>Eye Height: <strong style="color: #10b981;">{eye_height_mv:.1f} mV</strong></span>
        <span>Eye Width: <strong style="color: #38bdf8;">{eye_width_ps:.1f} ps</strong></span>
        <span>RMS Jitter: <strong style="color: #f59e0b;">{jitter_rms_ps:.2f} ps</strong></span>
        <span>Q-Factor: <strong style="color: #ffffff;">{q_factor:.2f}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_pmd_dispersion_card(
        cls,
        fiber_name: str,
        length_km: float,
        pmd_coeff: float,
        mean_dgd_ps: float,
        max_bit_rate_gbps: float,
        outage_risk: str
    ) -> str:
        """
        Renders an optical fiber Polarization Mode Dispersion (PMD) and DGD telemetry card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(fiber_name.strip())
        risk_clean = escape(outage_risk.strip())
        is_safe = "Sangat Rendah" in outage_risk or "Moderat" in outage_risk
        risk_color = "#10b981" if "Sangat Rendah" in outage_risk else ("#f59e0b" if "Moderat" in outage_risk else "#ef4444")

        return f"""    <div class="tu-pmd-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Polarization Mode Dispersion (PMD)</span>
        <span style="background: {risk_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{risk_clean}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Panjang Ruas: <strong>{length_km:.2f} km</strong></div>
        <div>Koefisien PMD: <strong>{pmd_coeff:.3f} ps/\u221akm</strong></div>
        <div>Mean DGD (\u27e8\u0394\u03c4\u27e9): <strong style="color: #f59e0b;">{mean_dgd_ps:.3f} ps</strong></div>
        <div>Kapasitas Laju Bit: <strong style="color: #38bdf8;">{max_bit_rate_gbps:.2f} Gbps</strong></div>
      </div>
    </div>"""

    @classmethod
    def render_cost231_hata_card(
        cls,
        area_name: str,
        freq_mhz: float,
        distance_km: float,
        path_loss_db: float,
        coverage_quality: str,
        is_metro: bool = False
    ) -> str:
        """
        Renders a cellular radio COST 231 Hata urban/suburban propagation telemetry card.
        """
        from xml.sax.saxutils import escape

        area_clean = escape(area_name.strip())
        quality_clean = escape(coverage_quality.strip())
        env_badge = "Metropolitan / Kota Besar" if is_metro else "Urban / Suburban"

        return f"""    <div class="tu-cost231-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Propagasi COST 231 Hata</span>
        <span style="background: #334155; color: #cbd5e1; font-size: 11px; padding: 3px 8px; border-radius: 4px;">{env_badge}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{area_clean}</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Frekuensi: <strong>{freq_mhz:.1f} MHz</strong></div>
        <div>Jarak Sel: <strong>{distance_km:.2f} km</strong></div>
        <div>Path Loss: <strong style="color: #f59e0b;">{path_loss_db:.2f} dB</strong></div>
        <div>Kualitas Sinyal: <strong style="color: #10b981;">{quality_clean}</strong></div>
      </div>
    </div>"""

    @classmethod
    def render_rain_attenuation_card(
        cls,
        link_name: str,
        freq_ghz: float,
        rain_rate: float,
        rain_attenuation_db: float,
        excess_margin_db: float,
        status: str
    ) -> str:
        """
        Renders a microwave terrestrial link ITU-R rain attenuation and fade margin card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(link_name.strip())
        status_clean = escape(status.strip())
        status_color = "#10b981" if excess_margin_db >= 10.0 else ("#f59e0b" if excess_margin_db >= 0.0 else "#ef4444")

        return f"""    <div class="tu-rain-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #0284c7; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Redaman Hujan ITU-R P.838</span>
        <span style="background: {status_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status_clean}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Frekuensi: <strong>{freq_ghz:.2f} GHz</strong></div>
        <div>Curah Hujan (R0.01): <strong>{rain_rate:.1f} mm/jam</strong></div>
        <div>Redaman Hujan Total: <strong style="color: #f59e0b;">{rain_attenuation_db:.2f} dB</strong></div>
        <div>Margin Tersisa (Excess): <strong style="color: {status_color};">{excess_margin_db:+.2f} dB</strong></div>
      </div>
    </div>"""

    @classmethod
    def render_studi_independen_card(
        cls,
        student_name: str,
        nim: str,
        partner_name: str,
        track_name: str,
        converted_sks: int,
        composite_score: float,
        letter_grade: str
    ) -> str:
        """
        Renders a student MBKM Studi / Riset Independen Bersertifikat (SIB) recognition card.
        """
        from xml.sax.saxutils import escape

        name_clean = escape(student_name.strip())
        nim_clean = escape(nim.strip())
        partner_clean = escape(partner_name.strip())
        track_clean = escape(track_name.strip())
        grade_clean = escape(letter_grade.strip())

        return f"""    <div class="tu-sib-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Studi Independen Bersertifikat</span>
        <span style="background: #0284c7; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{converted_sks} SKS Diakui</span>
      </div>
      <h4 style="margin: 0 0 6px 0; font-size: 16px; color: #ffffff;">{name_clean}</h4>
      <div style="font-size: 13px; color: #94a3b8; margin-bottom: 12px;">
        NIM: <code style="color: #38bdf8;">{nim_clean}</code> | Jalur: <strong>{track_clean}</strong>
      </div>
      <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 10px;">
        Mitra Penyelenggara: <strong>{partner_clean}</strong>
      </div>
      <div style="border-top: 1px solid #334155; padding-top: 10px; display: flex; justify-content: space-between; font-size: 13px;">
        <span>Skor Komposit: <strong>{composite_score:.2f}</strong></span>
        <span>Nilai Mutu: <strong style="color: #10b981;">{grade_clean}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_dispersion_compensation_svg_card(
        cls,
        title: str,
        smf_dispersion_ps: float,
        dcf_compensation_ps: float,
        net_dispersion_ps: float
    ) -> str:
        """
        Renders an optical dispersion compensation (DCF) scheme visualization card with responsive inline SVG.
        """
        from xml.sax.saxutils import escape

        title_clean = escape(title.strip())

        return f"""    <div class="tu-dcf-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Kompensasi Dispersi Serat (DCF)</span>
        <span style="font-size: 12px; color: #94a3b8;">Net: {net_dispersion_ps:+.2f} ps</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">{title_clean}</h4>
      <div style="display: flex; justify-content: center; margin: 12px 0;">
        <svg viewBox="0 0 280 100" width="280" height="100" style="background: #020617; border-radius: 6px; border: 1px solid #334155;" aria-label="Diagram Kompensasi Dispersi">
          <!-- SMF block (positive dispersion) -->
          <rect x="20" y="30" width="100" height="40" rx="4" fill="#0284c7" opacity="0.8" />
          <text x="70" y="54" fill="#ffffff" font-size="11" text-anchor="middle" font-weight="bold">SMF-28 (+D)</text>
          <!-- DCF block (negative dispersion) -->
          <rect x="160" y="30" width="100" height="40" rx="4" fill="#a855f7" opacity="0.8" />
          <text x="210" y="54" fill="#ffffff" font-size="11" text-anchor="middle" font-weight="bold">DCF (-D)</text>
          <!-- Connector arrow -->
          <line x1="120" y1="50" x2="160" y2="50" stroke="#38bdf8" stroke-width="2" />
        </svg>
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 12px; color: #94a3b8; border-top: 1px solid #334155; padding-top: 10px; text-align: center;">
        <div>Dispersi SMF: <strong style="color: #38bdf8;">{smf_dispersion_ps:+.1f} ps</strong></div>
        <div>Kompensasi DCF: <strong style="color: #c084fc;">{dcf_compensation_ps:+.1f} ps</strong></div>
        <div>Residu Sisa: <strong style="color: #10b981;">{net_dispersion_ps:+.1f} ps</strong></div>
      </div>
    </div>"""

    @classmethod
    def render_fwm_crosstalk_card(
        cls,
        channel_spacing_ghz: float,
        fiber_length_km: float,
        dispersion_ps_nm_km: float,
        fwm_efficiency_pct: float,
        crosstalk_suppression_dbc: float,
        risk_status: str
    ) -> str:
        """
        Renders an optical fiber DWDM Four-Wave Mixing (FWM) nonlinear crosstalk telemetry card.
        """
        from xml.sax.saxutils import escape

        status_clean = escape(risk_status.strip())
        is_safe = "Sangat Rendah" in risk_status or "Aman" in risk_status
        risk_color = "#10b981" if is_safe else ("#f59e0b" if "Moderat" in risk_status else "#ef4444")

        return f"""    <div class="tu-fwm-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Four-Wave Mixing (FWM) DWDM</span>
        <span style="background: {risk_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">{status_clean}</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">Telemetri Crosstalk Nirlinier FWM</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Spasi Kanal: <strong>{channel_spacing_ghz:.1f} GHz</strong></div>
        <div>Panjang Ruas: <strong>{fiber_length_km:.2f} km</strong></div>
        <div>Dispersi Kromatik D: <strong>{dispersion_ps_nm_km:.2f} ps/(nm·km)</strong></div>
        <div>Efisiensi FWM (\u03b7): <strong style="color: #38bdf8;">{fwm_efficiency_pct:.3f}%</strong></div>
      </div>
      <div style="border-top: 1px solid #334155; padding-top: 10px; font-size: 13px; display: flex; justify-content: space-between;">
        <span>Supresi Crosstalk: <strong style="color: #10b981;">{crosstalk_suppression_dbc:.2f} dBc</strong></span>
        <span>Status: <strong style="color: {risk_color};">{status_clean}</strong></span>
      </div>
    </div>"""

    @classmethod
    def render_erlang_traffic_card(
        cls,
        offered_traffic_erlangs: float,
        num_channels: int,
        blocking_pct: float,
        carried_traffic: float,
        gos_status: str
    ) -> str:
        """
        Renders a cellular radio and trunked network Erlang traffic and GoS performance card.
        """
        from xml.sax.saxutils import escape

        status_clean = escape(gos_status.strip())
        is_safe = blocking_pct <= 2.0
        status_color = "#10b981" if is_safe else ("#f59e0b" if blocking_pct <= 5.0 else "#ef4444")

        return f"""    <div class="tu-erlang-card" style="border: 1px solid #334155; border-radius: 8px; padding: 16px; background: #0f172a; margin: 16px 0; color: #f8fafc;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: #1e293b; color: #38bdf8; font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">Kapasitas Trafik Erlang-B/C</span>
        <span style="background: {status_color}; color: #ffffff; font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 600;">Blocking: {blocking_pct:.2f}%</span>
      </div>
      <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #ffffff;">Analisis Trunking & Grade of Service</h4>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; font-size: 13px;">
        <div>Trafik Ditawarkan: <strong>{offered_traffic_erlangs:.2f} Erlang</strong></div>
        <div>Jumlah Kanal Server: <strong>{num_channels} Kanal</strong></div>
        <div>Trafik Terlayani: <strong style="color: #38bdf8;">{carried_traffic:.2f} Erlang</strong></div>
        <div>Peluang Blocking: <strong style="color: {status_color};">{blocking_pct:.3f}%</strong></div>
      </div>
      <div style="border-top: 1px solid #334155; padding-top: 10px; font-size: 13px; display: flex; justify-content: space-between;">
        <span>Status GoS: <strong style="color: {status_color};">{status_clean}</strong></span>
        <span>Standar: <strong>GoS &le; 2%</strong></span>
      </div>
    </div>"""



























































