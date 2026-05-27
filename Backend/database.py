"""
database.py
Módulo de base de datos SQLite con Esquema Estrella para Ruta-Óptima.
Tablas:
  - dim_destino     (Dimensión)
  - dim_tipo_paquete (Dimensión)
  - dim_camion      (Dimensión)
  - fact_envio      (Tabla de Hechos)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ruta_optima.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_tablas():
    conn = get_connection()
    cur = conn.cursor()

    # ── Dimensión Destino ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_destino (
            id_destino   INTEGER PRIMARY KEY AUTOINCREMENT,
            ciudad       TEXT    NOT NULL,
            zona         TEXT    NOT NULL,
            distancia_km REAL    NOT NULL
        )
    """)

    # ── Dimensión Tipo de Paquete ──────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_tipo_paquete (
            id_tipo      INTEGER PRIMARY KEY AUTOINCREMENT,
            clasificacion TEXT   NOT NULL,
            peso_min_kg  REAL    NOT NULL,
            peso_max_kg  REAL    NOT NULL,
            tarifa_base  REAL    NOT NULL
        )
    """)

    # ── Dimensión Camión ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_camion (
            id_camion    INTEGER PRIMARY KEY AUTOINCREMENT,
            placa        TEXT    NOT NULL UNIQUE,
            capacidad_kg REAL    NOT NULL,
            conductor    TEXT    NOT NULL
        )
    """)

    # ── Tabla de Hechos: Envío ─────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_envio (
            id_envio     INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_envio  TEXT    NOT NULL,
            remitente    TEXT    NOT NULL,
            peso_kg      REAL    NOT NULL,
            costo_envio  REAL    NOT NULL,
            id_destino   INTEGER NOT NULL,
            id_tipo      INTEGER NOT NULL,
            id_camion    INTEGER NOT NULL,
            FOREIGN KEY (id_destino) REFERENCES dim_destino(id_destino),
            FOREIGN KEY (id_tipo)    REFERENCES dim_tipo_paquete(id_tipo),
            FOREIGN KEY (id_camion)  REFERENCES dim_camion(id_camion)
        )
    """)

    conn.commit()
    conn.close()


def insertar_datos_semilla():
    """Inserta al menos 5 registros por tabla si están vacías."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Semillas dim_destino ───────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM dim_destino")
    if cur.fetchone()[0] == 0:
        destinos = [
            ("Bogotá Centro",   "Zona 1",  5.0),
            ("Bogotá Norte",    "Zona 2", 12.0),
            ("Bogotá Sur",      "Zona 3", 18.0),
            ("Medellín",        "Zona 4", 420.0),
            ("Cali",            "Zona 5", 460.0),
            ("Barranquilla",    "Zona 6", 1000.0),
            ("Cartagena",       "Zona 7", 1030.0),
        ]
        cur.executemany(
            "INSERT INTO dim_destino (ciudad, zona, distancia_km) VALUES (?,?,?)",
            destinos
        )

    # ── Semillas dim_tipo_paquete ──────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM dim_tipo_paquete")
    if cur.fetchone()[0] == 0:
        tipos = [
            ("Documento",   0.0,  0.5,  5000.0),
            ("Paquetería",  0.5,  5.0, 12000.0),
            ("Carga",       5.0, 30.0, 25000.0),
            ("Carga Pesada",30.0,100.0, 60000.0),
            ("Sobredimensionado", 100.0, 9999.0, 120000.0),
        ]
        cur.executemany(
            "INSERT INTO dim_tipo_paquete (clasificacion, peso_min_kg, peso_max_kg, tarifa_base) VALUES (?,?,?,?)",
            tipos
        )

    # ── Semillas dim_camion ────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM dim_camion")
    if cur.fetchone()[0] == 0:
        camiones = [
            ("ABC-123", 1000.0, "Carlos Pérez"),
            ("XYZ-456", 2000.0, "Andrés Torres"),
            ("QRS-789", 5000.0, "Laura Gómez"),
            ("LMN-321", 1500.0, "Pedro Ruiz"),
            ("OPQ-654", 3000.0, "María López"),
        ]
        cur.executemany(
            "INSERT INTO dim_camion (placa, capacidad_kg, conductor) VALUES (?,?,?)",
            camiones
        )

    # ── Semillas fact_envio ────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM fact_envio")
    if cur.fetchone()[0] == 0:
        envios = [
            ("2026-01-10", "Empresa A",    0.3,   6500.0,  1, 1, 1),
            ("2026-01-11", "Empresa B",    2.5,  18000.0,  2, 2, 2),
            ("2026-01-12", "Empresa C",   10.0,  47500.0,  4, 3, 3),
            ("2026-01-13", "Persona D",    0.1,   5500.0,  1, 1, 1),
            ("2026-01-14", "Empresa E",   50.0, 110000.0,  5, 4, 4),
            ("2026-02-01", "Empresa F",    3.2,  20800.0,  3, 2, 2),
            ("2026-02-05", "Persona G",    0.4,   5200.0,  2, 1, 5),
            ("2026-02-10", "Empresa H",   25.0,  75000.0,  6, 3, 3),
            ("2026-03-01", "Empresa I",    8.0,  40000.0,  7, 3, 4),
            ("2026-03-15", "Persona J",    0.2,   6000.0,  1, 1, 1),
        ]
        cur.executemany(
            """INSERT INTO fact_envio
               (fecha_envio, remitente, peso_kg, costo_envio,
                id_destino, id_tipo, id_camion)
               VALUES (?,?,?,?,?,?,?)""",
            envios
        )

    conn.commit()
    conn.close()


