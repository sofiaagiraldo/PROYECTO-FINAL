"""Gestión SQLite modelo estrella (POO): hechos (envíos urbanos Bogotá) + dimensiones."""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path


class GestorBaseDatosLogistica:
    MIN_FILAS = 5

    def __init__(self, archivo_db: Path) -> None:
        self._path = archivo_db.resolve()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def ruta(self) -> Path:
        return self._path

    def conectar(self) -> sqlite3.Connection:
        cx = sqlite3.connect(self._path)
        cx.row_factory = sqlite3.Row
        cx.execute("PRAGMA foreign_keys = ON")
        return cx

    def filas_tabla(self, tabla: str) -> int:
        with self.conectar() as cx:
            return int(cx.execute(f"SELECT COUNT(*) c FROM {tabla}").fetchone()["c"])

    def requiere_inicializar(self) -> bool:
        esperadas = {"dim_fecha", "dim_zona", "dim_camion", "fact_envio"}
        if not self._path.exists():
            return True
        try:
            with self.conectar() as cx:
                existentes = {
                    r["name"]
                    for r in cx.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                    ).fetchall()
                }
            if esperadas - existentes:
                return True
            return any(self.filas_tabla(t) < self.MIN_FILAS for t in esperadas)
        except sqlite3.Error:
            return True

    def crear_estructura(self) -> None:
        ddl = """
        DROP TABLE IF EXISTS fact_envio;
        DROP TABLE IF EXISTS dim_fecha;
        DROP TABLE IF EXISTS dim_zona;
        DROP TABLE IF EXISTS dim_camion;

        CREATE TABLE dim_fecha (
            fecha_key INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL UNIQUE,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            nombre_mes TEXT NOT NULL
        );

        CREATE TABLE dim_zona (
            zona_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_localidad TEXT NOT NULL UNIQUE,
            sector_ciudad TEXT NOT NULL,
            factor_tarifa REAL NOT NULL CHECK (factor_tarifa > 0),
            tiempo_acceso_min INTEGER NOT NULL
        );

        CREATE TABLE dim_camion (
            camion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL UNIQUE,
            capacidad_nominal_kg REAL NOT NULL CHECK (capacidad_nominal_kg > 0),
            clase_unidad TEXT NOT NULL
        );

        CREATE TABLE fact_envio (
            envio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_key INTEGER NOT NULL,
            zona_id INTEGER NOT NULL,
            camion_id INTEGER NOT NULL,
            peso_kg REAL NOT NULL CHECK (peso_kg > 0),
            clase_servicio TEXT NOT NULL,
            costo_estimado_cop INTEGER NOT NULL CHECK (costo_estimado_cop > 0),
            kms_recorrido REAL NOT NULL CHECK (kms_recorrido >= 0),
            FOREIGN KEY (fecha_key) REFERENCES dim_fecha (fecha_key),
            FOREIGN KEY (zona_id) REFERENCES dim_zona (zona_id),
            FOREIGN KEY (camion_id) REFERENCES dim_camion (camion_id)
        );

        CREATE INDEX idx_fact_camion ON fact_envio(camion_id);
        CREATE INDEX idx_fact_zona ON fact_envio(zona_id);
        CREATE INDEX idx_fact_fecha ON fact_envio(fecha_key);
        """
        with self.conectar() as cx:
            cx.executescript(ddl)
            cx.commit()

    @staticmethod
    def _fecha_key(d: date) -> int:
        return int(d.strftime("%Y%m%d"))

    def poblar_dimensiones(self, cx: sqlite3.Connection) -> None:
        dias_totales = max(self.MIN_FILAS + 7, 12)
        inicio = date.today() - timedelta(days=dias_totales - 1)

        registros_fecha = []
        for offset in range(dias_totales):
            dia = inicio + timedelta(days=offset)
            registros_fecha.append(
                {
                    "fecha_key": self._fecha_key(dia),
                    "fecha": dia.isoformat(),
                    "anio": dia.year,
                    "mes": dia.month,
                    "nombre_mes": dia.strftime("%B"),
                }
            )

        zonas = [
            ("USAQUÉN", "Norte", 1.02, 31),
            ("CHAPINERO", "Central", 1.08, 26),
            ("PUENTE ARANDA", "Suroccidente", 1.13, 41),
            ("BOSA", "Sur", 1.17, 44),
            ("FONTIBÓN", "Aero / Carga rápida", 1.09, 21),
            ("ENGATIVÁ", "Occidente densidad media", 1.11, 35),
            ("KENNEDY", "Sur alta demanda", 1.15, 49),
            ("SUBA CENTRAL", "Norte ciudadano", 1.06, 40),
            ("SAN CRISTÓBAL OCC.", "Oriente medio", 1.06, 33),
            ("ANTONIO NARIÑO", "Centrosur ciudad", 1.06, 45),
            ("TEUSAQUILLO ANTIGUO", "Central alta mix", 1.06, 25),
            ("BOGOTÁ ANTIGUO", "Centro histórico", 1.14, 18),
        ]

        camiones = [
            ("EOQ982", 850.0, "Urbano chasis liviano"),
            ("FGL441", 3400.0, "Urbano mixto"),
            ("JXP203", 1520.0, "Urbano última milla"),
            ("NKR715", 5200.0, "Urbano pesado"),
            ("QWE118", 1100.0, "Urbano compacto"),
            ("TRS552", 2200.0, "Urbano multi-stop"),
            ("UVZ889", 1800.0, "Urbano standard"),
            ("WXY764", 2500.0, "Urbano mixto express"),
            ("ZZA001", 2100.0, "Urbano rotación"),
            ("ZZA002", 2300.0, "Urbano rotación"),
            ("ZZA003", 2400.0, "Urbano rotación"),
            ("ZZA004", 2600.0, "Urbano rotación"),
        ]

        cx.executemany(
            """
            INSERT INTO dim_fecha (fecha_key, fecha, anio, mes, nombre_mes)
            VALUES (:fecha_key, :fecha, :anio, :mes, :nombre_mes)
            """,
            registros_fecha,
        )
        cx.executemany(
            """
            INSERT INTO dim_zona (nombre_localidad, sector_ciudad, factor_tarifa, tiempo_acceso_min)
            VALUES (?, ?, ?, ?)
            """,
            zonas,
        )
        cx.executemany(
            """
            INSERT INTO dim_camion (placa, capacidad_nominal_kg, clase_unidad)
            VALUES (?, ?, ?)
            """,
            camiones,
        )

    def poblar_hechos_demo(self, cx: sqlite3.Connection, servicio_calculo: object) -> None:
        zonas = list(cx.execute("SELECT zona_id, factor_tarifa FROM dim_zona ORDER BY zona_id").fetchall())
        camiones = list(cx.execute("SELECT camion_id, capacidad_nominal_kg FROM dim_camion ORDER BY camion_id").fetchall())
        fechas = [int(r["fecha_key"]) for r in cx.execute("SELECT fecha_key FROM dim_fecha ORDER BY fecha_key DESC").fetchall()]

        plantillas = [
            (0.35, 8.2),
            (1.2, 12.4),
            (5.8, 15.1),
            (12.5, 18.8),
            (24.3, 22.4),
            (45.0, 27.6),
            (70.0, 35.2),
            (95.0, 44.3),
            (110.0, 49.5),
            (130.0, 55.7),
            (180.0, 66.2),
            (220.0, 77.4),
        ]

        filas: list[tuple] = []
        for idx, (peso_objetivo, kms) in enumerate(plantillas):
            zona = zonas[idx % len(zonas)]
            camion = camiones[idx % len(camiones)]
            cap = float(camion["capacidad_nominal_kg"])
            peso = min(float(peso_objetivo), cap * 0.95)
            if peso <= 0:
                peso = 0.2
            fk = fechas[idx % len(fechas)]

            res = servicio_calculo.cotizar(peso, float(zona["factor_tarifa"]))
            filas.append(
                (
                    fk,
                    int(zona["zona_id"]),
                    int(camion["camion_id"]),
                    round(peso, 3),
                    res.clase_servicio,
                    int(res.costo_estimado_cop),
                    round(kms, 2),
                )
            )

        cx.executemany(
            """
            INSERT INTO fact_envio (
                fecha_key, zona_id, camion_id, peso_kg,
                clase_servicio, costo_estimado_cop, kms_recorrido
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            filas,
        )

    def garantizar_lista(self, servicio_calculo: object) -> None:
        if not self.requiere_inicializar():
            return
        self.crear_estructura()
        cx = self.conectar()
        try:
            self.poblar_dimensiones(cx)
            self.poblar_hechos_demo(cx, servicio_calculo)
            cx.commit()
        finally:
            cx.close()
