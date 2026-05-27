#!/usr/bin/env bash
# Arranque local: artefactos BI + ventana Tkinter con dashboard.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH=.

echo "=== Ruta Óptima — arranque local ==="
echo ""

if [[ ! -x .venv/bin/python3 ]]; then
  echo ">> Paso recomendado: crear entorno e instalar dependencias"
  echo "   python3 -m venv .venv"
  echo "   source .venv/bin/activate"
  echo "   pip install -r requirements.txt"
  echo ""
else
  echo ">> Regenerando CSV, CADENA_BASE_DATOS.txt y RutaOptima.pbix..."
  .venv/bin/python3 -c "
from Backend.base_datos import GestorBaseDatosLogistica
from Backend.config import ruta_base_datos, ruta_pbix_esperado
from Backend.bootstrap import sincronizar_artefactos_bi
g = GestorBaseDatosLogistica(ruta_base_datos())
sincronizar_artefactos_bi(g)
pb = ruta_pbix_esperado()
if pb.exists():
    print('   OK:', pb)
else:
    print('   AVISO: no se generó el .pbix (¿pip install -r requirements.txt?)')
"
  echo ""
fi

echo ">> Abriendo ventana Tkinter (dashboard + CRUD)..."
if /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
  exec /usr/bin/python3 main.py
fi

if [[ -x .venv/bin/python3 ]] && .venv/bin/python3 -c "import tkinter" 2>/dev/null; then
  exec .venv/bin/python3 main.py
fi

echo ""
echo "ERROR: ningún Python con Tkinter."
echo "  macOS:  PYTHONPATH=. /usr/bin/python3 main.py"
echo "  Guía:   INSTRUCCIONES_LOCAL.md"
exit 1
