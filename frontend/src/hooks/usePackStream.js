import { useRef, useCallback } from "react";
import { WS_URL } from "../api.js";

// Hook que maneja la conexión WebSocket al endpoint /stream.
// Llama onEvent por cada paso y onDone con las métricas finales.
export function usePackStream() {
  const wsRef = useRef(null);

  const start = useCallback((manifest, { onEvent, onDone, onError }) => {
    // Cierra cualquier conexión previa.
    if (wsRef.current) wsRef.current.close();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => ws.send(JSON.stringify({ boxes: manifest }));

    ws.onmessage = (msg) => {
      const ev = JSON.parse(msg.data);
      if (ev.type === "done") {
        onDone?.(ev.metrics);
      } else {
        onEvent?.(ev);
      }
    };

    ws.onerror = () => onError?.("No se pudo conectar con el servidor.");
  }, []);

  const stop = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  return { start, stop };
}
