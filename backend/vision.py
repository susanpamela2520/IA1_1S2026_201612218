"""
vision.py - Detección de manos y extracción de landmarks con MediaPipe
"""
import base64
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Instancia global de MediaPipe (se reutiliza entre llamadas)
_hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.50,
    min_tracking_confidence=0.40,
)


def decode_frame(data: str) -> Optional[np.ndarray]:
    """Decodifica un frame en base64 (con o sin prefijo data:image/...)"""
    try:
        if "," in data:
            data = data.split(",", 1)[1]
        img_bytes = base64.b64decode(data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"[vision] Error decodificando frame: {e}")
        return None


def encode_frame(img: np.ndarray, quality: int = 75) -> str:
    """Codifica un frame BGR a JPEG base64."""
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf).decode("utf-8")


def extract_landmarks(
    frame_b64: str,
) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Extrae landmarks de la mano a partir de un frame base64.

    Returns
    -------
    features : ndarray of shape (63,) — x, y, z de 21 landmarks — o None
    annotated_b64 : frame con overlay de MediaPipe dibujado, en base64, o None
    """
    img = decode_frame(frame_b64)
    if img is None:
        return None, None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return None, None

    hand = results.multi_hand_landmarks[0]

    # Dibujar landmarks con estilo de MediaPipe
    mp_drawing.draw_landmarks(
        img,
        hand,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style(),
    )

    # Extraer features: coordenadas normalizadas x, y, z de los 21 puntos = 63 valores
    features = []
    for lm in hand.landmark:
        features.extend([lm.x, lm.y, lm.z])

    annotated_b64 = encode_frame(img)
    return np.array(features, dtype=np.float32), annotated_b64