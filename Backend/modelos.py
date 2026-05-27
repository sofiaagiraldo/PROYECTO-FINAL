"""
modelos.py
Clases de dominio (POO) para el sistema Ruta-Óptima.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# ── Clases Dimensión ───────────────────────────────────────────────────────────

@dataclass
class Destino:
    """Representa un destino de envío."""
    id_destino: int
    ciudad: str
    zona: str
    distancia_km: float

    def __str__(self):
        return f"{self.ciudad} ({self.zona}) — {self.distancia_km} km"


@dataclass
class TipoPaquete:
    """Clasificación de paquete por peso."""
    id_tipo: int
    clasificacion: str
    peso_min_kg: float
    peso_max_kg: float
    tarifa_base: float

    def __str__(self):
        return (f"{self.clasificacion}: "
                f"{self.peso_min_kg}–{self.peso_max_kg} kg | "
                f"Tarifa base: ${self.tarifa_base:,.0f}")


@dataclass
class Camion:
    """Camión disponible para transporte."""
    id_camion: int
    placa: str
    capacidad_kg: float
    conductor: str

    def __str__(self):
        return f"{self.placa} — {self.conductor} (cap. {self.capacidad_kg} kg)"


# ── Clase de Hechos ────────────────────────────────────────────────────────────

@dataclass
class Envio:
    """
    Representa un envío registrado en el sistema.
    Contiene la lógica de clasificación y cálculo de costo.
    """
    remitente: str
    peso_kg: float
    destino: Destino
    camion: Camion
    fecha_envio: str = field(default_factory=lambda: str(date.today()))
    id_envio: Optional[int] = None
    _tipo_paquete: Optional[TipoPaquete] = field(default=None, init=False, repr=False)
    _costo_envio: Optional[float] = field(default=None, init=False, repr=False)

    # ── Clasificación ──────────────────────────────────────────────────────────
    @staticmethod
    def clasificar(peso_kg: float) -> str:
        """Regla de negocio: clasifica según el peso."""
        if peso_kg < 0.5:
            return "Documento"
        elif peso_kg < 5.0:
            return "Paquetería"
        elif peso_kg < 30.0:
            return "Carga"
        elif peso_kg < 100.0:
            return "Carga Pesada"
        else:
            return "Sobredimensionado"

    # ── Cálculo de costo ───────────────────────────────────────────────────────
    def calcular_costo(self, tarifa_base: float) -> float:
        """
        Fórmula: tarifa_base + (distancia_km * 50 * peso_kg)
        Retorna el costo y lo almacena internamente.
        """
        costo = tarifa_base + (self.destino.distancia_km * 50 * self.peso_kg)
        self._costo_envio = costo
        return costo

    def resumen(self) -> str:
        clasificacion = self.clasificar(self.peso_kg)
        costo_str = (f"${self._costo_envio:,.0f} COP"
                     if self._costo_envio is not None else "No calculado")
        return (
            f"ID: {self.id_envio or 'N/A'} | "
            f"Fecha: {self.fecha_envio} | "
            f"Remitente: {self.remitente} | "
            f"Peso: {self.peso_kg} kg | "
            f"Tipo: {clasificacion} | "
            f"Destino: {self.destino.ciudad} | "
            f"Costo: {costo_str} | "
            f"Camión: {self.camion.placa}"
        )


# ── Clase de Servicio ─────────────────────────────────────────────────────────

class ServicioLogistica:
    """
    Capa de servicio que orquesta operaciones sobre envíos.
    Desacopla la lógica de negocio de la base de datos y la UI.
    """

    def __init__(self):
        from Backend.database import (
            inicializar_db, obtener_todos_envios,
            insertar_envio, actualizar_envio,
            eliminar_envio, obtener_destinos, obtener_camiones
        )
        self._insertar = insertar_envio
        self._actualizar = actualizar_envio
        self._eliminar = eliminar_envio
        self._obtener_todos = obtener_todos_envios
        self._obtener_destinos = obtener_destinos
        self._obtener_camiones = obtener_camiones
        inicializar_db()

    def registrar_envio(self, fecha, remitente, peso_kg, id_destino, id_camion):
        if peso_kg <= 0:
            raise ValueError("El peso debe ser mayor a 0 kg.")
        if not remitente.strip():
            raise ValueError("El nombre del remitente no puede estar vacío.")
        return self._insertar(fecha, remitente, float(peso_kg), id_destino, id_camion)

    def listar_envios(self):
        return self._obtener_todos()

    def modificar_envio(self, id_envio, fecha, remitente, peso_kg, id_destino, id_camion):
        if peso_kg <= 0:
            raise ValueError("El peso debe ser mayor a 0 kg.")
        self._actualizar(id_envio, fecha, remitente, float(peso_kg), id_destino, id_camion)

    def borrar_envio(self, id_envio):
        self._eliminar(id_envio)

    def obtener_destinos(self):
        return self._obtener_destinos()

    def obtener_camiones(self):
        return self._obtener_camiones()

    def generar_manifiesto(self) -> list[str]:
        """Genera manifiesto de carga ordenado por peso (ascendente)."""
        rows = self.listar_envios()
        lineas = ["=" * 80, "MANIFIESTO DE CARGA — RUTA-ÓPTIMA", "=" * 80]
        for r in rows:
            id_e, fecha, rem, peso, costo, ciudad, tipo, placa = r
            lineas.append(
                f"ID {id_e:>4} | {fecha} | {rem:<20} | "
                f"{peso:>7.2f} kg | {tipo:<20} | "
                f"${costo:>12,.0f} COP | {ciudad:<15} | {placa}"
            )
        lineas.append("=" * 80)
        return lineas
