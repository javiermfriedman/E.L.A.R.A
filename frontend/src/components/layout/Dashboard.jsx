import { useState, useEffect } from "react";
import "./Dashboard.css";
import TopBar from "./TopBar";
import LeftStrip from "./LeftStrip";
import Contacts from "../../panels/Contacts/Contacts";
import Agents from "../../panels/Agents/Agents";
import InitiateCall from "../../panels/InitiateCall/InitiateCall";
import MissionArchive from "../../panels/MissionArchive/MissionArchive";
import { getContacts, getAgents } from "../../services/api";

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
  const [selectedContact, setSelectedContact] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [agents, setAgents] = useState([]);
  const [ready, setReady] = useState(false);
  const [archiveKey, setArchiveKey] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem("elara_token");
    if (!token) return;

    async function load() {
      try {
        const [c, a] = await Promise.all([getContacts(), getAgents()]);
        setContacts(c);
        setAgents(a);
      } catch (err) {
        console.error("Dashboard load error:", err);
      } finally {
        setReady(true);
      }
    }
    load();
  }, []);

  if (!ready) return null;

  return (
    <div className="dashboard">
      <div className="dashboard__topbar">
        <TopBar />
      </div>
      <div className="dashboard__leftstrip">
        <LeftStrip onLogout={onLogout} />
      </div>
      <div className="dashboard__contacts">
        <Contacts
          contacts={contacts}
          setContacts={setContacts}
          selectedId={selectedContact?.id}
          onSelect={setSelectedContact}
        />
      </div>
      <div className="dashboard__hero">
        <InitiateCall
          contact={selectedContact}
          agent={selectedAgent}
          contacts={contacts}
          agents={agents}
          onSelectContact={setSelectedContact}
          onSelectAgent={setSelectedAgent}
          onCallComplete={() => setArchiveKey((k) => k + 1)}
        />
      </div>
      <div className="dashboard__agents">
        <Agents
          agents={agents}
          setAgents={setAgents}
          selectedId={selectedAgent?.id}
          onSelect={setSelectedAgent}
        />
      </div>
      <div className="dashboard__recentcalls">
        <MissionArchive refreshKey={archiveKey} />
      </div>
      <div className="dashboard__cinematic">
        <Panel label="◈ System" />
      </div>
    </div>
  );
}
