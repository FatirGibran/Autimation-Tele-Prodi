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

    @staticmethod
    def format_scheduled_reminder_card(article: Dict[str, Any], publish_at_str: str) -> str:
        """
        Renders a scheduled publishing notification card for Telegram editorial channels.
        """
        title = article.get("seo_title", article.get("topic", "N/A"))
        category = article.get("category", "Umum")
        slug = article.get("slug", "")
        return (
            f"⏰ **Pengingat Jadwal Terbit Artikel**\n\n"
            f"📌 **Judul:** {title}\n"
            f"🏷️ **Kategori:** `{category}`\n"
            f"📅 **Waktu Rilis:** `{publish_at_str}`\n"
            f"🔗 **Slug:** `{slug}`\n\n"
            f"💡 *Artikel siap dipublikasikan ke WordPress sesuai antrean jadwal.*"
        )

    @staticmethod
    def format_bibtex_telegram_card(article: Dict[str, Any], cite_key: Optional[str] = None) -> str:
        """
        Renders a ready-to-copy BibTeX citation block formatted for Telegram editorial channels.
        """
        title = article.get("seo_title", article.get("topic", "N/A"))
        slug = article.get("slug", "article")
        year = article.get("publish_date", "2026")[:4] if article.get("publish_date") else "2026"
        key = cite_key or f"telkom_bif_{slug.replace('-', '_')}_{year}"
        url = f"https://bif-pwt.telkomuniversity.ac.id/{slug}/"

        bibtex_code = (
            f"@article{{{key},\n"
            f'  title = {{{title}}},\n'
            f'  author = {{Tim Editorial S1 Informatika Telkom University Purwokerto}},\n'
            f'  journal = {{Portal Publikasi Ilmiah S1 Informatika}},\n'
            f'  year = {{{year}}},\n'
            f'  url = {{{url}}}\n'
            f"}}"
        )

        return (
            f"📚 **Sitasi Akademik BibTeX**\n\n"
            f"```bibtex\n{bibtex_code}\n```\n"
            f"💡 *Gunakan sitasi di atas untuk rujukan riset dan tugas akhir mahasiswa.*"
        )

    @staticmethod
    def format_plagiarism_alert_card(
        title: str,
        similarity_percentage: float,
        matched_sources: List[Dict[str, Any]]
    ) -> str:
        """
        Renders a similarity/plagiarism audit alert card with threshold indicators.
        """
        if similarity_percentage < 15.0:
            status_badge = "🟢 **AMAN (SIMILARITY RENDAH)**"
            advice = "Draf artikel memenuhi batas orisinalitas institusi (< 15%)."
        elif similarity_percentage <= 25.0:
            status_badge = "🟡 **PERHATIAN (SIMILARITY SEDANG)**"
            advice = "Periksa kembali bagian kutipan dan lakukan parafrase pada kalimat terdeteksi."
        else:
            status_badge = "🔴 **DITOLAK (SIMILARITY TINGGI)**"
            advice = "Tingkat kesamaan melebihi ambang batas toleransi (> 25%). Wajib revisi total."

        source_lines = []
        for s in matched_sources[:4]:
            source_url = s.get("url", "Sumber Eksternal")
            overlap = s.get("percent", 0.0)
            source_lines.append(f"  • `{overlap}%` - {source_url}")

        sources_text = "\n".join(source_lines) if source_lines else "  • Tidak ada sumber signifikan yang cocok."

        return (
            f"🔍 **Laporan Audit Orisinalitas Konten**\n\n"
            f"📌 **Artikel:** {title}\n"
            f"📊 **Skor Kesamaan:** `{similarity_percentage}%`\n"
            f"🏷️ **Status:** {status_badge}\n\n"
            f"🌐 **Sumber Kecocokan Teratas:**\n{sources_text}\n\n"
            f"💡 *Saran:* {advice}"
        )

    @staticmethod
    def format_conference_call_card(
        conf_name: str,
        deadline_str: str,
        tracks: List[str],
        submission_url: str
    ) -> str:
        """
        Renders an academic conference call for papers (CFP) alert card for Telegram.
        """
        tracks_text = "\n".join(f"  • {t}" for t in tracks) if tracks else "  • Informatika & Ilmu Komputer"
        return (
            f"📢 **Call for Papers: {conf_name}**\n\n"
            f"📅 **Batas Pengumpulan (Deadline):** `{deadline_str}`\n\n"
            f"📑 **Bidang / Track Riset:**\n{tracks_text}\n\n"
            f"🔗 **Tautan Pengumpulan:** {submission_url}\n\n"
            f"💡 *Mahasiswa dan dosen dianjurkan untuk mengirimkan naskah publikasi.*"
        )

    @staticmethod
    def format_compact_seo_summary(report: Dict[str, Any], slug: str) -> str:
        """
        Renders a compact, high-signal SEO validation summary card for Telegram bots.
        """
        score = report.get("score", 0)
        grade = report.get("grade", "N/A")
        errors = report.get("errors", [])
        warnings = report.get("warnings", [])

        status_emoji = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
        error_count = len(errors)
        warning_count = len(warnings)

        return (
            f"🎯 **Ringkasan Audit SEO Yoast**\n\n"
            f"🔗 **Slug:** `{slug}`\n"
            f"{status_emoji} **Skor:** `{score}/100` ({grade})\n"
            f"⚠️ **Errors:** `{error_count}` | **Warnings:** `{warning_count}`\n\n"
            f"💡 *{'Semua parameter SEO optimal, siap rilis.' if error_count == 0 else 'Perlu perbaikan sebelum artikel diterbitkan.'}*"
        )

    @staticmethod
    def format_capstone_defense_card(
        candidate_name: str,
        thesis_title: str,
        room_or_link: str,
        examiners: List[str],
        schedule_time: str
    ) -> str:
        """
        Renders a thesis/capstone defense announcement card for Telegram academic broadcast channels.
        """
        examiners_text = "\n".join(f"  • {e}" for e in examiners) if examiners else "  • Tim Dosen Penguji Prodi"
        return (
            f"🎓 **Jadwal Sidang Tugas Akhir Mahasiswa**\n\n"
            f"👤 **Mahasiswa:** {candidate_name}\n"
            f"📖 **Judul Skripsi:** {thesis_title}\n"
            f"⏰ **Waktu Pelaksanaan:** `{schedule_time}`\n"
            f"📍 **Ruangan / Tautan:** `{room_or_link}`\n\n"
            f"👥 **Dewan Penguji:**\n{examiners_text}\n\n"
            f"💡 *Sidang terbuka untuk mahasiswa aktif sebagai penonton referensi akademik.*"
        )





