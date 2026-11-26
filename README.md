# 📱 Dinámica QR Interactiva y Visor en Vivo para TV

Solución integral lista para eventos y stands con la paleta de colores y estilo oficial (Azul Real `#0040c0`, Verde Neón `#00e626`, ondas y estrellas brillantes).

---

## ⚡ ¿Cómo Funciona la Dinámica?

1. **Escaneo Automático:**
   * La persona apunta su celular al **Código QR**.
   * **¡Arranca de inmediato!** No necesita darle clic a ningún botón; en cuanto carga la página, la ruleta empieza a girar automáticamente.
2. **Sincronización en Vivo con la Pantalla (TV / Proyector):**
   * Mientras el celular de la persona gira la ruleta, **la pantalla de TV que estás proyectando reacciona al mismo tiempo en tiempo real**.
   * Al revelar el resultado, la pantalla grande anuncia en letras gigantes: **¡PREMIO!** (con confeti y fanfarria), **PROMOCIONAL** o **GRACIAS POR PARTICIPAR**.
3. **Probabilidades Ponderadas:**
   * **75%**: *Gracias por participar* (Sale la gran mayoría de veces).
   * **18%**: *Promocional* (Souvenirs / artículos).
   * **7%**: *Premio* (Premio mayor).

---

## 🚀 Cómo Usarlo

### Opción A: Prueba Rápida en tu Mac (Sin configurar nada)
1. Abre en tu navegador la pantalla de televisión:
   👉 **[`visor.html`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/visor.html)** (Pásalo a pantalla completa o a tu TV/Monitor con HDMI).
2. Abre en otra pestaña o ventana el juego del celular:
   👉 **[`index.html`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/index.html)**.
3. Verás que en cuanto abre `index.html`, **empieza a sortear solo** y el visor de la pantalla reacciona en vivo simultáneamente.

---

### Opción B: Evento en Vivo (Celulares en la red Wi-Fi y Pantalla Gigante)
1. En la carpeta `dinamica_qr`, haz doble clic sobre el archivo ejecutable:
   👉 **[`iniciar_pantalla.command`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/iniciar_pantalla.command)**.
2. Se abrirá una ventana que te indicará la dirección IP de tu computadora (por ejemplo: `http://192.168.1.50:5050`).
3. En tu pantalla grande o TV abre:
   `http://localhost:5050/visor`
4. ¡Cualquier persona que escanee el QR desde su teléfono en la misma red Wi-Fi participará automáticamente y se verá reflejado en la pantalla de TV al instante!

---

## 📁 Archivos Disponibles

* 🖥️ **[`visor.html`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/visor.html)**: Pantalla 16:9 para proyector o televisor.
* 📱 **[`index.html`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/index.html)**: Vista para el teléfono del usuario (auto-arranque sin clics).
* ⚙️ **[`servidor_dinamica.py`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/servidor_dinamica.py)**: Servidor en tiempo real con Server-Sent Events.
* 📦 **[`codigos_qr_generados/`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/mi-proyecto/dinamica_qr/codigos_qr_generados/)**: Carpeta con los códigos QR en PNG transparente y SVG vectorial.
