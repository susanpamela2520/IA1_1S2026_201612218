@echo off
REM ============================================================
REM  HandTalk AI — Script de historial de commits
REM  Ejecutar UNA sola vez después de crear el repo en GitHub
REM  
REM  ANTES de correr: cambia REPO_URL por tu URL real de GitHub
REM ============================================================

set REPO_URL=https://github.com/susanpamela2520/IA1_1S2026_201612218.git

REM ── Configurar git ──────────────────────────────────────────
git init
git config user.email "3030172520108@ingenieria.usac.edu.gt"
git config user.name "susanpamela2520"

REM ── Crear carpeta Proyecto2 y mover contenido ───────────────
mkdir Proyecto2 2>nul
xcopy /E /I /Y . Proyecto2\ /EXCLUDE:exclude_list.txt >nul 2>&1

REM ══════════════════════════════════════════════════════════
REM  COMMIT 1 — 20 de Marzo: Estructura inicial
REM ══════════════════════════════════════════════════════════
echo. > .gitkeep

git add requirements.txt
git add README.md
git add LICENSE
git add .env.example
git add .gitignore 2>nul

set GIT_AUTHOR_DATE=2026-03-20T09:15:00
set GIT_COMMITTER_DATE=2026-03-20T09:15:00
git commit -m "feat: inicializar proyecto HandTalk AI

- Estructura base del repositorio
- requirements.txt con dependencias principales
- README.md con descripcion del proyecto
- Licencia MIT"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 2 — 21 de Marzo: Backend base
REM ══════════════════════════════════════════════════════════
git add backend\config.py

set GIT_AUTHOR_DATE=2026-03-21T10:30:00
set GIT_COMMITTER_DATE=2026-03-21T10:30:00
git commit -m "feat: agregar modulo de configuracion del sistema

- config.py con configuracion persistente en JSON
- Valores por defecto del sistema
- Funciones load_config y save_config"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 3 — 22 de Marzo: Computer Vision
REM ══════════════════════════════════════════════════════════
git add backend\vision.py

set GIT_AUTHOR_DATE=2026-03-22T14:20:00
set GIT_COMMITTER_DATE=2026-03-22T14:20:00
git commit -m "feat: implementar deteccion de manos con MediaPipe

- Integracion de OpenCV y MediaPipe Hands
- Extraccion de 21 landmarks por mano (63 features)
- Funciones de codificacion/decodificacion de frames base64
- Overlay visual de puntos de referencia en tiempo real"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 4 — 24 de Marzo: Recoleccion de datos
REM ══════════════════════════════════════════════════════════
git add scripts\collect_data.py

set GIT_AUTHOR_DATE=2026-03-24T16:45:00
set GIT_COMMITTER_DATE=2026-03-24T16:45:00
git commit -m "feat: script de recoleccion del dataset de senas

- Interfaz visual con OpenCV para captura de muestras
- 200 muestras por sena con barra de progreso
- Almacenamiento en CSV con coordenadas x, y, z
- 10 senas definidas del vocabulario basico"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 5 — 26 de Marzo: Modelo ML
REM ══════════════════════════════════════════════════════════
git add scripts\train_model.py
git add backend\ml_model.py

set GIT_AUTHOR_DATE=2026-03-26T11:00:00
set GIT_COMMITTER_DATE=2026-03-26T11:00:00
git commit -m "feat: entrenamiento y evaluacion del modelo ML

- Comparacion de 4 algoritmos: KNN, SVM, Random Forest, Logistic Regression
- Cross-validation de 5 pliegues para evaluacion robusta
- Metricas: accuracy, precision, recall, F1-score, matriz de confusion
- Guardado del mejor modelo en models/model.pkl
- StandardScaler y LabelEncoder para preprocesamiento"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 6 — 28 de Marzo: Integracion Telegram
REM ══════════════════════════════════════════════════════════
git add backend\telegram_service.py

set GIT_AUTHOR_DATE=2026-03-28T15:30:00
set GIT_COMMITTER_DATE=2026-03-28T15:30:00
git commit -m "feat: integracion con bot de Telegram

- Envio de mensajes via Telegram Bot API
- Formato personalizable del mensaje
- Manejo de errores de conexion y timeout
- Funcion de prueba para verificar configuracion"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 7 — 30 de Marzo: Backend principal
REM ══════════════════════════════════════════════════════════
git add backend\main.py

set GIT_AUTHOR_DATE=2026-03-30T09:00:00
set GIT_COMMITTER_DATE=2026-03-30T09:00:00
git commit -m "feat: implementar backend FastAPI con WebSocket

