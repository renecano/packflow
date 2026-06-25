import PackageList from "./PackageList.jsx";

function pct(x) {
  return (x * 100).toFixed(1);
}

export default function Telemetry({ metrics, baseline, totalBoxes, packages, selectedId, onSelect }) {
  const util = metrics ? metrics.volume_utilization : 0;
  const placed = metrics ? metrics.n_placed : 0;
  const total = metrics ? metrics.n_total : totalBoxes;
  const weight = metrics ? metrics.total_weight : 0;
  const maxW = metrics ? metrics.max_weight : 1000;

  // Comparación PPO vs baseline (greedy).
  const baseUtil = baseline ? baseline.volume_utilization : null;
  const deltaPP = baseUtil != null ? (util - baseUtil) * 100 : null;

  return (
    <aside className="panel right">
      <div className="section">
        <div className="eyebrow">Telemetría</div>

        <div className="metric">
          <div className="label">
            <span>Utilización de volumen</span>
          </div>
          <div className="value">
            {pct(util)}
            <span className="unit">%</span>
          </div>
          <div className="bar">
            <span style={{ width: `${Math.min(100, util * 100)}%` }} />
          </div>
        </div>

        <div className="metric">
          <div className="label">
            <span>Paquetes cargados</span>
          </div>
          <div className="value">
            {placed}
            <span className="unit">/ {total}</span>
          </div>
        </div>

        <div className="metric">
          <div className="label">
            <span>Peso</span>
            <span>{Math.round(maxW)} kg máx</span>
          </div>
          <div className="value">
            {Math.round(weight)}
            <span className="unit">kg</span>
          </div>
          <div className="bar cyan">
            <span style={{ width: `${Math.min(100, (weight / maxW) * 100)}%` }} />
          </div>
        </div>
      </div>

      <div className="section">
        <div className="eyebrow">PPO vs. baseline (FFD greedy)</div>
        {baseline ? (
          <div className="compare">
            <div className="crow">
              <div className="top">
                <span>PPO</span>
                <b>{pct(util)}%</b>
              </div>
              <div className="bar">
                <span style={{ width: `${util * 100}%` }} />
              </div>
            </div>
            <div className="crow">
              <div className="top">
                <span>Greedy</span>
                <b>{pct(baseUtil)}%</b>
              </div>
              <div className="bar cyan">
                <span style={{ width: `${baseUtil * 100}%` }} />
              </div>
            </div>
            {deltaPP != null && (
              <div className="delta" style={{ color: deltaPP >= 0 ? "var(--ok)" : "var(--danger)" }}>
                {deltaPP >= 0 ? "▲" : "▼"} {Math.abs(deltaPP).toFixed(1)} pp de utilización
              </div>
            )}
          </div>
        ) : (
          <div className="empty">Carga un camión para comparar.</div>
        )}
      </div>

      <div className="section" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
        <div className="eyebrow">Paquetes</div>
        <PackageList packages={packages} selectedId={selectedId} onSelect={onSelect} />
      </div>
    </aside>
  );
}
