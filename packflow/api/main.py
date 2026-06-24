"""API de PackFlow (FastAPI).

Endpoints:
  GET  /health      — estado del servicio y qué agente está activo.
  POST /pack        — recibe un manifiesto, devuelve la solución completa.
  WS   /stream      — recibe un manifiesto y emite la carga paso a paso
                      (para animar el camión en Three.js).

El agente se elige al arrancar: si existe un checkpoint PPO se usa; si no,
cae a la política greedy (baseline). Así el backend funciona aunque el modelo
todavía se esté entrenando.
"""

from __future__ import annotations

import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from packflow.api.schemas import PackRequest, PackResponse
from packflow.api.solver import Agent, GreedyAgent, PolicyAgent, make_env, run_episode, solve

# Ruta del checkpoint PPO. Cuando el entrenamiento termine, apunta aquí el .zip
# (sin la extensión). Configurable por variable de entorno.
CHECKPOINT = os.environ.get("PACKFLOW_CHECKPOINT", "checkpoints/packflow_N20")

app = FastAPI(title="PackFlow API", version="0.1.0")

# CORS abierto para desarrollo local con el frontend de React (Vite: 5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_agent() -> Agent:
    """Intenta cargar el agente PPO; si no hay checkpoint, usa greedy."""
    if os.path.exists(CHECKPOINT + ".zip"):
        try:
            agent = PolicyAgent(CHECKPOINT)
            print(f"[PackFlow] Agente PPO cargado desde {CHECKPOINT}.zip")
            return agent
        except Exception as exc:  # pragma: no cover - depende del entorno
            print(f"[PackFlow] No se pudo cargar PPO ({exc}); uso greedy.")
    else:
        print(f"[PackFlow] Sin checkpoint en {CHECKPOINT}.zip; uso greedy.")
    return GreedyAgent()


agent: Agent = load_agent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": agent.name}


@app.post("/pack", response_model=PackResponse)
def pack(request: PackRequest) -> PackResponse:
    truck = (request.truck.W, request.truck.H, request.truck.D)
    env = make_env(request.boxes, truck, request.max_weight)
    sol = solve(env, agent)
    return PackResponse(**sol)


@app.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    """Recibe un manifiesto (JSON) y emite la carga paso a paso."""
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        request = PackRequest(**payload)
        truck = (request.truck.W, request.truck.H, request.truck.D)
        env = make_env(request.boxes, truck, request.max_weight)
        for event in run_episode(env, agent):
            await websocket.send_json(event.model_dump(exclude_none=True))
        await websocket.close()
    except WebSocketDisconnect:
        pass
