"""Arranque: logo Tkinter opcional + BD modelo estrella + exportaciones automáticas a BI."""

from __future__ import annotations

from pathlib import Path

from Backend.base_datos import GestorBaseDatosLogistica
from Backend.config import (
    archivo_instrucciones_conexion_bd,
    carpeta_export_csv_bi,
    ruta_base_datos,
)
from Backend.export_bi import escribir_instrucciones_conexion_bd, exportar_star_schema_para_power_bi
from Backend.generar_pbix import asegurar_archivo_pbix
from Backend.logica_reto import ServicioEnvios
from Backend.repositorio_envios import RepositorioManifiesto


def _asegurar_logo_respaldogif_si_falta_profesional(carpeta_frontend: Path) -> None:
    """Solo usa el gif minimo si no esta el PNG entregado (logo_marca.png)."""

    marca = carpeta_frontend / "logo_marca.png"
    if marca.exists():
        return

    gif = carpeta_frontend / "logo.gif"
    if gif.exists():
        return

    gif.write_bytes(
        b"GIF89a\x01\x00\x01\x00\x80\x01\x00"
        b"\x00\x00\x00\xff\xff\xff"
        b"\x21\xf9\x04\x01\x00\x00\x01\x00"
        b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
        b"D\x01\x00\x3b"
    )


def preparar_ecosistema_star_y_bi(carpeta_frontend: Path) -> tuple[GestorBaseDatosLogistica, RepositorioManifiesto]:
    _asegurar_logo_respaldogif_si_falta_profesional(carpeta_frontend)

    motor = ServicioEnvios()
    gestor = GestorBaseDatosLogistica(ruta_base_datos())

    gestor.garantizar_lista(motor)
    sincronizar_artefactos_bi(gestor)

    repositorio = RepositorioManifiesto(gestor, motor)
    return gestor, repositorio


def sincronizar_artefactos_bi(gestor: GestorBaseDatosLogistica) -> None:
    exportar_star_schema_para_power_bi(carpeta_export_csv_bi(), gestor.ruta)
    escribir_instrucciones_conexion_bd(archivo_instrucciones_conexion_bd(), gestor.ruta)
    asegurar_archivo_pbix(gestor.ruta)