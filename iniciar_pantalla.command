#!/bin/bash
# Doble clic para iniciar el Servidor de Dinámica QR y Visor para TV
cd "$(dirname "$0")"
echo "=========================================================="
echo "✨ INICIANDO SERVIDOR DE DINÁMICA QR Y VISOR DE TV ✨"
echo "=========================================================="
echo ""
echo "Conectando..."
../venv/bin/python3 servidor_dinamica.py
