"""
telegram_service.py - Integración con el bot de Telegram
"""
import requests
from typing import Optional


def send_message(token: str, chat_id: str, text: str) -> dict:
    """
    Envía un mensaje de texto vía Telegram Bot API.
    """
    if not token or not chat_id:
        return {"success": False, "error": "Token o chat_id no configurados"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            return {"success": True, "error": None}
        else:
            data = resp.json()
            return {
                "success": False,
                "error": data.get("description", f"HTTP {resp.status_code}"),
            }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout al conectar con Telegram"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Sin conexión a internet"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_bot(token: str, chat_id: str) -> dict:
    """Envía mensaje de prueba para verificar la configuración."""
    return send_message(
        token, chat_id,
        "✅ *HandTalk AI* conectado correctamente al bot de Telegram."
    )
