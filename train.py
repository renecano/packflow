"""Entrenamiento de PackFlow con MaskablePPO y curriculum learning.

Estrategia de curriculum: se empieza con pocos paquetes (N=4) y se escala
gradualmente (4 -> 8 -> 12 -> 16 -> 20) reutilizando los pesos de la fase
anterior. Con N=20 desde cero el entrenamiento diverge; el curriculum
estabiliza el aprendizaje, igual que escalar la complejidad del tráfico en
UrbanMind X.

Requisitos extra (ver requirements.txt):
    torch, stable-baselines3, sb3-contrib, tensorboard

Uso:
    python train.py
    tensorboard --logdir runs/
"""

from __future__ import annotations

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
from gymnasium import spaces
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

from packflow.env import PackEnv

# Camión fijo en todas las fases; solo cambia el número de paquetes.
GRID_SIZE = (12, 6, 8)

# Tamaño máximo de la cola. Fija la forma de la observación para que el
# curriculum pueda variar n_packages sin romper la transferencia de pesos.
MAX_PACKAGES = 20

# (n_packages, timesteps) por fase del curriculum.
CURRICULUM = [
    (4, 200_000),
    (8, 400_000),
    (12, 600_000),
    (16, 800_000),
    (20, 1_500_000),
]


class PackFeaturesExtractor(BaseFeaturesExtractor):
    """Extrae features de la observación Dict {voxel, queue}.

    El voxel grid 3D pasa por una CNN 3D; la cola de paquetes por un MLP.
    Los embeddings se concatenan en un único vector de features.
    """

    def __init__(self, observation_space: spaces.Dict, features_dim: int = 256):
        super().__init__(observation_space, features_dim)

        w, h, d = observation_space["voxel"].shape
        self.cnn = nn.Sequential(
            nn.Conv3d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv3d(16, 32, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        with torch.no_grad():
            dummy = torch.zeros(1, 1, w, h, d)
            cnn_out = self.cnn(dummy).shape[1]

        n_pkg, n_feat = observation_space["queue"].shape
        self.mlp = nn.Sequential(
            nn.Flatten(),
            nn.Linear(n_pkg * n_feat, 128),
            nn.ReLU(),
        )

        self.fusion = nn.Sequential(
            nn.Linear(cnn_out + 128, features_dim),
            nn.ReLU(),
        )

    def forward(self, obs: dict[str, torch.Tensor]) -> torch.Tensor:
        voxel = obs["voxel"].unsqueeze(1)  # (B, 1, W, H, D)
        cnn_feat = self.cnn(voxel)
        mlp_feat = self.mlp(obs["queue"])
        return self.fusion(torch.cat([cnn_feat, mlp_feat], dim=1))


def mask_fn(env: gym.Env) -> np.ndarray:
    return env.unwrapped.action_masks()


def make_env(n_packages: int, seed: int = 0) -> gym.Env:
    env = PackEnv(
        grid_size=GRID_SIZE,
        n_packages=n_packages,
        max_packages=MAX_PACKAGES,
        seed=seed,
    )
    return ActionMasker(env, mask_fn)


def main() -> None:
    policy_kwargs = dict(
        features_extractor_class=PackFeaturesExtractor,
        features_extractor_kwargs=dict(features_dim=256),
    )

    model: MaskablePPO | None = None
    for phase, (n_pkg, steps) in enumerate(CURRICULUM):
        print(f"\n=== Fase {phase}: N={n_pkg} paquetes, {steps:,} steps ===")
        env = make_env(n_pkg, seed=phase)

        if model is None:
            model = MaskablePPO(
                "MultiInputPolicy",
                env,
                policy_kwargs=policy_kwargs,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=256,
                clip_range=0.2,
                ent_coef=0.01,
                gamma=0.99,
                verbose=1,
                tensorboard_log="runs/",
            )
        else:
            model.set_env(env)

        model.learn(
            total_timesteps=steps,
            reset_num_timesteps=False,
            tb_log_name=f"packflow_N{n_pkg}",
        )
        model.save(f"checkpoints/packflow_N{n_pkg}")

        mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=20)
        print(f"Fase {phase} terminada — reward medio: {mean_r:.2f} ± {std_r:.2f}")

    print("\nEntrenamiento completo. Modelo final: checkpoints/packflow_N20.zip")


if __name__ == "__main__":
    main()
