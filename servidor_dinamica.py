#!/usr/bin/env python3
"""
Servidor en tiempo real para Dinámica de Sorteo QR y Visor de Pantalla (TV / Proyector)
Sincroniza en vivo los escaneos de los celulares con la pantalla grande.
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

# Estado global en memoria
estado = {
    "probabilidades": {
        "gracias": 75,
        "promocional": 18,
        "premio": 7
    },
    "estadisticas": {
        "total": 0,
        "gracias": 0,
        "promocional": 0,
        "premio": 0
    },
    "ultimo_evento": None,
    "historial": []
}

# Clientes suscritos al visor (Server-Sent Events)
suscriptores_visor = []


def obtener_ip_local():
    """Detecta la IP local de la computadora en la red Wi-Fi / LAN."""
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
    """Envía un evento en tiempo real a todas las pantallas de TV conectadas."""
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
@app.route("/jugar")
def ruta_jugar():
    """Página que abre el usuario en su celular al escanear el QR."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/visor")
def ruta_visor():
    """Pantalla gigante para proyectar en TV o transmisión en vivo."""
    return send_from_directory(BASE_DIR, "visor.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# --- API DE SINCRONIZACIÓN EN TIEMPO REAL ---

@app.route("/api/config", methods=["GET"])
def get_config():
    ip = obtener_ip_local()
    return jsonify({
        "probabilidades": estado["probabilidades"],
        "estadisticas": estado["estadisticas"],
        "ip_local": ip,
        "url_juego": f"http://{ip}:5050/jugar"
    })


@app.route("/api/tirada", methods=["POST"])
def registrar_tirada():
    """Llamado por el celular tan pronto se sortea automáticamente."""
    data = request.json or {}
    resultado = data.get("resultado", "GRACIAS POR PARTICIPAR")
    folio = data.get("folio", "PR-0000")
    timestamp = time.strftime("%H:%M:%S")

    estado["estadisticas"]["total"] += 1
    if resultado == "PREMIO":
        estado["estadisticas"]["premio"] += 1
    elif resultado == "PROMOCIONAL":
        estado["estadisticas"]["promocional"] += 1
    else:
        estado["estadisticas"]["gracias"] += 1

    evento = {
        "tipo": "NUEVA_TIRADA",
        "resultado": resultado,
        "folio": folio,
        "timestamp": timestamp,
        "estadisticas": estado["estadisticas"]
    }

    estado["ultimo_evento"] = evento
    estado["historial"].insert(0, evento)
    if len(estado["historial"]) > 20:
        estado["historial"].pop()

    # Notificar a los visores de TV en tiempo real
    notificar_visores(evento)

    return jsonify({"status": "ok", "evento": evento})


@app.route("/api/iniciando_escaneo", methods=["POST"])
def avisar_escaneo():
    """Avisa a la TV que alguien acaba de abrir la página y empezará a sortear."""
    evento = {
        "tipo": "INICIANDO_SORTEO",
        "timestamp": time.strftime("%H:%M:%S")
    }
    notificar_visores(evento)
    return jsonify({"status": "ok"})


@app.route("/api/stream")
def sse_stream():
    """Server-Sent Events: transmite en vivo cada sorteo a la pantalla de TV."""
    def event_stream():
        q = Queue()
        suscriptores_visor.append(q)
        try:
            # Enviar estado inicial
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
    print("\n" + "=" * 60)
    print("✨ SERVIDOR DE DINÁMICA QR Y VISOR EN VIVO INICIADO ✨")
    print("=" * 60)
    print(f"📱 URL para los Celulares (Escanear):  http://{ip}:{port}/jugar")
    print(f"🖥️  URL para la Pantalla / TV (Visor):  http://localhost:{port}/visor")
    print(f"📁 Modo local en esta máquina:        http://127.0.0.1:{port}/visor")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
