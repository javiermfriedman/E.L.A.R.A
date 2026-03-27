import { useState, useEffect, useRef } from "react";
import PanelWrapper from "../../components/ui/PanelWrapper";
import {
  deleteContacts,
  deleteRecordings,
  deleteAgents,
} from "../../services/api";
import "./SystemStatus.css";

const FEED_TEMPLATES = [
  () =>
    `SYN_${Math.floor(Math.random() * 0xffff)
      .toString(16)
      .toUpperCase()
      .padStart(4, "0")} >> NODE_${Math.floor(Math.random() * 99)
      .toString()
      .padStart(2, "0")}`,
  () =>
    `ENCRYPT [AES-256] KEY:${Math.floor(Math.random() * 0xffffffff)
      .toString(16)
      .toUpperCase()
      .padStart(8, "0")}`,
  () =>
    `PKT_DROP: ${(Math.random() * 0.4).toFixed(3)}% / LATENCY: ${Math.floor(Math.random() * 40 + 10)}ms`,
  () =>
    `ROUTE ${["ALPHA", "BRAVO", "DELTA", "ECHO", "FOXTROT"][Math.floor(Math.random() * 5)]} >> ${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.X.X`,
  () =>
    `AUTH_TOKEN: ${Math.random().toString(36).slice(2, 10).toUpperCase()}...VALID`,
  () =>
    `CHAOS_LVL: ${Math.floor(Math.random() * 100)}% | ENTROPY: ${(Math.random() * 9 + 1).toFixed(4)}`,
  () => `[WARN] NODE_${Math.floor(Math.random() * 99)} SIGNAL DEGRADED`,
  () =>
    `CIPHER_ROT: ${Math.floor(Math.random() * 26)} / SALT: ${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
  () =>
    `UPLINK ${["STABLE", "NOMINAL", "DEGRADED", "STRONG"][Math.floor(Math.random() * 4)]} — ${Math.floor(Math.random() * 100)}Mbps`,
  () =>
    `OP_HASH: ${Math.floor(Math.random() * 0xffffffff)
      .toString(16)
      .toUpperCase()}`,
  () =>
    `[ALERT] SIGNAL_SPIKE: CH_${Math.floor(Math.random() * 32)
      .toString()
      .padStart(2, "0")}`,
  () =>
    `COORD_LOCK: ${(Math.random() * 180 - 90).toFixed(4)}°N ${(Math.random() * 360 - 180).toFixed(4)}°E`,
];

function getFeedClass(line) {
  if (line.includes("[WARN]")) return "sys-feed__line--warn";
  if (line.includes("[ALERT]")) return "sys-feed__line--alert";
  if (
    line.includes("VALID") ||
    line.includes("STABLE") ||
    line.includes("NOMINAL")
  )
    return "sys-feed__line--hot";
  return "";
}

function Globe() {
  return (
    <div className="sys-globe">
      <svg
        className="sys-globe__svg"
        width="100"
        height="100"
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="40"
          className="sys-globe__ring"
          opacity="0.4"
        />
        {[0, 30, 60, 90, 120, 150].map((angle, i) => (
          <ellipse
            key={i}
            cx="50"
            cy="50"
            rx="40"
            ry={10 + i * 5}
            className="sys-globe__meridian"
            style={{
              transform: `rotate(${angle}deg)`,
              transformOrigin: "50px 50px",
            }}
          />
        ))}
        <ellipse
          cx="50"
          cy="50"
          rx="40"
          ry="14"
          className="sys-globe__ring sys-globe__ring--spin1"
          opacity="0.5"
        />
        <ellipse
          cx="50"
          cy="50"
          rx="40"
          ry="14"
          className="sys-globe__ring sys-globe__ring--spin2"
          opacity="0.3"
        />
        <ellipse
          cx="50"
          cy="50"
          rx="14"
          ry="40"
          className="sys-globe__ring sys-globe__ring--spin3"
          opacity="0.25"
        />
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="rgba(0,255,156,0.2)"
          strokeWidth="0.5"
        />
        <circle cx="65" cy="38" r="2" className="sys-globe__dot" />
        <circle
          cx="35"
          cy="58"
          r="1.5"
          className="sys-globe__dot"
          style={{ animationDelay: "1s" }}
        />
        <circle
          cx="58"
          cy="62"
          r="1.5"
          className="sys-globe__dot"
          style={{ animationDelay: "0.5s" }}
        />
        <line
          x1="10"
          y1="50"
          x2="90"
          y2="50"
          stroke="rgba(0,255,156,0.08)"
          strokeWidth="0.5"
        />
        <line
          x1="50"
          y1="10"
          x2="50"
          y2="90"
          stroke="rgba(0,255,156,0.08)"
          strokeWidth="0.5"
        />
      </svg>
      <div className="sys-globe__label">GLOBAL NODE NETWORK</div>
    </div>
  );
}

function PurgeModal({ onClose, onPurged }) {
  const [step, setStep] = useState("select"); // select | confirm | purging | done
  const [checks, setChecks] = useState({
    agents: false,
    targets: false,
    archives: false,
  });
  const [progress, setProgress] = useState(0);
  const [statuses, setStatuses] = useState({});

  const noneSelected = !checks.agents && !checks.targets && !checks.archives;

  function toggleCheck(key) {
    setChecks((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  async function handlePurge() {
    setStep("purging");
    const selected = Object.entries(checks)
      .filter(([, v]) => v)
      .map(([k]) => k);
    const total = selected.length;
    let done = 0;

    for (const key of selected) {
      setStatuses((prev) => ({ ...prev, [key]: "active" }));
      try {
        if (key === "agents") await deleteAgents();
        if (key === "targets") await deleteContacts();
        if (key === "archives") await deleteRecordings();
        setStatuses((prev) => ({ ...prev, [key]: "done" }));
      } catch (err) {
        setStatuses((prev) => ({ ...prev, [key]: "done" }));
      }
      done++;
      setProgress(Math.round((done / total) * 100));
      await new Promise((r) => setTimeout(r, 800));
    }

    setStep("done");
    setTimeout(() => {
      onClose();
      onPurged();
    }, 2000);
  }

  const ITEMS = [
    { key: "agents", label: "Operative Files", sub: "All deployed agents" },
    {
      key: "targets",
      label: "Target Dossiers",
      sub: "All registered contacts",
    },
    { key: "archives", label: "Mission Archive", sub: "All call recordings" },
  ];

  return (
    <div className="purge-overlay">
      <div className="purge-modal">
        <div className="purge-modal__header">
          <div className="purge-modal__title">⚠ System Purge Protocol</div>
          {step === "select" && (
            <button className="purge-modal__close" onClick={onClose}>
              ✕
            </button>
          )}
        </div>

        <div className="purge-modal__body">
          {step === "select" && (
            <>
              <div className="purge-modal__warning">
                WARNING — THIS ACTION IS IRREVERSIBLE
                <br />
                SELECT DATA CATEGORIES TO DESTROY
              </div>
              <div className="purge-modal__checks">
                {ITEMS.map(({ key, label, sub }) => (
                  <div
                    key={key}
                    className={`purge-check ${checks[key] ? "checked" : ""}`}
                    onClick={() => toggleCheck(key)}
                  >
                    <div className="purge-check__box">
                      {checks[key] ? "✕" : ""}
                    </div>
                    <div className="purge-check__info">
                      <div className="purge-check__label">{label}</div>
                      <div className="purge-check__sub">{sub}</div>
                    </div>
                  </div>
                ))}
              </div>
              <button
                className="purge-modal__confirm-btn"
                disabled={noneSelected}
                onClick={() => setStep("confirm")}
              >
                <span>⌗ Proceed to Purge</span>
              </button>
            </>
          )}

          {step === "confirm" && (
            <>
              <div className="purge-confirm__text">
                ARE YOU SURE?
                <br />
                THIS CANNOT BE UNDONE.
                <br />
                ALL SELECTED DATA WILL BE
                <br />
                PERMANENTLY DESTROYED.
              </div>
              <div className="purge-confirm__btns">
                <button
                  className="purge-confirm__no"
                  onClick={() => setStep("select")}
                >
                  ← ABORT
                </button>
                <button className="purge-confirm__yes" onClick={handlePurge}>
                  ⚠ CONFIRM PURGE
                </button>
              </div>
            </>
          )}

          {step === "purging" && (
            <div className="purge-progress">
              <div className="purge-progress__title">⚠ PURGE IN PROGRESS</div>
              <div className="purge-progress__items">
                {ITEMS.filter(({ key }) => checks[key]).map(
                  ({ key, label }) => (
                    <div
                      key={key}
                      className={`purge-progress__item purge-progress__item--${statuses[key] || "pending"}`}
                    >
                      <span>{label}</span>
                      <span>
                        {statuses[key] === "done"
                          ? "✓ DESTROYED"
                          : statuses[key] === "active"
                            ? "⌗ PURGING..."
                            : "— QUEUED"}
                      </span>
                    </div>
                  ),
                )}
              </div>
              <div className="purge-progress__bar-wrap">
                <div
                  className="purge-progress__bar-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {step === "done" && (
            <div className="purge-progress">
              <div className="purge-progress__done">
                ◉ PURGE COMPLETE
                <br />
                ALL DATA DESTROYED
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SystemStatus({ onPurged }) {
  const [showPurge, setShowPurge] = useState(false);
  const [feedLines, setFeedLines] = useState(() =>
    Array.from({ length: 8 }, () =>
      FEED_TEMPLATES[Math.floor(Math.random() * FEED_TEMPLATES.length)](),
    ),
  );
  const [uptime, setUptime] = useState(0);
  const [connections, setConnections] = useState(
    Math.floor(Math.random() * 40 + 10),
  );
  const [nodeSync, setNodeSync] = useState((Math.random() * 2 + 98).toFixed(3));

  useEffect(() => {
    const id = setInterval(() => {
      setFeedLines((prev) => {
        const newLine =
          FEED_TEMPLATES[Math.floor(Math.random() * FEED_TEMPLATES.length)]();
        return [...prev.slice(1), newLine];
      });
      setConnections(Math.floor(Math.random() * 40 + 10));
      setNodeSync((Math.random() * 2 + 98).toFixed(3));
    }, 1200);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => setUptime((u) => u + 1), 1000);
    return () => clearInterval(id);
  }, []);

  function formatUptime(secs) {
    const h = String(Math.floor(secs / 3600)).padStart(2, "0");
    const m = String(Math.floor((secs % 3600) / 60)).padStart(2, "0");
    const s = String(secs % 60).padStart(2, "0");
    return `${h}:${m}:${s}`;
  }

  return (
    <>
      <PanelWrapper title="◈ System Intel">
        <div className="sys-panel">
          <Globe />

          <div className="sys-divider">
            <div className="sys-divider__line" />
            <div className="sys-divider__label">◈ Encrypted Feed ◈</div>
            <div className="sys-divider__line" />
          </div>

          <div className="sys-feed">
            {feedLines.map((line, i) => (
              <div key={i} className={`sys-feed__line ${getFeedClass(line)}`}>
                {line}
              </div>
            ))}
          </div>

          <div className="sys-divider">
            <div className="sys-divider__line" />
            <div className="sys-divider__label">◈ System Metrics ◈</div>
            <div className="sys-divider__line" />
          </div>

          <div className="sys-stats">
            <div className="sys-stat">
              <div className="sys-stat__label">UPTIME</div>
              <div className="sys-stat__val">{formatUptime(uptime)}</div>
            </div>
            <div className="sys-stat">
              <div className="sys-stat__label">CONNECTIONS</div>
              <div className="sys-stat__val sys-stat__val--cyan">
                {connections}
              </div>
            </div>
            <div className="sys-stat">
              <div className="sys-stat__label">NODE SYNC</div>
              <div className="sys-stat__val sys-stat__val--amber">
                {nodeSync}%
              </div>
            </div>
            <div className="sys-stat">
              <div className="sys-stat__label">ENCRYPTION</div>
              <div className="sys-stat__val">AES-256</div>
            </div>
            <div className="sys-stat">
              <div className="sys-stat__label">CLEARANCE</div>
              <div className="sys-stat__val sys-stat__val--amber">LEVEL 7</div>
            </div>
            <div className="sys-stat">
              <div className="sys-stat__label">THREAT LVL</div>
              <div className="sys-stat__val sys-stat__val--red">ELEVATED</div>
            </div>
          </div>

          <div className="sys-purge-wrap">
            <button
              className="sys-purge-btn"
              onClick={() => setShowPurge(true)}
            >
              ⚠ SYSTEM PURGE
            </button>
          </div>
        </div>
      </PanelWrapper>

      {showPurge && (
        <PurgeModal
          onClose={() => setShowPurge(false)}
          onPurged={() => onPurged && onPurged()}
        />
      )}
    </>
  );
}
