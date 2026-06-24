"""Esquemas Pydantic para la API de PackFlow.

Definen el contrato de entrada (manifiesto de paquetes) y de salida
(solución de carga + métricas) entre el frontend y el backend.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BoxInput(BaseModel):
    """Un paquete del manifiesto enviado por el cliente."""

    id: int | None = Field(default=None, description="Id opcional; se asigna por orden si falta.")
    w: int = Field(ge=1, description="Largo en vóxeles.")
    h: int = Field(ge=1, description="Ancho en vóxeles.")
    d: int = Field(ge=1, description="Alto en vóxeles.")
    weight: float = Field(ge=0, description="Peso en kg.")
    fragility: float = Field(ge=0, le=1, description="Fragilidad en [0, 1].")
    delivery_order: int = Field(ge=0, description="Posición en la secuencia de descarga.")


class TruckConfig(BaseModel):
    """Dimensiones del camión (opcional; usa los defaults del entorno)."""

    W: int = 12
    H: int = 6
    D: int = 8


class PackRequest(BaseModel):
    """Petición de empaquetado."""

    boxes: list[BoxInput]
    truck: TruckConfig = Field(default_factory=TruckConfig)
    max_weight: float = 1000.0


class PlacedBox(BaseModel):
    id: int
    position: list[int]
    rotation: int
    size: list[int]
    weight: float
    fragility: float
    delivery_order: int


class SkippedBox(BaseModel):
    id: int
    weight: float
    fragility: float
    delivery_order: int


class Metrics(BaseModel):
    n_placed: int
    n_total: int
    volume_utilization: float
    total_weight: float
    max_weight: float


class PackResponse(BaseModel):
    truck: TruckConfig
    placed: list[PlacedBox]
    skipped: list[SkippedBox]
    metrics: Metrics
    agent: str = Field(description="Qué política resolvió: 'ppo' o 'greedy'.")


class StepEvent(BaseModel):
    """Un paso del agente, emitido por el WebSocket para animar la carga."""

    type: str  # "place" | "skip" | "done"
    step: int
    box_id: int | None = None
    position: list[int] | None = None
    rotation: int | None = None
    size: list[int] | None = None
    fragility: float | None = None
    delivery_order: int | None = None
    reward: float | None = None
    metrics: Metrics | None = None  # presente solo en el evento "done"
