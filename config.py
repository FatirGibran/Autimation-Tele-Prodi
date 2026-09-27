import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class WordPressConfig:
    api_url: str = field(default_factory=lambda: os.getenv("WP_API_URL", "https://bif-pwt.telkomuniversity.ac.id/wp-json/wp/v2"))
    username: str = field(default_factory=lambda: os.getenv("WP_USERNAME", ""))
    application_password: str = field(default_factory=lambda: os.getenv("WP_APP_PASSWORD", ""))
    default_author_id: int = field(default_factory=lambda: int(os.getenv("WP_DEFAULT_AUTHOR_ID", "1")))
    default_category_id: int = field(default_factory=lambda: int(os.getenv("WP_DEFAULT_CATEGORY_ID", "1")))

@dataclass(frozen=True)
class LLMConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model_name: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-2.5-flash"))
    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2")))
    max_output_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "4096")))

@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    allowed_chat_ids: list[int] = field(default_factory=lambda: [
        int(x.strip()) for x in os.getenv("TELEGRAM_ALLOWED_CHATS", "").split(",") if x.strip().isdigit()
    ])
    webhook_url: str = field(default_factory=lambda: os.getenv("TELEGRAM_WEBHOOK_URL", ""))
    webhook_port: int = field(default_factory=lambda: int(os.getenv("PORT", "8080")))

@dataclass(frozen=True)
class AppConfig:
    base_dir: Path = Path(__file__).parent.resolve()
    db_path: Path = field(default_factory=lambda: Path(__file__).parent.resolve() / "editorial.db")
    prompts_dir: Path = field(default_factory=lambda: Path(__file__).parent.resolve() / "prompts")
    articles_dir: Path = field(default_factory=lambda: Path(__file__).parent.resolve() / "articles")
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent.resolve() / "output")
    wp: WordPressConfig = field(default_factory=WordPressConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)

settings = AppConfig()
