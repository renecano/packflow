"""Smoke test: corrida corta para validar que el pipeline de entrenamiento
arranca correctamente antes de lanzar el curriculum completo.

Uso:
    python smoke_test.py
"""

from __future__ import annotations

import numpy as np
import torch

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy

from train import PackFeaturesExtractor, make_env


def main() -> None:
    print(f"PyTorch {torch.__version__} — CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    env = make_env(n_packages=4, seed=0)

    policy_kwargs = dict(
        features_extractor_class=PackFeaturesExtractor,
        features_extractor_kwargs=dict(features_dim=256),
    )

    model = MaskablePPO(
        "MultiInputPolicy",
        env,
        policy_kwargs=policy_kwargs,
        n_steps=512,
        batch_size=128,
        verbose=1,
    )

    print("\n--- Entrenando 30k steps (N=4) ---")
    model.learn(total_timesteps=30_000)

    mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"\nReward medio tras smoke test: {mean_r:.2f} ± {std_r:.2f}")
    print("Si llegaste hasta aquí sin errores, el pipeline funciona. ✓")


if __name__ == "__main__":
    main()
