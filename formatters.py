from typing import Dict, Any, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
