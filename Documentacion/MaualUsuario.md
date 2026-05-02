# Manual de Usuario — HandTalk AI

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería — Escuela de Ciencias y Sistemas**  
**Inteligencia Artificial 1, Sección A**  

**Estudiante:** Susan Pamela Herrera Monzón  
**Carné:** 201612218  

---

## ¿Qué hace HandTalk AI?

HandTalk AI es una aplicación que reconoce señas manuales en tiempo real usando la cámara de tu computadora. Coloca tu mano frente a la cámara, haz una seña, y el sistema te dice qué palabra detectó. También puedes armar un mensaje con varias palabras y enviarlo a Telegram.

---

## Lo que necesitas para usarlo

- Una computadora con cámara web
- Conexión a internet (para Telegram)
- Google Chrome o Firefox
- El sistema corriendo (ver sección de inicio)

---

## Cómo iniciar el sistema

Abre una terminal en la carpeta del proyecto y ejecuta:

```
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Luego abre tu navegador y ve a:
```
http://localhost:8000
```

Verás una pantalla de login. Ingresa con:
- **Usuario:** admin
- **Contraseña:** handtalk2026

---

## La interfaz tiene 4 pestañas

### 🎯 Reconocimiento

Esta es la pantalla principal. Aquí puedes ver la cámara en tiempo real y las predicciones del sistema.

**Paso a paso para reconocer una seña:**

1. Asegúrate de que la cámara esté encendida — verás tu imagen en la pantalla
2. Coloca tu mano frente a la cámara haciendo una de las señas disponibles
3. Mantén la mano quieta unos segundos
4. En el panel derecho aparecerá la palabra detectada y el porcentaje de confianza
5. Si quieres agregar esa palabra a un mensaje, haz clic en **"+ Agregar al mensaje"**
6. Repite con más señas para formar oraciones
7. Cuando tengas tu mensaje listo, haz clic en **"✈️ Enviar a Telegram"**

**Botones de la cámara:**
- **Pausar** — detiene el reconocimiento temporalmente
- **Landmarks** — muestra los puntos de detección sobre tu mano (los puntitos de colores)

**¿Qué significa el porcentaje de confianza?**  
Es qué tan seguro está el sistema de su predicción. Si dice 95% significa que está muy seguro. Si está por debajo del umbral configurado, la predicción se descarta y no se muestra.

---

### ⚙️ Administrador

Desde aquí puedes configurar el sistema. Necesitas estar con el login hecho para que los cambios se guarden.

**Configuración de Telegram:**
- Aquí se ingresa el token del bot y el chat ID
- Puedes personalizar el formato del mensaje que llega a Telegram
- El toggle de "Envío a Telegram activo" te permite desactivar el envío sin borrar la configuración
- El botón **"Probar"** manda un mensaje de prueba para verificar que todo funcione

**Parámetros del modelo:**
- **Umbral de confianza:** Si lo subes, el sistema solo acepta predicciones muy seguras. Si lo bajas, acepta más predicciones pero pueden ser menos precisas. El valor recomendado es entre 50% y 70%.
- **Captura activa:** Toggle para pausar o reanudar el reconocimiento

**Señas disponibles:**
- Muestra las 10 señas que el modelo puede reconocer
- Puedes agregar o eliminar señas de la lista (si reentrenar el modelo con esas señas)

**Estado del modelo:**
- Muestra si el modelo está cargado correctamente y cuántas clases reconoce
- El botón "Recargar modelo" sirve cuando se reentrena sin reiniciar el sistema

---

### 📊 Métricas

Muestra estadísticas de la sesión actual:

- **Frames procesados** — cuántas imágenes analizó el sistema
- **Manos detectadas** — cuántas veces encontró una mano en la imagen
- **Predicciones exitosas** — cuántas veces logró identificar una seña
- **Baja confianza** — cuántas predicciones descartó por no pasar el umbral
- **Mensajes enviados** — cuántos mensajes llegaron a Telegram correctamente
- **Tiempo promedio** — cuánto tarda el sistema en procesar cada frame

---

### 📨 Historial

Aquí puedes ver todos los mensajes que se han enviado a Telegram, con la fecha, hora, la seña detectada y si el envío fue exitoso.

El botón **"Limpiar historial"** borra todos los registros.

---

## Las señas que reconoce el sistema

| Seña | Cómo hacerla |
|---|---|
| **hola** | Mano abierta, palma al frente |
| **gracias** | Mano plana tocando el mentón |
| **ayuda** | Pulgar arriba apoyado sobre la palma |
| **si** | Puño cerrado |
| **no** | Dedo índice extendido |
| **por_favor** | Mano abierta con palma hacia arriba |
| **bien** | Pulgar arriba |
| **mal** | Pulgar abajo |
| **agua** | Tres dedos en forma de W |
| **comida** | Dedos juntos apuntando hacia la boca |

---

## Consejos para que funcione mejor

- Trata de estar en un lugar con buena iluminación
- Coloca la mano a una distancia cómoda de la cámara, no muy cerca ni muy lejos
- Mantén la mano quieta mientras el sistema captura la seña
- Si el sistema no detecta tu mano, ajusta la iluminación o acerca un poco más la mano
- Si las predicciones no son correctas, baja un poco el umbral de confianza desde la pestaña Administrador

---

## Capturas de pantalla

### Pantalla principal — reconocimiento en tiempo real
La cámara muestra tu imagen, y cuando detecta una mano aparecen los puntos de colores sobre ella. En el panel derecho se muestra la seña detectada.

### Módulo administrador
Permite configurar Telegram, ajustar el umbral de confianza y gestionar las señas disponibles.

### Historial de mensajes
Registro de todos los mensajes enviados con su estado.

---

## ¿Qué hago si algo no funciona?

**La cámara no aparece:**  
El navegador puede haberle negado el permiso. Haz clic en el ícono de cámara en la barra de direcciones y permite el acceso.

**El sistema no detecta mi mano:**  
Prueba con mejor iluminación o acerca un poco más la mano a la cámara.

**Las predicciones no son correctas:**  
Baja el umbral de confianza en la pestaña Administrador. También asegúrate de hacer la seña de manera clara y sin mover mucho la mano.

**El mensaje no llega a Telegram:**  
Verifica en la pestaña Administrador que el token y el chat ID estén correctos. Usa el botón "Probar" para verificar la conexión.

---

*Manual de usuario elaborado por Susan Pamela Herrera Monzón — 201612218*