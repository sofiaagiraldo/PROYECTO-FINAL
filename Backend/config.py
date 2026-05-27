"""Rutas y constantes globales del ecosistema."""

from pathlib import Path

NOMBRE_BASE_DATOS = "ruta_optima.db"
NOMBRE_ARCHIVO_PBIX = "RutaOptima.pbix"


def raiz_del_proyecto() -> Path:
    return Path(__file__).resolve().parents[1]


def ruta_base_datos() -> Path:
    return raiz_del_proyecto() / "data" / NOMBRE_BASE_DATOS


def ruta_pbix_esperado() -> Path:
    return raiz_del_proyecto() / "powerbi" / NOMBRE_ARCHIVO_PBIX


def carpeta_export_csv_bi() -> Path:
    return raiz_del_proyecto() / "powerbi" / "csv_refresh"


def archivo_instrucciones_conexion_bd() -> Path:
    """Archivo texto con path absoluto al .db para actualizar datos en Power BI."""
    return raiz_del_proyecto() / "powerbi" / "CADENA_BASE_DATOS.txt"
