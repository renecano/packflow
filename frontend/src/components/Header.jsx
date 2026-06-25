export default function Header({ health, running }) {
  const connected = !!health;
  return (
    <header className="header">
      <div className="brand">
        <h1>
          PACK<span className="mark">FLOW</span>
        </h1>
        <span className="tag">carga 3D autónoma · RL</span>
      </div>
      <div className="status">
        <span>
          <span className={`dot ${connected ? (running ? "busy" : "on") : ""}`} />
          {connected ? (running ? "cargando" : "listo") : "sin conexión"}
        </span>
        <span>
          agente <b>{health?.agent ?? "—"}</b>
        </span>
      </div>
    </header>
  );
}
