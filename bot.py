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
    ContextTypes,
    filters,
)

from parser import parse_telegram_input, parse_llm_response, validate_yoast_seo

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("EditorialBot")

PROMPT_FILE = Path(__file__).parent / "prompts" / "system_prompt.md"

def get_system_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "You are Content Engineer & WordPress Editorial Specialist for S1 Teknik Informatika Telkom University Purwokerto."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 **Bot Otomasi Editorial S1 Teknik Informatika Telkom University Purwokerto**\n\n"
        "Kirimkan prompt dengan format berikut untuk membuat artikel siap terbit (All Green Yoast SEO):\n\n"
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
        "📚 **Panduan Penggunaan Bot Otomasi Editorial**\n\n"
        "1. Kirim pesan sesuai template `/start`.\n"
        "2. Bot akan memanggil engine LLM dengan Master System Prompt editorial.\n"
        "3. Output akan diberikan dalam 2 bagian:\n"
        "   - Yoast SEO Metadata (Keyphrase, SEO Title, Slug, Meta Description)\n"
        "   - File HTML lengkap untuk ditempel ke Elementor Custom HTML.\n"
        "4. Copy-paste ke dashboard WordPress post dan simpan."
    )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def generate_editorial_content(parsed_input: dict, system_prompt: str) -> str:
    """
    Invokes LLM engine (Google Gemini API) to generate editorial article.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum disetel di file .env")

    # Using google-genai client
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
        model="gemini-2.5-flash",
        contents=user_payload,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.3,
        }
    )
    return response.text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text.lower().startswith("topik:"):
        await update.message.reply_text(
            "⚠️ Format pesan tidak dikenali. Ketik `/help` untuk melihat contoh format trigger.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    status_msg = await update.message.reply_text("⏳ Sedang memproses artikel dan optimasi Yoast SEO...")

    try:
        parsed_input = parse_telegram_input(text)
        system_prompt = get_system_prompt()
        
        # Check if API key is present; otherwise notify
        if not os.getenv("GEMINI_API_KEY"):
            await status_msg.edit_text(
                "❌ Error: `GEMINI_API_KEY` belum disetel pada environment server bot. "
                "Harap konfigurasikan file `.env`.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        raw_llm_output = generate_editorial_content(parsed_input, system_prompt)
        parsed_output = parse_llm_response(raw_llm_output)
        seo_check = validate_yoast_seo(parsed_output)

        seo_status_icon = "🟢" if seo_check["passed"] else "🟡"

        # 1. Reply Yoast SEO Metadata
        seo_reply = (
            f"### {seo_status_icon} YOAST SEO METADATA\n\n"
            f"- **Focus Keyphrase:** `{parsed_output['focus_keyphrase']}`\n"
            f"- **SEO Title:** {parsed_output['seo_title']}\n"
            f"- **Slug:** `{parsed_output['slug']}`\n"
            f"- **Meta Description:** {parsed_output['meta_description']}\n\n"
            f"📊 *Validasi Karakter Meta:* {seo_check['checks']['meta_description_length']['detail']}"
        )
        await status_msg.edit_text(seo_reply, parse_mode=ParseMode.MARKDOWN)

        # 2. Save and send HTML file directly
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        filename = f"{parsed_output['slug'] or 'article'}.html"
        output_file = output_dir / filename
        output_file.write_text(parsed_output["html_code"] or raw_llm_output, encoding="utf-8")

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
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN belum disetel di environment atau .env")
        sys.exit(1)

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Telegram Editorial siap dijalankan...")
    application.run_polling()

if __name__ == "__main__":
    main()
