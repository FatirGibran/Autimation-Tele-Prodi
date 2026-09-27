import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import settings
from parser import parse_telegram_input, parse_llm_response
from seo_validator import YoastSEOValidator
from sanitizer import HTMLSanitizer
from storage import StorageManager
from formatters import TelegramFormatter
from wordpress_client import WordPressClient

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("EditorialBot")

storage = StorageManager(settings.db_path)

def get_system_prompt(template_name: str = "system_prompt.md") -> str:
    path = settings.prompts_dir / template_name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are Content Engineer & WordPress Editorial Specialist for S1 Teknik Informatika Telkom University Purwokerto."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 **Bot Otomasi Editorial S1 Teknik Informatika Telkom University Purwokerto**\n\n"
        "Kirim pesan dengan format berikut untuk membuat artikel siap terbit:\n\n"
        "```\n"
        "Topik: Judul Topik Berita / Riset\n"
        "Tanggal: 28 September 2026\n"
        "Kategori: Cloud & Edge Computing\n"
        "Image URL: https://bif-pwt.telkomuniversity.ac.id/wp-content/...\n"
        "Poin Utama:\n"
        "- Poin 1\n"
        "- Poin 2\n"
        "- Poin 3\n"
        "```"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "📚 **Menu Bantuan & Panduan Bot**\n\n"
        "• `/start` - Menampilkan format pesan pemicu\n"
        "• `/list` - Menampilkan daftar artikel yang pernah dibuat\n"
        "• `/help` - Dokumentasi perintah bot"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    articles = storage.list_articles(limit=10)
    if not articles:
        await update.message.reply_text("Belum ada riwayat artikel tersimpan.")
        return

    lines = ["📚 **10 Artikel Terakhir:**\n"]
    for a in articles:
        lines.append(f"• `{a['publish_date']}`: *{a['seo_title']}* (`{a['status']}`)")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

