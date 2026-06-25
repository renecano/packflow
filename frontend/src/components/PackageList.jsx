import { fragilityColor } from "../scenarios.js";

// Lista de paquetes del manifiesto con su estado (cargado / saltado / pendiente).
// Al hacer clic se sincroniza con el resaltado en la escena 3D.
export default function PackageList({ packages, selectedId, onSelect }) {
  if (!packages.length) {
    return <div className="empty">Selecciona un escenario.</div>;
  }
  return (
    <div className="pkg-list">
      {packages.map((p) => (
        <button
          key={p.id}
          className={`pkg ${p.status} ${p.id === selectedId ? "sel" : ""}`}
          onClick={() => onSelect(p.id === selectedId ? null : p.id)}
        >
          <span className="swatch" style={{ background: fragilityColor(p.fragility) }} />
          <span className="pid">#{p.id}</span>
          <span className="dims">
            {p.w}×{p.h}×{p.d}
          </span>
          <span className="seq">e{p.delivery_order}</span>
          <span className={`st ${p.status}`}>
            {p.status === "placed" ? "cargado" : p.status === "skipped" ? "saltado" : "—"}
          </span>
        </button>
      ))}
    </div>
  );
}
