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
}};\n"""

        return header + "\n" + html_content.strip()

    @staticmethod
    def generate_research_project_json_ld(
        name: str,
        description: str,
        funder: str,
        award_amount: str,
        lead_investigator: str,
        project_url: str = "https://bif-pwt.telkomuniversity.ac.id"
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/ResearchProject and FundingAward structured JSON-LD.
        """
        return {
            "@context": "https://schema.org",
            "@type": "ResearchProject",
            "name": name,
            "description": description,
            "url": project_url,
            "funder": {
                "@type": "Organization",
                "name": funder
            },
            "funding": {
                "@type": "Grant",
                "name": f"Grant for {name}",
                "amount": award_amount,
                "funder": {
                    "@type": "Organization",
                    "name": funder
                }
            },
            "employee": {
                "@type": "Person",
                "name": lead_investigator,
                "jobTitle": "Principal Investigator"
            }
        }

    @staticmethod
    def to_nuxt_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Nuxt Content v2 / Gatsby compatible markdown with YAML frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        category = metadata.get("category", "")
        tags = metadata.get("tags", [])
        tags_yaml = "\n".join(f"  - {t}" for t in tags) if tags else "  - akademik"

        frontmatter = f"""---
title: "{title}"
description: "{desc}"
slug: "{slug}"
category: "{category}"
tags:
{tags_yaml}
navigation: true
---"""
        return frontmatter + "\n\n" + html_content.strip()

    @staticmethod
    def generate_academic_event_json_ld(
        event_name: str,
        description: str,
        start_time: str,
        end_time: str,
        location_name: str,
        speaker_name: str,
        event_url: str = "https://bif-pwt.telkomuniversity.ac.id"
    ) -> Dict[str, Any]:
        """
        Generates schema.org/Event (EducationEvent/Seminar) JSON-LD structured data.
        """
        return {
            "@context": "https://schema.org",
            "@type": "EducationEvent",
            "name": event_name,
            "description": description,
            "startDate": start_time,
            "endDate": end_time,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
                "@type": "Place",
                "name": location_name,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Purwokerto",
                    "addressRegion": "Jawa Tengah",
                    "addressCountry": "ID"
                }
            },
            "performer": {
                "@type": "Person",
                "name": speaker_name
            },
            "organizer": {
                "@type": "Organization",
                "name": "S1 Teknik Informatika Telkom University Purwokerto",
                "url": event_url
            }
        }

    @staticmethod
    def to_sveltekit_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to MDSveX / SvelteKit markdown format with structured metadata.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        date = metadata.get("publish_date", "2026-10-01")
        category = metadata.get("category", "")
        tags = metadata.get("tags", [])
        tags_json = json.dumps(tags if isinstance(tags, list) else [t.strip() for t in tags.split(",") if t.strip()])

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'date: "{date}"',
            f'slug: "{slug}"',
            f'category: "{category}"',
            f'tags: {tags_json}',
            "layout: article",
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_university_organization_json_ld(
        name: str = "Telkom University Purwokerto",
        url: str = "https://bif-pwt.telkomuniversity.ac.id",
        faculty_name: str = "Fakultas Informatika",
        accreditation: str = "Baik Sekali"
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/CollegeOrUniversity structured data for institutional knowledge graph.
        """
        return {
            "@context": "https://schema.org",
            "@type": "CollegeOrUniversity",
            "name": name,
            "url": url,
            "department": {
                "@type": "EducationalOrganization",
                "name": faculty_name
            },
            "hasCredential": {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "Akreditasi Institusi",
                "name": accreditation
            },
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Purwokerto",
                "addressRegion": "Jawa Tengah",
                "addressCountry": "ID"
            }
        }

    @staticmethod
    def to_eleventy_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Eleventy (11ty) static site generator markdown format with layout and permalink.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        date = metadata.get("publish_date", "2026-10-01")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_yaml = "\n".join(f"  - {t}" for t in tags) if tags else "  - post"

        frontmatter = [
            "---",
            "layout: layouts/post.njk",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'date: {date}',
            f'permalink: "/posts/{slug}/"' if slug else 'permalink: "/posts/"',
            "tags:",
            tags_yaml,
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_scholarly_article_json_ld(
        title: str,
        authors: List[str],
        abstract: str,
        date_published: str,
        doi_url: str,
        publisher: str = "Telkom University Purwokerto"
    ) -> Dict[str, Any]:
        """
        Generates a Schema.org ScholarlyArticle JSON-LD structured data payload.
        """
        author_entries = [
            {"@type": "Person", "name": a.strip()}
            for a in authors
            if a.strip()
        ]
        if not author_entries:
            author_entries = [{"@type": "Organization", "name": publisher}]

        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "headline": title.strip(),
            "name": title.strip(),
            "author": author_entries,
            "description": abstract.strip(),
            "datePublished": date_published.strip(),
            "publisher": {
                "@type": "Organization",
                "name": publisher
            }
        }
        if doi_url.strip():
            data["sameAs"] = doi_url.strip()
            data["url"] = doi_url.strip()

        return data

    @staticmethod
    def to_zola_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Zola static site generator markdown format using TOML frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        date = metadata.get("publish_date", "2026-10-01")
        category = metadata.get("category", "Akademik").replace('"', '\\"')
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        tags_toml = ", ".join(f'"{t}"' for t in tags)

        lines = [
            "+++",
            f'title = "{title}"',
            f'description = "{desc}"',
            f'date = {date}',
            f'slug = "{slug}"',
            "[taxonomies]",
            f'categories = ["{category}"]',
            f'tags = [{tags_toml}]',
            "+++",
            "",
            html_content.strip()
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_tech_article_json_ld(
        title: str,
        dependencies: List[str],
        proficiency_level: str,
        content: str,
        date_published: str,
        publisher: str = "Telkom University Purwokerto"
    ) -> Dict[str, Any]:
        """
        Generates schema.org TechArticle JSON-LD structured data for technical lab guides and engineering tutorials.
        """
        deps_clean = [d.strip() for d in dependencies if d.strip()]
        return {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": title.strip(),
            "dependencies": ", ".join(deps_clean) if deps_clean else "None",
            "proficiencyLevel": proficiency_level.strip(),
            "articleBody": content.strip(),
            "datePublished": date_published.strip(),
            "publisher": {
                "@type": "EducationalOrganization",
                "name": publisher.strip()
            }
        }

    @staticmethod
    def to_pelican_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Pelican static site generator Markdown format with colon-separated headers.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        date = metadata.get("publish_date", "2026-10-01").strip()
        category = metadata.get("category", "Akademik").strip()
        slug = metadata.get("slug", "").strip()
        summary = metadata.get("meta_description", "").strip()
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_str = ", ".join(tags)

        lines = [
            f"Title: {title}",
            f"Date: {date}",
            f"Category: {category}",
            f"Tags: {tags_str}",
            f"Slug: {slug}",
            f"Summary: {summary}",
            "",
            html_content.strip()
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_dataset_json_ld(
        dataset_name: str,
        description: str,
        creator_name: str,
        license_url: str,
        keywords: List[str],
        download_url: str = "",
        publisher_name: str = "Telkom University Purwokerto"
    ) -> Dict[str, Any]:
        """
        Generates schema.org Dataset JSON-LD structured data for academic lab datasets and research benchmarks.
        """
        kw_clean = [k.strip() for k in keywords if k.strip()]
        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": dataset_name.strip(),
            "description": description.strip(),
            "creator": {
                "@type": "Person",
                "name": creator_name.strip()
            },
            "license": license_url.strip(),
            "keywords": kw_clean,
            "publisher": {
                "@type": "EducationalOrganization",
                "name": publisher_name.strip()
            }
        }
        if download_url.strip():
            data["distribution"] = [
                {
                    "@type": "DataDownload",
                    "contentUrl": download_url.strip()
                }
            ]
        return data

    @staticmethod
    def to_docusaurus_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Docusaurus static site Markdown with standard frontmatter and sidebar configuration.
        """
        sidebar_label = metadata.get("sidebar_label", metadata.get("seo_title", metadata.get("topic", ""))).strip()
        doc_id = metadata.get("slug", "doc").strip()
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        desc = metadata.get("meta_description", "").strip()
        sidebar_pos = metadata.get("sidebar_position", 1)
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_yaml = ", ".join(f'"{t}"' for t in tags)

        lines = [
            "---",
            f"id: {doc_id}",
            f'title: "{title}"',
            f'sidebar_label: "{sidebar_label}"',
            f"sidebar_position: {sidebar_pos}",
            f'description: "{desc}"',
            f"tags: [{tags_yaml}]",
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_special_announcement_json_ld(
        title: str,
        text: str,
        date_posted: str,
        expires_date: str,
        category: str,
        publisher: str = "Telkom University Purwokerto"
    ) -> Dict[str, Any]:
        """
        Generates Schema.org SpecialAnnouncement JSON-LD for academic advisories and urgent campus alerts.
        """
        return {
            "@context": "https://schema.org",
            "@type": "SpecialAnnouncement",
            "name": title.strip(),
            "text": text.strip(),
            "datePosted": date_posted.strip(),
            "expires": expires_date.strip(),
            "category": category.strip(),
            "publisher": {
                "@type": "EducationalOrganization",
                "name": publisher.strip()
            }
        }

    @staticmethod
    def to_mkdocs_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to MkDocs static site Markdown with Material frontmatter, title, description, and tags.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        desc = metadata.get("meta_description", "").strip()
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        tags_yaml = ", ".join(f'"{t}"' for t in tags)

        lines = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f"tags: [{tags_yaml}]",
            "---",
            "",
            f"# {title}",
            "",
            html_content.strip()
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_credential_json_ld(
        credential_name: str,
        description: str,
        credential_category: str,
        recognized_by: str,
        educational_level: str
    ) -> Dict[str, Any]:
        """
        Generates Schema.org EducationalOccupationalCredential JSON-LD for degrees and professional certifications.
        """
        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalCredential",
            "name": credential_name.strip(),
            "description": description.strip(),
            "credentialCategory": credential_category.strip(),
            "educationalLevel": educational_level.strip(),
            "recognizedBy": {
                "@type": "EducationalOrganization",
                "name": recognized_by.strip()
            }
        }

    @staticmethod
    def to_starlight_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Astro Starlight static site documentation Markdown with sidebar order and badge.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        desc = metadata.get("meta_description", "").strip()
        sidebar_label = metadata.get("sidebar_label", title).strip()
        order = metadata.get("sidebar_order", metadata.get("sidebar_position", 1))

        lines = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            "sidebar:",
            f'  label: "{sidebar_label}"',
            f'  order: {order}',
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_academic_event_json_ld(
        event_name: str,
        description: str,
        start_date: str,
        end_date: str,
        location_name: str,
        core_rank: str,
        organizer: str,
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/Event structured JSON-LD for academic conferences with CORE rank metadata.
        """
        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": event_name.strip(),
            "description": description.strip(),
            "startDate": start_date.strip(),
            "endDate": end_date.strip(),
            "location": {
                "@type": "Place",
                "name": location_name.strip()
            },
            "organizer": {
                "@type": "Organization",
                "name": organizer.strip()
            },
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "CORE Rank",
                    "value": core_rank.strip().upper()
                }
            ]
        }
        if url:
            data["url"] = url.strip()
        return data

    @staticmethod
    def to_hexo_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Hexo static blog generator markdown with frontmatter tags and categories.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        date = metadata.get("publish_date", "").strip()
        tags = metadata.get("tags", [])
        category = metadata.get("category", "").strip()

        lines = [
            "---",
            f'title: "{title}"',
            f'date: {date}',
        ]
        if category:
            lines.append("categories:")
            lines.append(f'  - "{category}"')
        if tags and isinstance(tags, list):
            lines.append("tags:")
            for t in tags:
                lines.append(f'  - "{str(t).strip()}"')
        lines.append("---")
        lines.append("")
        lines.append(html_content.strip())
        return "\n".join(lines)

    @staticmethod
    def generate_government_grant_json_ld(
        grant_name: str,
        description: str,
        agency_name: str,
        recipient_name: str,
        amount: float,
        year: int,
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/GovernmentService structured JSON-LD for research grant funding awards.
        """
        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "GovernmentService",
            "name": grant_name.strip(),
            "description": description.strip(),
            "provider": {
                "@type": "GovernmentOrganization",
                "name": agency_name.strip()
            },
            "serviceAudience": {
                "@type": "Audience",
                "audienceType": "Academic Researchers"
            },
            "offers": {
                "@type": "Offer",
                "price": float(amount),
                "priceCurrency": "IDR",
                "recipient": {
                    "@type": "Person",
                    "name": recipient_name.strip()
                }
            },
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "Fiscal Year",
                    "value": str(year)
                }
            ]
        }
        if url:
            data["url"] = url.strip()
        return data

    @staticmethod
    def to_vitepress_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to VitePress static documentation markdown with structured frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        description = metadata.get("meta_description", "").strip()
        date = metadata.get("publish_date", "").strip()
        outline = metadata.get("outline", [2, 3])

        lines = [
            "---",
            f'title: "{title}"',
        ]
        if description:
            lines.append(f'description: "{description}"')
        if date:
            lines.append(f'date: "{date}"')
        lines.append(f'outline: {json.dumps(outline)}')
        lines.append("---")
        lines.append("")
        lines.append(html_content.strip())
        return "\n".join(lines)

    @staticmethod
    def generate_financial_assistance_json_ld(
        scholarship_name: str,
        sponsor_name: str,
        recipient_name: str,
        amount: float,
        semester: str,
        academic_year: str,
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates Schema.org/FinancialAssistance structured JSON-LD for educational scholarships and student financial aid.
        """
        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "FinancialAssistance",
            "name": scholarship_name.strip(),
            "provider": {
                "@type": "Organization",
                "name": sponsor_name.strip()
            },
            "recipient": {
                "@type": "Person",
                "name": recipient_name.strip()
            },
            "amount": {
                "@type": "MonetaryAmount",
                "currency": "IDR",
                "value": float(amount)
            },
            "description": f"Alokasi beasiswa pendidikan {scholarship_name.strip()} semester {semester.strip()} tahun akademik {academic_year.strip()}.",
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "Semester",
                    "value": semester.strip()
                },
                {
                    "@type": "PropertyValue",
                    "name": "Academic Year",
                    "value": academic_year.strip()
                }
            ]
        }
        if url:
            data["url"] = url.strip()
        return data

    @staticmethod
    def to_jekyll_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Jekyll static site generator markdown format with standard frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        date = metadata.get("publish_date", "").strip()
        layout = metadata.get("layout", "post").strip()
        category = metadata.get("category", "").strip()
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        lines = [
            "---",
            f"layout: {layout}",
            f'title: "{title}"',
        ]
        if date:
            lines.append(f"date: {date}")
        if category:
            lines.append(f'category: "{category}"')
        if tags and isinstance(tags, list):
            lines.append("tags:")
            for t in tags:
                lines.append(f'  - "{str(t).strip()}"')
        lines.append("---")
        lines.append("")
        lines.append(html_content.strip())
        return "\n".join(lines)

    @staticmethod
    def generate_thesis_json_ld(
        title: str,
        student_name: str,
        advisor_name: str,
        graduation_year: int,
        abstract: str,
        in_support_of: str = "Sarjana Teknik (S.T.)",
        university_name: str = "Telkom University Purwokerto",
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates Schema.org Thesis / ScholarlyArticle JSON-LD metadata for undergraduate dissertations.
        """
        data: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Thesis",
            "name": title.strip(),
            "headline": title.strip(),
            "inSupportOf": in_support_of.strip(),
            "author": {
                "@type": "Person",
                "name": student_name.strip()
            },
            "contributor": [
                {
                    "@type": "Person",
                    "name": advisor_name.strip(),
                    "roleName": "Thesis Advisor"
                }
            ],
            "sourceOrganization": {
                "@type": "CollegeOrUniversity",
                "name": university_name.strip()
            },
            "datePublished": f"{int(graduation_year)}",
            "description": abstract.strip()
        }
        if url:
            data["url"] = url.strip()
        return data

    @staticmethod
    def to_quartz_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Quartz 4.0 digital garden markdown format with frontmatter and wikilink tags.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        date = metadata.get("publish_date", "").strip()
        category = metadata.get("category", "").strip()
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        lines = [
            "---",
            f'title: "{title}"',
        ]
        if date:
            lines.append(f"date: {date}")
        if tags and isinstance(tags, list):
            lines.append("tags:")
            for t in tags:
                lines.append(f'  - "{str(t).strip()}"')
        if category:
            lines.append(f'description: "{category} note"')
        lines.append("---")
        lines.append("")
        lines.append(html_content.strip())
        return "\n".join(lines)

    @staticmethod
    def generate_educational_credential_json_ld(
        credential_name: str,
        recipient_name: str,
        issuer_name: str,
        valid_from: str,
        credential_category: str = "Certificate",
        cert_id: str = "",
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates schema.org EducationalOccupationalCredential structured data (JSON-LD)
        for academic certifications, fast-track credentials, and laboratory training compliance.
        """
        payload: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalCredential",
            "name": credential_name.strip(),
            "credentialCategory": credential_category.strip(),
            "recognizedBy": {
                "@type": "EducationalOrganization",
                "name": issuer_name.strip()
            },
            "validFrom": valid_from.strip(),
            "about": {
                "@type": "Person",
                "name": recipient_name.strip()
            }
        }
        if cert_id:
            payload["identifier"] = cert_id.strip()
        if url:
            payload["url"] = url.strip()
        return payload

    @staticmethod
    def to_astro_starlight_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Astro Starlight documentation markdown format with sidebar order and badge frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).strip()
        description = metadata.get("meta_description", "").strip()
        category = metadata.get("category", "").strip()
        sidebar_order = metadata.get("sidebar_order", 1)

        lines = [
            "---",
            f'title: "{title}"',
        ]
        if description:
            lines.append(f'description: "{description}"')
        lines.append("sidebar:")
        lines.append(f"  order: {int(sidebar_order)}")
        if category:
            lines.append(f'  badge: "{category}"')
        lines.append("---")
        lines.append("")
        lines.append(html_content.strip())
        return "\n".join(lines)

    @staticmethod
    def generate_community_action_project_json_ld(
        project_title: str,
        description: str,
        leader_name: str,
        location: str,
        funder_name: str = "Telkom University Purwokerto",
        fiscal_year: int = 2026,
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates schema.org Project & CommunityAction JSON-LD metadata for university community service (PKM).
        """
        payload: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Project",
            "name": project_title.strip(),
            "description": description.strip(),
            "founder": {
                "@type": "Person",
                "name": leader_name.strip()
            },
            "locationCreated": {
                "@type": "Place",
                "name": location.strip()
            },
            "funder": {
                "@type": "Organization",
                "name": funder_name.strip()
            },
            "temporalCoverage": str(fiscal_year)
        }
        if url:
            payload["url"] = url.strip()
        return payload

    @staticmethod
    def to_docusaurus_v3_tabs_markdown(
        metadata: Dict[str, Any],
        html_content: str,
        tabs: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Exports content formatted for Docusaurus v3 MDX with tabbed code blocks or content sections.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "")
        sidebar_position = metadata.get("sidebar_position", 1)

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
        ]
        if slug:
            frontmatter.append(f'slug: /{slug.lstrip("/")}')
        frontmatter.append(f'sidebar_position: {int(sidebar_position)}')
        frontmatter.append("---")

        output = ["\n".join(frontmatter), ""]
        if tabs:
            output.append("import Tabs from '@theme/Tabs';")
            output.append("import TabItem from '@theme/TabItem';")
            output.append("")

        output.append(html_content.strip())

        if tabs:
            output.append("")
            output.append("<Tabs>")
            for tab in tabs:
                label = tab.get("label", "Tab")
                val = tab.get("value", label.lower().replace(" ", "_"))
                content = tab.get("content", "")
                output.append(f'  <TabItem value="{val}" label="{label}">')
                output.append(f'    {content.strip()}')
                output.append("  </TabItem>")
            output.append("</Tabs>")

        return "\n".join(output)

    @staticmethod
    def generate_educational_organization_json_ld(
        name: str,
        alternate_name: str,
        url: str,
        logo_url: str,
        description: str,
        address: Dict[str, str],
        accreditation: str = "Unggul (LAM INFOKOM)"
    ) -> Dict[str, Any]:
        """
        Generates schema.org EducationalOrganization JSON-LD metadata for university department/program.
        """
        payload: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "EducationalOrganization",
            "name": name.strip(),
            "alternateName": alternate_name.strip(),
            "url": url.strip(),
            "logo": logo_url.strip(),
            "description": description.strip(),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address.get("street", ""),
                "addressLocality": address.get("locality", "Purwokerto"),
                "addressRegion": address.get("region", "Jawa Tengah"),
                "postalCode": address.get("postal_code", "53147"),
                "addressCountry": address.get("country", "ID")
            }
        }
        if accreditation:
            payload["hasCredential"] = {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "Program Accreditation",
                "name": accreditation.strip()
            }
        return payload

    @staticmethod
    def to_nextjs_contentlayer_mdx(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Next.js Contentlayer MDX format with typed date, tags, and summary frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        date = metadata.get("publish_date", "2026-10-21")
        category = metadata.get("category", "Umum").replace('"', '\\"')
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'date: "{date}"',
            f'description: "{desc}"',
            f'category: "{category}"',
            f'tags: {json.dumps(tags)}',
            "published: true",
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_startup_incubation_project_json_ld(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates Schema.org Project and Organization JSON-LD metadata for university-incubated startups.
        """
        name = metadata.get("startup_name", "Startup Inovasi").strip()
        founder = metadata.get("founder", "Mahasiswa").strip()
        sector = metadata.get("sector", "Teknologi Informasi & Komunikasi").strip()
        url = metadata.get("url", "https://bif-pwt.telkomuniversity.ac.id/startup").strip()
        desc = metadata.get("description", f"Startup inkubasi prodi: {name}").strip()

        return {
            "@context": "https://schema.org",
            "@type": "Project",
            "name": name,
            "description": desc,
            "url": url,
            "founder": {
                "@type": "Person",
                "name": founder
            },
            "category": sector,
            "funder": {
                "@type": "EducationalOrganization",
                "name": "Program Wirausaha Merdeka Telkom University Purwokerto"
            }
        }

    @staticmethod
    def to_remix_route_mdx(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports article to Remix / React Router v7 MDX format with route meta headers and breadcrumbs.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        slug = metadata.get("slug", "").replace('"', '\\"')
        date = metadata.get("publish_date", "2026-10-21")

        frontmatter = [
            "---",
            "meta:",
            f'  - title: "{title}"',
            f'  - name: "description"',
            f'    content: "{desc}"',
            f'  - property: "og:title"',
            f'    content: "{title}"',
            f'  - property: "og:description"',
            f'    content: "{desc}"',
            "handle:",
            f'  breadcrumb: "{title}"',
            f'  slug: "{slug}"',
            f'  publishDate: "{date}"',
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_academic_exchange_program_json_ld(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates Schema.org EducationalOccupationalProgram JSON-LD metadata
        for international student exchange programs (e.g., IISMA MBKM).
        """
        prog_name = metadata.get("program_name", "Indonesian International Student Mobility Awards (IISMA)").strip()
        desc = metadata.get("description", "Program mobilitas dan pertukaran mahasiswa sarjana luar negeri.").strip()
        host = metadata.get("host_university", "Global Partner University").strip()
        country = metadata.get("country", "International").strip()
        category = metadata.get("category", "S1 Teknik Telekomunikasi").strip()
        url = metadata.get("url", "https://iisma.kemdikbud.go.id").strip()

        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalProgram",
            "name": prog_name,
            "description": desc,
            "url": url,
            "educationalProgramMode": "Full-time overseas exchange",
            "occupationalCategory": category,
            "timeToComplete": "P1S",
            "provider": {
                "@type": "EducationalOrganization",
                "name": "Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi"
            },
            "educationalCredentialAwarded": "Rekognisi 20 SKS MBKM",
            "hasCourse": {
                "@type": "Course",
                "name": "Studi Akademik Internasional",
                "provider": {
                    "@type": "CollegeOrUniversity",
                    "name": host,
                    "address": {
                        "@type": "PostalAddress",
                        "addressCountry": country
                    }
                }
            }
        }

    @staticmethod
    def to_vitepress_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports editorial content to VitePress documentation Markdown format
        with outline control, lastUpdated timestamps, and clean YAML frontmatter.
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        date = metadata.get("publish_date", "2026-10-23")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            "outline: [2, 3]",
            f'lastUpdated: "{date}"',
            f'tags: {json.dumps(tags)}',
            "editLink: false",
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_humanitarian_action_json_ld(
        action_title: str,
        description: str,
        student_name: str,
        partner_org: str,
        location: str,
        start_date: str = "2026-08-01",
        url: str = ""
    ) -> Dict[str, Any]:
        """
        Generates Schema.org Project / VolunteerService JSON-LD for MBKM Proyek Kemanusiaan disaster relief.
        """
        payload: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Project",
            "name": action_title.strip(),
            "description": description.strip(),
            "startDate": start_date.strip(),
            "location": {
                "@type": "Place",
                "name": location.strip()
            },
            "founder": {
                "@type": "Person",
                "name": student_name.strip()
            },
            "funder": {
                "@type": "Organization",
                "name": partner_org.strip()
            }
        }
        if url:
            payload["url"] = url.strip()
        return payload

    @staticmethod
    def to_hugo_academic_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports editorial content to Hugo Academic / Wowchemy / Hugo Blox Markdown format
        with YAML frontmatter (title, summary, authors, tags, categories, math, highlight).
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        date = metadata.get("publish_date", "2026-10-24")
        category = metadata.get("category", "General")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'summary: "{desc}"',
            f'date: "{date}"',
            f'categories: ["{category}"]',
            f'tags: {json.dumps(tags)}',
            "authors: [\"admin\"]",
            "featured: false",
            "draft: false",
            "math: true",
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)

    @staticmethod
    def generate_faq_page_json_ld(faq_items: List[Dict[str, str]], title: str = "") -> Dict[str, Any]:
        """
        Generates schema.org compliant FAQPage JSON-LD structured data dictionary.
        """
        entities = []
        for item in faq_items:
            q = item.get("question", item.get("q", "")).strip()
            a = item.get("answer", item.get("a", "")).strip()
            if q and a:
                entities.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                })

        doc: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": entities
        }
        if title.strip():
            doc["name"] = title.strip()
        return doc

    @staticmethod
    def to_mkdocs_material_markdown(metadata: Dict[str, Any], html_content: str) -> str:
        """
        Exports editorial content to MkDocs Material Markdown documentation format
        with YAML frontmatter (title, description, icon, status, tags).
        """
        title = metadata.get("seo_title", metadata.get("topic", "")).replace('"', '\\"')
        desc = metadata.get("meta_description", "").replace('"', '\\"')
        icon = metadata.get("icon", "material/book-open-page-variant")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        frontmatter = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f'icon: "{icon}"',
            f'tags: {json.dumps(tags)}',
            "---",
            "",
            html_content.strip()
        ]
        return "\n".join(frontmatter)



































