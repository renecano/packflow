import { SCENARIOS } from "../scenarios.js";
import DecisionLog from "./DecisionLog.jsx";

export default function ControlPanel({ selected, onSelect, onRun, onReset, running, canRun, logLines }) {
  return (
    <aside className="panel">
      <div className="section">
        <div className="eyebrow">Escenario</div>
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            className={`scenario ${selected === s.id ? "active" : ""}`}
            onClick={() => onSelect(s.id)}
            disabled={running}
          >
            <div className="name">{s.name}</div>
            <div className="meta">{s.meta}</div>
          </button>
        ))}
      </div>

      <div className="section">
        <button className="run-btn" onClick={onRun} disabled={!canRun || running}>
          {running ? "Cargando camión…" : "Cargar camión"}
        </button>
        <button className="ghost-btn" onClick={onReset} disabled={running}>
          Vaciar
        </button>
      </div>

      <DecisionLog lines={logLines} />
    </aside>
  );
}
