import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _get_val(key: str, default=None):
    """Retrieve value from environment variables."""
    val = os.getenv(key)
    if val is not None and val != "":
        return val
    return default

def _get_int(key: str, default: int = 0) -> int:
    val = _get_val(key, default)
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def _get_int_list(key: str, default: list = None) -> list:
    if default is None:
        default = []
    val = os.getenv(key)
    if val is not None and val != "":
        try:
            return [int(x.strip()) for x in val.split(",") if x.strip()]
        except ValueError:
            pass
    return default

class Config:
    BOT_TOKEN: str = _get_val("BOT_TOKEN", "")
    COMMAND_PREFIX: str = _get_val("COMMAND_PREFIX", "z")
    TIMEZONE: str = _get_val("TIMEZONE", "Asia/Dhaka")

    GUILD_ID: int = _get_int("GUILD", 0)
    ROLE_USER: int = _get_int("ROLE_USER", 0)
    ROLE_ADMIN: int = _get_int("ROLE_ADMIN", 0)

    CHANNEL_INFO: int = _get_int("CHANNEL_INFO", 0)
    CHANNEL_LIFELESS: int = _get_int("CHANNEL_LIFELESS", 0)

    DELETE_LOG: int = _get_int("DELETE_LOG", 0)
    JOIN_LOG: int = _get_int("JOIN_LOG", 0)
    RESET_INFO: int = _get_int("RESET_INFO", 0)
    YAP_CHAT: int = _get_int("YAP_CHAT", 0)

    AUTHOR: list[int] = _get_int_list("AUTHOR", [])
    TARGET_ID: int = _get_int("TARGET_ID", 0)

    # AI Configuration (OpenRouter)
    AI_TOKEN: str = _get_val("AI_TOKEN", "")
    AI_BASE_URL: str = _get_val("AI_BASE_URL", "https://openrouter.ai/api/v1")
    AI_CHANNEL: int = _get_int("AI_CHANNEL", 0)
    AI_MODEL: str = _get_val("AI_MODEL", "~openai/gpt-sol-latest")
    AI_SITE_URL: str = _get_val("AI_SITE_URL", "")
    AI_SITE_NAME: str = _get_val("AI_SITE_NAME", "FinalBot")
    AI_SYSTEM_PROMPT: str = _get_val("AI_SYSTEM_PROMPT", """You are the AI assistant for the Discord server "Basement of Gamers (BOGS)".
    
=== HARD RULES (STRICT) ===
1. You are replying to the author. NEVER mention the author.
2. Mention other users ONLY if necessary.
3. When mentioning a user, use EXACT Discord format:
   <@USER_ID>
4. NEVER use @username or nickname text.
5. NEVER invent or guess a USER_ID.
6. If no valid USER_ID is provided, do not mention anyone.

=== CONTEXT ===
- You may receive recent chat history as plain text.
- Use it only to understand context.
- Do not repeat the history.
- Focus only on the latest user message.

=== TONE ===
- Casual Discord group-chat style.
- Short and direct.
- Under 500 characters.
- 0–2 emojis max.
- If the question is good → answer clearly.
- If the question is low-effort → light teasing allowed.
- No moral lectures. No policy talk. No disclaimers.

=== GOAL ===
Sound like a real server member: helpful, sharp, occasionally funny.""")

    # Database Configuration
    DB_HOST: str = _get_val("DB_HOST", "")
    DB_USER: str = _get_val("DB_USER", "")
    DB_PASSWORD: str = _get_val("DB_PASSWORD", "")
    DB_PORT: int = _get_int("DB_PORT", 3306)
    DB_NAME: str = _get_val("DB_NAME", "")

    @classmethod
    def get_db_config(cls) -> dict:
        return {
            "host": cls.DB_HOST,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "port": str(cls.DB_PORT),
            "database": cls.DB_NAME,
        }

config = Config()
