import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class ArticleExporter:
    @staticmethod
    def to_elementor_json(title: str, html_content: str) -> Dict[str, Any]:
        """
        Converts the scoped HTML container into a valid Elementor JSON template.
        """
        return {
            "version": "0.4",
            "title": f"Editorial - {title}",
            "type": "section",
            "content": [
                {
                    "id": "tu_editorial_section",
                    "elType": "section",
                    "settings": {
                        "layout": "boxed",
                        "content_width": {"unit": "px", "size": 820}
                    },
                    "elements": [
                        {
                            "id": "tu_editorial_column",
                            "elType": "column",
                            "settings": {"_column_size": 100},
                            "elements": [
                                {
                                    "id": "tu_html_widget",
                                    "elType": "widget",
                                    "widgetType": "html",
                                    "settings": {
                                        "html": html_content
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def to_markdown_with_frontmatter(metadata: Dict[str, Any], html_content: str) -> str:
        frontmatter = [
            "---",
            f"title: \"{metadata.get('seo_title', '')}\"",
            f"focus_keyphrase: \"{metadata.get('focus_keyphrase', '')}\"",
            f"slug: \"{metadata.get('slug', '')}\"",
            f"meta_description: \"{metadata.get('meta_description', '')}\"",
            f"category: \"{metadata.get('category', '')}\"",
            f"date: \"{metadata.get('publish_date', '')}\"",
            "---",
            "",
            html_content
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def to_html_document(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Wraps scoped HTML in a standalone HTML5 document with OpenGraph and SEO meta tags.
        """
        title = metadata.get("seo_title", "")
        meta_desc = metadata.get("meta_description", "")
        slug = metadata.get("slug", "")
        canonical = f"https://bif-pwt.telkomuniversity.ac.id/{slug}/" if slug else ""

        return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <link rel="canonical" href="{canonical}">
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #ffffff;
      color: #1e293b;
    }}
  </style>
</head>
<body>
{html_content}
</body>
</html>"""

    @classmethod
    def export_bundle(cls, output_dir: Path, slug: str, metadata: Dict[str, Any], html_content: str) -> Dict[str, Path]:
        """
        Exports article HTML, standalone page, markdown with frontmatter, and Elementor JSON.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}

        html_path = output_dir / f"{slug}.html"
        html_path.write_text(html_content, encoding="utf-8")
        paths["html"] = html_path

        standalone_path = output_dir / f"{slug}_standalone.html"
        standalone_path.write_text(cls.to_html_document(metadata, html_content), encoding="utf-8")
        paths["standalone_html"] = standalone_path

        md_path = output_dir / f"{slug}.md"
        md_path.write_text(cls.to_markdown_with_frontmatter(metadata, html_content), encoding="utf-8")
        paths["markdown"] = md_path

        elementor_path = output_dir / f"{slug}_elementor.json"
        elementor_data = cls.to_elementor_json(metadata.get("seo_title", slug), html_content)
        elementor_path.write_text(json.dumps(elementor_data, indent=2), encoding="utf-8")
        paths["elementor_json"] = elementor_path

        return paths

    @staticmethod
    def generate_json_ld(metadata: Dict[str, Any], article_type: str = "NewsArticle") -> str:
        slug = metadata.get("slug", "")
        url = f"https://bif-pwt.telkomuniversity.ac.id/{slug}/" if slug else "https://bif-pwt.telkomuniversity.ac.id/"
        data = {
            "@context": "https://schema.org",
            "@type": article_type,
            "headline": metadata.get("seo_title", ""),
            "description": metadata.get("meta_description", ""),
            "datePublished": metadata.get("publish_date", ""),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": url
            },
            "publisher": {
                "@type": "Organization",
                "name": "S1 Teknik Informatika Telkom University Purwokerto",
                "url": "https://bif-pwt.telkomuniversity.ac.id"
            }
        }
        if metadata.get("image_url"):
            data["image"] = [metadata["image_url"]]
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_rss_feed(articles: List[Dict[str, Any]], channel_info: Dict[str, str]) -> str:
        """
        Generates standard RSS 2.0 XML feed from a list of articles.
        """
        from xml.sax.saxutils import escape

        ch_title = escape(channel_info.get("title", "Portal Riset & Berita S1 Teknik Informatika"))
        ch_link = escape(channel_info.get("link", "https://bif-pwt.telkomuniversity.ac.id"))
        ch_desc = escape(channel_info.get("description", "Publikasi berkala seputar inovasi teknologi, riset, dan prestasi prodi."))

        items_xml = []
        for art in articles:
            item_title = escape(art.get("seo_title", art.get("topic", "")))
            slug = art.get("slug", "")
            item_link = f"https://bif-pwt.telkomuniversity.ac.id/{slug}/" if slug else ch_link
            item_desc = escape(art.get("meta_description", ""))
            pub_date = escape(art.get("publish_date", ""))
            cat = escape(art.get("category", "Umum"))
            items_xml.append(f"""    <item>
      <title>{item_title}</title>
      <link>{item_link}</link>
      <guid>{item_link}</guid>
      <pubDate>{pub_date}</pubDate>
      <category>{cat}</category>
      <description>{item_desc}</description>
    </item>""")

        body = "\n".join(items_xml)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{ch_title}</title>
    <link>{ch_link}</link>
    <description>{ch_desc}</description>
    <language>id-ID</language>
{body}
  </channel>
</rss>"""

    @staticmethod
    def generate_sitemap_xml(articles: List[Dict[str, Any]], base_url: str = "https://bif-pwt.telkomuniversity.ac.id") -> str:
        """
        Generates standard XML sitemap for search engine web crawlers.
        """
        from xml.sax.saxutils import escape

        clean_base = base_url.rstrip("/")
        urls = [f"""  <url>
    <loc>{clean_base}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""]

        for art in articles:
            slug = art.get("slug", "")
            if not slug:
                continue
            loc = f"{clean_base}/{slug}/"
            lastmod = art.get("publish_date", "")
            urls.append(f"""  <url>
    <loc>{escape(loc)}</loc>
    <lastmod>{escape(lastmod)}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

        body = "\n".join(urls)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>"""

    @staticmethod
    def generate_social_meta_tags(metadata: Dict[str, Any], canonical_url: str = "") -> str:
        """
        Generates standard OpenGraph and Twitter Cards metadata HTML tags.
        """
        from xml.sax.saxutils import escape
        title = escape(metadata.get("seo_title", ""))
        desc = escape(metadata.get("meta_description", ""))
        image = escape(metadata.get("image_url", ""))
        url = escape(canonical_url)

        tags = [
            '<meta property="og:type" content="article" />',
            f'<meta property="og:title" content="{title}" />',
            f'<meta property="og:description" content="{desc}" />',
        ]
        if url:
            tags.append(f'<meta property="og:url" content="{url}" />')
        if image:
            tags.append(f'<meta property="og:image" content="{image}" />')

        tags.extend([
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{title}" />',
            f'<meta name="twitter:description" content="{desc}" />',
        ])
        if image:
            tags.append(f'<meta name="twitter:image" content="{image}" />')

        return "\n".join(tags)

    @staticmethod
    def generate_breadcrumb_schema(breadcrumbs: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates schema.org/BreadcrumbList JSON-LD structured data.
        """
        elements = []
        for idx, item in enumerate(breadcrumbs, start=1):
            elements.append({
                "@type": "ListItem",
                "position": idx,
                "name": item.get("name", ""),
                "item": item.get("url", "")
            })
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": elements
        }

    @staticmethod
    def generate_atom_feed(articles: List[Dict[str, Any]], feed_info: Dict[str, str]) -> str:
        """
        Generates RFC 4287 compliant Atom 1.0 XML syndication feed.
        """
        from xml.sax.saxutils import escape

        feed_id = escape(feed_info.get("id", "https://bif-pwt.telkomuniversity.ac.id/atom.xml"))
        title = escape(feed_info.get("title", "S1 Teknik Informatika Telkom University Purwokerto"))
        updated = escape(feed_info.get("updated", "2026-10-01T00:00:00Z"))
        author = escape(feed_info.get("author", "Tim Editorial Prodi"))
        base_url = feed_info.get("base_url", "https://bif-pwt.telkomuniversity.ac.id").rstrip("/")

        entries = []
        for art in articles:
            slug = art.get("slug", "")
            if not slug:
                continue
            entry_url = f"{base_url}/{slug}/"
            entry_title = escape(art.get("seo_title", art.get("topic", "")))
            entry_summary = escape(art.get("meta_description", ""))
            pub_date = art.get("publish_date", "2026-01-01")
            updated_date = f"{pub_date}T00:00:00Z"

            entries.append(f"""  <entry>
    <id>{escape(entry_url)}</id>
    <title>{entry_title}</title>
    <link href="{escape(entry_url)}" rel="alternate" />
    <updated>{escape(updated_date)}</updated>
    <summary>{entry_summary}</summary>
    <author><name>{author}</name></author>
  </entry>""")

        body = "\n".join(entries)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>{feed_id}</id>
  <title>{title}</title>
  <updated>{updated}</updated>
  <author><name>{author}</name></author>
  <link href="{feed_id}" rel="self" />
{body}
</feed>"""

    @staticmethod
    def generate_json_feed(articles: List[Dict[str, Any]], feed_info: Dict[str, str]) -> str:
        """
        Generates standard JSON Feed v1.1 formatted syndication feed.
        """
        base_url = feed_info.get("base_url", "https://bif-pwt.telkomuniversity.ac.id").rstrip("/")
        items = []
        for art in articles:
            slug = art.get("slug", "")
            if not slug:
                continue
            item = {
                "id": f"{base_url}/{slug}/",
                "url": f"{base_url}/{slug}/",
                "title": art.get("seo_title", art.get("topic", "")),
                "summary": art.get("meta_description", ""),
                "date_published": art.get("publish_date", ""),
            }
            if art.get("html_content"):
                item["content_html"] = art["html_content"]
            if art.get("image_url"):
                item["image"] = art["image_url"]
            items.append(item)

        feed_data = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": feed_info.get("title", "S1 Teknik Informatika Telkom University Purwokerto"),
            "home_page_url": base_url,
            "feed_url": feed_info.get("feed_url", f"{base_url}/feed.json"),
            "items": items
        }
        return json.dumps(feed_data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_plain_text(html_content: str) -> str:
        """
        Extracts clean plain text formatted with paragraph breaks, stripping HTML elements.
        Useful for text search indexing, CLI terminal rendering, or speech synthesis.
        """
        if not html_content:
            return ""
        import html
        # Replace block elements with newlines
        text = re.sub(r"<(?:p|div|h[1-6]|li|blockquote|tr)[^>]*>", "\n", html_content, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        clean_lines = [l for l in lines if l]
        return "\n\n".join(clean_lines)

    @staticmethod
    def to_hugo_markdown(metadata: Dict[str, Any], html_content: str, is_draft: bool = False) -> str:
        """
        Formats article content for Hugo static site generator with extended archetype frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        category = metadata.get("category", "")
        date = metadata.get("publish_date", "")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        tags_yaml = json.dumps(tags)
        cats_yaml = json.dumps([category] if category else [])

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'date: {date}' if date else 'date: 2026-10-01',
            f'slug: "{slug}"',
            f'draft: {"true" if is_draft else "false"}',
            f'description: "{desc}"',
            f'categories: {cats_yaml}',
            f'tags: {tags_yaml}',
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_course_json_ld(course_data: Dict[str, Any]) -> str:
        """
        Generates schema.org Course structured data JSON-LD script for academic courses.
        """
        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": course_data.get("name", ""),
            "description": course_data.get("description", ""),
            "courseCode": course_data.get("course_code", ""),
            "provider": {
                "@type": "CollegeOrUniversity",
                "name": "Telkom University Purwokerto",
                "sameAs": "https://bif-pwt.telkomuniversity.ac.id"
            }
        }
        if course_data.get("credits"):
            schema["numberOfCredits"] = course_data["credits"]
        if course_data.get("prerequisites"):
            schema["coursePrerequisites"] = course_data["prerequisites"]
        if course_data.get("url"):
            schema["url"] = course_data["url"]

        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n</script>'

    @staticmethod
    def to_mdx(metadata: Dict[str, Any], html_content: str, framework: str = "astro") -> str:
        """
        Exports article to MDX format tailored for modern static documentation
        and content frameworks (Astro or Docusaurus).
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        date = metadata.get("publish_date", "2026-10-01")
        image = metadata.get("image_url", "")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        tags_json = json.dumps(tags)

        if framework.lower() == "docusaurus":
            frontmatter = [
                "---",
                f'title: "{title}"',
                f'description: "{desc}"',
                f'slug: /{slug}' if slug else "",
                f'authors: [editorial_team]',
                f'tags: {tags_json}',
                f'date: {date}',
                "---",
            ]
        else:
            frontmatter = [
                "---",
                f'title: "{title}"',
                f'description: "{desc}"',
                f'pubDate: {date}',
                f'heroImage: "{image}"' if image else "",
                f'tags: {tags_json}',
                "---",
            ]

        clean_fm = [line for line in frontmatter if line]
        return "\n".join(clean_fm) + "\n\n" + html_content.strip()

    @staticmethod
    def generate_enhanced_social_meta(
        metadata: Dict[str, Any],
        image_dimensions: Optional[Tuple[int, int]] = (1200, 630),
        site_name: str = "S1 Teknik Informatika Telkom University Purwokerto"
    ) -> str:
        """
        Generates production-grade OpenGraph and Twitter Card metadata tags with image dimensions.
        """
        title = metadata.get("seo_title", metadata.get("topic", ""))
        desc = metadata.get("meta_description", "")
        slug = metadata.get("slug", "")
        canonical = f"https://bif-pwt.telkomuniversity.ac.id/{slug}/" if slug else "https://bif-pwt.telkomuniversity.ac.id"
        image = metadata.get("image_url", "https://bif-pwt.telkomuniversity.ac.id/wp-content/uploads/og-default.jpg")
        pub_date = metadata.get("publish_date", "")

        tags = [
            f'<meta property="og:locale" content="id_ID">',
            f'<meta property="og:type" content="article">',
            f'<meta property="og:site_name" content="{site_name}">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{desc}">',
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:image" content="{image}">',
        ]
        if image_dimensions:
            w, h = image_dimensions
            tags.append(f'<meta property="og:image:width" content="{w}">')
            tags.append(f'<meta property="og:image:height" content="{h}">')
        if pub_date:
            tags.append(f'<meta property="article:published_time" content="{pub_date}">')

        tags.extend([
            f'<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{desc}">',
            f'<meta name="twitter:image" content="{image}">',
        ])
        return "\n".join(tags)

    @staticmethod
    def generate_program_json_ld(
        program_name: str = "S1 Teknik Informatika",
        description: str = "Program Studi Sarjana Teknik Informatika Telkom University Purwokerto berfokus pada AI, Cloud Computing, dan Rekayasa Perangkat Lunak.",
        degree: str = "Sarjana Komputer (S.Kom.)",
        program_url: str = "https://bif-pwt.telkomuniversity.ac.id"
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/EducationalOccupationalProgram structured data for university degree programs.
        """
        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalProgram",
            "name": program_name,
            "description": description,
            "url": program_url,
            "timeToComplete": "P4Y",
            "educationalCredentialAwarded": degree,
            "provider": {
                "@type": "CollegeOrUniversity",
                "name": "Telkom University Purwokerto",
                "url": "https://bif-pwt.telkomuniversity.ac.id",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Purwokerto",
                    "addressRegion": "Jawa Tengah",
                    "addressCountry": "ID"
                }
            }
        }

    @staticmethod
    def to_nextjs_mdx(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Next.js Contentlayer/App Router compatible MDX with typed metadata export.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        date = metadata.get("publish_date", "")
        tags = metadata.get("tags", [])
        tags_json = json.dumps(tags) if isinstance(tags, list) else "[]"

        header = f"""export const metadata = {{
  title: "{title}",
  description: "{desc}",
  slug: "{slug}",
  date: "{date}",
  tags: {tags_json},
}};"""

        return header + "\n\n" + html_content.strip()











