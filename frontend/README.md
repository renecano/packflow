# PackFlow — Frontend

Consola de visualización 3D del agente de carga, construida con React + Vite +
Three.js (`@react-three/fiber` y `@react-three/drei`).

## Requisitos

- Node.js 18+ y el backend de PackFlow corriendo (por defecto en
  `http://localhost:8000`).

## Arrancar en desarrollo

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Asegúrate de tener el backend levantado en otra
terminal:

```bash
uvicorn packflow.api.main:app --reload
```

## Apuntar a otro backend

Crea un archivo `.env` en `frontend/`:

```
VITE_API_URL=http://localhost:8000
```

## Cómo funciona

1. Eliges un escenario (manifiesto preconfigurado) en el panel izquierdo.
2. Al pulsar **Cargar camión**, el frontend abre un WebSocket a `/stream` y
   recibe la carga paso a paso, animando cada caja en la escena 3D.
3. El **log de decisiones** narra en vivo cada colocación o salto del agente.
4. Al terminar, se pide la solución del baseline greedy a `/pack` para la barra
   comparativa de la telemetría.

Las cajas se colorean por fragilidad: verde (resistente) → ámbar → rojo (frágil).

## Build de producción

```bash
npm run build      # genera dist/
npm run preview    # sirve dist/ localmente
```

El `dist/` se puede desplegar en Netlify, Vercel o GitHub Pages. Recuerda
configurar `VITE_API_URL` apuntando al backend desplegado.
