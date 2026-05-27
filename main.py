"""
main.py
Punto de entrada principal del Ecosistema Ruta-Óptima.
Orquesta la inicialización del Backend y el arranque del Frontend.

Uso:
    python main.py
"""

import sys
import os

# Garantizar que el directorio raíz esté en el path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("  🚚  RUTA-ÓPTIMA — Sistema de Clasificación de Envíos")
    print("  Universidad de La Sabana | Programación y Decisiones")
    print("=" * 60)

    # 1. Inicializar base de datos
    print("[1/2] Inicializando base de datos SQLite...")
    try:
        from Backend.database import inicializar_db
        inicializar_db()
        print("      ✅ Base de datos lista.")
    except Exception as e:
        print(f"      ❌ Error al inicializar DB: {e}")
        sys.exit(1)

    # 2. Lanzar la interfaz gráfica
    print("[2/2] Lanzando interfaz gráfica (Tkinter)...")
    try:
        from Frontend.app import iniciar
        iniciar()
    except Exception as e:
        print(f"      ❌ Error al lanzar la interfaz: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
