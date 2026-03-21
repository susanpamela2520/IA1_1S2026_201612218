"""
config.py - Gestión de configuración del sistema HandTalk AI
"""
import json
import os
from pathlib import Path

CONFIG_FILE = Path("../config/settings.json")

DEFAULT_CONFIG = {
    "confidence_threshold": 0.50,
    "telegram_enabled": True,
    "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    "telegram_message_format": "🤟 HandTalk AI detectó: *{word}*\n📊 Confianza: {confidence:.0%}\n🕐 {timestamp}",
    "available_signs": [
        "hola", "gracias", "ayuda", "si", "no",
        "por_favor", "bien", "mal", "agua", "comida"
    ],
    "capture_active": True,
    "message_history": []
}


def load_config() -> dict:
    """Carga la configuración desde archivo JSON, con fallback a defaults."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                stored = json.load(f)
            # Merge: garantiza que nuevas keys de DEFAULT existan
            merged = DEFAULT_CONFIG.copy()
            merged.update(stored)
            return merged
        except (json.JSONDecodeError, IOError):
            pass
    # Primera vez: guardar defaults
    save_config(DEFAULT_CONFIG.copy())
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Persiste la configuración en disco."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)