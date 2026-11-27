#!/usr/bin/env python3
"""
Servidor en tiempo real para Dinámica del Dado COOSAJO MICOOPE:
- /       -> index.html (MONITOR para TV / Proyector)
- /jugar  -> jugar.html (Juego del dado móvil)
- /admin  -> admin.html (Panel de control y reseteo de conteo)

Control de Dispositivos Únicos:
Cuenta a cada persona (dispositivo) una sola vez en el total de participantes,
permitiendo que la misma persona lance y escanee cuantas veces quiera.
"""

import os
import sys
import json
import time
import socket
from queue import Queue
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)

dispositivos_unicos = set()

estado = {
    "probabilidades": {
        "gracias": 75,
        "promocional": 18,
        "premio": 7
    },
    "estadisticas": {
        "personas_unicas": 0,
        "total_lanzamientos": 0,
        "gracias": 0,
        "promocional": 0,
        "premio": 0
    },
    "ultimo_evento": None,
    "historial": []
}

suscriptores_visor = []


def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def notificar_visores(data):
    for q in list(suscriptores_visor):
        try:
            q.put_nowait(data)
        except Exception:
            suscriptores_visor.remove(q)


@app.after_request
def cors(res):
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type"
    res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return res


# --- RUTAS DE PÁGINAS ---

@app.route("/")
@app.route("/monitor")
def ruta_monitor():
    """INDEX: El MONITOR para la pantalla de TV / Proyector."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/jugar")
@app.route("/dado")
def ruta_jugar():
    """JUGAR: Donde están los datos y el dado rodante del participante."""
    return send_from_directory(BASE_DIR, "jugar.html")


@app.route("/admin")
def ruta_admin():
    """ADMIN: Panel para resetear el conteo y ajustar probabilidades."""
    return send_from_directory(BASE_DIR, "admin.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# --- APIS DE SINCRONIZACIÓN Y RESET ---

@app.route("/api/config", methods=["GET", "POST"])
def get_config():
    if request.method == "POST":
        data = request.json or {}
        if "probabilidades" in data:
            estado["probabilidades"].update(data["probabilidades"])
        return jsonify({"status": "ok", "probabilidades": estado["probabilidades"]})

    ip = obtener_ip_local()
    return jsonify({
        "probabilidades": estado["probabilidades"],
        "estadisticas": estado["estadisticas"],
        "ip_local": ip,
        "url_juego": f"http://{ip}:5050/jugar",
        "url_monitor": f"http://{ip}:5050/",
        "url_admin": f"http://{ip}:5050/admin"
    })


@app.route("/api/reset", methods=["POST"])
def reset_estadisticas():
    """Resetea el conteo a 0 desde el admin y lo refleja en el monitor."""
    dispositivos_unicos.clear()
    estado["estadisticas"] = {
        "personas_unicas": 0,
        "total_lanzamientos": 0,
        "gracias": 0,
        "promocional": 0,
        "premio": 0
    }
    estado["ultimo_evento"] = None
    estado["historial"] = []

    evento = {
        "tipo": "RESET_ESTADISTICAS",
        "timestamp": time.strftime("%H:%M:%S")
    }
    notificar_visores(evento)
    return jsonify({"status": "ok", "message": "Conteo reseteado a cero"})


@app.route("/api/tirada", methods=["POST"])
def registrar_tirada():
    data = request.json or {}
    resultado = data.get("resultado", "GRACIAS POR PARTICIPAR")
    folio = data.get("folio", "PR-0000")
    device_id = data.get("device_id", "anonimo")
    tirada_id = data.get("tirada_id", f"t_{device_id}_{int(time.time())}_{folio}")
    timestamp = time.strftime("%H:%M:%S")

    # Registro de dispositivo único (una persona = un conteo en personas)
    es_persona_nueva = device_id not in dispositivos_unicos
    dispositivos_unicos.add(device_id)

    estado["estadisticas"]["personas_unicas"] = len(dispositivos_unicos)
    estado["estadisticas"]["total_lanzamientos"] += 1

    if resultado == "PREMIO":
        estado["estadisticas"]["premio"] += 1
    elif resultado == "PROMOCIONAL":
        estado["estadisticas"]["promocional"] += 1
    else:
        estado["estadisticas"]["gracias"] += 1

    evento = {
        "tipo": "NUEVA_TIRADA",
        "tirada_id": tirada_id,
        "resultado": resultado,
        "folio": folio,
        "device_id": device_id,
        "es_persona_nueva": es_persona_nueva,
        "timestamp": timestamp,
        "estadisticas": estado["estadisticas"]
    }

    estado["ultimo_evento"] = evento
    estado["historial"].insert(0, evento)
    if len(estado["historial"]) > 50:
        estado["historial"].pop()

    notificar_visores(evento)
    return jsonify({"status": "ok", "evento": evento})


@app.route("/api/iniciando_escaneo", methods=["POST"])
def avisar_escaneo():
    data = request.json or {}
    evento = {
        "tipo": "INICIANDO_SORTEO",
        "device_id": data.get("device_id"),
        "timestamp": time.strftime("%H:%M:%S")
    }
    notificar_visores(evento)
    return jsonify({"status": "ok"})


@app.route("/api/stream")
def sse_stream():
    def event_stream():
        q = Queue()
        suscriptores_visor.append(q)
        try:
            yield f"data: {json.dumps({'tipo': 'CONECTADO', 'estadisticas': estado['estadisticas'], 'ultimo_evento': estado['ultimo_evento']})}\n\n"
            while True:
                msg = q.get()
                yield f"data: {json.dumps(msg)}\n\n"
        except GeneratorExit:
            if q in suscriptores_visor:
                suscriptores_visor.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")


def main():
    ip = obtener_ip_local()
    port = 5050
    print("\n" + "=" * 65)
    print("✨ DINÁMICA DEL DADO COOSAJO MICOOPE - SERVIDOR INICIADO ✨")
    print("=" * 65)
    print(f"🖥️  MONITOR (TV / Pantalla):       http://localhost:{port}/  (o /monitor)")
    print(f"📱 PARTICIPANTES (Escanear):     http://{ip}:{port}/jugar")
    print(f"⚙️  ADMIN (Resetear conteo):       http://localhost:{port}/admin")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
