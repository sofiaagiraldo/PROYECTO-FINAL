"""Consultas agregadas para el dashboard operativo (Tkinter)."""

from __future__ import annotations

from typing import Any

from Backend.base_datos import GestorBaseDatosLogistica


def resumen_kpis(gestor: GestorBaseDatosLogistica) -> dict[str, float | int]:
    cx = gestor.conectar()
    try:
        fila = cx.execute(
            """
            SELECT
              COUNT(*) AS total_envios,
              COALESCE(SUM(costo_estimado_cop), 0) AS costo_total_cop,
              COALESCE(AVG(peso_kg), 0) AS peso_promedio_kg,
              COALESCE(SUM(kms_recorrido), 0) AS kms_totales
            FROM fact_envio
            """
        ).fetchone()
    finally:
        cx.close()
    return {
        "total_envios": int(fila["total_envios"]),
        "costo_total_cop": int(fila["costo_total_cop"]),
        "peso_promedio_kg": float(fila["peso_promedio_kg"]),
        "kms_totales": float(fila["kms_totales"]),
    }


def peso_por_clase(gestor: GestorBaseDatosLogistica) -> list[tuple[str, float]]:
    cx = gestor.conectar()
    try:
        filas = cx.execute(
            """
            SELECT clase_servicio AS etiqueta, SUM(peso_kg) AS valor
            FROM fact_envio
            GROUP BY clase_servicio
            ORDER BY valor DESC
            """
        ).fetchall()
    finally:
        cx.close()
    return [(str(r["etiqueta"]), float(r["valor"])) for r in filas]


def costo_medio_por_fecha(gestor: GestorBaseDatosLogistica, limite: int = 12) -> list[tuple[str, float]]:
    cx = gestor.conectar()
    try:
        filas = cx.execute(
            """
            SELECT d.fecha AS etiqueta, AVG(f.costo_estimado_cop) AS valor
            FROM fact_envio f
            JOIN dim_fecha d ON d.fecha_key = f.fecha_key
            GROUP BY d.fecha
            ORDER BY d.fecha ASC
            LIMIT ?
            """,
            (int(limite),),
        ).fetchall()
    finally:
        cx.close()
    return [(str(r["etiqueta"]), float(r["valor"])) for r in filas]


def envios_por_zona(gestor: GestorBaseDatosLogistica, limite: int = 8) -> list[tuple[str, float]]:
    cx = gestor.conectar()
    try:
        filas = cx.execute(
            """
            SELECT z.nombre_localidad AS etiqueta, COUNT(*) AS valor
            FROM fact_envio f
            JOIN dim_zona z ON z.zona_id = f.zona_id
            GROUP BY z.nombre_localidad
            ORDER BY valor DESC
            LIMIT ?
            """,
            (int(limite),),
        ).fetchall()
    finally:
        cx.close()
    return [(str(r["etiqueta"]), float(r["valor"])) for r in filas]


def puntos_kms_vs_peso(gestor: GestorBaseDatosLogistica) -> list[dict[str, Any]]:
    cx = gestor.conectar()
    try:
        filas = cx.execute(
            """
            SELECT f.peso_kg, f.kms_recorrido, z.nombre_localidad AS zona
            FROM fact_envio f
            JOIN dim_zona z ON z.zona_id = f.zona_id
            ORDER BY f.envio_id
            """
        ).fetchall()
    finally:
        cx.close()
    return [
        {"peso": float(r["peso_kg"]), "kms": float(r["kms_recorrido"]), "zona": str(r["zona"])}
        for r in filas
    ]


def paquete_dashboard(gestor: GestorBaseDatosLogistica) -> dict[str, Any]:
    return {
        "kpis": resumen_kpis(gestor),
        "peso_clase": peso_por_clase(gestor),
        "costo_fecha": costo_medio_por_fecha(gestor),
        "envios_zona": envios_por_zona(gestor),
        "scatter": puntos_kms_vs_peso(gestor),
    }
