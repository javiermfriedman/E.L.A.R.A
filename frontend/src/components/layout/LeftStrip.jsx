import { useState, useEffect } from "react";
import "./LeftStrip.css";

const WAVE_BARS = 10;
const HEX_LINES = 6;

function randomHex() {
  return Array.from({ length: 4 }, () =>
    Math.floor(Math.random() * 0xffff)
      .toString(16)
      .toUpperCase()
      .padStart(4, "0"),
  ).join(" ");
}

function formatCountdown(secs) {
  const h = String(Math.floor(secs / 3600)).padStart(2, "0");
  const m = String(Math.floor((secs % 3600) / 60)).padStart(2, "0");
  const s = String(secs % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

export default function LeftStrip({ onLogout }) {
  const [metrics, setMetrics] = useState({ cpu: 42, voice: 78, chaos: 31 });
  const [hexLines, setHexLines] = useState(() =>
    Array.from({ length: HEX_LINES }, randomHex),
  );
  const [coords, setCoords] = useState({
    lat: "40.7128° N",
    lng: "74.0060° W",
  });
  const [countdown, setCountdown] = useState(847);

  // Fluctuate metrics
  useEffect(() => {
    const id = setInterval(() => {
      setMetrics({
        cpu: Math.min(
          99,
          Math.max(10, (prev) => prev, Math.floor(Math.random() * 30) + 30),
        ),
        voice: Math.min(99, Math.max(50, Math.floor(Math.random() * 40) + 50)),
        chaos: Math.min(99, Math.max(5, Math.floor(Math.random() * 60) + 5)),
      });
    }, 2000);
    return () => clearInterval(id);
  }, []);

  // Scroll hex data
  useEffect(() => {
    const id = setInterval(() => {
      setHexLines((prev) => [...prev.slice(1), randomHex()]);
    }, 800);
    return () => clearInterval(id);
  }, []);

  // Drift coordinates
  useEffect(() => {
    const id = setInterval(() => {
      const lat = (40.7128 + (Math.random() - 0.5) * 0.001).toFixed(4);
      const lng = (74.006 + (Math.random() - 0.5) * 0.001).toFixed(4);
      setCoords({ lat: `${lat}° N`, lng: `${lng}° W` });
    }, 3000);
    return () => clearInterval(id);
  }, []);

  // Countdown timer
  useEffect(() => {
    const id = setInterval(() => {
      setCountdown((c) => (c <= 0 ? 3600 : c - 1));
    }, 1000);
    return () => clearInterval(id);
  }, []);

  function metricColor(val) {
    if (val > 75) return "--red";
    if (val > 50) return "--amber";
    return "--green";
  }

  return (
    <div className="leftstrip">
      {/* Logo */}
      <div className="ls-logo">
        <div className="ls-logo__name">E.L.A.R.A</div>
        <div className="ls-logo__sub">OPS CMD</div>
      </div>

      <div className="ls-divider" />

      {/* Home button */}
      <button className="ls-home" onClick={onLogout} title="Return to Login">
        <span className="ls-home__icon">⌂</span>
        <span className="ls-home__label">Home</span>
      </button>

      <div className="ls-divider" />

      {/* Metric bars */}
      <div className="ls-metrics">
        {[
          { label: "CPU", val: metrics.cpu },
          { label: "VOICE", val: metrics.voice },
          { label: "CHAOS", val: metrics.chaos },
        ].map(({ label, val }) => (
          <div className="ls-metric" key={label}>
            <div className="ls-metric__label">{label}</div>
            <div className="ls-metric__track">
              <div
                className={`ls-metric__fill ls-metric__fill${metricColor(val)}`}
                style={{ width: `${val}%` }}
              />
            </div>
            <div className="ls-metric__value">{val}%</div>
          </div>
        ))}
      </div>

      <div className="ls-divider" />

      {/* Waveform */}
      <div className="ls-wave">
        {Array.from({ length: WAVE_BARS }).map((_, i) => (
          <div
            key={i}
            className="ls-wave__bar"
            style={{ animationDelay: `${(i / WAVE_BARS) * 1.4}s` }}
          />
        ))}
      </div>

      <div className="ls-divider" />

      {/* Hex scroll */}
      <div className="ls-hex">
        {hexLines.map((line, i) => (
          <div
            key={i}
            className="ls-hex__line"
            style={{ animationDelay: `${i * 0.3}s` }}
          >
            {line}
          </div>
        ))}
      </div>

      <div className="ls-divider" />

      {/* Coordinates */}
      <div className="ls-coords">
        <div className="ls-coords__label">COORDS</div>
        <div className="ls-coords__value">{coords.lat}</div>
        <div className="ls-coords__value">{coords.lng}</div>
      </div>

      <div className="ls-divider" />

      {/* Status indicators */}
      <div className="ls-status">
        {[
          { label: "SYS", color: "green" },
          { label: "NET", color: "cyan" },
          { label: "LLM", color: "amber" },
        ].map(({ label, color }) => (
          <div className="ls-status__row" key={label}>
            <div className={`ls-status__dot ls-status__dot--${color}`} />
            <div className="ls-status__text">{label}</div>
          </div>
        ))}
      </div>

      <div className="ls-divider" />

      {/* Operatives */}
      <div className="ls-operatives">
        <div className="ls-operatives__label">OPS ONLINE</div>
        <div className="ls-operatives__value">07</div>
      </div>

      <div className="ls-divider" />

      {/* Countdown */}
      <div className="ls-countdown">
        <div className="ls-countdown__label">NEXT OP</div>
        <div className="ls-countdown__value">{formatCountdown(countdown)}</div>
      </div>
    </div>
  );
}
