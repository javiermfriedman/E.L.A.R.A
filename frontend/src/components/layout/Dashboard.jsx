import "./Dashboard.css";
import TopBar from "./TopBar";
import LeftStrip from "./LeftStrip";

// Temporary placeholders
function Panel({ label, style }) {
  return (
    <div
      style={{
        border: "1px solid rgba(0,255,156,0.15)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "var(--color-text-dim)",
        fontFamily: "var(--font-mono)",
        fontSize: "11px",
        letterSpacing: "0.2em",
        textTransform: "uppercase",
        background: "var(--color-bg-panel)",
        ...style,
      }}
    >
      {label}
    </div>
  );
}

export default function Dashboard({ onLogout }) {
  return (
    <div className="dashboard">
      <div className="dashboard__topbar">
        <TopBar />
      </div>
      <div className="dashboard__leftstrip">
        <LeftStrip onLogout={onLogout} />
      </div>
      <div className="dashboard__contacts">
        <Panel label="◈ Contacts" />
      </div>
      <div className="dashboard__hero">
        <Panel
          label="★ Initiate Call"
          style={{
            border: "1px solid rgba(0,255,156,0.5)",
            boxShadow: "var(--glow-primary)",
          }}
        />
      </div>
      <div className="dashboard__agents">
        <Panel label="◈ Agents" />
      </div>
      <div className="dashboard__recentcalls">
        <Panel label="◈ Recent Calls" />
      </div>
      <div className="dashboard__cinematic">
        <Panel label="◈ System" />
      </div>
    </div>
  );
}
