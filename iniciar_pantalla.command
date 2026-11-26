#!/bin/bash
# Doble clic para iniciar el Servidor de Dinámica QR y Visor para TV
cd "$(dirname "$0")"
echo "=========================================================="
echo "✨ INICIANDO SERVIDOR DE DINÁMICA QR Y VISOR DE TV ✨"
echo "=========================================================="
echo ""

if [ -f "../mi-proyecto/venv/bin/python3" ]; then
    ../mi-proyecto/venv/bin/python3 servidor_dinamica.py
elif [ -f "./venv/bin/python3" ]; then
    ./venv/bin/python3 servidor_dinamica.py
else
    python3 servidor_dinamica.py
fi
