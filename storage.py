import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(article_id, meta_key),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_article ON article_meta(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    export_type TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_exports_article ON article_exports(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL UNIQUE,
                    scheduled_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sched_time ON article_schedules(scheduled_at);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_engagement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL UNIQUE,
                    view_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_eng_article ON article_engagement(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    parent_id INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES article_categories(id) ON DELETE SET NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_parent ON article_categories(parent_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_locks (
                    article_id INTEGER PRIMARY KEY,
                    locked_by TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    user_identifier TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(article_id, user_identifier),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bm_user ON article_bookmarks(user_identifier);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_reading_metrics (
                    article_id INTEGER PRIMARY KEY,
                    word_count INTEGER NOT NULL,
                    reading_time_min INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'all',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, channel, category)
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_category ON editorial_subscribers(category);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_view_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    referrer TEXT,
                    user_agent_hash TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_view_article ON article_view_logs(article_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_view_time ON article_view_logs(viewed_at);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    assignee TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_assignee ON editorial_tasks(assignee);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON editorial_tasks(status);")




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

    def set_article_meta(self, article_id: int, key: str, value: str) -> None:
        """
        Stores or updates arbitrary key-value metadata for an article.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_meta (article_id, meta_key, meta_value)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id, meta_key) DO UPDATE SET meta_value = excluded.meta_value;
            """, (article_id, key.strip(), value.strip()))

    def get_article_meta(self, article_id: int, key: Optional[str] = None) -> Any:
        """
        Retrieves custom metadata for an article (single key string value, or dict of all keys).
        """
        with self._get_connection() as conn:
            if key:
                cursor = conn.execute(
                    "SELECT meta_value FROM article_meta WHERE article_id = ? AND meta_key = ?",
                    (article_id, key.strip())
                )
                row = cursor.fetchone()
                return row["meta_value"] if row else None
            else:
                cursor = conn.execute(
                    "SELECT meta_key, meta_value FROM article_meta WHERE article_id = ?",
                    (article_id,)
                )
                return {row["meta_key"]: row["meta_value"] for row in cursor.fetchall()}

    def delete_article_meta(self, article_id: int, key: str) -> bool:
        """
        Deletes a specific metadata key for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM article_meta WHERE article_id = ? AND meta_key = ?",
                (article_id, key.strip())
            )
            return cursor.rowcount > 0

    def log_export_event(self, article_id: int, export_type: str, destination_path: str) -> int:
        """
        Records an export audit event for tracking generated deliverables.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_exports (article_id, export_type, destination_path)
                VALUES (?, ?, ?)
            """, (article_id, export_type.strip(), destination_path.strip()))
            return cursor.lastrowid

    def get_export_history(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Fetches all recorded export events for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_exports WHERE article_id = ? ORDER BY id DESC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def enable_wal_mode(self) -> str:
        """
        Enables SQLite Write-Ahead Logging (WAL) mode for high-concurrency access.
        Returns the active journal mode string.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA journal_mode=WAL;")
            row = cursor.fetchone()
            return row[0].upper() if row else "UNKNOWN"

    def list_categories(self) -> List[Dict[str, Any]]:
        """
        Retrieves distinct categories across active articles with counts.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(1) as article_count
                FROM articles
                WHERE is_deleted = 0
                GROUP BY category
                ORDER BY article_count DESC, category ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_articles_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves non-deleted articles filtered by a specific category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM articles
                WHERE LOWER(TRIM(category)) = LOWER(TRIM(?)) AND is_deleted = 0
                ORDER BY id DESC
                LIMIT ?
            """, (category, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_editorial_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Aggregates editorial analytics and publishing velocity within the specified rolling window.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(1) as cnt
                FROM articles
                WHERE is_deleted = 0
                  AND created_at >= datetime('now', ?)
                GROUP BY status
            """, (f"-{days} days",))
            status_counts = {row["status"]: row["cnt"] for row in cursor.fetchall()}

            cursor = conn.execute("""
                SELECT COUNT(1) as total, COUNT(DISTINCT category) as categories_active
                FROM articles
                WHERE is_deleted = 0
                  AND created_at >= datetime('now', ?)
            """, (f"-{days} days",))
            meta_row = cursor.fetchone()
            total = meta_row["total"] if meta_row else 0
            cat_count = meta_row["categories_active"] if meta_row else 0

            published = status_counts.get("published", 0)
            velocity_per_day = round(published / max(1, days), 2)

            return {
                "window_days": days,
                "total_articles": total,
                "status_breakdown": status_counts,
                "published_count": published,
                "active_categories": cat_count,
                "publishing_velocity_per_day": velocity_per_day,
            }

    def prune_revisions(self, retention_days: int = 30, keep_minimum: int = 2) -> int:
        """
        Prunes historical revisions older than retention_days while retaining
        at least keep_minimum recent revisions per article.
        If retention_days is 0 or negative, prunes all revisions exceeding keep_minimum.
        Returns the number of deleted revisions.
        """
        with self._get_connection() as conn:
            if retention_days > 0:
                time_filter = "AND created_at < datetime('now', ?)"
                params = (keep_minimum, f"-{retention_days} days")
            else:
                time_filter = ""
                params = (keep_minimum,)

            cursor = conn.execute(f"""
                DELETE FROM article_revisions
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (PARTITION BY article_id ORDER BY revision_num DESC) as rn
                        FROM article_revisions
                    ) WHERE rn <= ?
                )
                {time_filter}
            """, params)
            return cursor.rowcount

    def schedule_publication(self, article_id: int, scheduled_at: str) -> int:
        """
        Schedules an article for automated publishing at a specific ISO timestamp.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_schedules (article_id, scheduled_at, status)
                VALUES (?, ?, 'pending')
                ON CONFLICT(article_id) DO UPDATE SET
                    scheduled_at = excluded.scheduled_at,
                    status = 'pending';
            """, (article_id, scheduled_at.strip()))
            return cursor.lastrowid

    def get_pending_schedules(self, before_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves articles queued for scheduled publication, optionally filtered up to before_time.
        """
        with self._get_connection() as conn:
            if before_time:
                cursor = conn.execute("""
                    SELECT s.*, a.seo_title, a.slug, a.category, a.status as article_status
                    FROM article_schedules s
                    JOIN articles a ON s.article_id = a.id
                    WHERE s.status = 'pending' AND s.scheduled_at <= ? AND a.is_deleted = 0
                    ORDER BY s.scheduled_at ASC;
                """, (before_time.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT s.*, a.seo_title, a.slug, a.category, a.status as article_status
                    FROM article_schedules s
                    JOIN articles a ON s.article_id = a.id
                    WHERE s.status = 'pending' AND a.is_deleted = 0
                    ORDER BY s.scheduled_at ASC;
                """)
            return [dict(row) for row in cursor.fetchall()]

    def cancel_schedule(self, article_id: int) -> bool:
        """
        Cancels an active scheduled publication entry.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE article_schedules SET status = 'cancelled' WHERE article_id = ? AND status = 'pending';",
                (article_id,)
            )
            return cursor.rowcount > 0

    def export_database_dump(self) -> Dict[str, Any]:
        """
        Exports all articles, tags, revisions, metadata, and schedules into a serializable dump dict.
        """
        with self._get_connection() as conn:
            articles = [dict(r) for r in conn.execute("SELECT * FROM articles;").fetchall()]
            tags = [dict(r) for r in conn.execute("SELECT * FROM article_tags;").fetchall()]
            meta = [dict(r) for r in conn.execute("SELECT * FROM article_meta;").fetchall()]
            revisions = [dict(r) for r in conn.execute("SELECT * FROM article_revisions;").fetchall()]
            schedules = [dict(r) for r in conn.execute("SELECT * FROM article_schedules;").fetchall()]

            return {
                "schema_version": "2.3.0",
                "dump_created_at": datetime.utcnow().isoformat(),
                "articles": articles,
                "article_tags": tags,
                "article_meta": meta,
                "article_revisions": revisions,
                "article_schedules": schedules,
            }

    def import_database_dump(self, dump_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Imports articles and tags from a dump dictionary into the database,
        skipping existing records that share the same slug.
        Returns counts of imported items.
        """
        imported_articles = 0
        imported_tags = 0
        with self._get_connection() as conn:
            for art in dump_data.get("articles", []):
                slug = art.get("slug", "").strip()
                if not slug:
                    continue
                existing = conn.execute("SELECT id FROM articles WHERE slug = ?", (slug,)).fetchone()
                if existing:
                    continue

                cursor = conn.execute("""
                    INSERT INTO articles (
                        topic, category, publish_date, image_url, focus_keyphrase,
                        seo_title, slug, meta_description, html_content, status, wp_post_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    art.get("topic", "N/A"),
                    art.get("category", "Umum"),
                    art.get("publish_date", "2026-10-01"),
                    art.get("image_url", ""),
                    art.get("focus_keyphrase", ""),
                    art.get("seo_title", ""),
                    slug,
                    art.get("meta_description", ""),
                    art.get("html_content", ""),
                    art.get("status", "draft"),
                    art.get("wp_post_id")
                ))
                new_id = cursor.lastrowid
                imported_articles += 1

                old_id = art.get("id")
                for tag_row in dump_data.get("article_tags", []):
                    if tag_row.get("article_id") == old_id:
                        conn.execute(
                            "INSERT OR IGNORE INTO article_tags (article_id, tag) VALUES (?, ?)",
                            (new_id, tag_row.get("tag", "").strip())
                        )
                        imported_tags += 1

        return {
            "articles_imported": imported_articles,
            "tags_imported": imported_tags,
        }

    def record_engagement(self, article_id: int, views_increment: int = 1, shares_increment: int = 0) -> Dict[str, Any]:
        """
        Increments view and share counts for an article and returns updated stats.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_engagement (article_id, view_count, share_count, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(article_id) DO UPDATE SET
                    view_count = view_count + excluded.view_count,
                    share_count = share_count + excluded.share_count,
                    last_updated = CURRENT_TIMESTAMP;
            """, (article_id, max(0, views_increment), max(0, shares_increment)))

            cursor = conn.execute(
                "SELECT * FROM article_engagement WHERE article_id = ?;",
                (article_id,)
            )
            return dict(cursor.fetchone())

    def get_top_engaged_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves top performing articles ranked by total views and shares.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT e.*, a.seo_title, a.slug, a.category
                FROM article_engagement e
                JOIN articles a ON e.article_id = a.id
                WHERE a.is_deleted = 0
                ORDER BY e.view_count DESC, e.share_count DESC
                LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, slug: str, parent_id: Optional[int] = None, description: Optional[str] = None) -> int:
        """
        Adds a new hierarchical category for editorial taxonomy.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_categories (name, slug, parent_id, description)
                VALUES (?, ?, ?, ?);
            """, (name.strip(), slug.strip().lower(), parent_id, description))
            return cursor.lastrowid

    def get_category_tree(self) -> List[Dict[str, Any]]:
        """
        Retrieves all categories organized into a parent-children tree structure.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM article_categories ORDER BY parent_id ASC, name ASC;")
            all_cats = [dict(r) for r in cursor.fetchall()]

        by_id = {c["id"]: {**c, "children": []} for c in all_cats}
        roots = []
        for c in by_id.values():
            p_id = c.get("parent_id")
            if p_id and p_id in by_id:
                by_id[p_id]["children"].append(c)
            else:
                roots.append(c)
        return roots

    def get_category_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves category data by its URL slug.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM article_categories WHERE slug = ?;", (slug.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def acquire_article_lock(self, article_id: int, user_id: str, ttl_seconds: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Acquires or refreshes an editing lease lock for an article.
        Returns (True, None) on success, or (False, locked_by_user) if locked by someone else.
        """
        now = datetime.utcnow()
        now_iso = now.isoformat()
        expires_iso = (now + timedelta(seconds=ttl_seconds)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute("SELECT locked_by, expires_at FROM article_locks WHERE article_id = ?;", (article_id,))
            row = cursor.fetchone()

            if row:
                locked_by = row["locked_by"]
                expires_at = row["expires_at"]
                if locked_by != user_id and expires_at > now_iso:
                    return False, locked_by

            conn.execute("""
                INSERT INTO article_locks (article_id, locked_by, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id) DO UPDATE SET
                    locked_by = excluded.locked_by,
                    expires_at = excluded.expires_at,
                    created_at = CURRENT_TIMESTAMP;
            """, (article_id, user_id, expires_iso))
            return True, None

    def release_article_lock(self, article_id: int, user_id: str) -> bool:
        """
        Releases an active editing lease if held by the given user.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM article_locks WHERE article_id = ? AND locked_by = ?;",
                (article_id, user_id)
            )
            return cursor.rowcount > 0

    def get_article_lock_status(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves active lock status for an article if still valid.
        """
        now_iso = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_locks WHERE article_id = ? AND expires_at > ?;",
                (article_id, now_iso)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def batch_replace_content(
        self,
        target_str: str,
        replace_str: str,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a transactional search-and-replace across article drafts
        for seo_title, meta_description, and html_content.
        """
        if not target_str:
            return {"articles_updated": 0, "total_replacements": 0}

        updated_count = 0
        total_replacements = 0

        with self._get_connection() as conn:
            query = "SELECT id, seo_title, meta_description, html_content FROM articles WHERE is_deleted = 0"
            params = []
            if status_filter:
                query += " AND status = ?"
                params.append(status_filter)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                art_id = row["id"]
                title = row["seo_title"] or ""
                desc = row["meta_description"] or ""
                html = row["html_content"] or ""

                matches = title.count(target_str) + desc.count(target_str) + html.count(target_str)
                if matches > 0:
                    new_title = title.replace(target_str, replace_str)
                    new_desc = desc.replace(target_str, replace_str)
                    new_html = html.replace(target_str, replace_str)

                    conn.execute("""
                        UPDATE articles SET
                            seo_title = ?,
                            meta_description = ?,
                            html_content = ?
                        WHERE id = ?;
                    """, (new_title, new_desc, new_html, art_id))
                    updated_count += 1
                    total_replacements += matches

        return {
            "articles_updated": updated_count,
            "total_replacements": total_replacements
        }

    def get_category_analytics(self) -> List[Dict[str, Any]]:
        """
        Aggregates article count, total views, and average views grouped by category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    a.category,
                    COUNT(a.id) AS total_articles,
                    COALESCE(SUM(e.view_count), 0) AS total_views,
                    COALESCE(AVG(e.view_count), 0.0) AS avg_views
                FROM articles a
                LEFT JOIN article_engagement e ON a.id = e.article_id
                WHERE a.is_deleted = 0
                GROUP BY a.category
                ORDER BY total_views DESC, total_articles DESC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def add_bookmark(self, article_id: int, user_identifier: str, notes: Optional[str] = None) -> int:
        """
        Adds an article to the user's reading list or bookmarks.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_bookmarks (article_id, user_identifier, notes)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id, user_identifier) DO UPDATE SET notes = excluded.notes;
            """, (article_id, user_identifier.strip(), notes.strip() if notes else None))
            return cursor.lastrowid

    def list_bookmarks(self, user_identifier: str) -> List[Dict[str, Any]]:
        """
        Lists all bookmarked articles for a specific user.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT b.id AS bookmark_id, b.article_id, b.notes, b.created_at AS bookmarked_at,
                       a.seo_title, a.slug, a.category, a.status
                FROM article_bookmarks b
                JOIN articles a ON b.article_id = a.id
                WHERE b.user_identifier = ? AND a.is_deleted = 0
                ORDER BY b.created_at DESC;
            """, (user_identifier.strip(),))
            return [dict(row) for row in cursor.fetchall()]

    def remove_bookmark(self, article_id: int, user_identifier: str) -> bool:
        """
        Removes an article from the user's reading list.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM article_bookmarks
                WHERE article_id = ? AND user_identifier = ?;
            """, (article_id, user_identifier.strip()))
            return cursor.rowcount > 0

    def get_applied_migrations(self) -> List[str]:
        """
        Retrieves all applied migration versions ordered chronologically.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY applied_at ASC;")
            return [row["version"] for row in cursor.fetchall()]

    def record_migration(self, version: str) -> None:
        """
        Records an applied migration version into the tracking table.
        """
        with self._get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES (?);", (version.strip(),))

    def update_reading_metrics(self, article_id: int, word_count: int, reading_time_min: int) -> None:
        """
        Records or updates word count and calculated reading time metrics for an article.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_reading_metrics (article_id, word_count, reading_time_min, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(article_id) DO UPDATE SET
                    word_count = excluded.word_count,
                    reading_time_min = excluded.reading_time_min,
                    updated_at = CURRENT_TIMESTAMP;
            """, (article_id, word_count, reading_time_min))

    def get_reading_metrics(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves reading time and word count statistics for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT article_id, word_count, reading_time_min, updated_at
                FROM article_reading_metrics
                WHERE article_id = ?;
            """, (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def subscribe_user(self, user_id: str, channel: str, category: str = "all") -> bool:
        """
        Subscribes a user to editorial publication notifications for a given category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO editorial_subscribers (user_id, channel, category)
                VALUES (?, ?, ?);
            """, (user_id.strip(), channel.strip().lower(), category.strip().lower()))
            return cursor.rowcount > 0

    def get_subscribers(self, category: str = "all") -> List[Dict[str, Any]]:
        """
        Retrieves active subscribers matching the category or subscribed to 'all'.
        """
        cat = category.strip().lower()
        with self._get_connection() as conn:
            if cat == "all":
                cursor = conn.execute("""
                    SELECT id, user_id, channel, category, created_at
                    FROM editorial_subscribers;
                """)
            else:
                cursor = conn.execute("""
                    SELECT id, user_id, channel, category, created_at
                    FROM editorial_subscribers
                    WHERE category = ? OR category = 'all';
                """, (cat,))
            return [dict(row) for row in cursor.fetchall()]

    def unsubscribe_user(self, user_id: str, category: str = "all") -> bool:
        """
        Unsubscribes a user from notifications for a specific category or all categories.
        """
        cat = category.strip().lower()
        with self._get_connection() as conn:
            if cat == "all":
                cursor = conn.execute("""
                    DELETE FROM editorial_subscribers
                    WHERE user_id = ?;
                """, (user_id.strip(),))
            else:
                cursor = conn.execute("""
                    DELETE FROM editorial_subscribers
                    WHERE user_id = ? AND category = ?;
                """, (user_id.strip(), cat))
            return cursor.rowcount > 0

    def compare_revisions(self, article_id: int, rev_a: int, rev_b: int) -> Dict[str, Any]:
        """
        Compares two stored revisions of an article, computing character and word count deltas.
        """
        with self._get_connection() as conn:
            cur_a = conn.execute(
                "SELECT revision_num, html_content, meta_description, created_at FROM article_revisions WHERE article_id = ? AND revision_num = ?",
                (article_id, rev_a)
            )
            row_a = cur_a.fetchone()
            cur_b = conn.execute(
                "SELECT revision_num, html_content, meta_description, created_at FROM article_revisions WHERE article_id = ? AND revision_num = ?",
                (article_id, rev_b)
            )
            row_b = cur_b.fetchone()

            if not row_a or not row_b:
                return {
                    "article_id": article_id,
                    "found": False,
                    "error": "One or both revisions not found"
                }

            content_a = row_a["html_content"] or ""
            content_b = row_b["html_content"] or ""
            words_a = len(content_a.split())
            words_b = len(content_b.split())
            chars_a = len(content_a)
            chars_b = len(content_b)

            return {
                "article_id": article_id,
                "found": True,
                "rev_a": {
                    "revision_num": rev_a,
                    "word_count": words_a,
                    "char_count": chars_a,
                    "meta_description": row_a["meta_description"],
                    "created_at": row_a["created_at"]
                },
                "rev_b": {
                    "revision_num": rev_b,
                    "word_count": words_b,
                    "char_count": chars_b,
                    "meta_description": row_b["meta_description"],
                    "created_at": row_b["created_at"]
                },
                "deltas": {
                    "word_diff": words_b - words_a,
                    "char_diff": chars_b - chars_a,
                    "meta_changed": row_a["meta_description"] != row_b["meta_description"]
                }
            }

    def record_article_view(self, article_id: int, referrer: str = "", user_agent_hash: str = "") -> int:
        """
        Records an individual timestamped article view event for analytics.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_view_logs (article_id, referrer, user_agent_hash)
                VALUES (?, ?, ?)
            """, (article_id, referrer.strip(), user_agent_hash.strip()))
            conn.execute("""
                INSERT INTO article_engagement (article_id, view_count, share_count)
                VALUES (?, 1, 0)
                ON CONFLICT(article_id) DO UPDATE SET
                    view_count = view_count + 1,
                    last_updated = CURRENT_TIMESTAMP;
            """, (article_id,))
            return cursor.lastrowid

    def get_article_views_by_date(self, article_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Returns time-series daily view count aggregates for the specified article over recent days.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT DATE(viewed_at) as view_date, COUNT(1) as views
                FROM article_view_logs
                WHERE article_id = ? AND viewed_at >= DATETIME('now', ? || ' days')
                GROUP BY DATE(viewed_at)
                ORDER BY view_date ASC;
            """, (article_id, f"-{days}"))
            return [{"date": row["view_date"], "views": row["views"]} for row in cursor.fetchall()]

    def create_editorial_task(self, article_id: int, assignee: str, task_type: str, due_date: str) -> int:
        """
        Creates an editorial review, proofreading, or fact-checking task assignment.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO editorial_tasks (article_id, assignee, task_type, due_date, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (article_id, assignee.strip(), task_type.strip(), due_date.strip()))
            return cursor.lastrowid

    def list_editorial_tasks(self, status: str = "pending") -> List[Dict[str, Any]]:
        """
        Lists editorial tasks optionally filtered by status ('pending', 'in_progress', 'completed', 'all').
        """
        with self._get_connection() as conn:
            if status.lower() == "all":
                cursor = conn.execute("""
                    SELECT id, article_id, assignee, task_type, due_date, status, created_at
                    FROM editorial_tasks
                    ORDER BY id DESC;
                """)
            else:
                cursor = conn.execute("""
                    SELECT id, article_id, assignee, task_type, due_date, status, created_at
                    FROM editorial_tasks
                    WHERE status = ?
                    ORDER BY id DESC;
                """, (status.strip().lower(),))
            return [dict(row) for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Updates the completion status of an editorial task.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE editorial_tasks
                SET status = ?
                WHERE id = ?;
            """, (status.strip().lower(), task_id))
            return cursor.rowcount > 0





















