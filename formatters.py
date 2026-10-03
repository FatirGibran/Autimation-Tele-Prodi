from typing import Dict, Any, List, Optional

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
