"""
vision.py - Detección de manos y extracción de landmarks con MediaPipe
"""
import cv2
import numpy as np
from typing import Optional, Tuple

try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    MEDIAPIPE_OK = True
except Exception:
    MEDIAPIPE_OK = False

if MEDIAPIPE_OK:
    _hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.50,
        min_tracking_confidence=0.40,
    )
else:
    _hands = None

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


def extract_landmarks(frame_b64: str):
    if not MEDIAPIPE_OK or _hands is None:
        return None, None

    img = decode_frame(frame_b64)
    if img is None:
        return None, None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return None, None

    hand = results.multi_hand_landmarks[0]

    if MEDIAPIPE_OK:
        mp_drawing.draw_landmarks(
            img, hand, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style(),
        )

    features = []
    for lm in hand.landmark:
        features.extend([lm.x, lm.y, lm.z])

    return np.array(features, dtype=np.float32), encode_frame(img)