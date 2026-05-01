import base64
import cv2
import numpy as np
from typing import Optional, Tuple

# Importar MediaPipe de forma segura
try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision

    # Usar la API nueva de MediaPipe (Tasks API)
    base_options = mp_python.BaseOptions(
        model_asset_path=None
    )
    MEDIAPIPE_OK = False  # Usaremos el método alternativo
except Exception:
    MEDIAPIPE_OK = False

# Método alternativo con la API clásica
try:
    import mediapipe as mp
    _hands_module = mp.solutions.hands
    _drawing = mp.solutions.drawing_utils
    _styles = mp.solutions.drawing_styles
    _hands = _hands_module.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.50,
        min_tracking_confidence=0.40,
    )
    MEDIAPIPE_OK = True
    print("[vision] ✅ MediaPipe cargado correctamente")
except Exception as e:
    print(f"[vision] ❌ MediaPipe no disponible: {e}")
    MEDIAPIPE_OK = False
    _hands = None


def decode_frame(data: str) -> Optional[np.ndarray]:
    try:
        if "," in data:
            data = data.split(",", 1)[1]
        img_bytes = base64.b64decode(data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[vision] Error decodificando frame: {e}")
        return None


def encode_frame(img: np.ndarray, quality: int = 75) -> str:
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf).decode("utf-8")


def extract_landmarks(
    frame_b64: str,
) -> Tuple[Optional[np.ndarray], Optional[str]]:
    if not MEDIAPIPE_OK or _hands is None:
        return None, None

    img = decode_frame(frame_b64)
    if img is None:
        return None, None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    try:
        results = _hands.process(img_rgb)
    except Exception as e:
        print(f"[vision] Error procesando frame: {e}")
        return None, None

    if not results.multi_hand_landmarks:
        return None, None

    hand = results.multi_hand_landmarks[0]

    try:
        _drawing.draw_landmarks(
            img, hand,
            _hands_module.HAND_CONNECTIONS,
            _styles.get_default_hand_landmarks_style(),
            _styles.get_default_hand_connections_style(),
        )
    except Exception:
        pass

    features = []
    for lm in hand.landmark:
        features.extend([lm.x, lm.y, lm.z])

    return np.array(features, dtype=np.float32), encode_frame(img)