def generate_editorial_content(parsed_input: dict, system_prompt: str) -> str:
    api_key = settings.llm.api_key
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum disetel.")

    from google import genai
    client = genai.Client(api_key=api_key)

    user_payload = (
        f"Topik: {parsed_input['topik']}\n"
        f"Tanggal: {parsed_input['tanggal']}\n"
        f"Kategori: {parsed_input['kategori']}\n"
        f"Image URL: {parsed_input['image_url']}\n"
        f"Poin Utama:\n" + "\n".join(f"- {p}" for p in parsed_input['poin_utama'])
    )

    response = client.models.generate_content(
        model=settings.llm.model_name,
        contents=user_payload,
        config={
            "system_instruction": system_prompt,
            "temperature": settings.llm.temperature,
        }
    )
    return response.text

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    action, _, slug = data.partition(":")

    if action == "copy_kw":
        with storage._get_connection() as conn:
            row = conn.execute("SELECT focus_keyphrase FROM articles WHERE slug = ?", (slug,)).fetchone()
            kw = row[0] if row else "N/A"
        await query.message.reply_text(f"🎯 **Focus Keyphrase:**\n`{kw}`", parse_mode=ParseMode.MARKDOWN)

    elif action == "copy_meta":
        with storage._get_connection() as conn:
            row = conn.execute("SELECT meta_description FROM articles WHERE slug = ?", (slug,)).fetchone()
            desc = row[0] if row else "N/A"
        await query.message.reply_text(f"📝 **Meta Description:**\n`{desc}`", parse_mode=ParseMode.MARKDOWN)

    elif action == "wp_draft":
        if not (settings.wp.username and settings.wp.application_password):
            await query.message.reply_text("❌ Kredensial WordPress belum lengkap di file `.env`.")
            return

        with storage._get_connection() as conn:
            row = conn.execute("SELECT * FROM articles WHERE slug = ?", (slug,)).fetchone()
            if not row:
                await query.message.reply_text("❌ Artikel tidak ditemukan di database.")
                return

        article_data = dict(row)
        try:
            client = WordPressClient(settings.wp.api_url, settings.wp.username, settings.wp.application_password)
            res = client.create_post(
                title=article_data["seo_title"],
                content=article_data["html_content"],
                slug=article_data["slug"],
                status="draft",
                categories=[settings.wp.default_category_id],
                yoast_meta={
                    "focus_keyphrase": article_data["focus_keyphrase"],
                    "seo_title": article_data["seo_title"],
                    "meta_description": article_data["meta_description"],
                }
            )
            storage.update_wp_post_id(article_data["id"], res.get("id", 0), status="draft_in_wp")
            await query.message.reply_text(
                f"✅ Berhasil membuat draft di WordPress! ID Post: `{res.get('id')}`\n"
                f"Link edit: `{settings.wp.api_url.replace('/wp-json/wp/v2', '')}/wp-admin/post.php?post={res.get('id')}&action=edit`",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await query.message.reply_text(f"❌ Gagal publikasi ke WordPress: `{str(e)}`")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text.lower().startswith("topik:"):
        await update.message.reply_text(
            "⚠️ Format pesan tidak dikenali. Ketik `/start` untuk melihat format pemicu.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    status_msg = await update.message.reply_text("⏳ Sedang memproses dan mengoptimasi Yoast SEO...")

    try:
        parsed_input = parse_telegram_input(text)
        system_prompt = get_system_prompt()

        if not settings.llm.api_key:
            await status_msg.edit_text("❌ Error: `GEMINI_API_KEY` belum disetel pada `.env`.")
            return

        raw_llm_output = generate_editorial_content(parsed_input, system_prompt)
        parsed_output = parse_llm_response(raw_llm_output)

        # Check duplicate keyphrase
        if storage.is_keyphrase_used(parsed_output["focus_keyphrase"]):
            await update.message.reply_text(
                f"⚠️ *Peringatan:* Focus Keyphrase `{parsed_output['focus_keyphrase']}` sudah pernah digunakan sebelumnya. "
                "Disarankan merevisi keyphrase agar tidak saling kanibalisasi pada Yoast SEO.",
                parse_mode=ParseMode.MARKDOWN
            )

        # Sanitize HTML
        clean_html, sanitizer_warnings = HTMLSanitizer.sanitize(parsed_output["html_code"])
        parsed_output["html_code"] = clean_html

        # Evaluate Yoast SEO
        seo_report = YoastSEOValidator.evaluate(parsed_output, clean_html)
        if sanitizer_warnings:
            seo_report["warnings"].extend(sanitizer_warnings)

        # Save to database
        article_record = {
            "topic": parsed_input["topik"],
            "category": parsed_input["kategori"],
            "publish_date": parsed_input["tanggal"],
            "image_url": parsed_input["image_url"],
            "focus_keyphrase": parsed_output["focus_keyphrase"],
            "seo_title": parsed_output["seo_title"],
            "slug": parsed_output["slug"],
            "meta_description": parsed_output["meta_description"],
            "html_content": clean_html,
            "status": "ready" if seo_report["is_all_green"] else "needs_review"
        }
        try:
            storage.save_article(article_record)
        except Exception as e:
            logger.warning("Could not save article to sqlite: %s", e)

        # Send formatted report
        has_wp = bool(settings.wp.username and settings.wp.application_password)
        reply_md = TelegramFormatter.format_seo_report(parsed_output, seo_report)
        reply_kb = TelegramFormatter.build_article_action_keyboard(parsed_output["slug"], has_wp_configured=has_wp)

        await status_msg.edit_text(reply_md, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_kb)

        # Send HTML file
        settings.output_dir.mkdir(exist_ok=True)
        filename = f"{parsed_output['slug'] or 'article'}.html"
        output_file = settings.output_dir / filename
        output_file.write_text(clean_html, encoding="utf-8")

        with open(output_file, "rb") as doc:
            await update.message.reply_document(
                document=doc,
                filename=filename,
                caption="📄 File HTML siap tempel ke widget Custom HTML Elementor WordPress."
            )

    except Exception as e:
        logger.exception("Error processing message")
        await status_msg.edit_text(f"❌ Terjadi kesalahan: `{str(e)}`", parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    bot_token = settings.telegram.bot_token
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN belum disetel di environment atau .env")
        sys.exit(1)

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    print("Bot Telegram Editorial aktif dan siap melayani permintaan...")
    application.run_polling()

if __name__ == "__main__":
    main()
