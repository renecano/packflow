"""Tests de validación de PackEnv."""

import numpy as np
import pytest

from packflow.env import Box, PackEnv


@pytest.fixture
def env():
    return PackEnv(grid_size=(12, 6, 8), n_packages=20, seed=42)


def test_reset_returns_valid_obs(env):
    obs, info = env.reset(seed=0)
    assert set(obs.keys()) == {"voxel", "queue"}
    assert obs["voxel"].shape == (12, 6, 8)
    assert obs["queue"].shape == (20, 7)
    assert obs["voxel"].sum() == 0  # camión vacío
    assert env.observation_space.contains(obs)
    assert info["current_idx"] == 0


def test_obs_is_within_space_bounds(env):
    obs, _ = env.reset(seed=1)
    assert np.all(obs["queue"] >= 0.0) and np.all(obs["queue"] <= 1.0)
    assert np.all(obs["voxel"] >= 0.0) and np.all(obs["voxel"] <= 1.0)


def test_skip_advances_without_placing(env):
    env.reset(seed=0)
    obs, reward, term, trunc, info = env.step(env.skip_action)
    assert info["current_idx"] == 1
    assert info["n_placed"] == 0
    assert not term
    assert obs["voxel"].sum() == 0


def test_action_mask_skip_always_valid(env):
    env.reset(seed=0)
    mask = env.action_masks()
    assert mask.shape == (env.action_space.n,)
    assert mask[env.skip_action]
    assert mask.any()


def test_placement_marks_voxels(env):
    env.reset(seed=0)
    # Coloca el primer paquete en el suelo, esquina, sin rotar.
    box = env.boxes[0]
    action = env._encode_action(0, 0, 0, 0)
    assert env.action_masks()[action], "la colocación base debería ser válida"
    obs, reward, *_ = env.step(action)
    rw, rh, rd = box.dims(0)
    assert obs["voxel"][:rw, :rh, :rd].sum() == rw * rh * rd
    assert reward > 0  # volumen + posible secuencia


def test_collision_is_invalid(env):
    env.reset(seed=0)
    box0 = env.boxes[0]
    env.step(env._encode_action(0, 0, 0, 0))
    # Intentar colocar el siguiente paquete encimado en (0,0,0) debe ser inválido.
    rw, rh, rd = box0.dims(0)
    overlap_action = env._encode_action(0, 0, 0, 0)
    assert not env._is_valid(env.boxes[1], 0, 0, 0, 0)
    # Pero colocarlo justo encima (con soporte) puede ser válido.
    assert not env.action_masks()[overlap_action]


def test_gravity_blocks_floating_box(env):
    env.reset(seed=0)
    box = env.boxes[0]
    # Sin nada debajo, colocar en z alto debe ser inválido (sin soporte).
    assert not env._is_valid(box, 0, 0, 5, 0)


def test_full_episode_terminates(env):
    env.reset(seed=0)
    term = False
    steps = 0
    while not term:
        mask = env.action_masks()
        valid = np.flatnonzero(mask)
        action = int(valid[0])  # política trivial: primera acción válida
        _, _, term, _, info = env.step(action)
        steps += 1
        assert steps <= env.n_packages
    assert steps == env.n_packages
    assert info["current_idx"] == env.n_packages


def test_weight_limit_respected():
    # Paquetes pesados que exceden el límite -> algunos no caben por peso.
    boxes = [
        Box(id=i, w=2, h=2, d=2, weight=60.0, fragility=0.0, delivery_order=i)
        for i in range(20)
    ]
    env = PackEnv(grid_size=(12, 6, 8), max_weight=200.0)
    env.reset(options={"boxes": boxes})
    term = False
    while not term:
        mask = env.action_masks()
        action = int(np.flatnonzero(mask)[0])
        _, _, term, _, _ = env.step(action)
    assert env.total_weight <= 200.0


def test_get_solution_structure(env):
    env.reset(seed=0)
    env.step(env._encode_action(0, 0, 0, 0))
    sol = env.get_solution()
    assert "truck" in sol and "placed" in sol and "metrics" in sol
    assert sol["metrics"]["n_total"] == 20
    assert 0.0 <= sol["metrics"]["volume_utilization"] <= 1.0


def test_fixed_manifest_overrides_n_packages():
    boxes = [Box(id=i, w=1, h=1, d=1, weight=1.0, fragility=0.0, delivery_order=i)
             for i in range(5)]
    env = PackEnv(n_packages=20)
    env.reset(options={"boxes": boxes})
    assert env.n_packages == 5
    assert len(env.boxes) == 5
