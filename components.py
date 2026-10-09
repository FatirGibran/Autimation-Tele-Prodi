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

