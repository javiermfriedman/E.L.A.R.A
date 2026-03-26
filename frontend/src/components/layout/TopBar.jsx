import { useState, useEffect } from "react";
import { useElara } from "../../context/ElaraContext";
import "./TopBar.css";

const THREAT_SEGS = 8;

function useTick(ms) {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), ms);
    return () => clearInterval(id);
  }, [ms]);
  return tick;
}

export default function TopBar() {
  const { user } = useElara();
  const tick1s = useTick(1000);
  const tick3s = useTick(3000);

  const [time, setTime] = useState("");
  const [ping, setPing] = useState(24);
  const [missions] = useState(Math.floor(Math.random() * 900) + 100);
  const threatLevel = 3; // 1–8, could be dynamic later

  useEffect(() => {
    const now = new Date();
    setTime(
      now.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
    );
  }, [tick1s]);

  useEffect(() => {
    setPing(Math.floor(Math.random() * 40) + 12);
  }, [tick3s]);

  function getThreatClass(i) {
    if (i >= threatLevel) return "";
    if (i < 3) return "active-green";
    if (i < 6) return "active-amber";
    return "active-red";
  }

  const operative = user?.username || "GHOST-7";

  return (
    <div className="topbar">
      {/* LEFT */}
      <div className="topbar__left">
        <div className="topbar__logo">
          <div className="topbar__logo-name">E.L.A.R.A v1.0.0</div>
          <div className="topbar__logo-sub">Prank Ops Command</div>
        </div>

        <div className="topbar__sep" />

        <div className="topbar__operative">
          <div className="topbar__operative-label">Operative</div>
          <div className="topbar__operative-value">{operative}</div>
        </div>

        <div className="topbar__sep" />

        <div className="topbar__access">
          <div className="topbar__access-label">Clearance</div>
          <div className="topbar__access-value">[ LVL 7 ]</div>
        </div>
      </div>

      {/* CENTER */}
      <div className="topbar__center">
        <div className="topbar__title-wrap">
          <div className="topbar__title-line" />
          <div className="topbar__title">
            Top Secret — Prank Ops Command Center
          </div>
          <div className="topbar__title-line topbar__title-line--right" />
        </div>
      </div>

      {/* RIGHT */}
      <div className="topbar__right">
        <div className="topbar__threat">
          <div className="topbar__threat-label">Threat Level</div>
          <div className="topbar__threat-bar">
            {Array.from({ length: THREAT_SEGS }).map((_, i) => (
              <div
                key={i}
                className={`topbar__threat-seg ${getThreatClass(i)}`}
              />
            ))}
          </div>
        </div>

        <div className="topbar__sep" />

        <div className="topbar__missions">
          <div className="topbar__missions-label">Missions</div>
          <div className="topbar__missions-value">
            {String(missions).padStart(4, "0")}
          </div>
        </div>

        <div className="topbar__sep" />

        <div className="topbar__ping">
          <div className="topbar__ping-label">Ping</div>
          <div className="topbar__ping-value">{ping}ms</div>
        </div>

        <div className="topbar__sep" />

        <div className="topbar__clock-wrap">
          <div className="topbar__clock-label">System Time</div>
          <div className="topbar__clock">{time}</div>
        </div>
      </div>
    </div>
  );
}
