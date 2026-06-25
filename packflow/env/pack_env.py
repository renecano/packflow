"""PackEnv — entorno Gymnasium custom para 3D bin packing con RL.

El agente carga un camión procesando una cola de paquetes en orden. En cada
paso decide dónde colocar el paquete actual (posición + rotación) o saltarlo
(skip). El episodio termina cuando se han procesado los N paquetes.

Restricciones modeladas:
  - Geometría: el paquete debe caber sin colisiones dentro del camión.
  - Gravedad: la base del paquete debe quedar apoyada (suelo u otros paquetes)
    al menos en una fracción `support_threshold`.
  - Peso: no se excede el peso máximo del camión.
  - Fragilidad: apilar peso sobre paquetes frágiles se penaliza.
  - Secuencia de entrega: se premia colocar los paquetes de descarga tardía al
    fondo y los de descarga temprana cerca de la puerta (x = 0).

Recompensa (opción "viajes adicionales"):
    R = r_volume + r_sequence - r_damage - r_overflow

  r_volume   (+) por cada paquete colocado, proporcional a su volumen.
  r_sequence (±) coincidencia entre orden de entrega y posición en el eje x.
  r_damage   (-) por apilar peso sobre frágiles.
  r_overflow (-) terminal, por cada paquete que quedó sin cargar (ponderado por
             su volumen: dejar fuera un paquete grande duele más).
"""

from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from numpy.lib.stride_tricks import sliding_window_view

from .box import Box

# Número de features por paquete en el tensor de la cola.
#   [w, h, d, fragility, delivery_order, weight, state]
# state: 0.0 = pendiente, 0.5 = paquete actual, 1.0 = ya procesado
N_FEATURES = 7


