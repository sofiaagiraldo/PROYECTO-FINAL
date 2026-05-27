"""Exportación SQLite → CSV y archivo de texto con la ruta de la BD (Power BI Desktop)."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

_TABLAS_STAR = ["dim_fecha", "dim_zona", "dim_camion", "fact_envio"]


def exportar_star_schema_para_power_bi(carpeta_destino_csv: Path, archivo_sqlite: Path) -> None:
    carpeta_destino_csv.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(str(archivo_sqlite))
    try:
        for tabla in _TABLAS_STAR:
            cur = conexion.execute(f'SELECT * FROM "{tabla}" ORDER BY ROWID')
            columnas = [d[0] for d in cur.description]
            filas = cur.fetchall()
            destino_csv = carpeta_destino_csv / f"{tabla}.csv"

            with destino_csv.open("w", newline="", encoding="utf-8") as salida_txt:
                w = csv.writer(salida_txt)
                w.writerow(columnas)
                w.writerows(filas)
    finally:
        conexion.close()


def escribir_instrucciones_conexion_bd(archivo_salida: Path, archivo_db: Path) -> None:
    texto = (
        "Ruta absoluta SQLite (copiar/pegar como referencia rápida al enlazar desde Power BI):\n"
        f"{archivo_db.resolve()}\n\n"
        "CSV paralelos refrescados cada arranque: carpeta sibling `csv_refresh/` (ver `bootstrap`).\n"
    )
    archivo_salida.write_text(texto, encoding="utf-8")
