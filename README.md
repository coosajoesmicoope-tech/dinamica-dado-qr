# 🎲 Dinámica Interactiva del Dado COOSAJO es MICOOPE

Sistema integral para eventos y dinámicas con dado físico de 6 caras, sincronización en vivo y pantalla de televisión.

---

## 📂 Estructura de los 3 Módulos Separados

| Archivo | Rol | Descripción |
| :--- | :--- | :--- |
| **`index.html`** | 🖥️ **EL MONITOR** | **Pantalla gigante para televisor / proyector** (16:9). Muestra el dado 3D gigante rodando en sincronía en el centro, la fanfarria, el confeti y los marcadores en vivo. **No tiene código QR** (solo dice *"🎲 LANZA EL DADO Y ESCANEA EL QR 🎲"*). |
| **`jugar.html`** | 📱 **DONDE ESTÁN LOS DATOS** | **Página móvil para el participante**. Se abre al escanear la cara del dado que cayó, hace rodar el dado 3D automáticamente y revela el resultado con folio de seguridad. |
| **`admin.html`** | ⚙️ **ADMINISTRADOR** | **Panel de control**. Incluye el botón rojo **"🗑️ RESETEAR CONTEO A 0"**, métricas en vivo, historial detallado de tiradas y control de probabilidades. |

---

## 🚀 Cómo Iniciar y Usar

### 1. Servidor Local en Vivo (Para eventos con Wi-Fi)
Haz doble clic en:
👉 **[`iniciar_pantalla.command`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/dinamica-dado-qr/iniciar_pantalla.command)**

Se iniciará el servidor local y te mostrará:
* 🖥️ **Monitor (TV):** `http://localhost:5050/` (o `index.html`)
* 📱 **Móvil (Participantes):** `http://<TU_IP>:5050/jugar`
* ⚙️ **Admin (Resetear):** `http://localhost:5050/admin`

---

### 2. Uso Directo en tu Mac (Sin servidor, sincronización local)
Puedes abrir directamente en pestañas de tu navegador:
1. 🖥️ **[Abrir Monitor (index.html)](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/dinamica-dado-qr/index.html)**
2. 📱 **[Abrir Juego Móvil (jugar.html)](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/dinamica-dado-qr/jugar.html)**
3. ⚙️ **[Abrir Panel Admin (admin.html)](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/dinamica-dado-qr/admin.html)**

---

## 🖨️ Plantilla Imprimible del Dado de 6 Caras

* **[`plantilla_imprimible_dado_6_caras.png`](file:///Users/sjejacome/Library/CloudStorage/OneDrive-CooperativadeAhorroyCreditoIntegralSanJose/Documentos/dinamica-dado-qr/codigos_qr_generados/plantilla_imprimible_dado_6_caras.png)**: Hoja de 300 DPI lista para imprimir en tamaño carta/A4, recortar los 6 cuadrados y pegarlos en las 6 caras del dado físico.
