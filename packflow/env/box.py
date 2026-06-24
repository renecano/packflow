"""Definición de un paquete (Box) para PackFlow.

Cada paquete es un cuboide con dimensiones enteras en vóxeles más atributos
físicos y logísticos (peso, fragilidad, orden de entrega).
"""

from __future__ import annotations

from dataclasses import dataclass


# Las 6 orientaciones ortogonales de un cuboide. Cada tupla es una permutación
# de los ejes (w, h, d). El índice de rotación que el agente elige selecciona
# una de estas permutaciones.
ROTATIONS = (
    (0, 1, 2),  # 0: (w, h, d)  — sin rotar
    (0, 2, 1),  # 1: (w, d, h)
    (1, 0, 2),  # 2: (h, w, d)
    (1, 2, 0),  # 3: (h, d, w)
    (2, 0, 1),  # 4: (d, w, h)
    (2, 1, 0),  # 5: (d, h, w)
)


@dataclass
class Box:
    """Un paquete a cargar.

    Attributes
    ----------
    id : int
        Identificador único dentro del manifiesto (también es el orden en que
        el agente procesa la cola).
    w, h, d : int
        Dimensiones en vóxeles a lo largo de los ejes x, y, z (largo, ancho,
        alto) en su orientación base.
    weight : float
        Peso en kg.
    fragility : float
        Qué tan frágil es el paquete, en [0, 1]. 0 = indestructible,
        1 = extremadamente frágil. Penaliza apilar peso encima.
    delivery_order : int
        Posición en la secuencia de descarga de la ruta. 0 = se entrega primero
        (debe quedar accesible cerca de la puerta), N-1 = se entrega al final
        (puede ir al fondo del camión).
    """

    id: int
    w: int
    h: int
    d: int
    weight: float
    fragility: float
    delivery_order: int

    @property
    def base_volume(self) -> int:
        """Volumen en vóxeles, independiente de la orientación."""
        return self.w * self.h * self.d

    def dims(self, rotation: int) -> tuple[int, int, int]:
        """Devuelve (rw, rh, rd) para una orientación dada.

        Parameters
        ----------
        rotation : int
            Índice en ROTATIONS (0..5).

        Returns
        -------
        tuple[int, int, int]
            Dimensiones rotadas a lo largo de los ejes (x, y, z).
        """
        base = (self.w, self.h, self.d)
        perm = ROTATIONS[rotation]
        return base[perm[0]], base[perm[1]], base[perm[2]]