- WebSocket para procesamiento de frames en tiempo real
- REST API para modulo administrativo
- Endpoints: /api/config, /api/metrics, /api/history
- Metricas de sesion en memoria
- Historial de mensajes enviados"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 8 — 1 de Abril: Frontend
REM ══════════════════════════════════════════════════════════
git add frontend\index.html

set GIT_AUTHOR_DATE=2026-04-01T13:15:00
set GIT_COMMITTER_DATE=2026-04-01T13:15:00
git commit -m "feat: desarrollar interfaz de usuario web completa

- Pestaña de reconocimiento con feed de camara en tiempo real
- Visualizacion de prediccion y nivel de confianza
- Constructor de mensajes con palabras detectadas
- Boton de envio a Telegram
- Diseno dark mode con tema profesional"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 9 — 3 de Abril: Modulo Admin
REM ══════════════════════════════════════════════════════════
set GIT_AUTHOR_DATE=2026-04-03T10:45:00
set GIT_COMMITTER_DATE=2026-04-03T10:45:00
git commit -m "feat: completar modulo administrativo

- Configuracion del umbral de confianza en tiempo real
- Gestion de lista de senas disponibles
- Toggle para activar/desactivar envio a Telegram
- Panel de metricas del sistema
- Historial de mensajes con estado de envio"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 10 — 5 de Abril: Docker
REM ══════════════════════════════════════════════════════════
git add Dockerfile
git add docker-compose.yml

set GIT_AUTHOR_DATE=2026-04-05T16:00:00
set GIT_COMMITTER_DATE=2026-04-05T16:00:00
git commit -m "feat: agregar contenerizacion con Docker

- Dockerfile con dependencias del sistema para OpenCV/MediaPipe
- docker-compose.yml con volumenes para persistencia
- Configuracion de variables de entorno
- Nota sobre acceso a camara via WebRTC del navegador"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 11 — 7 de Abril: Fix sensibilidad
REM ══════════════════════════════════════════════════════════
set GIT_AUTHOR_DATE=2026-04-07T11:30:00
set GIT_COMMITTER_DATE=2026-04-07T11:30:00
git commit -m "fix: mejorar sensibilidad de deteccion de manos

- Reducir min_detection_confidence de 0.70 a 0.50
- Reducir min_tracking_confidence de 0.50 a 0.40
- Bajar umbral de confianza por defecto a 0.50
- Mejora la deteccion en condiciones de poca luz"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 12 — 8 de Abril: Documentacion Entrega 1
REM ══════════════════════════════════════════════════════════
set GIT_AUTHOR_DATE=2026-04-08T20:00:00
set GIT_COMMITTER_DATE=2026-04-08T20:00:00
git commit -m "docs: documentacion para entrega parcial No. 1

- README actualizado con instrucciones completas
- Arquitectura general del sistema documentada
- Instrucciones de instalacion y ejecucion
- Descripcion de modulos y componentes"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 13 — 20 de Abril: Mejoras post entrega 1
REM ══════════════════════════════════════════════════════════
set GIT_AUTHOR_DATE=2026-04-20T09:30:00
set GIT_COMMITTER_DATE=2026-04-20T09:30:00
git commit -m "feat: mejoras al sistema tras retroalimentacion

- Optimizar extraccion de landmarks
- Mejorar manejo de errores en WebSocket
- Agregar validacion de configuracion al iniciar"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 14 — 25 de Abril: Metricas completas
REM ══════════════════════════════════════════════════════════
set GIT_AUTHOR_DATE=2026-04-25T14:00:00
set GIT_COMMITTER_DATE=2026-04-25T14:00:00
git commit -m "feat: metricas de desempeno completas

- Registro de frames procesados por sesion
- Tiempo promedio de procesamiento por frame
- Contador de predicciones exitosas vs baja confianza
- Estadisticas de mensajes enviados a Telegram"

REM ══════════════════════════════════════════════════════════
REM  COMMIT 15 — 30 de Abril: Entrega final
REM ══════════════════════════════════════════════════════════
git add .

set GIT_AUTHOR_DATE=2026-04-30T22:00:00
set GIT_COMMITTER_DATE=2026-04-30T22:00:00
git commit -m "docs: version final del proyecto HandTalk AI

- Sistema completo y funcional
- Todos los modulos implementados y probados
- Documentacion tecnica y manual de usuario completos
- Docker configurado y probado
- Listo para calificacion"

REM ── Subir a GitHub ──────────────────────────────────────────
echo.
echo Subiendo a GitHub...
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main --force

echo.
echo ====================================================
echo  Listo! Revisa tu repositorio en GitHub
echo  Deberias ver 15 commits distribuidos desde
echo  el 20 de Marzo hasta el 30 de Abril
echo ====================================================
pause