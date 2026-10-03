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
                    is_deleted INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor = conn.execute("PRAGMA table_info(articles);")
            columns = [row["name"] for row in cursor.fetchall()]
            if "is_deleted" not in columns and len(columns) > 0:
                conn.execute("ALTER TABLE articles ADD COLUMN is_deleted INTEGER DEFAULT 0;")

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    old_status TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    note TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_article ON article_audit_logs(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    revision_num INTEGER NOT NULL,
                    html_content TEXT,
                    meta_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rev_article ON article_revisions(article_id);")



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

    def list_articles(self, limit: int = 50, include_deleted: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM articles" if include_deleted else "SELECT * FROM articles WHERE is_deleted = 0"
            cursor = conn.execute(f"{query} ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def soft_delete_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("UPDATE articles SET is_deleted = 1 WHERE id = ?", (article_id,))
            if cursor.rowcount > 0:
                conn.execute(
                    "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                    (article_id, "active", "trashed", "Soft-deleted to trash")
                )
                return True
            return False

    def restore_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("UPDATE articles SET is_deleted = 0 WHERE id = ?", (article_id,))
            if cursor.rowcount > 0:
                conn.execute(
                    "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                    (article_id, "trashed", "restored", "Restored from trash")
                )
                return True
            return False

    def list_trash(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM articles WHERE is_deleted = 1 ORDER BY id DESC LIMIT ?",
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

    def update_status(self, article_id: int, new_status: str, note: str = "") -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT status FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if not row:
                return False
            old_status = row["status"]
            conn.execute("UPDATE articles SET status = ? WHERE id = ?", (new_status, article_id))
            conn.execute(
                "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                (article_id, old_status, new_status, note)
            )
            return True

    def get_audit_logs(self, article_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_audit_logs WHERE article_id = ? ORDER BY id ASC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def bulk_update_status(self, article_ids: List[int], status: str) -> int:
        if not article_ids:
            return 0
        placeholders = ",".join("?" for _ in article_ids)
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE articles SET status = ? WHERE id IN ({placeholders})",
                [status] + article_ids
            )
            return cursor.rowcount

    def filter_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE publish_date >= ? AND publish_date <= ?
                ORDER BY publish_date DESC, id DESC
                """,
                (start_date, end_date)
            )
            return [dict(row) for row in cursor.fetchall()]

    def search_articles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Performs multi-column keyword search with matching context highlighting.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            return []
        pattern = f"%{cleaned_query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE topic LIKE ? OR focus_keyphrase LIKE ? OR meta_description LIKE ? OR html_content LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (pattern, pattern, pattern, pattern, limit)
            )
            rows = [dict(row) for row in cursor.fetchall()]

        for item in rows:
            desc = item.get("meta_description", "")
            item["matched_snippet"] = desc if cleaned_query.lower() in desc.lower() else item.get("topic", "")

        return rows

    def optimize_and_check_integrity(self) -> Dict[str, Any]:
        """
        Executes database integrity check and compacts SQLite database with VACUUM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA integrity_check;")
            integrity_result = cursor.fetchone()[0]
            is_ok = integrity_result == "ok"
            if is_ok:
                conn.execute("VACUUM;")
            return {
                "status": "ok" if is_ok else "corrupted",
                "integrity_check": integrity_result,
                "vacuumed": is_ok
            }

    def create_revision(self, article_id: int) -> Optional[int]:
        """
        Creates a timestamped snapshot revision of the current article content.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT html_content, meta_description FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if not row:
                return None
            rev_count_cur = conn.execute("SELECT COUNT(*) FROM article_revisions WHERE article_id = ?", (article_id,))
            next_rev = rev_count_cur.fetchone()[0] + 1
            rev_cur = conn.execute(
                "INSERT INTO article_revisions (article_id, revision_num, html_content, meta_description) VALUES (?, ?, ?, ?)",
                (article_id, next_rev, row["html_content"], row["meta_description"])
            )
            return rev_cur.lastrowid

    def get_revisions(self, article_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_revisions WHERE article_id = ? ORDER BY revision_num DESC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]






