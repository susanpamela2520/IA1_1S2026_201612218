# 🤟 HandTalk AI

Sistema inteligente de reconocimiento de señas manuales en tiempo real mediante Computer Vision y Machine Learning.

**Curso:** Inteligencia Artificial 1 — Universidad San Carlos de Guatemala  
**Carnet:** 201612218  
**Tecnologías:** Python · OpenCV · MediaPipe · scikit-learn · FastAPI · WebSocket · Docker

---

## Arquitectura General

```
Browser (Host)                    Backend (Docker / local)
──────────────────────────────    ──────────────────────────────
WebRTC Camera                     FastAPI (uvicorn)
     │                                 │
     │  WebSocket (frames JPEG b64) ──►│ vision.py   ← MediaPipe
     │                                 │    │
     │◄── {word, confidence, img} ──── │ ml_model.py ← model.pkl
     │                                 │    │
     │  [botón Telegram] ─────────────►│ telegram_service.py
     │                                 │
     │  REST /api/* ─────────────────► │ config.py, metrics
```

### Componentes

| Módulo | Descripción |
|---|---|
| `backend/vision.py` | Detección de manos con MediaPipe, extrae 63 features (x,y,z × 21 landmarks) |
| `backend/ml_model.py` | Carga el modelo entrenado (.pkl) y realiza inferencia |
| `backend/telegram_service.py` | Envío de mensajes via Telegram Bot API |
| `backend/config.py` | Gestión de configuración persistente en JSON |
| `backend/main.py` | FastAPI: WebSocket en tiempo real + REST para módulo admin |
| `frontend/index.html` | UI web completa (captura, predicción, admin, métricas) |
| `scripts/collect_data.py` | Recolección del dataset de landmarks |
| `scripts/train_model.py` | Entrenamiento y evaluación de modelos |

---

## Instalación y Ejecución

### Opción A — Ejecución local (recomendada para desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/IA1_1S2026_Carnet.git
cd IA1_1S2026_Carnet/Proyecto2

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Recolectar datos (necesitas cámara conectada)
python scripts/collect_data.py

# 5. Entrenar modelo
python scripts/train_model.py

# 6. Iniciar backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 7. Abrir navegador en http://localhost:8000
```

### Opción B — Docker

```bash
# 1. Copiar variables de entorno
cp .env.example .env
# Editar .env con tu token de Telegram

# 2. Recolectar datos y entrenar (requiere cámara — hacerlo ANTES de Docker)
python scripts/collect_data.py
python scripts/train_model.py

# 3. Levantar contenedor
docker-compose up --build -d

# 4. Abrir navegador en http://localhost:8000

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

> **Nota sobre la cámara en Docker:** El frontend usa WebRTC del navegador del host para acceder a la cámara. Los frames se envían al backend vía WebSocket. No se necesita `--device /dev/video0`.

---

## Uso del Sistema

### Módulo Principal (Reconocimiento)

1. Abre `http://localhost:8000` en Chrome/Firefox.
2. Permite acceso a la cámara cuando el navegador lo solicite.
3. Coloca tu mano frente a la cámara realizando una seña.
4. El sistema detecta la mano y muestra la predicción con su porcentaje de confianza.
5. Haz clic en **"+ Agregar al mensaje"** para acumular palabras.
6. Haz clic en **"✈️ Enviar a Telegram"** para enviar el mensaje acumulado.

Controles adicionales:
- **⏸ Pausar** — detiene el envío de frames al backend.
- **👁 Landmarks** — muestra los puntos de MediaPipe sobre la imagen.

### Módulo Administrador

Pestaña **⚙️ Administrador**:
- **Configuración Telegram:** Token del bot, Chat ID, formato del mensaje, activar/desactivar envío.
- **Parámetros del modelo:** Umbral de confianza (predicciones por debajo se descartan).
- **Señas disponibles:** Ver y modificar la lista de señas reconocidas.
- **Estado del modelo:** Ver clases cargadas, recargar modelo tras reentrenamiento.

### Métricas

Pestaña **📊 Métricas**:
- Frames procesados, manos detectadas, predicciones exitosas, tiempo promedio de procesamiento, mensajes enviados.

### Historial

Pestaña **📨 Historial**: Lista de todos los mensajes enviados a Telegram con timestamp, confianza y estado.

---

## Recolección de Datos y Entrenamiento

### Señas incluidas por defecto

| Seña | Descripción |
|---|---|
| hola | Saludo |
| gracias | Agradecimiento |
| ayuda | Solicitar ayuda |
| si | Afirmación |
| no | Negación |
| por_favor | Cortesía |
| bien | Estado positivo |
| mal | Estado negativo |
| agua | Pedir agua |
| comida | Pedir comida |

### Agregar nuevas señas

1. Editar `SIGNS` en `scripts/collect_data.py`.
2. Ejecutar `python scripts/collect_data.py`.
3. Volver a entrenar con `python scripts/train_model.py`.
4. Recargar modelo desde la UI (Administrador → Recargar modelo).

### Algoritmos evaluados

El script de entrenamiento compara automáticamente:
- **Random Forest** (200 estimadores) ← generalmente mejor
- **SVM RBF** (kernel radial)
- **KNN** (k=7, pesos por distancia)
- **Logistic Regression**

Métricas reportadas: accuracy, precision, recall, F1-score, cross-validation 5-fold.

---

## Configuración del Bot de Telegram

1. Hablar con [@BotFather](https://t.me/BotFather) en Telegram.
2. Crear bot con `/newbot`, obtener el **Token**.
3. Agregar el bot al grupo o iniciar conversación.
4. Obtener el **Chat ID** con [@userinfobot](https://t.me/userinfobot).
5. Ingresar token y chat ID en la pestaña Administrador.
6. Probar con el botón **"🧪 Probar"**.

---

## Estructura del Repositorio

```
Proyecto2/
├── backend/
│   ├── main.py                 # FastAPI app (WebSocket + REST)
│   ├── vision.py               # MediaPipe hand detection
│   ├── ml_model.py             # Model inference
│   ├── telegram_service.py     # Telegram Bot API
│   └── config.py               # Config persistence
├── frontend/
│   └── index.html              # Web UI (single file)
├── scripts/
│   ├── collect_data.py         # Dataset collection tool
│   └── train_model.py          # Model training + evaluation
├── dataset/
│   └── landmarks.csv           # Dataset de landmarks (generado)
├── models/
│   ├── model.pkl               # Modelo entrenado
│   ├── scaler.pkl              # StandardScaler
│   ├── label_encoder.pkl       # LabelEncoder
│   └── training_results.json   # Métricas del entrenamiento
├── config/
│   └── settings.json           # Configuración del sistema
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Licencia

MIT License — Ver `LICENSE` para detalles.

---

## Colaboradores del curso
- roberto1206
- ixchop98
