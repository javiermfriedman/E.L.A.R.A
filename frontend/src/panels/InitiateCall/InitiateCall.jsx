import { useState, useEffect, useRef } from "react";
import { initiateCall, getCallStatus, cancelCall } from "../../services/api";
import "./InitiateCall.css";

const CHATTER_IDLE = [
  "sys_check: all nodes nominal",
  "voice_engine: codec ready",
  "awaiting_launch_cmd",
];

const CHATTER_CALLING = [
  "route_confirmed: twilio active",
  "voice_stream: initializing...",
  "transmission_in_progress",
];

function CallStatusModal({ callSid, contact, agent, onClose }) {
  const [status, setStatus] = useState("ringing");
  const [duration, setDuration] = useState(0);
  const [done, setDone] = useState(false);
  const [aborting, setAborting] = useState(false);
  const [aborted, setAborted] = useState(false);
  const intervalRef = useRef(null);
  const durationRef = useRef(null);

  useEffect(() => {
    durationRef.current = setInterval(() => setDuration((d) => d + 1), 1000);

    intervalRef.current = setInterval(async () => {
      try {
        const data = await getCallStatus(callSid);
        setStatus(data.status);
        if (
          ["completed", "failed", "busy", "no-answer", "canceled"].includes(
            data.status,
          )
        ) {
          setDone(true);
          clearInterval(intervalRef.current);
          clearInterval(durationRef.current);
        }
      } catch (err) {
        console.error("Status poll error:", err);
      }
    }, 3000);

    return () => {
      clearInterval(intervalRef.current);
      clearInterval(durationRef.current);
    };
  }, [callSid]);

  async function handleAbort() {
    setAborting(true);
    try {
      await cancelCall(callSid);
      setStatus("canceled");
      setAborted(true);
      setDone(true);
      clearInterval(intervalRef.current);
      clearInterval(durationRef.current);
      setTimeout(() => onClose(), 2000);
    } catch (err) {
      console.error("Abort error:", err);
    } finally {
      setAborting(false);
    }
  }

  function formatDuration(secs) {
    const m = String(Math.floor(secs / 60)).padStart(2, "0");
    const s = String(secs % 60).padStart(2, "0");
    return `00:${m}:${s}`;
  }

  function getTagClass(s) {
    if (s === "ringing" || s === "queued") return "ic-modal__tag--ringing";
    if (s === "in-progress") return "ic-modal__tag--in-progress";
    if (s === "completed") return "ic-modal__tag--completed";
    if (s === "canceled") return "ic-modal__tag--failed";
    return "ic-modal__tag--failed";
  }

  return (
    <div className="ic-modal-overlay">
      <div className="ic-modal">
        <div className="ic-modal__header">
          <div className="ic-modal__title">◈ Transmission In Progress</div>
        </div>

        <div className="ic-modal__body">
          <div className="ic-modal__row">
            <div className="ic-modal__key">Target</div>
            <div className="ic-modal__val">
              {contact?.name} · {contact?.phone_number}
            </div>
          </div>
          <div className="ic-modal__row">
            <div className="ic-modal__key">Operative</div>
            <div className="ic-modal__val">{agent?.name}</div>
          </div>
          <div className="ic-modal__row">
            <div className="ic-modal__key">Call SID</div>
            <div className="ic-modal__val ic-modal__val--cyan">{callSid}</div>
          </div>
          <div className="ic-modal__row">
            <div className="ic-modal__key">Status</div>
            <div className={`ic-modal__tag ${getTagClass(status)}`}>
              ● {status.toUpperCase()}
            </div>
          </div>
          <div className="ic-modal__row">
            <div className="ic-modal__key">Duration</div>
            <div className="ic-modal__val ic-modal__val--green">
              {formatDuration(duration)}
            </div>
          </div>
        </div>

        <div
          className="ic-modal__footer"
          style={{ flexDirection: "column", gap: "8px" }}
        >
          {aborted ? (
            <div className="ic-modal__aborted">
              ⚠ MISSION ABORTED — CLOSING...
            </div>
          ) : done ? (
            <div className="ic-modal__footer-done">◉ TRANSMISSION COMPLETE</div>
          ) : (
            <>
              <div className="ic-modal__footer-live">
                ◉ LIVE — POLLING EVERY 3S
              </div>
              <button
                className="ic-modal__abort"
                onClick={handleAbort}
                disabled={aborting}
              >
                <span>{aborting ? "⌗ ABORTING..." : "⚠ ABORT MISSION"}</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function InitiateCall({
  contact,
  agent,
  contacts,
  agents,
  onSelectContact,
  onSelectAgent,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [callSid, setCallSid] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [chatter, setChatter] = useState(CHATTER_IDLE);

  const isReady = !!contact && !!agent;

  // Rotate chatter lines
  useEffect(() => {
    const lines = showModal ? CHATTER_CALLING : CHATTER_IDLE;
    setChatter(lines);
  }, [showModal]);

  async function handleLaunch() {
    if (!isReady) return;
    setLoading(true);
    setError("");
    try {
      const result = await initiateCall(
        String(agent.id),
        contact.name,
        contact.phone_number,
      );
      setCallSid(result.call_sid);
      setShowModal(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function getPreflightVal(key) {
    switch (key) {
      case "target":
        return contact
          ? { label: "LOCKED", cls: "green" }
          : { label: "AWAITING", cls: "dim" };
      case "operative":
        return agent
          ? { label: "READY", cls: "cyan" }
          : { label: "AWAITING", cls: "dim" };
      case "voice":
        return agent
          ? { label: "ONLINE", cls: "green" }
          : { label: "STANDBY", cls: "dim" };
      case "route":
        return isReady
          ? { label: "ACTIVE", cls: "amber" }
          : { label: "IDLE", cls: "dim" };
      default:
        return { label: "—", cls: "dim" };
    }
  }

  return (
    <>
      <div className="ic-panel">
        {/* Titlebar */}
        <div className="ic-titlebar">
          <div className="ic-titlebar__left">
            <div className="ic-titlebar__dot" />
            <div className="ic-titlebar__title">★ Prank Ops Console</div>
          </div>
          <div className="ic-titlebar__tag">
            {isReady ? "ARMED" : "STANDBY"}
          </div>
        </div>

        {/* Target dossier */}
        <div className="ic-dossier">
          <div className="ic-dossier__bg">
            {contact?.image ? (
              <img
                src={`data:image/png;base64,${contact.image}`}
                alt={contact.name}
              />
            ) : (
              <div className="ic-dossier__bg-placeholder">◎</div>
            )}
          </div>
          <div className="ic-dossier__scanlines" />
          <div className="ic-dossier__sweep" />
          <div className="ic-dossier__vignette" />
          <div className="ic-dossier__overlay">
            <div className="ic-dossier__top">
              <div className="ic-dossier__id">
                {contact
                  ? `TGT-${String(contact.id).padStart(4, "0")} // CIVILIAN`
                  : "TGT-???? // UNASSIGNED"}
              </div>
              {contact && (
                <div className="ic-dossier__locked">▣ SUBJECT LOCKED</div>
              )}
            </div>
            {contact ? (
              <div className="ic-dossier__bottom">
                <div className="ic-dossier__name">{contact.name}</div>
                <div className="ic-dossier__phone">{contact.phone_number}</div>
                <div className="ic-dossier__status">
                  ▸ PROFILE LOADED — COMMS CHANNEL VERIFIED
                </div>
              </div>
            ) : (
              <div className="ic-dossier__empty-label">— SELECT TARGET —</div>
            )}
          </div>
        </div>

        {/* Target swap */}
        <div className="ic-swap">
          <div className="ic-swap__label">Override Target</div>
          <select
            className="ic-swap__select"
            value={contact?.id || ""}
            onChange={(e) => {
              const found = contacts.find(
                (c) => String(c.id) === e.target.value,
              );
              if (found) onSelectContact(found);
            }}
          >
            <option value="">— select target —</option>
            {contacts.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="ic-divider">
          <div className="ic-divider__line" />
          <div className="ic-divider__label">◈ Operative Assignment ◈</div>
          <div className="ic-divider__line" />
        </div>

        {/* Agent operative block */}
        <div className="ic-operative">
          <div className="ic-operative__bg">
            {agent?.image ? (
              <img
                src={`data:image/png;base64,${agent.image}`}
                alt={agent.name}
              />
            ) : (
              <div className="ic-operative__bg-placeholder">◈</div>
            )}
          </div>
          <div className="ic-operative__scanlines" />
          <div className="ic-operative__vignette" />
          <div className="ic-operative__overlay">
            <div className="ic-operative__top">
              <div className="ic-operative__id">
                {agent
                  ? `OPR-${String(agent.id).padStart(3, "0")} // AI-VOICE`
                  : "OPR-??? // UNASSIGNED"}
              </div>
              {agent && (
                <div className="ic-operative__status">◉ STANDING BY</div>
              )}
            </div>
            {agent ? (
              <div className="ic-operative__bottom">
                <div className="ic-operative__name">{agent.name}</div>
                <div className="ic-operative__voice">
                  VOICE: {agent.voice_id?.slice(0, 12)}...
                </div>
                <div className="ic-operative__ready">
                  ▸ OPERATIVE READY — PERSONA LOADED
                </div>
              </div>
            ) : (
              <div className="ic-operative__empty-label">
                — SELECT OPERATIVE —
              </div>
            )}
          </div>
        </div>

        {/* Agent swap */}
        <div className="ic-swap">
          <div className="ic-swap__label">Override Operative</div>
          <select
            className="ic-swap__select"
            value={agent?.id || ""}
            onChange={(e) => {
              const found = agents.find((a) => String(a.id) === e.target.value);
              if (found) onSelectAgent(found);
            }}
          >
            <option value="">— select operative —</option>
            {agents.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </div>

        <div className="ic-divider">
          <div className="ic-divider__line" />
          <div className="ic-divider__label">◈ System Preflight ◈</div>
          <div className="ic-divider__line" />
        </div>

        {/* Preflight status */}
        <div className="ic-preflight">
          {[
            { key: "target", label: "Target" },
            { key: "operative", label: "Operative" },
            { key: "voice", label: "Voice Engine" },
            { key: "route", label: "Transmission" },
          ].map(({ key, label }) => {
            const { label: val, cls } = getPreflightVal(key);
            return (
              <div className="ic-preflight__row" key={key}>
                <div className="ic-preflight__key">{label}</div>
                <div className={`ic-preflight__val ic-preflight__val--${cls}`}>
                  ● {val}
                </div>
              </div>
            );
          })}
        </div>

        <div className="ic-divider">
          <div className="ic-divider__line" />
          <div className="ic-divider__label">◈ Sys Chatter ◈</div>
          <div className="ic-divider__line" />
        </div>

        {/* Sys chatter */}
        <div className="ic-chatter">
          {chatter.map((line, i) => (
            <div
              key={i}
              className={`ic-chatter__line ${i === chatter.length - 1 ? "ic-chatter__line--active" : ""}`}
            >
              [{new Date().toLocaleTimeString("en-US", { hour12: false })}]{" "}
              {line}
              {i === chatter.length - 1 && (
                <span className="ic-chatter__cursor" />
              )}
            </div>
          ))}
          {error && (
            <div
              className="ic-chatter__line"
              style={{ color: "var(--color-red)" }}
            >
              [ERR] {error}
            </div>
          )}
        </div>

        {/* Launch */}
        <div className="ic-launch">
          <button
            className="ic-launch__btn"
            onClick={handleLaunch}
            disabled={!isReady || loading}
          >
            <span>
              {loading ? "⌗ INITIATING..." : "⌗ INITIATE TRANSMISSION"}
            </span>
          </button>
          <div className="ic-launch__sub">
            {isReady
              ? "ALL SYSTEMS GO — CLEARANCE LVL 7"
              : "AWAITING TARGET + OPERATIVE SELECTION"}
          </div>
        </div>
      </div>

      {showModal && callSid && (
        <CallStatusModal
          callSid={callSid}
          contact={contact}
          agent={agent}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}
