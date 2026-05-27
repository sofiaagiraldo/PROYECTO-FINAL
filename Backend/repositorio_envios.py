"""Acceso OO a `fact_envio` con reglas del Reto 1 (clasificación + costo)."""

from __future__ import annotations

from typing import Any

from Backend.base_datos import GestorBaseDatosLogistica
from Backend.entidades import RegistroEnvio
from Backend.logica_reto import ServicioEnvios


class RepositorioManifiesto:
    """CRUD central del manifiesto logístico (tabla de hechos)."""

    def __init__(self, bd: GestorBaseDatosLogistica, motor: ServicioEnvios | None = None) -> None:
        self.bd = bd
        self._motor = motor or ServicioEnvios()

    def combos_zonas_camiones_fechas(
        self,
    ) -> tuple[list[tuple[int, str]], list[tuple[int, str]], list[tuple[int, str]]]:
        cx = self.bd.conectar()
        try:
            zonas = cx.execute(
                """
                SELECT zona_id, nombre_localidad, sector_ciudad
                FROM dim_zona ORDER BY nombre_localidad
                """
            ).fetchall()
            camiones = cx.execute(
                """
                SELECT camion_id, placa, capacidad_nominal_kg, clase_unidad
                FROM dim_camion ORDER BY placa
                """
            ).fetchall()
            fechas = cx.execute(
                "SELECT fecha_key, fecha FROM dim_fecha ORDER BY fecha_key DESC LIMIT 720"
            ).fetchall()
        finally:
            cx.close()

        z_combo = [(int(z["zona_id"]), f"{z['nombre_localidad']} ({z['sector_ciudad']})") for z in zonas]
        c_combo = [
            (int(c["camion_id"]), f"{c['placa']} — cap {float(c['capacidad_nominal_kg']):,.0f} kg")
            for c in camiones
        ]
        f_combo = [(int(f["fecha_key"]), str(f["fecha"])) for f in fechas]
        return z_combo, c_combo, f_combo

    def factor_tarifa_zona(self, zona_id: int) -> float:
        cx = self.bd.conectar()
        try:
            fila = cx.execute(
                "SELECT factor_tarifa FROM dim_zona WHERE zona_id = ? LIMIT 1", (int(zona_id),)
            ).fetchone()
        finally:
            cx.close()
        if not fila:
            raise LookupError(f"No existe la zona #{zona_id}.")
        return float(fila["factor_tarifa"])

    def capacidad_camion(self, camion_id: int) -> float:
        cx = self.bd.conectar()
        try:
            fila = cx.execute(
                "SELECT capacidad_nominal_kg FROM dim_camion WHERE camion_id = ? LIMIT 1",
                (int(camion_id),),
            ).fetchone()
        finally:
            cx.close()
        if not fila:
            raise LookupError(f"No existe el camión #{camion_id}.")
        return float(fila["capacidad_nominal_kg"])

    def crear_envio(self, registro: RegistroEnvio) -> int:
        if registro.envio_id is not None:
            raise ValueError("Un envío nuevo no debe traer ID prefijado.")

        factor = self.factor_tarifa_zona(registro.zona_id)
        cap = self.capacidad_camion(registro.camion_id)
        peso = float(registro.peso_kg)
        if peso > cap:
            raise ValueError(f"El peso ({peso} kg) excede la capacidad nominal ({cap} kg).")

        res = self._motor.cotizar(peso, factor)
        kms = round(12.0 + res.costo_estimado_cop / 45_000.0, 2)

        cx = self.bd.conectar()
        try:
            cur = cx.execute(
                """
                INSERT INTO fact_envio (
                    fecha_key, zona_id, camion_id,
                    peso_kg, clase_servicio,
                    costo_estimado_cop, kms_recorrido
                )
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    int(registro.fecha_key),
                    int(registro.zona_id),
                    int(registro.camion_id),
                    round(peso, 4),
                    res.clase_servicio,
                    int(res.costo_estimado_cop),
                    kms,
                ),
            )
            cx.commit()
            nuevo_id = int(cur.lastrowid)
        finally:
            cx.close()
        return nuevo_id

    def listar_manifiesto_orden_peso(self) -> list[dict[str, Any]]:
        cx = self.bd.conectar()
        try:
            filas = cx.execute(
                """
                SELECT
                  f.envio_id,
                  d.fecha,
                  z.nombre_localidad,
                  c.placa,
                  f.peso_kg,
                  f.clase_servicio,
                  f.costo_estimado_cop,
                  f.kms_recorrido
                FROM fact_envio f
                JOIN dim_fecha d ON d.fecha_key = f.fecha_key
                JOIN dim_zona z ON z.zona_id = f.zona_id
                JOIN dim_camion c ON c.camion_id = f.camion_id
                ORDER BY f.peso_kg DESC, f.envio_id ASC
                """
            ).fetchall()
            return [dict(r) for r in filas]
        finally:
            cx.close()

    def actualizar_envio(self, registro: RegistroEnvio) -> None:
        if registro.envio_id is None:
            raise ValueError("Falta envio_id para actualizar.")

        factor = self.factor_tarifa_zona(registro.zona_id)
        cap = self.capacidad_camion(registro.camion_id)
        peso = float(registro.peso_kg)
        if peso > cap:
            raise ValueError("Peso por encima de la capacidad del camión seleccionado.")

        res = self._motor.cotizar(peso, factor)
        kms = round(11.5 + res.costo_estimado_cop / 46_000.0, 2)

        cx = self.bd.conectar()
        try:
            afectadas = cx.execute(
                """
                UPDATE fact_envio SET
                  fecha_key = ?,
                  zona_id = ?,
                  camion_id = ?,
                  peso_kg = ?,
                  clase_servicio = ?,
                  costo_estimado_cop = ?,
                  kms_recorrido = ?
                WHERE envio_id = ?
                """,
                (
                    int(registro.fecha_key),
                    int(registro.zona_id),
                    int(registro.camion_id),
                    round(peso, 4),
                    res.clase_servicio,
                    int(res.costo_estimado_cop),
                    kms,
                    int(registro.envio_id),
                ),
            ).rowcount
            cx.commit()
        finally:
            cx.close()
        if int(afectadas) != 1:
            raise LookupError("No se encontró el envío a actualizar.")

    def borrar_envio(self, envio_id: int) -> None:
        cx = self.bd.conectar()
        try:
            afectadas = cx.execute("DELETE FROM fact_envio WHERE envio_id = ?", (int(envio_id),)).rowcount
            cx.commit()
        finally:
            cx.close()
        if int(afectadas) != 1:
            raise LookupError("No se pudo borrar (ID inexistente).")

    def obtener_envio(self, envio_id: int) -> RegistroEnvio:
        cx = self.bd.conectar()
        try:
            fila = cx.execute(
                """
                SELECT envio_id, fecha_key, zona_id, camion_id, peso_kg
                  FROM fact_envio
                 WHERE envio_id = ?
                 LIMIT 1
                """,
                (int(envio_id),),
            ).fetchone()
        finally:
            cx.close()
        if not fila:
            raise LookupError("Envío inexistente.")
        return RegistroEnvio(
            envio_id=int(fila["envio_id"]),
            fecha_key=int(fila["fecha_key"]),
            zona_id=int(fila["zona_id"]),
            camion_id=int(fila["camion_id"]),
            peso_kg=float(fila["peso_kg"]),
        )
