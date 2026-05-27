"""Dominio RETO 1 — Logística Bogotá: clasificación por peso y cotización."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoNegocio:
    clase_servicio: str  # Documento | Paquetería | Carga
    costo_estimado_cop: int


class ServicioEnvios:
    """Encapsula reglas públicas descritas en el taller (clasificación por kg)."""

    @staticmethod
    def clasificar_por_peso(peso_kg: float) -> str:
        if peso_kg <= 0:
            raise ValueError("El peso del paquete debe ser mayor que cero (kg).")
        if peso_kg < 2:
            return "Documento"
        if peso_kg <= 30:
            return "Paquetería"
        return "Carga"

    @classmethod
    def cotizar(cls, peso_kg: float, factor_zona: float) -> ResultadoNegocio:
        if factor_zona <= 0:
            raise ValueError("El factor territorial de zona debe ser positivo.")

        clase = cls.clasificar_por_peso(peso_kg)

        base = int(
            round(
                {
                    "Documento": 4_900 + peso_kg * 600,
                    "Paquetería": 12_600 + peso_kg * 440,
                    "Carga": 35_800 + peso_kg * 920,
                }[clase]
                * factor_zona,
            ),
        )

        return ResultadoNegocio(clase_servicio=clase, costo_estimado_cop=max(base, 2_900))
