"""Lógica de resolución de PackFlow.

Define dos "agentes" que eligen acciones en el entorno:
  - GreedyAgent: baseline sin dependencias pesadas. Coloca cada paquete en la
    primera posición válida; si no cabe, lo salta.
  - PolicyAgent: carga un modelo MaskablePPO entrenado (import perezoso de
    torch/sb3, solo cuando hay checkpoint).

El solver corre un episodio paso a paso y puede tanto devolver la solución
completa (para POST /pack) como emitir eventos por paso (para el WebSocket).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol

import numpy as np

from packflow.env import Box, PackEnv
from packflow.api.schemas import BoxInput, StepEvent


class Agent(Protocol):
    name: str

    def act(self, env: PackEnv, obs: dict[str, np.ndarray], mask: np.ndarray) -> int:
        ...


class GreedyAgent:
    """Baseline: primera acción de colocación válida, o skip si no hay."""

    name = "greedy"

    def act(self, env: PackEnv, obs: dict[str, np.ndarray], mask: np.ndarray) -> int:
        valid = np.flatnonzero(mask)
        placements = valid[valid != env.skip_action]
        return int(placements[0]) if len(placements) else int(env.skip_action)


class PolicyAgent:
    """Agente PPO entrenado. Carga el modelo de forma perezosa."""

    name = "ppo"

    def __init__(self, checkpoint_path: str) -> None:
        # Import perezoso: torch/sb3 solo se cargan si se usa este agente.
        from sb3_contrib import MaskablePPO

        self.model = MaskablePPO.load(checkpoint_path, device="cpu")

    def act(self, env: PackEnv, obs: dict[str, np.ndarray], mask: np.ndarray) -> int:
        action, _ = self.model.predict(obs, action_masks=mask, deterministic=True)
        return int(action)


def _build_boxes(box_inputs: list[BoxInput]) -> list[Box]:
    boxes = []
    for i, b in enumerate(box_inputs):
        boxes.append(
            Box(
                id=b.id if b.id is not None else i,
                w=b.w,
                h=b.h,
                d=b.d,
                weight=b.weight,
                fragility=b.fragility,
                delivery_order=b.delivery_order,
            )
        )
    return boxes


def make_env(
    box_inputs: list[BoxInput],
    truck: tuple[int, int, int],
    max_weight: float,
) -> PackEnv:
    env = PackEnv(grid_size=truck, n_packages=len(box_inputs), max_weight=max_weight)
    env.reset(options={"boxes": _build_boxes(box_inputs)})
    return env


def run_episode(env: PackEnv, agent: Agent) -> Iterator[StepEvent]:
    """Corre un episodio y emite un StepEvent por paso, más uno final 'done'."""
    step = 0
    terminated = False
    while not terminated:
        box = env.boxes[env.current_idx]
        obs = env._get_obs()
        mask = env.action_masks()
        action = agent.act(env, obs, mask)

        if action == env.skip_action:
            _, reward, terminated, _, _ = env.step(action)
            yield StepEvent(
                type="skip",
                step=step,
                box_id=box.id,
                reward=round(float(reward), 4),
                fragility=box.fragility,
                delivery_order=box.delivery_order,
            )
        else:
            x, y, z, rotation = env._decode_action(action)
            rw, rh, rd = box.dims(rotation)
            _, reward, terminated, _, _ = env.step(action)
            yield StepEvent(
                type="place",
                step=step,
                box_id=box.id,
                position=[x, y, z],
                rotation=rotation,
                size=[rw, rh, rd],
                fragility=box.fragility,
                delivery_order=box.delivery_order,
                reward=round(float(reward), 4),
            )
        step += 1

    sol = env.get_solution()
    from packflow.api.schemas import Metrics

    yield StepEvent(type="done", step=step, metrics=Metrics(**sol["metrics"]))


def solve(env: PackEnv, agent: Agent) -> dict[str, Any]:
    """Resuelve el episodio completo y devuelve la solución serializable."""
    for _ in run_episode(env, agent):
        pass  # consumir el generador hasta el final
    sol = env.get_solution()
    sol["agent"] = agent.name
    return sol
