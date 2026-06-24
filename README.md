# Backend de PackFlow (FastAPI)

API que sirve el agente de carga 3D. Funciona aunque el modelo PPO todavía se
esté entrenando: si no encuentra un checkpoint, usa una política greedy como
baseline.

## Arrancar el servidor

```bash
uvicorn packflow.api.main:app --reload
```

Por defecto en `http://localhost:8000`. Documentación interactiva automática en
`http://localhost:8000/docs`.

## Usar el modelo entrenado

Cuando tengas el checkpoint del entrenamiento (`packflow_N20.zip`), colócalo en
`checkpoints/` o apunta la variable de entorno:

```bash
# Windows PowerShell
$env:PACKFLOW_CHECKPOINT = "C:\ruta\a\packflow_N20"
uvicorn packflow.api.main:app --reload
```

Verifica qué agente está activo:

```bash
curl http://localhost:8000/health
# {"status":"ok","agent":"ppo"}   <- o "greedy" si no hay checkpoint
```

## Endpoints

### `POST /pack`
Recibe un manifiesto y devuelve la solución completa.

```json
{
  "boxes": [
    {"w": 3, "h": 2, "d": 2, "weight": 40, "fragility": 0.1, "delivery_order": 7},
    {"w": 2, "h": 2, "d": 3, "weight": 25, "fragility": 0.9, "delivery_order": 0}
  ],
  "truck": {"W": 12, "H": 6, "D": 8},
  "max_weight": 1000
}
```

Respuesta: `placed` (con `position`, `rotation`, `size` por paquete), `skipped`,
`metrics` y `agent`.

### `WS /stream`
Mismo manifiesto de entrada. Emite un evento JSON por paso (`place` / `skip`),
ideal para animar la carga en el frontend, y un evento final `done` con las
métricas.

### `GET /health`
Estado del servicio y qué política está activa.
