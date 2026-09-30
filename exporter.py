import json
from pathlib import Path
from typing import Dict, Any

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

