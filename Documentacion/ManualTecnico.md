# Manual Técnico — HandTalk AI

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería — Escuela de Ciencias y Sistemas**  
**Inteligencia Artificial 1, Sección A**  

**Estudiante:** Susan Pamela Herrera Monzón  
**Carné:** 201612218  

---

## ¿De qué trata este proyecto?

HandTalk AI es un sistema que reconoce señas manuales usando la cámara de la computadora. La idea es que una persona haga una seña con la mano frente a la cámara, el sistema la detecte y muestre qué palabra representa. También puede enviar ese mensaje a través de un bot de Telegram.

Lo desarrollé usando Python como lenguaje principal, junto con OpenCV y MediaPipe para la parte de visión por computadora, y scikit-learn para entrenar el modelo de clasificación.

---

## Arquitectura del sistema

El sistema tiene dos partes principales que se comunican entre sí:

```
Navegador (Frontend)
        │
        │  WebSocket — manda frames de la cámara cada 100ms
        ▼
Backend FastAPI (Python)
        │
        ├── vision.py      → detecta la mano con MediaPipe
        ├── ml_model.py    → clasifica la seña con el modelo entrenado
        ├── config.py      → maneja la configuración del sistema
        └── telegram_service.py → envía mensajes al bot
```

**¿Por qué WebSocket y no REST?**  
Porque necesitaba enviar frames de video de manera continua y recibir respuestas en tiempo real. Con peticiones HTTP normales habría mucho delay.

### Módulo de usuario
Es la parte principal. Captura video desde la cámara del navegador, lo manda al backend como imágenes en base64, el backend extrae los landmarks de la mano y predice qué seña es. El resultado se muestra en pantalla con el nivel de confianza.

### Módulo administrativo
Permite configurar el sistema sin tocar el código. Desde aquí se puede cambiar el umbral de confianza, activar o desactivar Telegram, ver las señas disponibles y revisar el historial de mensajes enviados. Está protegido con usuario y contraseña.

---

## Tecnologías utilizadas

| Tecnología | Para qué la usé |
|---|---|
| Python 3.12 | Lenguaje principal del backend |
| FastAPI | Framework web y manejo de WebSockets |
| OpenCV | Captura y procesamiento de imágenes |
| MediaPipe Hands | Detección de manos y extracción de landmarks |
| scikit-learn | Entrenamiento y uso del modelo de ML |
| HTML/CSS/JS | Interfaz de usuario en el navegador |
| Telegram Bot API | Envío de mensajes |
| Docker | Contenedorización del sistema |

---

## El modelo de Machine Learning

### ¿Qué son los landmarks?
MediaPipe detecta 21 puntos clave en la mano (las articulaciones de cada dedo y la palma). De cada punto extrae 3 coordenadas: x, y, z. Eso da un total de **63 valores numéricos** por frame, que son los que el modelo usa para clasificar la seña.

### Dataset
Recolecté 200 muestras por cada una de las 10 señas, para un total de 2,000 muestras. Las señas que entrené son: hola, gracias, ayuda, sí, no, por favor, bien, mal, agua y comida.

La recolección se hace con el script `scripts/collect_data.py`, que abre la cámara y guarda los landmarks en un archivo CSV.

### Entrenamiento
El script `scripts/train_model.py` compara 4 algoritmos:
- Random Forest
- SVM con kernel RBF
- KNN (k=7)
- Regresión Logística

Usa cross-validation de 5 pliegues para evaluar cada uno y se queda con el que tenga mejor accuracy en el conjunto de prueba. El modelo ganador se guarda como `model.pkl`.

### Resultados del entrenamiento
El mejor modelo fue **Random Forest** con:
- Accuracy: 1.0000
- Precision: 1.0000
- Recall: 1.0000
- F1-Score: 1.0000

La matriz de confusión mostró cero errores en todas las clases, lo que indica que las señas están suficientemente diferenciadas entre sí.

---

## Proceso de entrenamiento paso a paso

**1. Recolección de datos**
```bash
python scripts/collect_data.py
```
Se abre la cámara. Para cada seña, el usuario hace la pose y presiona ESPACIO. El sistema captura 200 muestras automáticamente.

**2. Entrenamiento**
```bash
python scripts/train_model.py
```
Carga el CSV, escala los datos con StandardScaler, divide en 80% entrenamiento y 20% prueba, entrena los 4 algoritmos, evalúa con métricas y guarda el mejor modelo.

**3. Archivos generados**
- `models/model.pkl` — el modelo entrenado
- `models/scaler.pkl` — el escalador de datos
- `models/label_encoder.pkl` — codificador de etiquetas
- `models/training_results.json` — métricas de todos los algoritmos

---

## Instalación y ejecución

### Requisitos
- Python 3.10 o superior
- Cámara web conectada
- Navegador moderno (Chrome o Firefox)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/IA1_1S2026_201612218.git
cd IA1_1S2026_201612218

# 2. Crear entorno virtual
python -m venv venv

# Windows CMD
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Recolectar datos (solo la primera vez)
python scripts/collect_data.py

# 5. Entrenar el modelo (solo la primera vez)
python scripts/train_model.py

# 6. Iniciar el servidor
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 7. Abrir en el navegador
# http://localhost:8000
```

### Con Docker
```bash
docker-compose up --build
```

---

## Diagrama de flujo general

```
Usuario hace seña
       │
       ▼
Cámara del navegador captura frame
       │
       ▼ (WebSocket, base64)
Backend recibe el frame
       │
       ▼
OpenCV decodifica la imagen
       │
       ▼
MediaPipe detecta la mano
       │
       ├── No hay mano → responde "sin mano detectada"
       │
       ▼
Extrae 63 landmarks (x, y, z × 21 puntos)
       │
       ▼
StandardScaler normaliza los valores
       │
       ▼
Random Forest predice la seña
       │
       ├── Confianza < umbral → descarta predicción
       │
       ▼
Envía resultado al navegador
       │
       ▼
Se muestra la palabra y el porcentaje de confianza
```

---

## Estructura de archivos

```
IA1_1S2026_201612218/
├── backend/
│   ├── main.py              ← API principal con WebSocket
│   ├── vision.py            ← Detección de manos con MediaPipe
│   ├── ml_model.py          ← Carga y uso del modelo
│   ├── telegram_service.py  ← Integración con Telegram
│   └── config.py            ← Configuración persistente
├── frontend/
│   └── index.html           ← Interfaz de usuario completa
├── scripts/
│   ├── collect_data.py      ← Recolección del dataset
│   └── train_model.py       ← Entrenamiento del modelo
├── dataset/
│   └── landmarks.csv        ← Dataset de landmarks
├── models/
│   ├── model.pkl            ← Modelo entrenado
│   ├── scaler.pkl           ← Escalador
│   └── label_encoder.pkl    ← Encoder de etiquetas
├── config/
│   └── settings.json        ← Configuración del sistema
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Credenciales del módulo administrativo

- **Usuario:** admin  
- **Contraseña:** handtalk2026

---

*Manual técnico elaborado por Susan Pamela Herrera Monzón — 201612218*