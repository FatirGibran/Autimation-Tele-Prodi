import time
from typing import Dict, Any, List, Optional, Tuple

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
except ImportError:
    class InlineKeyboardButton:
        def __init__(self, text: str, callback_data: Optional[str] = None, **kwargs):
            self.text = text
            self.callback_data = callback_data

    class InlineKeyboardMarkup:
        def __init__(self, inline_keyboard: List[List[Any]]):
            self.inline_keyboard = inline_keyboard


class CommandRateLimiter:
    """
    In-memory sliding cooldown rate limiter for Telegram bot users to prevent API flooding.
    """
    def __init__(self, default_cooldown: float = 3.0):
        self.default_cooldown = default_cooldown
        self._last_invocations: Dict[int, float] = {}

    def is_allowed(self, user_id: int, cooldown_seconds: Optional[float] = None) -> Tuple[bool, float]:
        now = time.time()
        cd = cooldown_seconds if cooldown_seconds is not None else self.default_cooldown
        last_time = self._last_invocations.get(user_id, 0.0)
        elapsed = now - last_time

        if elapsed >= cd:
            self._last_invocations[user_id] = now
            return True, 0.0
        else:
            remaining = round(cd - elapsed, 1)
            return False, remaining

    def reset(self, user_id: Optional[int] = None) -> None:
        if user_id is not None:
            self._last_invocations.pop(user_id, None)
        else:
            self._last_invocations.clear()

