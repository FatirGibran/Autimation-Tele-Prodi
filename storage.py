import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

class StorageManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    category TEXT NOT NULL,
                    publish_date TEXT NOT NULL,
                    image_url TEXT,
                    focus_keyphrase TEXT NOT NULL,
                    seo_title TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    meta_description TEXT NOT NULL,
                    html_content TEXT,
                    status TEXT DEFAULT 'draft',
                    wp_post_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_keyphrase ON articles(focus_keyphrase);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_slug ON articles(slug);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (article_id, tag),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tag ON article_tags(tag);")

    def is_keyphrase_used(self, keyphrase: str) -> bool:
        normalized = keyphrase.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(1) FROM articles WHERE LOWER(TRIM(focus_keyphrase)) = ?",
                (normalized,)
            )
            count = cursor.fetchone()[0]
            return count > 0

    def is_slug_used(self, slug: str) -> bool:
        normalized = slug.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(1) FROM articles WHERE LOWER(TRIM(slug)) = ?",
                (normalized,)
            )
            count = cursor.fetchone()[0]
            return count > 0

    def save_article(self, data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO articles (
                    topic, category, publish_date, image_url, focus_keyphrase,
                    seo_title, slug, meta_description, html_content, status, wp_post_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["topic"],
                data["category"],
                data["publish_date"],
                data.get("image_url", ""),
                data["focus_keyphrase"],
                data["seo_title"],
                data["slug"],
                data["meta_description"],
                data.get("html_content", ""),
                data.get("status", "draft"),
                data.get("wp_post_id")
            ))
            return cursor.lastrowid

    def list_articles(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM articles ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_wp_post_id(self, article_id: int, wp_post_id: int, status: str = "published") -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE articles SET wp_post_id = ?, status = ? WHERE id = ?",
                (wp_post_id, status, article_id)
            )

    def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM articles WHERE slug = ?", (slug.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_articles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        pattern = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE LOWER(topic) LIKE ?
                   OR LOWER(focus_keyphrase) LIKE ?
                   OR LOWER(seo_title) LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (pattern, pattern, pattern, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(1) FROM articles").fetchone()[0]
            published = conn.execute("SELECT COUNT(1) FROM articles WHERE status IN ('published', 'draft_in_wp')").fetchone()[0]
            ready = conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'ready'").fetchone()[0]
            needs_review = conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'needs_review'").fetchone()[0]
            return {
                "total_articles": total,
                "published_count": published,
                "ready_count": ready,
                "needs_review_count": needs_review,
            }

    def add_tags(self, article_id: int, tags: List[str]) -> None:
        with self._get_connection() as conn:
            for tag in tags:
                normalized = tag.strip().lower()
                if normalized:
                    conn.execute(
                        "INSERT OR IGNORE INTO article_tags (article_id, tag) VALUES (?, ?)",
                        (article_id, normalized)
                    )

    def get_article_tags(self, article_id: int) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT tag FROM article_tags WHERE article_id = ? ORDER BY tag ASC",
                (article_id,)
            )
            return [row["tag"] for row in cursor.fetchall()]

    def get_articles_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        normalized = tag.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT a.* FROM articles a
                JOIN article_tags t ON a.id = t.article_id
                WHERE t.tag = ?
                ORDER BY a.id DESC LIMIT ?
                """,
                (normalized, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

