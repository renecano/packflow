# PackFlow

Optimización de carga 3D para vehículos de reparto usando Reinforcement Learning.

Un agente PPO entrenado en un entorno Gymnasium custom resuelve el problema de
3D bin packing con restricciones dinámicas: tamaño, peso, fragilidad y secuencia
de entrega. Cuando no todos los paquetes caben en un viaje, el agente aprende a
decidir **qué dejar para el siguiente viaje** minimizando el volumen desperdiciado.

## Estado del proyecto

- [x] **Fase 1 — Entorno RL** (`packflow/env/`): `PackEnv` + `Box`, action masking,
      recompensa con overflow suave, tests y validación con `env_checker`.
- [ ] **Fase 2 — Agente PPO** (`train.py`): feature extractor 3D + curriculum.
- [ ] **Fase 3 — Full stack**: backend FastAPI + frontend React/Three.js.
- [ ] **Fase 4 — Demo y portafolio**.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso rápido

```python
import numpy as np
from packflow.env import PackEnv

env = PackEnv(grid_size=(12, 6, 8), n_packages=20, seed=0)
obs, info = env.reset(seed=0)

terminated = False
while not terminated:
    mask = env.action_masks()                 # acciones válidas
    action = int(np.flatnonzero(mask)[0])      # política trivial (placeholder)
    obs, reward, terminated, truncated, info = env.step(action)

print(env.get_solution()["metrics"])
```

## Diseño del entorno

**Camión**: voxel grid 3D `12×6×8` (576 vóxeles). La puerta está en `x = 0`.

**Observación** (`Dict`):
- `voxel`: grid binario `(12, 6, 8)` de ocupación.
- `queue`: `(20, 7)` — por paquete `[w, h, d, fragilidad, orden_entrega,
  peso, estado]`. `estado`: 0 = pendiente, 0.5 = actual, 1 = procesado.

**Acción** (`Discrete`): `12·6·8·6 + 1`. Cada acción codifica `(x, y, z, rotación)`
o la acción extra de **skip** (no cargar el paquete actual). Un `action_masks()`
expone en cada paso qué colocaciones son válidas (caben, no colisionan, quedan
apoyadas y no exceden el peso).

**Recompensa**:

```
R = r_volume + r_sequence − r_damage − r_overflow
```

| Componente   | Cuándo            | Descripción                                            |
|--------------|-------------------|--------------------------------------------------------|
| `r_volume`   | al colocar        | + proporcional al volumen del paquete                  |
| `r_sequence` | al colocar        | ± coincidencia entre orden de entrega y posición en x  |
| `r_damage`   | al colocar        | − apilar peso sobre paquetes frágiles                  |
| `r_overflow` | terminal          | − por cada paquete no cargado, ponderado por su volumen |

## Entrenamiento

```bash
python train.py
tensorboard --logdir runs/
```

El curriculum escala `N`: 4 → 8 → 12 → 16 → 20, reutilizando los pesos de la
fase anterior.

## Tests

```bash
pytest tests/ -q
```
