// URL del backend. Configurable con VITE_API_URL al hacer el build.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_URL = API_URL.replace(/^http/, "ws") + "/stream";

export async function checkHealth() {
  const r = await fetch(`${API_URL}/health`);
  if (!r.ok) throw new Error("backend no disponible");
  return r.json(); // { status, agent }
}

// Resuelve el manifiesto completo con un agente específico (sin animar).
// Se usa para la barra comparativa (baseline greedy).
export async function packWith(boxes, agentName) {
  const r = await fetch(`${API_URL}/pack`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ boxes, agent: agentName }),
  });
  if (!r.ok) throw new Error("fallo /pack");
  return r.json();
}
