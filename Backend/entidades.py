from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegistroEnvio:
    envio_id: int | None
    fecha_key: int
    zona_id: int
    camion_id: int
    peso_kg: float


@dataclass(frozen=True)
class ResumenDimension:
    texto: str
    id: int
