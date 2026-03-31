import { useState, useEffect, useRef } from "react";
import { getRecordingAudio, deleteRecording } from "../../services/api";
import "./FileModal.css";

function TapeReel({ spinning }) {
  return (
    <div className="tape-reel">
      <div className={`tape-reel__outer ${spinning ? "spinning" : ""}`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="tape-reel__spoke" />
        ))}
        <div className="tape-reel__hub" />
      </div>
    </div>
  );
}

const EXTRACT_PHASES = [
  { at: 0, label: "INITIATING SECURE CHANNEL..." },
  { at: 1500, label: "DECRYPTING CLASSIFIED INTEL..." },
  { at: 3000, label: "EXTRACTING AUDIO FILE..." },
  { at: 4500, label: "EXTRACTION COMPLETE" },
];

function randomHex(len) {
  return Array.from({ length: len }, () =>
    Math.floor(Math.random() * 16).toString(16).toUpperCase()
  ).join("");
}

function ExtractionOverlay({ recording, onComplete }) {
  const [phase, setPhase] = useState(0);
  const [progress, setProgress] = useState(0);
  const [hexLines, setHexLines] = useState(() =>
    Array.from({ length: 10 }, () => randomHex(48))
  );
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    const timers = EXTRACT_PHASES.map((p, i) =>
      setTimeout(() => setPhase(i), p.at)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    const start = Date.now();
    const duration = 4500;
    const id = setInterval(() => {
      const elapsed = Date.now() - start;
      setProgress(Math.min(100, Math.round((elapsed / duration) * 100)));
      if (elapsed >= duration) clearInterval(id);
    }, 50);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setHexLines((prev) => [...prev.slice(1), randomHex(48)]);
    }, 120);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (phase === 3) {
      const t = setTimeout(() => {
        setComplete(true);
        setTimeout(onComplete, 1000);
      }, 600);
      return () => clearTimeout(t);
    }
  }, [phase, onComplete]);

  const d = new Date(recording.created_at);
  const dateTag = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`;

  return (
    <div className="extract-overlay">
      <div className="extract-modal">
        <div className="extract__header">
          <span className="extract__header-icon">◈</span>
          SECURE EXTRACTION PROTOCOL
        </div>

        <div className="extract__hex-stream">
          {hexLines.map((line, i) => (
            <div key={i} className="extract__hex-line">{line}</div>
          ))}
        </div>

        <div className="extract__info">
          <div className="extract__info-row">
            <span className="extract__info-key">TARGET</span>
            <span className="extract__info-val">{recording.target_name}</span>
          </div>
          <div className="extract__info-row">
            <span className="extract__info-key">OP-ID</span>
            <span className="extract__info-val extract__info-val--blue">ID-{recording.id}</span>
          </div>
          <div className="extract__info-row">
            <span className="extract__info-key">FILE</span>
            <span className="extract__info-val extract__info-val--dim">
              {recording.target_name}_{dateTag}.wav
            </span>
          </div>
        </div>

        <div className={`extract__status ${phase === 3 ? "extract__status--done" : ""}`}>
          {EXTRACT_PHASES[phase].label}
        </div>

        <div className="extract__bar-wrap">
          <div className="extract__bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="extract__percent">{progress}%</div>

        {complete && (
          <div className="extract__complete">
            ◉ FILE SECURED — INITIATING TRANSFER
          </div>
        )}
      </div>
    </div>
  );
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return (
    d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }) +
    " " +
    d.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
    })
  );
}

export default function FileModal({ recording, onClose, onDeleted }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState("");
  const [deleteStep, setDeleteStep] = useState("idle"); // idle | confirm | deleting | destroyed
  const [extracting, setExtracting] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    async function loadAudio() {
      try {
        const url = await getRecordingAudio(recording.id);
        setAudioUrl(url);
      } catch (err) {
        setError("AUDIO UNAVAILABLE");
        console.error("Audio load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAudio();

    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [recording.id]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    function handleEnded() {
      setPlaying(false);
    }
    audio.addEventListener("ended", handleEnded);
    return () => audio.removeEventListener("ended", handleEnded);
  }, [audioUrl]);

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  }

  function triggerDownload() {
    if (!audioUrl) return;
    const d = new Date(recording.created_at);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    const filename = `${recording.target_name}_${y}${m}${day}.wav`;
    const a = document.createElement("a");
    a.href = audioUrl;
    a.download = filename;
    a.click();
  }

  function handleDownload() {
    if (!audioUrl) return;
    setExtracting(true);
  }

  function handleExtractionComplete() {
    triggerDownload();
    setExtracting(false);
  }

  async function handleDelete() {
    setDeleteStep("deleting");
    if (audioRef.current) audioRef.current.pause();
    setPlaying(false);
    try {
      await deleteRecording(recording.id);
      setDeleteStep("destroyed");
      setTimeout(() => {
        onDeleted?.();
        onClose();
      }, 2200);
    } catch {
      setDeleteStep("idle");
    }
  }

  if (deleteStep === "destroyed") {
    return (
      <div className="file-modal-overlay">
        <div className="file-modal file-modal--destroyed">
          <div className="file-destroy">
            <div className="file-destroy__icon">◉</div>
            <div className="file-destroy__text">FILE DESTROYED</div>
            <div className="file-destroy__sub">
              RECORD ID-{recording.id} PERMANENTLY ERASED
            </div>
            <div className="file-destroy__bar">
              <div className="file-destroy__bar-fill" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="file-modal-overlay" onClick={onClose}>
      <div className="file-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="file-modal__header">
          <div className="file-modal__title">◈ Classified Mission File</div>
          <button className="file-modal__close" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Metadata */}
        <div className="file-modal__meta">
          <div className="file-modal__row">
            <div className="file-modal__key">Operation</div>
            <div className="file-modal__val file-modal__val--amber">
              ID-{recording.id}
            </div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Target</div>
            <div className="file-modal__val">{recording.target_name}</div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Comms</div>
            <div className="file-modal__val file-modal__val--dim">
              {recording.to_number}
            </div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Mission Date</div>
            <div className="file-modal__val file-modal__val--dim">
              {formatDate(recording.created_at)}
            </div>
          </div>
        </div>

        {/* Tape deck */}
        <div className="tape-deck">
          {loading ? (
            <div className="tape-deck__loading">⌗ LOADING AUDIO INTEL...</div>
          ) : error ? (
            <div
              className="tape-deck__loading"
              style={{ color: "var(--color-red)" }}
            >
              {error}
            </div>
          ) : (
            <>
              <div className="tape-deck__reels">
                <TapeReel spinning={playing} />
                <div className="tape-deck__path">
                  <div className="tape-deck__path-line" />
                  <div className="tape-deck__path-label">TAPE</div>
                  <div className="tape-deck__path-line" />
                </div>
                <TapeReel spinning={playing} />
              </div>

              <div className="tape-deck__controls">
                <button
                  className="tape-deck__play"
                  onClick={togglePlay}
                  disabled={!audioUrl}
                >
                  {playing ? "▐▐" : "▶"}
                </button>
                <div
                  className={`tape-deck__status ${playing ? "tape-deck__status--playing" : ""}`}
                >
                  {playing ? "● PLAYING" : "● STOPPED"}
                </div>
              </div>

              {audioUrl && (
                <audio ref={audioRef} src={audioUrl} preload="auto" />
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="file-modal__footer">
          <div className="file-modal__footer-label">
            ELARA PRANK OPS — EYES ONLY
          </div>

          <div className="file-modal__footer-right">
            <button
              className="file-modal__download-btn"
              onClick={handleDownload}
              disabled={!audioUrl}
            >
              ↓ DOWNLOAD
            </button>

            {deleteStep === "idle" && (
              <button
                className="file-modal__delete-btn"
                onClick={() => setDeleteStep("confirm")}
              >
                ⚠ DESTROY
              </button>
            )}

            {deleteStep === "confirm" && (
              <div className="file-modal__confirm-bar">
                <span className="file-modal__confirm-text">ARE YOU SURE?</span>
                <button
                  className="file-modal__confirm-no"
                  onClick={() => setDeleteStep("idle")}
                >
                  ABORT
                </button>
                <button
                  className="file-modal__confirm-yes"
                  onClick={handleDelete}
                >
                  ⚠ DESTROY
                </button>
              </div>
            )}

            {deleteStep === "deleting" && (
              <div className="file-modal__deleting">
                <span className="file-modal__deleting-text">⌗ DESTROYING...</span>
              </div>
            )}

            <div className="file-modal__footer-tag">CLASSIFIED</div>
          </div>
        </div>

        {extracting && (
          <ExtractionOverlay
            recording={recording}
            onComplete={handleExtractionComplete}
          />
        )}
      </div>
    </div>
  );
}
