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

    @staticmethod
    def format_weekly_editorial_digest(
        week_range: str,
        published_count: int,
        top_categories: List[Dict[str, Any]],
        highlights: List[str]
    ) -> str:
        """
        Renders a weekly publishing summary digest card for editorial teams on Telegram.
        """
        categories_text = "\n".join(
            f"  • {c.get('name', 'Umum')}: {c.get('count', 0)} artikel" for c in top_categories
        ) if top_categories else "  • Tidak ada kategori spesifik"
        highlights_text = "\n".join(f"  ✨ {h}" for h in highlights) if highlights else "  ✨ Tidak ada catatan khusus"
        return (
            f"📊 **Ringkasan Editorial Mingguan ({week_range})**\n\n"
            f"📝 Total Diterbitkan: `{published_count}` artikel\n\n"
            f"📂 **Distribusi Kategori:**\n{categories_text}\n\n"
            f"🌟 **Sorotan Redaksi:**\n{highlights_text}\n\n"
            f"🚀 *Tetap produktif dan jaga standar kualitas konten prodi!*"
        )

    @staticmethod
    def format_conference_reminder_card(
        conf_name: str,
        deadline: str,
        venue: str,
        registration_fee: str,
        submit_url: str
    ) -> str:
        """
        Renders an academic call-for-papers and conference deadline reminder card for Telegram.
        """
        return (
            f"📢 **Pemberitahuan Call for Papers Konferensi Ilmiah**\n\n"
            f"🏛 **Konferensi:** {conf_name}\n"
            f"⏳ **Batas Akhir (Deadline):** `{deadline}`\n"
            f"📍 **Lokasi / Venue:** {venue}\n"
            f"💰 **Biaya Registrasi:** {registration_fee}\n"
            f"🔗 **Tautan Submit:** {submit_url}\n\n"
            f"💡 *Mahasiswa dan dosen disarankan segera menyelesaikan naskah sebelum batas akhir.*"
        )

    @staticmethod
    def format_student_achievement_broadcast(
        event_name: str,
        winner_names: List[str],
        award_title: str,
        level: str,
        supervisor_name: str
    ) -> str:
        """
        Renders a fast-breaking student achievement and competition victory card for Telegram broadcasts.
        """
        winners_text = "\n".join(f"  🏆 {w}" for w in winner_names) if winner_names else "  🏆 Mahasiswa Prestasi Prodi"
        return (
            f"🎉 **Prestasi Membanggakan Mahasiswa Informatika!**\n\n"
            f"🏅 **Peringkat / Gelar:** {award_title} ({level})\n"
            f"🎪 **Ajang Kompetisi:** {event_name}\n\n"
            f"👥 **Nama Pemenang:**\n{winners_text}\n\n"
            f"👨‍🏫 **Dosen Pembimbing:** {supervisor_name}\n\n"
            f"👏 *Selamat atas pencapaian gemilang yang mengharumkan almamater!*"
        )

    @staticmethod
    def format_scholarship_announcement_card(
        scholarship_name: str,
        sponsor: str,
        coverage: str,
        deadline: str,
        eligibility: List[str],
        apply_url: str
    ) -> str:
        """
        Renders an academic scholarship call-for-application announcement card for Telegram broadcast.
        """
        elig_text = "\n".join(f"  • {e.strip()}" for e in eligibility) if eligibility else "  • Mahasiswa aktif prodi"
        return (
            f"🎓 **Informasi Pembukaan Beasiswa Pendidikan**\n\n"
            f"📌 **Program:** {scholarship_name}\n"
            f"🏢 **Penyelenggara / Sponsor:** {sponsor}\n"
            f"💵 **Cakupan Beasiswa:** {coverage}\n"
            f"⏳ **Batas Pendaftaran:** `{deadline}`\n\n"
            f"📋 **Persyaratan Utama:**\n{elig_text}\n\n"
            f"🔗 **Pendaftaran Resmi:** {apply_url}\n\n"
            f"✨ *Manfaatkan kesempatan ini untuk mendukung kelancaran studi Anda!*"
        )

    @staticmethod
    def format_journal_publication_alert(
        paper_title: str,
        authors: List[str],
        journal_name: str,
        quartile: str,
        doi_url: str
    ) -> str:
        """
        Renders a fast-breaking academic journal publication alert card for Telegram broadcast.
        """
        authors_text = ", ".join(authors) if authors else "Dosen & Peneliti Prodi"
        return (
            f"📑 **Publikasi Jurnal Ilmiah Internasional Baru!**\n\n"
            f"📖 **Judul Paper:** \"{paper_title}\"\n"
            f"👥 **Penulis:** {authors_text}\n"
            f"🏛 **Jurnal:** {journal_name}\n"
            f"📊 **Klaster / Reputasi:** `{quartile}`\n"
            f"🔗 **Tautan DOI:** {doi_url}\n\n"
            f"🚀 *Kontribusi nyata civitas akademika dalam kemajuan riset dan teknologi.*"
        )

    @staticmethod
    def format_patent_registration_card(
        patent_title: str,
        patent_number: str,
        inventors: List[str],
        filing_date: str,
        official_url: str = ""
    ) -> str:
        """
        Renders an intellectual property (IPR/Paten) registration card formatted for Telegram broadcasts.
        """
        invs_text = ", ".join(inv.strip() for inv in inventors if inv.strip()) or "Dosen & Peneliti Prodi"
        url_text = f"\n🔗 **Pangkalan Data DJKI:** {official_url}" if official_url.strip() else ""
        return (
            f"💡 **Paten & Hak Kekayaan Intelektual Resmi Terdaftar!**\n\n"
            f"📜 **Judul Invensi:** \"{patent_title.strip()}\"\n"
            f"🔢 **Nomor Paten / Pendaftaran:** `{patent_number.strip()}`\n"
            f"👥 **Inventor:** {invs_text}\n"
            f"📅 **Tanggal Terdaftar / Permohonan:** `{filing_date.strip()}`{url_text}\n\n"
            f"🎉 *Selamat kepada para inventor atas perlindungan hukum karya cipta teknologi!*"
        )

    @staticmethod
    def format_credit_transfer_approval_card(
        student_name: str,
        host_univ: str,
        approved_courses: List[Dict[str, str]],
        total_ects: float,
        total_sks: int
    ) -> str:
        """
        Renders a credit transfer approval telegram card for exchange/study abroad students.
        """
        lines = []
        for c in approved_courses:
            h_name = c.get("host_course", "")
            d_name = c.get("home_course", "")
            sks = c.get("sks", "")
            lines.append(f"  • {h_name} ➔ {d_name} ({sks} SKS)")
        courses_text = "\n".join(lines) if lines else "  • Seluruh mata kuliah terdaftar telah disetujui"

        return (
            f"🎓 **Persetujuan Konversi & Transfer Kredit Akademik**\n\n"
            f"👤 **Mahasiswa:** {student_name.strip()}\n"
            f"🏛 **Universitas Mitra:** {host_univ.strip()}\n"
            f"⚖️ **Total Beban:** `{total_ects:.1f} ECTS` ➔ `{total_sks} SKS`\n\n"
            f"📚 **Daftar Ekuivalensi Matakuliah:**\n{courses_text}\n\n"
            f"✅ *Nilai dan SKS telah diverifikasi oleh Tim Kurikulum Prodi.*"
        )

    @staticmethod
    def format_workshop_invitation_card(
        workshop_title: str,
        speaker_name: str,
        speaker_title: str,
        schedule_time: str,
        platform_or_room: str,
        registration_url: str,
        quota: int = 0
    ) -> str:
        """
        Renders an academic webinar/workshop broadcast card formatted for Telegram editorial channels.
        """
        quota_text = f"\n👥 **Kuota Peserta:** `{quota} kursi`" if quota > 0 else ""
        return (
            f"📢 **Undangan Workshop & Pelatihan Akademik**\n\n"
            f"🎯 **Topik:** \"{workshop_title.strip()}\"\n"
            f"🎙 **Narasumber:** {speaker_name.strip()} ({speaker_title.strip()})\n"
            f"📅 **Waktu:** `{schedule_time.strip()}`\n"
            f"📍 **Lokasi / Media:** {platform_or_room.strip()}{quota_text}\n"
            f"🔗 **Pendaftaran:** {registration_url.strip()}\n\n"
            f"✨ *Terbuka untuk civitas akademika dan mahasiswa prodi. Tempat terbatas!*"
        )

    @staticmethod
    def format_thesis_defense_schedule_broadcast(
        student_name: str,
        nim: str,
        thesis_title: str,
        room: str,
        schedule: str,
        chief_examiner: str
    ) -> str:
        """
        Renders a final thesis examination / defense schedule broadcast card for Telegram.
        """
        return (
            f"🎓 **Jadwal Sidang Terbuka Tugas Akhir Mahasiswa**\n\n"
            f"👤 **Nama Mahasiswa:** {student_name.strip()} (`{nim.strip()}`)\n"
            f"📖 **Judul Skripsi:** \"{thesis_title.strip()}\"\n"
            f"🏛 **Ketua Dewan Penguji:** {chief_examiner.strip()}\n"
            f"📅 **Waktu Pelaksanaan:** `{schedule.strip()}`\n"
            f"📍 **Ruang Sidang / Media:** {room.strip()}\n\n"
            f"🕊 *Mari doakan kelancaran dan kesuksesan sidang mahasiswa bersangkutan.*"
        )

    @staticmethod
    def format_community_service_broadcast(
        activity_title: str,
        partner_name: str,
        location: str,
        leader_name: str,
        sdgs_theme: str,
        beneficiaries: int = 0
    ) -> str:
        """
        Renders a community service (Pengabdian kepada Masyarakat / PKM) broadcast card for Telegram.
        """
        ben_text = f"\n👥 **Penerima Manfaat:** `{beneficiaries} Orang`" if beneficiaries > 0 else ""
        return (
            f"🤝 **Laporan Kegiatan Pengabdian kepada Masyarakat (PKM)**\n\n"
            f"🎯 **Kegiatan:** \"{activity_title.strip()}\"\n"
            f"🏢 **Mitra Sasaran:** {partner_name.strip()}\n"
            f"📍 **Lokasi:** {location.strip()}\n"
            f"👤 **Ketua Pengabdi:** {leader_name.strip()}\n"
            f"🌱 **Fokus SDGs:** `{sdgs_theme.strip()}`{ben_text}\n\n"
            f"🌟 *Wujud nyata Tri Dharma Perguruan Tinggi untuk kemaslahatan masyarakat.*"
        )

    @staticmethod
    def format_competition_award_broadcast(
        competition_name: str,
        award_title: str,
        team_name: str,
        member_names: List[str],
        organizer: str
    ) -> str:
        """
        Renders a celebratory student competition award victory card for Telegram broadcast.
        """
        members_text = ", ".join(m.strip() for m in member_names if m.strip()) or "Mahasiswa Prodi"
        return (
            f"🏆 **Selamat & Sukses atas Prestasi Mahasiswa!**\n\n"
            f"🎖 **Capaian Prestasi:** {award_title.strip()}\n"
            f"🎪 **Ajang Kompetisi:** \"{competition_name.strip()}\"\n"
            f"🏢 **Penyelenggara:** {organizer.strip()}\n"
            f"👥 **Nama Tim:** {team_name.strip()}\n"
            f"👤 **Anggota Tim:** {members_text}\n\n"
            f"🎉 *Semoga menjadi inspirasi dan pemacu semangat berprestasi civitas akademika!*"
        )

    @staticmethod
    def format_yudisium_congratulations_broadcast(
        student_name: str,
        nim: str,
        thesis_title: str,
        ipk: float,
        predicate: str,
        yudisium_date: str
    ) -> str:
        """
        Renders a celebratory graduation (Yudisium) degree conferral broadcast card for Telegram.
        """
        return (
            f"🎓 **Selamat & Sukses atas Kelulusan Yudisium Sarjana!**\n\n"
            f"👤 **Nama Lulusan:** {student_name.strip()} (`{nim.strip()}`)\n"
            f"📖 **Judul Skripsi:** \"{thesis_title.strip()}\"\n"
            f"📊 **Indeks Prestasi Kumulatif (IPK):** `{ipk:.2f}`\n"
            f"🎖 **Predikat Kelulusan:** *{predicate.strip()}*\n"
            f"📅 **Tanggal Yudisium:** `{yudisium_date.strip()}`\n\n"
            f"💐 *Selamat menyandang gelar Sarjana dan berkontribusi nyata bagi bangsa dan almamater!*"
        )

    @staticmethod
    def format_visiting_lecture_broadcast(
        speaker_name: str,
        speaker_origin: str,
        lecture_topic: str,
        date_time: str,
        venue: str,
        registration_url: str = ""
    ) -> str:
        """
        Renders an international visiting professor / public guest lecture invitation card for Telegram.
        """
        reg_text = f"\n🔗 **Tautan Registrasi:** {registration_url.strip()}" if registration_url else ""
        return (
            f"🌐 **Undangan Kuliah Umum Dosen Tamu Internasional (Visiting Professor)**\n\n"
            f"🎙 **Narasumber:** {speaker_name.strip()}\n"
            f"🏛 **Asal Institusi:** {speaker_origin.strip()}\n"
            f"📚 **Topik Kuliah:** \"{lecture_topic.strip()}\"\n"
            f"📅 **Waktu Pelaksanaan:** `{date_time.strip()}`\n"
            f"📍 **Tempat / Media:** {venue.strip()}{reg_text}\n\n"
            f"✨ *Terbuka untuk seluruh civitas akademika dan mahasiswa program studi.*"
        )

    @staticmethod
    def format_kkn_village_completion_broadcast(
        group_code: str,
        village_name: str,
        district: str,
        regency: str,
        supervisor_dpl: str,
        student_count: int,
        theme: str,
        flagship_outcome: str,
        documentation_url: str = ""
    ) -> str:
        """
        Renders a thematic student community engagement (KKN) village project completion bulletin for Telegram.
        """
        doc_link = f"\n🔗 **Dokumentasi & Laporan:** {documentation_url.strip()}" if documentation_url else ""
        return (
            f"🏡 **Diseminasi & Penutupan KKN Tematik Mahasiswa**\n\n"
            f"🏷 **Kelompok:** `{group_code.strip()}`\n"
            f"📍 **Lokasi Pengabdian:** Desa {village_name.strip()}, Kec. {district.strip()}, Kab. {regency.strip()}\n"
            f"👨‍🏫 **Dosen Pembimbing Lapangan (DPL):** {supervisor_dpl.strip()}\n"
            f"👥 **Jumlah Mahasiswa:** {student_count} Mahasiswa\n"
            f"🎯 **Tema Program:** {theme.strip()}\n"
            f"🏆 **Program Unggulan:** {flagship_outcome.strip()}{doc_link}\n\n"
            f"👏 *Apresiasi setinggi-tingginya kepada seluruh mahasiswa dan masyarakat desa mitra.*"
        )

    @staticmethod
    def format_core_conference_presentation_broadcast(
        paper_title: str,
        presenter_name: str,
        conference_name: str,
        acronym: str,
        core_tier: str,
        city: str,
        date_str: str,
        paper_url: str = ""
    ) -> str:
        """
        Renders a CORE-ranked international conference presentation announcement card for Telegram.
        """
        paper_link = f"\n🔗 **Tautan Publikasi / Makalah:** {paper_url.strip()}" if paper_url else ""
        tier = core_tier.strip().upper()
        return (
            f"🎖 **Diseminasi Riset Konferensi Internasional (CORE Ranked)**\n\n"
            f"📄 **Judul Makalah:** \"{paper_title.strip()}\"\n"
            f"👤 **Pemakalah:** {presenter_name.strip()}\n"
            f"🌐 **Forum Konferensi:** {conference_name.strip()} ({acronym.strip()})\n"
            f"🏅 **Peringkat CORE:** Peringkat {tier}\n"
            f"📍 **Lokasi:** {city.strip()}\n"
            f"📅 **Waktu Pelaksanaan:** `{date_str.strip()}`{paper_link}\n\n"
            f"👏 *Selamat dan sukses atas kontribusi riset bereputasi di kancah internasional!*"
        )

    @staticmethod
    def format_bima_grant_award_broadcast(
        project_title: str,
        lead_researcher: str,
        scheme_name: str,
        funding_amount: float,
        fiscal_year: int,
        contract_no: str = ""
    ) -> str:
        """
        Renders a Kemdikbud BIMA research grant award announcement card for Telegram.
        """
        contract_text = f"\n📜 **Nomor Kontrak:** `{contract_no.strip()}`" if contract_no else ""
        return (
            f"🎉 **Pengumuman Pemenang Hibah Riset Kemdikbud BIMA**\n\n"
            f"📑 **Judul Penelitian:** \"{project_title.strip()}\"\n"
            f"👨‍🏫 **Ketua Peneliti:** {lead_researcher.strip()}\n"
            f"🏷 **Skema Riset:** {scheme_name.strip()}\n"
            f"💰 **Pagu Anggaran Disetujui:** `Rp {funding_amount:,.0f}`\n"
            f"📅 **Tahun Anggaran:** `{fiscal_year}`{contract_text}\n\n"
            f"💐 *Selamat atas pendanaan hibah nasional, semoga memberikan dampak signifikan bagi sains dan institusi!*"
        )

    @staticmethod
    def format_kerja_praktik_showcase_broadcast(
        student_name: str,
        nim: str,
        company_name: str,
        project_title: str,
        duration_weeks: int,
        report_url: str = ""
    ) -> str:
        """
        Renders a student Kerja Praktik (KP) internship completion bulletin for Telegram.
        """
        doc_link = f"\n🔗 **Laporan & Dokumentasi:** {report_url.strip()}" if report_url else ""
        return (
            f"💼 **Diseminasi & Kelulusan Kerja Praktik (KP) Mahasiswa**\n\n"
            f"👤 **Nama Praktikan:** {student_name.strip()} (`{nim.strip()}`)\n"
            f"🏢 **Mitra Industri:** {company_name.strip()}\n"
            f"⚙️ **Judul Proyek:** \"{project_title.strip()}\"\n"
            f"⏱ **Durasi Magang:** {duration_weeks} Minggu{doc_link}\n\n"
            f"👏 *Selamat atas penyelesaian masa praktik industri dan kontribusi nyata di dunia kerja!*"
        )

    @staticmethod
    def format_accreditation_announcement_telegram(
        program_name: str,
        agency: str,
        rating: str,
        sk_number: str,
        valid_until: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a study program accreditation decree achievement announcement card for Telegram.
        """
        portal_link = f"\n🔗 **Verifikasi Status Akreditasi:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🏆 **Pengumuman Resmi Akreditasi Program Studi**\n\n"
            f"🎓 **Program Studi:** {program_name.strip()}\n"
            f"🏛 **Badan Akreditasi:** {agency.strip()}\n"
            f"⭐ **Peringkat Akreditasi:** **{rating.strip()}**\n"
            f"📜 **Nomor SK:** `{sk_number.strip()}`\n"
            f"📅 **Masa Berlaku Hingga:** `{valid_until.strip()}`{portal_link}\n\n"
            f"💐 *Selamat dan sukses kepada seluruh civitas akademika atas pencapaian mutu pendidikan unggul!*"
        )

    @staticmethod
    def format_scholarship_announcement_telegram(
        student_name: str,
        nim: str,
        scholarship_type: str,
        sponsor_name: str,
        amount_idr: float,
        semester: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student scholarship aid allocation announcement bulletin for Telegram.
        """
        portal_link = f"\n🔗 **Informasi & Surat Keputusan:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🎓 **Pengumuman Penerima Beasiswa & Bantuan Pendidikan**\n\n"
            f"👤 **Penerima Beasiswa:** {student_name.strip()} (`{nim.strip()}`)\n"
            f"🏷 **Skema Beasiswa:** {scholarship_type.strip()}\n"
            f"🏢 **Mitra / Sponsor:** {sponsor_name.strip()}\n"
            f"💰 **Besaran Bantuan:** `Rp {amount_idr:,.0f}`\n"
            f"📅 **Periode Semester:** {semester.strip()}{portal_link}\n\n"
            f"👏 *Selamat atas pencapaian beasiswa, pertahankan prestasi akademik dan dedikasi belajar!*"
        )

    @staticmethod
    def format_cum_laude_announcement_telegram(
        student_name: str,
        nim: str,
        ipk: float,
        honor_predicate: str,
        thesis_title: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a graduation judicium cum laude honor announcement bulletin for Telegram.
        """
        portal_link = f"\n🔗 **Verifikasi Yudisium:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🎓 **Apresiasi Kelulusan Dengan Pujian (Cum Laude)**\n\n"
            f"👤 **Nama Wisudawan:** {student_name.strip()} (`{nim.strip()}`)\n"
            f"⭐ **Predikat Yudisium:** **{honor_predicate.strip()}**\n"
            f"📊 **Indeks Prestasi Kumulatif (IPK):** `{float(ipk):.2f}`\n"
            f"📑 **Judul Tugas Akhir:**\n_{thesis_title.strip()}_{portal_link}\n\n"
            f"💐 *Selamat atas kelulusan yang membanggakan, semoga ilmu yang diperoleh berkah dan bermanfaat!*"
        )

    @staticmethod
    def format_tridharma_grant_announcement_telegram(
        lecturer_name: str,
        nidn: str,
        project_title: str,
        grant_amount: float,
        fiscal_year: int,
        publication_target: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a lecturer internal Tridharma research grant award announcement for Telegram.
        """
        portal_link = f"\n🔗 **Detail Hibah LPPM:** {portal_url.strip()}" if portal_url else ""
        amount_str = f"Rp {float(grant_amount):,.0f}".replace(",", ".")
        return (
            f"🔬 **Pengumuman Pemenang Hibah Riset Internal LPPM**\n\n"
            f"👨‍🏫 **Ketua Peneliti:** {lecturer_name.strip()} (`NIDN: {nidn.strip()}`)\n"
            f"📅 **Tahun Anggaran:** {int(fiscal_year)}\n"
            f"💡 **Judul Riset:**\n_{project_title.strip()}_\n"
            f"💰 **Dana Disetujui:** `{amount_str}`\n"
            f"🎯 **Target Luaran:** {publication_target.strip()}{portal_link}\n\n"
            f"👏 *Selamat kepada penerima hibah riset internal, selamat berkarya dan menghasilkan inovasi telekomunikasi!*"
        )

    @staticmethod
    def format_fast_track_announcement_telegram(
        student_name: str,
        nim: str,
        ipk: float,
        masters_program: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student selection announcement for the accelerated Fast-Track Master's program.
        """
        portal_link = f"\n🔗 **Portal Akademik:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🚀 **Pengumuman Seleksi Program Akselerasi S1 + S2 (Fast-Track)**\n\n"
            f"👤 **Nama Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"📊 **Indeks Prestasi Kumulatif (IPK):** `{float(ipk):.2f}`\n"
            f"🎓 **Program Studi Magister:** {masters_program.strip()}{portal_link}\n\n"
            f"🌟 *Selamat kepada mahasiswa terpilih program Fast-Track Magister Teknik Elektro/Telekomunikasi!*"
        )

    @staticmethod
    def format_hki_copyright_announcement_telegram(
        work_title: str,
        creators: List[str],
        reg_number: str,
        creation_type: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a DJKI Kemenkumham Intellectual Property / HKI copyright grant announcement for Telegram.
        """
        portal_link = f"\n🔗 **Pangkalan Data DJKI:** {portal_url.strip()}" if portal_url else ""
        creators_str = ", ".join(c.strip() for c in creators if c.strip())
        return (
            f"📜 **Pengumuman Pencatatan Hak Cipta / HKI Kemenkumham**\n\n"
            f"💡 **Judul Ciptaan:**\n_{work_title.strip()}_\n"
            f"🏷️ **Jenis Ciptaan:** {creation_type.strip()}\n"
            f"🔢 **Nomor Pencatatan:** `{reg_number.strip()}`\n"
            f"👥 **Pencipta:** {creators_str}{portal_link}\n\n"
            f"🎉 *Selamat dan sukses atas perolehan sertifikat Hak Cipta, memajukan portofolio kekayaan intelektual Program Studi!*"
        )

    @staticmethod
    def format_msib_internship_announcement_telegram(
        student_name: str,
        nim: str,
        partner_name: str,
        internship_role: str,
        converted_sks: int,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student certified MSIB industrial internship completion announcement for Telegram.
        """
        portal_link = f"\n🔗 **Portal MBKM:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🏢 **Apresiasi Kelulusan Magang Bersertifikat (MSIB Kampus Merdeka)**\n\n"
            f"👤 **Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"🏭 **Mitra Industri:** {partner_name.strip()}\n"
            f"💼 **Peran / Divisi:** {internship_role.strip()}\n"
            f"📚 **Rekognisi Kurikulum:** `{int(converted_sks)} SKS Disetujui`{portal_link}\n\n"
            f"👏 *Selamat atas pencapaian pengalaman profesional industri telekomunikasi riil!*"
        )

    @staticmethod
    def format_pkm_grant_announcement_telegram(
        project_title: str,
        team_leader: str,
        nidn: str,
        partner_name: str,
        budget_amount: float,
        fiscal_year: int,
        portal_url: str = ""
    ) -> str:
        """
        Renders a lecturer Tridharma Community Service (PKM) internal grant award announcement for Telegram.
        """
        portal_link = f"\n🔗 **Portal Pengabdian LPPM:** {portal_url.strip()}" if portal_url else ""
        amount_str = f"Rp {float(budget_amount):,.0f}".replace(",", ".")
        return (
            f"🤝 **Pengumuman Penetapan Pemenang Hibah Pengabdian Masyarakat (PKM)**\n\n"
            f"💡 **Judul Pengabdian:**\n_{project_title.strip()}_\n"
            f"👨‍🏫 **Ketua Pengabdi:** {team_leader.strip()} (`NIDN: {nidn.strip()}`)\n"
            f"🏘️ **Mitra Sasaran:** {partner_name.strip()}\n"
            f"💰 **Dana Disetujui:** `{amount_str}` (`T.A. {int(fiscal_year)}`){portal_link}\n\n"
            f"🌟 *Selamat mengabdi dan menghadirkan kemanfaatan teknologi telekomunikasi bagi masyarakat luas!*"
        )

    @staticmethod
    def format_satellite_link_announcement_telegram(
        satellite_name: str,
        downlink_freq_ghz: float,
        station_name: str,
        cnr_db: float,
        link_margin_db: float,
        modulation: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a satellite ground station downlink budget calculation bulletin for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Telemetri Satelit:** {portal_url.strip()}" if portal_url else ""
        margin_prefix = "+" if link_margin_db >= 0 else ""
        return (
            f"🛰️ **Hasil Audit Link Budget Komunikasi Satelit**\n\n"
            f"📡 **Satelit Transponder:** {satellite_name.strip()} (`{float(downlink_freq_ghz):.2f} GHz`)\n"
            f"🏢 **Stasiun Bumi (Earth Station):** {station_name.strip()}\n"
            f"📶 **Carrier-to-Noise (C/N):** `{float(cnr_db):.2f} dB`\n"
            f"🛡️ **Fade Link Margin:** `{margin_prefix}{float(link_margin_db):.2f} dB`\n"
            f"🎛️ **Rekomendasi Modulasi:** `{modulation.strip()}`{portal_link}\n\n"
            f"🚀 *Perhitungan link budget memenuhi ambang batas keandalan transmisi satelit DVB-S2!*"
        )

    @staticmethod
    def format_kampus_mengajar_announcement_telegram(
        student_name: str,
        nim: str,
        target_school: str,
        converted_sks: int,
        letter_grade: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student Kampus Mengajar teaching completion announcement for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal MBKM Kemdikbud:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🏫 **Apresiasi Kelulusan Program Kampus Mengajar MBKM**\n\n"
            f"👤 **Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"🎒 **Sekolah Penugasan:** {target_school.strip()}\n"
            f"📊 **Nilai Mutu:** `{letter_grade.strip()}`\n"
            f"📚 **Konversi Kurikulum:** `{int(converted_sks)} SKS Diakui`{portal_link}\n\n"
            f"👏 *Terima kasih atas kontribusi dan dedikasi dalam memajukan literasi dan numerasi pendidikan dasar!*"
        )

    @staticmethod
    def format_radar_telemetry_announcement_telegram(
        radar_name: str,
        freq_ghz: float,
        peak_power_kw: float,
        antenna_gain_dbi: float,
        rcs_m2: float,
        max_range_km: float,
        portal_url: str = ""
    ) -> str:
        """
        Renders a monostatic radar telemetry detection range summary for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Radar Telemetri:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🎯 **Hasil Audit Telemetri Jangkauan Radar Monostatik**\n\n"
            f"📡 **Sistem Radar:** {radar_name.strip()} (`{float(freq_ghz):.2f} GHz`)\n"
            f"⚡ **Peak Transmit Power:** `{float(peak_power_kw):.1f} kW`\n"
            f"📶 **Gain Antena:** `{float(antenna_gain_dbi):.1f} dBi`\n"
            f"🎯 **Target RCS (\u03c3):** `{float(rcs_m2):.2f} m\u00b2`\n"
            f"📏 **Jangkauan Maksimum (R_max):** `{float(max_range_km):.2f} km`{portal_link}\n\n"
            f"🔭 *Perhitungan persamaan radar terverifikasi memenuhi standar deteksi gelombang mikro IEEE AES!*"
        )

    @staticmethod
    def format_wirausaha_merdeka_telegram(
        student_name: str,
        nim: str,
        startup_name: str,
        business_sector: str,
        composite_score: float,
        converted_sks: int,
        letter_grade: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student Wirausaha Merdeka (WMK) startup incubation completion card for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Wirausaha Merdeka:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🚀 **Apresiasi Kelulusan MBKM Wirausaha Merdeka (WMK)**\n\n"
            f"👤 **Founder/Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"🏢 **Startup:** {startup_name.strip()} (`{business_sector.strip()}`)\n"
            f"📊 **Skor Komposit:** `{float(composite_score):.1f} / 100` (`Mutu: {letter_grade.strip()}`)\n"
            f"📚 **Konversi Kurikulum:** `{int(converted_sks)} SKS Diakui`{portal_link}\n\n"
            f"💡 *Selamat atas dedikasi dan inovasi pengembangan startup teknologi telekomunikasi!*"
        )

    @staticmethod
    def format_otdr_telemetry_telegram(
        link_name: str,
        fiber_length_km: float,
        wavelength_nm: int,
        total_loss_db: float,
        attenuation_db_km: float,
        quality_status: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders an OTDR fiber attenuation and trace audit summary for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Telemetri Optik:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🔬 **Hasil Audit Redaman Serat Optik OTDR**\n\n"
            f"🛣️ **Ruas Link Optik:** {link_name.strip()}\n"
            f"📏 **Panjang Kabel:** `{float(fiber_length_km):.2f} km` (`{int(wavelength_nm)} nm`)\n"
            f"📉 **Total Link Loss:** `{float(total_loss_db):.2f} dB`\n"
            f"📊 **Koefisien Redaman (\u03b1):** `{float(attenuation_db_km):.4f} dB/km`\n"
            f"🛡️ **Status Kelayakan:** `{quality_status.strip()}`{portal_link}\n\n"
            f"✨ *Hasil trace reflectometry terverifikasi memenuhi standar transmisi serat optik ITU-T G.652!*"
        )

    @staticmethod
    def format_iisma_exchange_telegram(
        student_name: str,
        nim: str,
        host_university: str,
        country: str,
        gpa_host: float,
        converted_sks: int,
        letter_grade: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders an IISMA international student exchange award announcement for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal IISMA Kemdikbud:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🌍 **Apresiasi Prestasi IISMA MBKM Luar Negeri**\n\n"
            f"👤 **Awardee/Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"🏛️ **Universitas Tujuan:** {host_university.strip()} ({country.strip()})\n"
            f"📊 **Capaian Akademik:** `IPK {float(gpa_host):.2f} / 4.00` (`Mutu: {letter_grade.strip()}`)\n"
            f"📚 **Rekognisi Kurikulum:** `{int(converted_sks)} SKS Diakui`{portal_link}\n\n"
            f"🎉 *Selamat atas keberhasilan menuntaskan studi internasional dan mengharumkan almamater!*"
        )

    @staticmethod
    def format_fspl_link_budget_telegram(
        link_name: str,
        freq_mhz: float,
        distance_km: float,
        fspl_db: float,
        rx_power_dbm: float,
        fade_margin_db: float,
        is_viable: bool,
        portal_url: str = ""
    ) -> str:
        """
        Renders an RF FSPL and wireless link budget audit report for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Pemantauan RF:** {portal_url.strip()}" if portal_url else ""
        status_text = "LAYAK / STABIL (Viable)" if is_viable else "PUTUS / REDUP (Outage)"
        return (
            f"📡 **Laporan Audit Wireless Link Budget & FSPL**\n\n"
            f"🌐 **Nama Tautan:** {link_name.strip()}\n"
            f"📶 **Frekuensi Kerja:** `{float(freq_mhz):.1f} MHz`\n"
            f"📏 **Jarak Transmisi:** `{float(distance_km):.2f} km`\n"
            f"📉 **Path Loss Bebas (FSPL):** `{float(fspl_db):.2f} dB`\n"
            f"🎯 **Daya Terima (Prx):** `{float(rx_power_dbm):.2f} dBm`\n"
            f"🛡️ **Fade Margin:** `{float(fade_margin_db):+.2f} dB` (`{status_text}`){portal_link}\n\n"
            f"✨ *Hasil audit kalkulasi propagasi gelombang elektromagnetik prodi terverifikasi!*"
        )

    @staticmethod
    def format_proyek_kemanusiaan_telegram(
        student_name: str,
        nim: str,
        partner_org: str,
        location: str,
        converted_sks: int,
        letter_grade: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a student MBKM Proyek Kemanusiaan completion announcement for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal MBKM Kemanusiaan:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🤝 **Apresiasi Mahasiswa MBKM Proyek Kemanusiaan**\n\n"
            f"👤 **Nama Relawan/Mahasiswa:** {student_name.strip()} (`NIM: {nim.strip()}`)\n"
            f"🏢 **Mitra Kebencanaan:** {partner_org.strip()}\n"
            f"📍 **Lokasi Pengabdian:** {location.strip()}\n"
            f"📊 **Nilai Mutu Akhir:** `{letter_grade.strip()}`\n"
            f"📚 **Rekognisi Kurikulum:** `{int(converted_sks)} SKS Diakui`{portal_link}\n\n"
            f"❤️ *Dedikasi nyata mahasiswa teknik telekomunikasi dalam mitigasi kebencanaan dan kepedulian sosial!*"
        )

    @staticmethod
    def format_rain_attenuation_telegram(
        link_name: str,
        freq_ghz: float,
        distance_km: float,
        rain_rate_mm_hr: float,
        rain_attenuation_db: float,
        excess_margin_db: float,
        status: str,
        portal_url: str = ""
    ) -> str:
        """
        Renders a microwave terrestrial link ITU-R rain attenuation and outage report for Telegram broadcast.
        """
        portal_link = f"\n🔗 **Portal Pemantauan Microwave:** {portal_url.strip()}" if portal_url else ""
        return (
            f"🌧️ **Laporan Redaman Hujan Microwave Terestrial (ITU-R P.838)**\n\n"
            f"🌐 **Nama Tautan:** {link_name.strip()}\n"
            f"📶 **Frekuensi Kerja:** `{float(freq_ghz):.2f} GHz`\n"
            f"📏 **Jarak Lintasan:** `{float(distance_km):.2f} km`\n"
            f"🌧️ **Intensitas Hujan (R0.01):** `{float(rain_rate_mm_hr):.1f} mm/jam`\n"
            f"📉 **Redaman Hujan Total:** `{float(rain_attenuation_db):.2f} dB`\n"
            f"🛡️ **Margin Tersisa (Excess):** `{float(excess_margin_db):+.2f} dB`\n"
            f"📊 **Status Keandalan:** `{status.strip()}`{portal_link}\n\n"
            f"✨ *Hasil audit transmisi gelombang mikro dan mitigasi cuaca prodi terverifikasi!*"
        )

























