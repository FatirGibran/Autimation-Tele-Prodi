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