def inicializar_db():
    crear_tablas()
    insertar_datos_semilla()


# ── Helpers CRUD ───────────────────────────────────────────────────────────────

def obtener_todos_envios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id_envio, f.fecha_envio, f.remitente, f.peso_kg,
               f.costo_envio, d.ciudad, t.clasificacion, c.placa
        FROM fact_envio f
        JOIN dim_destino     d ON f.id_destino = d.id_destino
        JOIN dim_tipo_paquete t ON f.id_tipo    = t.id_tipo
        JOIN dim_camion       c ON f.id_camion  = c.id_camion
        ORDER BY f.peso_kg ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def insertar_envio(fecha, remitente, peso_kg, id_destino, id_camion):
    """Clasifica automáticamente y calcula costo. Retorna id del nuevo envío."""
    conn = get_connection()
    cur = conn.cursor()

    # Clasificar tipo por peso
    cur.execute("""
        SELECT id_tipo, tarifa_base
        FROM dim_tipo_paquete
        WHERE ? >= peso_min_kg AND ? < peso_max_kg
        ORDER BY peso_min_kg ASC
        LIMIT 1
    """, (peso_kg, peso_kg))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"No se encontró clasificación para peso {peso_kg} kg")
    id_tipo, tarifa_base = row

    # Obtener distancia del destino
    cur.execute("SELECT distancia_km FROM dim_destino WHERE id_destino=?", (id_destino,))
    dist_row = cur.fetchone()
    if not dist_row:
        conn.close()
        raise ValueError("Destino no encontrado")
    distancia_km = dist_row[0]

    # Costo = tarifa_base + (distancia_km * 50 * peso_kg)
    costo = tarifa_base + (distancia_km * 50 * peso_kg)

    cur.execute("""
        INSERT INTO fact_envio
        (fecha_envio, remitente, peso_kg, costo_envio, id_destino, id_tipo, id_camion)
        VALUES (?,?,?,?,?,?,?)
    """, (fecha, remitente, peso_kg, costo, id_destino, id_tipo, id_camion))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id, costo


def actualizar_envio(id_envio, fecha, remitente, peso_kg, id_destino, id_camion):
    conn = get_connection()
    cur = conn.cursor()

    # Recalcular tipo y costo
    cur.execute("""
        SELECT id_tipo, tarifa_base FROM dim_tipo_paquete
        WHERE ? >= peso_min_kg AND ? < peso_max_kg
        LIMIT 1
    """, (peso_kg, peso_kg))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"No se encontró clasificación para peso {peso_kg} kg")
    id_tipo, tarifa_base = row

    cur.execute("SELECT distancia_km FROM dim_destino WHERE id_destino=?", (id_destino,))
    distancia_km = cur.fetchone()[0]
    costo = tarifa_base + (distancia_km * 50 * peso_kg)

    cur.execute("""
        UPDATE fact_envio
        SET fecha_envio=?, remitente=?, peso_kg=?, costo_envio=?,
            id_destino=?, id_tipo=?, id_camion=?
        WHERE id_envio=?
    """, (fecha, remitente, peso_kg, costo, id_destino, id_tipo, id_camion, id_envio))
    conn.commit()
    conn.close()


def eliminar_envio(id_envio):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM fact_envio WHERE id_envio=?", (id_envio,))
    conn.commit()
    conn.close()


def obtener_destinos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_destino, ciudad, zona, distancia_km FROM dim_destino")
    rows = cur.fetchall()
    conn.close()
    return rows


def obtener_camiones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_camion, placa, conductor FROM dim_camion")
    rows = cur.fetchall()
    conn.close()
    return rows