class TelegramFormatter:
    @staticmethod
    def format_seo_report(metadata: Dict[str, Any], validation_result: Dict[str, Any]) -> str:
        icon = "🟢" if validation_result.get("is_all_green", False) else "🟡"
        score = validation_result.get("score", 100)

        lines = [
            f"### {icon} YOAST SEO METADATA (Score: {score}/100)\n",
            f"🎯 **Focus Keyphrase:** `{metadata.get('focus_keyphrase', '')}`",
            f"📌 **SEO Title:** {metadata.get('seo_title', '')}",
            f"🔗 **Slug:** `{metadata.get('slug', '')}`",
            f"📝 **Meta Description:** {metadata.get('meta_description', '')}\n",
            "**Audit Status:**"
        ]

        for check_name, check_data in validation_result.get("checks", {}).items():
            status_symbol = "✅" if check_data.get("passed", False) else "❌"
            label = check_name.replace("_", " ").title()
            val_info = f" ({check_data.get('value')})" if "value" in check_data else ""
            lines.append(f"{status_symbol} {label}{val_info}")

        if validation_result.get("warnings"):
            lines.append("\n⚠️ **Catatan Peringatan:**")
            for w in validation_result["warnings"]:
                lines.append(f"- {w}")

        return "\n".join(lines)

    @staticmethod
    def build_article_action_keyboard(slug: str, has_wp_configured: bool = False) -> InlineKeyboardMarkup:
        buttons: List[List[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton("📋 Copy Keyphrase", callback_data=f"copy_kw:{slug}"),
                InlineKeyboardButton("📋 Copy Meta Desc", callback_data=f"copy_meta:{slug}"),
            ]
        ]
        if has_wp_configured:
            buttons.append([
                InlineKeyboardButton("🚀 Publikasikan Draft ke WP", callback_data=f"wp_draft:{slug}")
            ])
        buttons.append([
            InlineKeyboardButton("🔍 Audit Ulang SEO", callback_data=f"re_audit:{slug}")
        ])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def format_stats_report(stats: Dict[str, Any]) -> str:
        lines = [
            "📊 **Ringkasan Statistik Editorial**\n",
            f"• 📚 Total Artikel: `{stats.get('total_articles', 0)}`",
            f"• 🚀 Terpublikasi / WP Draft: `{stats.get('published_count', 0)}`",
            f"• 🟢 Siap Terbit (Ready): `{stats.get('ready_count', 0)}`",
            f"• 🟡 Perlu Review: `{stats.get('needs_review_count', 0)}`",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_article_summary_card(article: Dict[str, Any]) -> str:
        lines = [
            f"📄 **Detail Artikel (ID: {article.get('id', 'N/A')})**\n",
            f"📌 **Judul:** {article.get('seo_title', article.get('topic', ''))}",
            f"🏷️ **Kategori:** {article.get('category', 'N/A')}",
            f"📅 **Tanggal:** {article.get('publish_date', 'N/A')}",
            f"🎯 **Keyphrase:** `{article.get('focus_keyphrase', '')}`",
            f"🔗 **Slug:** `{article.get('slug', '')}`",
            f"📊 **Status:** `{article.get('status', 'draft')}`",
        ]
        if article.get("wp_post_id"):
            lines.append(f"🌐 **WP Post ID:** `{article['wp_post_id']}`")
        return "\n".join(lines)

    @staticmethod
    def format_score_progress_bar(score: int, width: int = 10) -> str:
        """
        Renders a Unicode visual progress bar for SEO score indication.
        """
        clamped = max(0, min(100, score))
        filled = round((clamped / 100) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        rating = "Sempurna" if clamped >= 95 else ("Optimal" if clamped >= 80 else ("Perlu Perbaikan" if clamped >= 60 else "Kritis"))
        return f"[{bar}] {clamped}/100 ({rating})"

    @staticmethod
    def format_readability_badge(score: float, label: str = "") -> str:
        """
        Renders an Indonesian readability assessment badge for Telegram chat messages.
        """
        icon = "🟢" if score >= 60.0 else ("🟡" if score >= 40.0 else "🔴")
        desc = label or ("Keterbacaan Baik" if score >= 60.0 else "Perlu Penyederhanaan Kalimat")
        return f"{icon} **Skor Keterbacaan:** `{score:.1f}` — *{desc}*"

    @staticmethod
    def build_review_management_keyboard(article_id: int, slug: str = "") -> Dict[str, Any]:
        """
        Builds inline keyboard markup schema for Telegram bot review workflows.
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ Setujui & Terbitkan", "callback_data": f"approve:{article_id}"},
                    {"text": "✏️ Minta Revisi", "callback_data": f"revise:{article_id}"},
                ],
                [
                    {"text": "📊 Detail Analisis", "callback_data": f"analyze:{article_id}"},
                    {"text": "🗑️ Arsipkan", "callback_data": f"archive:{article_id}"},
                ],
            ]
        }

    @staticmethod
    def format_editorial_diff_preview(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> str:
        """
        Renders a compact Telegram markdown preview of editorial changes between two revisions.
        """
        lines = [
            f"🔄 **Perbandingan Revisi Editorial (ID: {new_data.get('id', old_data.get('id', 'N/A'))})**\n",
        ]

        old_title = old_data.get("seo_title", old_data.get("topic", ""))
        new_title = new_data.get("seo_title", new_data.get("topic", ""))
        if old_title != new_title:
            lines.append(f"📌 **Judul:**\n  ~~{old_title}~~\n  ➡️ `{new_title}`")
        else:
            lines.append(f"📌 **Judul:** `{new_title}` *(tetap)*")

        old_fk = old_data.get("focus_keyphrase", "")
        new_fk = new_data.get("focus_keyphrase", "")
        if old_fk != new_fk:
            lines.append(f"🎯 **Keyphrase:** ~~{old_fk}~~ ➡️ `{new_fk}`")

        old_st = old_data.get("status", "")
        new_st = new_data.get("status", "")
        if old_st != new_st:
            lines.append(f"📊 **Status:** `{old_st}` ➡️ `{new_st}`")

        old_wc = len(old_data.get("html_content", "").split())
        new_wc = len(new_data.get("html_content", "").split())
        diff_wc = new_wc - old_wc
        diff_sign = f"+{diff_wc}" if diff_wc > 0 else str(diff_wc)
        lines.append(f"📝 **Panjang Teks:** `{new_wc}` kata ({diff_sign} kata)")

        return "\n".join(lines)


