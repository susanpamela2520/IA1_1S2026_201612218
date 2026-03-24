"""
Controles:
    ESPACIO  → iniciar captura de la seña mostrada
    Q        → saltar esta seña / salir
"""
import csv
import sys
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

# ─── Configuración ────────────────────────────────────────────────────────────
SIGNS = [
    "hola", "gracias", "ayuda", "si", "no",
    "por_favor", "bien", "mal", "agua", "comida",
]
SAMPLES_PER_SIGN = 200       # muestras por seña
DATASET_PATH = Path(__file__).parent.parent / "dataset" / "landmarks.csv"

# Header del CSV: x0..x20, y0..y20, z0..z20, label
HEADER = (
    [f"x{i}" for i in range(21)]
    + [f"y{i}" for i in range(21)]
    + [f"z{i}" for i in range(21)]
    + ["label"]
)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# ─── Utilidades ───────────────────────────────────────────────────────────────

def count_existing(sign: str) -> int:
    if not DATASET_PATH.exists():
        return 0
    with open(DATASET_PATH, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)          # saltar header
        return sum(1 for row in reader if row and row[-1] == sign)


def draw_ui(frame, sign: str, count: int, needed: int, collecting: bool):
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Barra superior
    cv2.rectangle(overlay, (0, 0), (w, 55), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    cv2.putText(frame, f"HandTalk AI  |  Seña: {sign.upper()}", (12, 36),
                cv2.FONT_HERSHEY_DUPLEX, 0.85, (255, 220, 80), 1, cv2.LINE_AA)

    # Barra de progreso
    prog_x = int((count / max(needed, 1)) * (w - 20))
    cv2.rectangle(frame, (10, h - 30), (w - 10, h - 10), (40, 40, 40), -1)
    color = (80, 220, 120) if collecting else (80, 140, 220)
    cv2.rectangle(frame, (10, h - 30), (10 + prog_x, h - 10), color, -1)
    cv2.putText(frame, f"{count}/{needed}", (12, h - 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    # Estado
    if not collecting:
        msg = "ESPACIO = iniciar  |  Q = saltar"
        cv2.putText(frame, msg, (12, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (200, 200, 200), 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, "⚫ CAPTURANDO...", (12, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (80, 220, 120), 2, cv2.LINE_AA)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        sys.exit(1)

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.70,
        min_tracking_confidence=0.50,
    ) as hands:

        for sign in SIGNS:
            existing = count_existing(sign)
            needed = SAMPLES_PER_SIGN - existing
            if needed <= 0:
                print(f"✅ '{sign}': ya tiene {existing} muestras — omitiendo")
                continue

            print(f"\n📌 Preparar seña: '{sign.upper()}'  ({needed} muestras faltantes)")
            collecting = False
            collected_rows = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)

                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    mp_draw.draw_landmarks(
                        frame, hand, mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style(),
                    )

                    if collecting and len(collected_rows) < needed:
                        features = []
                        for lm in hand.landmark:
                            features.extend([lm.x, lm.y, lm.z])
                        collected_rows.append(features + [sign])
                        time.sleep(0.04)   # ~25 fps de captura

                count_done = len(collected_rows)
                draw_ui(frame, sign, count_done, needed, collecting)

                cv2.imshow("HandTalk AI — Recolección de Datos", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord(" "):
                    collecting = True
                elif key == ord("q"):
                    break

                if count_done >= needed:
                    print(f"   ✅ {needed} muestras capturadas para '{sign}'")
                    break

            # Guardar al CSV
            if collected_rows:
                file_exists = DATASET_PATH.exists()
                with open(DATASET_PATH, "a", newline="") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(HEADER)
                    writer.writerows(collected_rows)
                print(f"   💾 Guardadas {len(collected_rows)} filas en dataset/landmarks.csv")

    cap.release()
    cv2.destroyAllWindows()
    print("\n🎉 ¡Recolección completada!")
    print(f"   Dataset: {DATASET_PATH}")


if __name__ == "__main__":
    main()
