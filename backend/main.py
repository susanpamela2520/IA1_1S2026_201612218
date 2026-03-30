"""
main.py - Backend principal de HandTalk AI
FastAPI + WebSocket para procesamiento en tiempo real
"""
import json
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import DEFAULT_CONFIG, load_config, save_config
from ml_model import classifier
from telegram_service import send_message, test_bot
from vision import extract_landmarks

# ─────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────
app = FastAPI(title="HandTalk AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ─────────────────────────────────────────────
#  Métricas en memoria
# ─────────────────────────────────────────────
_metrics = {
    "total_frames": 0,
    "hands_detected": 0,
    "successful_predictions": 0,
    "low_confidence": 0,
    "messages_sent_ok": 0,
    "messages_sent_fail": 0,
    "processing_times_ms": deque(maxlen=200),   # últimas 200 mediciones
    "errors": deque(maxlen=50),
}


def _add_to_history(config: dict, record: dict) -> dict:
    history = config.get("message_history", [])
    history.append(record)
    if len(history) > 200:
        history = history[-200:]
    config["message_history"] = history
    return config


# ─────────────────────────────────────────────
#  Rutas estáticas
# ─────────────────────────────────────────────
@app.get("/")
async def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ─────────────────────────────────────────────
#  WebSocket — procesamiento en tiempo real
# ─────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    cfg = load_config()

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            kind = msg.get("type")

            # ── Procesar frame ──────────────────────────────────────────
            if kind == "frame":
                if not cfg.get("capture_active", True):
                    await ws.send_text(json.dumps({"type": "paused"}))
                    continue

                t0 = time.perf_counter()
                _metrics["total_frames"] += 1

                frame_b64 = msg["data"]
                features, annotated = extract_landmarks(frame_b64)

                elapsed_ms = (time.perf_counter() - t0) * 1000
                _metrics["processing_times_ms"].append(elapsed_ms)

                if features is None:
                    await ws.send_text(json.dumps({
                        "type": "prediction",
                        "hand_detected": False,
                        "word": None,
                        "confidence": 0.0,
                        "annotated_image": None,
                        "processing_ms": round(elapsed_ms, 1),
                    }))
                    continue

                _metrics["hands_detected"] += 1
                cfg = load_config()          # recarga para cambios en vivo
                word, conf = classifier.predict(features, cfg["confidence_threshold"])

                if word:
                    _metrics["successful_predictions"] += 1
                else:
                    _metrics["low_confidence"] += 1

                await ws.send_text(json.dumps({
                    "type": "prediction",
                    "hand_detected": True,
                    "word": word,
                    "confidence": round(conf, 4),
                    "annotated_image": (
                        f"data:image/jpeg;base64,{annotated}" if annotated else None
                    ),
                    "processing_ms": round(elapsed_ms, 1),
                }))

            # ── Enviar mensaje a Telegram ───────────────────────────────
            elif kind == "send_telegram":
                cfg = load_config()
                word = msg.get("word", "")
                conf = msg.get("confidence", 0.0)
                ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                text = cfg["telegram_message_format"].format(
                    word=word, confidence=conf, timestamp=ts
                )

                if cfg.get("telegram_enabled", True):
                    result = send_message(
                        cfg["telegram_bot_token"],
                        cfg["telegram_chat_id"],
                        text,
                    )
                    success = result["success"]
                else:
                    success = False
                    result = {"error": "Envío a Telegram desactivado"}

                if success:
                    _metrics["messages_sent_ok"] += 1
                else:
                    _metrics["messages_sent_fail"] += 1

                # Guardar historial
                cfg = _add_to_history(cfg, {
                    "word": word,
                    "confidence": round(conf, 4),
                    "message": text,
                    "sent_ok": success,
                    "error": result.get("error"),
                    "timestamp": ts,
                })
                save_config(cfg)

                await ws.send_text(json.dumps({
                    "type": "telegram_result",
                    "success": success,
                    "error": result.get("error"),
                }))

            # ── Reload modelo desde disco ───────────────────────────────
            elif kind == "reload_model":
                classifier.reload()
                await ws.send_text(json.dumps({
                    "type": "model_reloaded",
                    "loaded": classifier.is_loaded,
                    "classes": classifier.classes,
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[ws] Error inesperado: {e}")


# ─────────────────────────────────────────────
#  REST API — Módulo Administrador
# ─────────────────────────────────────────────

@app.get("/api/config")
async def get_config():
    cfg = load_config()
    # No exponer token en claro (ocultar parcialmente)
    safe = cfg.copy()
    if safe.get("telegram_bot_token"):
        t = safe["telegram_bot_token"]
        safe["telegram_bot_token"] = t[:6] + "..." + t[-4:] if len(t) > 10 else "***"
    return safe


@app.put("/api/config")
async def update_config(body: dict):
    cfg = load_config()
    # Si el token viene parcialmente oculto, no sobrescribir
    if "telegram_bot_token" in body:
        if "..." in body["telegram_bot_token"]:
            body.pop("telegram_bot_token")
    cfg.update(body)
    save_config(cfg)
    return {"status": "ok"}


@app.put("/api/config/token")
async def update_token(body: dict):
    """Ruta separada para actualizar el token completo."""
    cfg = load_config()
    if "telegram_bot_token" in body:
        cfg["telegram_bot_token"] = body["telegram_bot_token"]
    if "telegram_chat_id" in body:
        cfg["telegram_chat_id"] = body["telegram_chat_id"]
    save_config(cfg)
    return {"status": "ok"}


@app.post("/api/config/reset")
async def reset_config():
    save_config(DEFAULT_CONFIG.copy())
    return {"status": "reset"}


@app.get("/api/metrics")
async def get_metrics():
    times = list(_metrics["processing_times_ms"])
    avg = sum(times) / len(times) if times else 0
    total_p = _metrics["successful_predictions"] + _metrics["low_confidence"]
    accuracy = _metrics["successful_predictions"] / total_p if total_p else 0

    return {
        "total_frames_processed": _metrics["total_frames"],
        "hands_detected": _metrics["hands_detected"],
        "successful_predictions": _metrics["successful_predictions"],
        "low_confidence_predictions": _metrics["low_confidence"],
        "messages_sent_ok": _metrics["messages_sent_ok"],
        "messages_sent_fail": _metrics["messages_sent_fail"],
        "avg_processing_ms": round(avg, 2),
        "prediction_accuracy": round(accuracy, 4),
        "recent_errors": list(_metrics["errors"]),
    }


@app.get("/api/history")
async def get_history():
    cfg = load_config()
    return {"history": cfg.get("message_history", [])}


@app.delete("/api/history")
async def clear_history():
    cfg = load_config()
    cfg["message_history"] = []
    save_config(cfg)
    return {"status": "cleared"}


@app.get("/api/model/status")
async def model_status():
    return {
        "loaded": classifier.is_loaded,
        "classes": classifier.classes,
        "model_path": str(Path("../models/model.pkl").resolve()),
    }


@app.post("/api/telegram/test")
async def telegram_test():
    cfg = load_config()
    result = test_bot(cfg["telegram_bot_token"], cfg["telegram_chat_id"])
    return result


@app.get("/api/signs")
async def get_signs():
    cfg = load_config()
    return {"signs": cfg["available_signs"]}