class PackEnv(gym.Env):
    """Entorno de carga 3D para un agente PPO.

    Parameters
    ----------
    grid_size : tuple[int, int, int]
        Dimensiones del camión en vóxeles (W, H, D) = (largo, ancho, alto).
    n_packages : int
        Número de paquetes en la cola por episodio.
    max_weight : float
        Peso máximo del camión en kg.
    support_threshold : float
        Fracción mínima de la base que debe estar apoyada para que una
        colocación sea válida, en [0, 1].
    reward_coeffs : dict | None
        Coeficientes de las componentes de recompensa. Claves:
        'volume', 'sequence', 'damage', 'overflow'.
    seed : int | None
        Semilla del generador de números aleatorios.
    """

    metadata = {"render_modes": ["ansi"]}

    def __init__(
        self,
        grid_size: tuple[int, int, int] = (12, 6, 8),
        n_packages: int = 20,
        max_packages: int | None = None,
        max_weight: float = 1000.0,
        support_threshold: float = 0.8,
        reward_coeffs: dict[str, float] | None = None,
        seed: int | None = None,
    ) -> None:
        super().__init__()

        self.W, self.H, self.D = grid_size
        self.grid_volume = self.W * self.H * self.D
        self.n_packages = n_packages
        # max_packages fija el tamaño del espacio de observación (la tabla de la
        # cola). Permite que el curriculum varíe n_packages manteniendo una
        # observación de forma constante (las filas sobrantes se rellenan con
        # ceros). Si no se especifica, es igual a n_packages.
        self.max_packages = max_packages if max_packages is not None else n_packages
        assert self.n_packages <= self.max_packages, (
            "n_packages no puede exceder max_packages"
        )
        self.max_weight = max_weight
        self.support_threshold = support_threshold

        self.reward_coeffs = {
            "volume": 1.0,
            "sequence": 0.5,
            "damage": 1.0,
            "overflow": 2.0,
        }
        if reward_coeffs:
            self.reward_coeffs.update(reward_coeffs)

        # Espacio de acciones discreto: una acción por (x, y, z, rotación)
        # más una acción extra de "skip" al final.
        self.n_place_actions = self.W * self.H * self.D * 6
        self.action_space = spaces.Discrete(self.n_place_actions + 1)
        self.skip_action = self.n_place_actions

        # Espacio de observaciones: el voxel grid binario + la cola de paquetes.
        self.observation_space = spaces.Dict(
            {
                "voxel": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=(self.W, self.H, self.D),
                    dtype=np.float32,
                ),
                "queue": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=(self.max_packages, N_FEATURES),
                    dtype=np.float32,
                ),
            }
        )

        # Rango de dimensiones de los paquetes generados aleatoriamente.
        self._dim_range = (1, max(2, min(self.W, self.H, self.D) // 2))

        self._rng = np.random.default_rng(seed)

        # Estado mutable (se fija en reset()).
        self.occupancy: np.ndarray | None = None
        self.id_grid: np.ndarray | None = None
        self.boxes: list[Box] = []
        self.current_idx = 0
        self.total_weight = 0.0
        # placements[box_id] = (x, y, z, rotation) o None si no se colocó.
        self.placements: dict[int, tuple[int, int, int, int] | None] = {}

    # ------------------------------------------------------------------ #
    # API de Gymnasium
    # ------------------------------------------------------------------ #
    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)

        self.occupancy = np.zeros((self.W, self.H, self.D), dtype=np.int8)
        self.id_grid = np.full((self.W, self.H, self.D), -1, dtype=np.int32)
        self.current_idx = 0
        self.total_weight = 0.0

        # Permite inyectar un manifiesto fijo (útil para el demo y los tests).
        if options and "boxes" in options:
            self.boxes = list(options["boxes"])
            self.n_packages = len(self.boxes)
            assert self.n_packages <= self.max_packages, (
                f"el manifiesto tiene {self.n_packages} paquetes pero "
                f"max_packages={self.max_packages}"
            )
        else:
            self.boxes = self._generate_boxes()

        self.placements = {box.id: None for box in self.boxes}

        return self._get_obs(), self._get_info()

    def step(
        self, action: int
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        assert self.occupancy is not None, "Llama a reset() antes de step()."
        action = int(action)
        box = self.boxes[self.current_idx]
        reward = 0.0

        if action == self.skip_action:
            # El agente decide no cargar este paquete.
            self.placements[box.id] = None
        else:
            x, y, z, rotation = self._decode_action(action)
            if self._is_valid(box, x, y, z, rotation):
                reward = self._place(box, x, y, z, rotation)
            else:
                # Acción inválida (no debería ocurrir con masking). Se trata
                # como skip y no se penaliza más allá del overflow futuro.
                self.placements[box.id] = None

        self.current_idx += 1
        terminated = self.current_idx >= self.n_packages
        truncated = False

        if terminated:
            reward += self._overflow_penalty()

        return self._get_obs(), float(reward), terminated, truncated, self._get_info()

    def render(self) -> str:
        """Render ANSI sencillo: capas del camión vistas desde arriba."""
        if self.occupancy is None:
            return "<PackEnv sin inicializar>"
        lines = [f"Camión {self.W}x{self.H}x{self.D} — capa por altura (z):"]
        for z in range(self.D):
            lines.append(f"  z={z}:")
            for y in range(self.H):
                row = "    " + " ".join(
                    f"{self.id_grid[x, y, z]:>2}" if self.occupancy[x, y, z] else " ."
                    for x in range(self.W)
                )
                lines.append(row)
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Action masking (consumido por MaskablePPO vía get_action_masks)
    # ------------------------------------------------------------------ #
    def action_masks(self) -> np.ndarray:
        """Máscara booleana de acciones válidas para el paquete actual.

        El skip siempre es válido. Una colocación es válida si el paquete cabe,
        no colisiona, queda apoyado y no excede el peso máximo.

        Versión vectorizada: usa ventanas deslizantes de NumPy para evaluar
        todas las posiciones de cada rotación a la vez, en lugar de un triple
        bucle en Python. Produce exactamente la misma máscara, mucho más rápido.
        """
        mask = np.zeros(self.action_space.n, dtype=bool)
        mask[self.skip_action] = True

        if self.current_idx >= self.n_packages:
            return mask

        box = self.boxes[self.current_idx]
        # Si el paquete no cabe por peso, ninguna colocación es válida.
        if self.total_weight + box.weight > self.max_weight:
            return mask

        occ = self.occupancy
        W, H, D, thr = self.W, self.H, self.D, self.support_threshold

        for rotation in range(6):
            rw, rh, rd = box.dims(rotation)
            if rw > W or rh > H or rd > D:
                continue
            nx, ny, nz = W - rw + 1, H - rh + 1, D - rd + 1

            # Colisión: suma de la ventana (rw, rh, rd) == 0 → región libre.
            win = sliding_window_view(occ, (rw, rh, rd))  # (nx, ny, nz, rw, rh, rd)
            free = win.sum(axis=(3, 4, 5)) == 0  # (nx, ny, nz)

            # Soporte (gravedad): z=0 apoya en el suelo; z>0 exige que la capa
            # inferior tenga al menos `thr` de su base ocupada.
            support = np.ones((nx, ny, nz), dtype=bool)
            base_area = rw * rh
            for z in range(1, nz):
                layer = occ[:, :, z - 1]  # (W, H)
                s2 = sliding_window_view(layer, (rw, rh)).sum(axis=(2, 3))  # (nx, ny)
                support[:, :, z] = (s2 / base_area) >= thr

            valid = free & support
            xs, ys, zs = np.nonzero(valid)
            idxs = ((xs * H + ys) * D + zs) * 6 + rotation
            mask[idxs] = True

        return mask

    # ------------------------------------------------------------------ #
    # Serialización para el frontend / FastAPI
    # ------------------------------------------------------------------ #
    def get_solution(self) -> dict[str, Any]:
        """Devuelve la solución actual lista para serializar a JSON.

        Incluye, por paquete, su posición de anclaje, rotación, dimensiones
        finales y atributos, además de métricas agregadas.
        """
        placed = []
        skipped = []
        used_volume = 0
        for box in self.boxes:
            entry = {
                "id": box.id,
                "weight": box.weight,
                "fragility": box.fragility,
                "delivery_order": box.delivery_order,
            }
            pos = self.placements.get(box.id)
            if pos is None:
                skipped.append(entry)
            else:
                x, y, z, rotation = pos
                rw, rh, rd = box.dims(rotation)
                used_volume += box.base_volume
                entry.update(
                    {
                        "position": [x, y, z],
                        "rotation": rotation,
                        "size": [rw, rh, rd],
                    }
                )
                placed.append(entry)

        return {
            "truck": {"W": self.W, "H": self.H, "D": self.D},
            "placed": placed,
            "skipped": skipped,
            "metrics": {
                "n_placed": len(placed),
                "n_total": self.n_packages,
                "volume_utilization": round(used_volume / self.grid_volume, 4),
                "total_weight": round(self.total_weight, 2),
                "max_weight": self.max_weight,
            },
        }

    # ------------------------------------------------------------------ #
    # Helpers internos
    # ------------------------------------------------------------------ #
    def _generate_boxes(self) -> list[Box]:
        lo, hi = self._dim_range
        delivery = self._rng.permutation(self.n_packages)
        boxes = []
        for i in range(self.n_packages):
            boxes.append(
                Box(
                    id=i,
                    w=int(self._rng.integers(lo, hi + 1)),
                    h=int(self._rng.integers(lo, hi + 1)),
                    d=int(self._rng.integers(lo, hi + 1)),
                    weight=float(round(self._rng.uniform(1.0, 50.0), 2)),
                    fragility=float(round(self._rng.uniform(0.0, 1.0), 2)),
                    delivery_order=int(delivery[i]),
                )
            )
        return boxes

    def _decode_action(self, action: int) -> tuple[int, int, int, int]:
        rotation = action % 6
        rest = action // 6
        z = rest % self.D
        rest //= self.D
        y = rest % self.H
        x = rest // self.H
        return x, y, z, rotation

    def _encode_action(self, x: int, y: int, z: int, rotation: int) -> int:
        return ((x * self.H + y) * self.D + z) * 6 + rotation

    def _is_valid(self, box: Box, x: int, y: int, z: int, rotation: int) -> bool:
        rw, rh, rd = box.dims(rotation)

        # Límites del camión.
        if x + rw > self.W or y + rh > self.H or z + rd > self.D:
            return False

        # Colisión: la región objetivo debe estar libre.
        region = self.occupancy[x : x + rw, y : y + rh, z : z + rd]
        if region.any():
            return False

        # Peso.
        if self.total_weight + box.weight > self.max_weight:
            return False

        # Soporte (gravedad).
        if z == 0:
            return True  # apoyado en el suelo
        base_below = self.occupancy[x : x + rw, y : y + rh, z - 1]
        support_frac = base_below.sum() / (rw * rh)
        return support_frac >= self.support_threshold

    def _place(self, box: Box, x: int, y: int, z: int, rotation: int) -> float:
        rw, rh, rd = box.dims(rotation)

        # Daño a frágiles que quedan justo debajo de la base del paquete.
        damage = 0.0
        if z > 0:
            below_ids = self.id_grid[x : x + rw, y : y + rh, z - 1].ravel()
            base_cells = rw * rh
            weight_norm = box.weight / self.max_weight
            for bid in np.unique(below_ids):
                if bid < 0:
                    continue
                contact = int((below_ids == bid).sum())
                frag = self.boxes[int(bid)].fragility
                damage += frag * (contact / base_cells) * weight_norm

        # Aplicar la colocación al grid.
        self.occupancy[x : x + rw, y : y + rh, z : z + rd] = 1
        self.id_grid[x : x + rw, y : y + rh, z : z + rd] = box.id
        self.total_weight += box.weight
        self.placements[box.id] = (x, y, z, rotation)

        # Componentes de recompensa inmediatas.
        r_volume = self.reward_coeffs["volume"] * (box.base_volume / self.grid_volume)

        # Coincidencia entre orden de entrega y posición en el eje x.
        # La puerta del camión está en x = 0: descarga temprana -> x bajo;
        # descarga tardía -> x alto (al fondo).
        x_center_norm = (x + rw / 2) / self.W
        delivery_norm = (
            box.delivery_order / (self.n_packages - 1) if self.n_packages > 1 else 0.0
        )
        # 1 - 2|Δ| ∈ [-1, 1]: premia coincidir, penaliza invertir la secuencia.
        seq_match = 1.0 - 2.0 * abs(x_center_norm - delivery_norm)
        r_sequence = self.reward_coeffs["sequence"] * seq_match

        r_damage = self.reward_coeffs["damage"] * damage

        return r_volume + r_sequence - r_damage

    def _overflow_penalty(self) -> float:
        """Penalización terminal por paquetes no cargados (viajes extra)."""
        penalty = 0.0
        for box in self.boxes:
            if self.placements.get(box.id) is None:
                penalty += box.base_volume / self.grid_volume
        return -self.reward_coeffs["overflow"] * penalty

    def _get_obs(self) -> dict[str, np.ndarray]:
        voxel = self.occupancy.astype(np.float32)

        # Tabla de tamaño fijo (max_packages). Las filas de los paquetes que no
        # existen en este episodio quedan en cero y se marcan como procesadas
        # (state=1) para que el agente las ignore como contexto.
        queue = np.zeros((self.max_packages, N_FEATURES), dtype=np.float32)
        max_dim = max(self.W, self.H, self.D)
        denom = self.n_packages - 1 if self.n_packages > 1 else 1
        for i, box in enumerate(self.boxes):
            if i < self.current_idx:
                state = 1.0  # ya procesado
            elif i == self.current_idx:
                state = 0.5  # paquete actual
            else:
                state = 0.0  # pendiente
            queue[i] = [
                box.w / max_dim,
                box.h / max_dim,
                box.d / max_dim,
                box.fragility,
                box.delivery_order / denom,
                box.weight / self.max_weight,
                state,
            ]
        # Padding: filas no usadas marcadas como procesadas.
        if self.n_packages < self.max_packages:
            queue[self.n_packages :, 6] = 1.0
        return {"voxel": voxel, "queue": queue}

    def _get_info(self) -> dict[str, Any]:
        n_placed = sum(1 for p in self.placements.values() if p is not None)
        return {
            "current_idx": self.current_idx,
            "n_placed": n_placed,
            "total_weight": self.total_weight,
            "volume_utilization": (
                sum(
                    self.boxes[bid].base_volume
                    for bid, p in self.placements.items()
                    if p is not None
                )
                / self.grid_volume
            ),
        }