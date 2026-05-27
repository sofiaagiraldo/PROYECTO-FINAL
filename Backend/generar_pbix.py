"""Genera o actualiza powerbi/RutaOptima.pbix (modelo estrella + medida DAX)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from Backend.config import carpeta_export_csv_bi, ruta_pbix_esperado


def _inferir_tipo(columna: str, filas: list[dict[str, Any]]) -> str:
    for fila in filas:
        valor = fila.get(columna)
        if valor is None:
            continue
        if isinstance(valor, bool):
            return "Boolean"
        if isinstance(valor, int):
            return "Int64"
        if isinstance(valor, float):
            return "Double"
        return "String"
    return "String"


def _cargar_tabla(conexion: sqlite3.Connection, nombre: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    cur = conexion.execute(f'SELECT * FROM "{nombre}" ORDER BY 1')
    columnas = [d[0] for d in cur.description]
    filas = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
    esquema = [{"name": c, "data_type": _inferir_tipo(c, filas)} for c in columnas]
    return filas, esquema


def asegurar_archivo_pbix(archivo_sqlite: Path) -> Path | None:
    """Construye el .pbix si pbix-mcp esta instalado. Devuelve la ruta o None."""

    try:
        from pbix_mcp.builder import PBIXBuilder
    except ImportError:
        return None

    destino = ruta_pbix_esperado()
    destino.parent.mkdir(parents=True, exist_ok=True)
    carpeta_csv = carpeta_export_csv_bi()

    conexion = sqlite3.connect(str(archivo_sqlite))
    conexion.row_factory = sqlite3.Row
    try:
        builder = PBIXBuilder()
        tablas = ["dim_fecha", "dim_zona", "dim_camion", "fact_envio"]
        for tabla in tablas:
            filas, esquema = _cargar_tabla(conexion, tabla)
            csv_abs = (carpeta_csv / f"{tabla}.csv").resolve()
            builder.add_table(
                tabla,
                esquema,
                rows=filas,
                source_csv=str(csv_abs),
            )

        builder.add_relationship("fact_envio", "fecha_key", "dim_fecha", "fecha_key")
        builder.add_relationship("fact_envio", "zona_id", "dim_zona", "zona_id")
        builder.add_relationship("fact_envio", "camion_id", "dim_camion", "camion_id")
        builder.add_measure(
            "fact_envio",
            "Costo Medio COP por Envio",
            "DIVIDE(SUM(fact_envio[costo_estimado_cop]), COUNTROWS(fact_envio), 0)",
        )
        builder.add_measure("fact_envio", "Total Kg", "SUM(fact_envio[peso_kg])")
        builder.add_measure("fact_envio", "Total Kms", "SUM(fact_envio[kms_recorrido])")

        builder.save(str(destino.resolve()))
    finally:
        conexion.close()

    return destino if destino.exists() else None
