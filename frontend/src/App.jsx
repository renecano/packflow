import { useState, useEffect, useCallback, useMemo } from "react";
import Header from "./components/Header.jsx";
import ControlPanel from "./components/ControlPanel.jsx";
import Telemetry from "./components/Telemetry.jsx";
import TruckScene from "./components/TruckScene.jsx";
import { usePackStream } from "./hooks/usePackStream.js";
import { checkHealth, packWith } from "./api.js";
import { SCENARIOS } from "./scenarios.js";

const TRUCK = { W: 12, H: 6, D: 8 };

export default function App() {
  const [health, setHealth] = useState(null);
  const [selected, setSelected] = useState(SCENARIOS[0].id);
  const [placed, setPlaced] = useState([]);
  const [log, setLog] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [running, setRunning] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  const { start } = usePackStream();
  const scenario = useMemo(() => SCENARIOS.find((s) => s.id === selected), [selected]);

  // Lista de paquetes con su estado actual, para la lista lateral.
  const packages = useMemo(() => {
    return scenario.boxes.map((b, id) => {
      const isPlaced = placed.some((p) => p.id === id);
      const status = isPlaced ? "placed" : metrics ? "skipped" : "pending";
      return { id, ...b, status };
    });
  }, [scenario, placed, metrics]);

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  const reset = useCallback(() => {
    setPlaced([]);
    setLog([]);
    setMetrics(null);
    setBaseline(null);
    setSelectedId(null);
  }, []);

  const handleSelect = useCallback(
    (id) => {
      setSelected(id);
      reset();
    },
    [reset]
  );

  const run = useCallback(() => {
    reset();
    setRunning(true);
    const boxes = scenario.boxes;

    start(boxes, {
      onEvent: (ev) => {
        if (ev.type === "place") {
          setPlaced((prev) => [
            ...prev,
            { id: ev.box_id, position: ev.position, size: ev.size, fragility: ev.fragility },
          ]);
          const atBack = ev.position[0] >= TRUCK.W / 2;
          setLog((prev) => [
            ...prev,
            {
              step: String(ev.step).padStart(2, "0"),
              type: "place",
              tag: "PLACE",
              text: `#${ev.box_id} → ${atBack ? "fondo" : "puerta"} · entrega ${ev.delivery_order}`,
            },
          ]);
        } else if (ev.type === "skip") {
          setLog((prev) => [
            ...prev,
            {
              step: String(ev.step).padStart(2, "0"),
              type: "skip",
              tag: "SKIP ",
              text: `#${ev.box_id} · sin espacio → siguiente viaje`,
            },
          ]);
        }
      },
      onDone: async (m) => {
        setMetrics(m);
        setLog((prev) => [
          ...prev,
          {
            step: "··",
            type: "done",
            tag: "DONE ",
            text: `${m.n_placed}/${m.n_total} cargados · ${(m.volume_utilization * 100).toFixed(1)}% volumen`,
          },
        ]);
        setRunning(false);
        // Baseline para la comparación.
        try {
          const base = await packWith(boxes, "greedy");
          setBaseline(base.metrics);
        } catch {
          /* sin baseline */
        }
      },
      onError: () => {
        setRunning(false);
        setLog((prev) => [
          ...prev,
          { step: "!!", type: "skip", tag: "ERROR", text: "Sin conexión con el servidor." },
        ]);
      },
    });
  }, [scenario, start, reset]);

  return (
    <div className="app">
      <Header health={health} running={running} />
      <div className="layout">
        <ControlPanel
          selected={selected}
          onSelect={handleSelect}
          onRun={run}
          onReset={reset}
          running={running}
          canRun={!!health}
          logLines={log}
        />

        <div className="stage">
          <TruckScene
            truck={TRUCK}
            placed={placed}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <div className="legend">
            <div className="row">
              <span className="sw" style={{ background: "#3dd68c" }} /> resistente
            </div>
            <div className="row">
              <span className="sw" style={{ background: "#f2a93b" }} /> sensible
            </div>
            <div className="row">
              <span className="sw" style={{ background: "#e5484d" }} /> frágil
            </div>
          </div>
          <div className="stage-overlay">
            camión 12 × 6 × 8 · puerta al frente · arrastra para orbitar
          </div>
        </div>

        <Telemetry
          metrics={metrics}
          baseline={baseline}
          totalBoxes={scenario.boxes.length}
          packages={packages}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      </div>
    </div>
  );
}
