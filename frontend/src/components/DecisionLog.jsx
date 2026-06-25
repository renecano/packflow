import { useEffect, useRef } from "react";

// El log de decisiones: narra en vivo lo que el agente hace. Es el elemento
// distintivo del demo — convierte la inferencia del agente en algo legible.
export default function DecisionLog({ lines }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="log">
      <div className="section" style={{ borderBottom: "1px solid var(--border-soft)" }}>
        <div className="eyebrow" style={{ margin: 0 }}>
          Decisiones del agente
        </div>
      </div>
      <div className="stream">
        {lines.length === 0 && <div className="empty">A la espera de un manifiesto…</div>}
        {lines.map((l, i) => (
          <div key={i} className={`line ${l.type}`}>
            <span className="t">{l.step}</span>
            <span className="tag">{l.tag}</span>
            <span>{l.text}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
